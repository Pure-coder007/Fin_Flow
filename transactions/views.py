from django.shortcuts import render
from user_authentication.models import *
from rest_framework.response import Response
from user_authentication.utils import wallet_funding_success
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.throttling import ScopedRateThrottle
from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import F, Subquery, OuterRef
from django.core.cache import cache
import logging
from django.db import transaction
from django.contrib.auth.hashers import check_password


logger = logging.getLogger(__name__)


# Get user wallet details
class GetWalletDetails(APIView):
    throttle_classes = [ScopedRateThrottle]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_scope = "get_wallet_details"

    def get(self, request):
        user = request.user

        user_details = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone_number": user.phone_number,
            "profile_pic": user.profile_pic,
            "state": user.state,
        }

        user_wallet = user.account
        return Response(
            {
                "account_number": user_wallet.account_number,
                "wallet_balance": user_wallet.wallet_balance,
                "book_balance": user_wallet.book_balance,
                "account_opening_date": user_wallet.date,
                "user": user_details,
            },
            status=status.HTTP_200_OK,
        )


# Fund wallet


class FundWallet(APIView):
    throttle_classes = [ScopedRateThrottle]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_scope = "fund_wallet"

    def post(self, request):
        user = request.user
        amount = request.data.get("amount")

        if not amount:
            return Response(
                {"error": "Amount is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            amount = float(amount)
        except ValueError:
            return Response(
                {"error": "Invalid amount format"}, status=status.HTTP_400_BAD_REQUEST
            )

        if amount <= 0:
            return Response(
                {"error": "Please enter a valid amount greater than 0"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.account.wallet_balance += amount
        user.account.book_balance += amount
        user.account.save()

        # Send confirmation email
        try:
            result = wallet_funding_success(user.email, amount)
            print("Wallet funding success email sent:", result)
        except Exception as e:
            logger.error(f"Failed to send wallet funding success email: {str(e)}")
            print(f"Failed to send wallet funding success email: {str(e)}")

        return Response(
            {
                "message": "Wallet funded successfully, a confirmation mail has been sent to your email. Thank you for using Fin flow to manage your finances",
                "amount": amount,
                "wallet_balance": user.account.wallet_balance,
                "book_balance": user.account.book_balance,
            },
            status=status.HTTP_200_OK,
        )


# Send money to another user
class SendMoney(APIView):
    throttle_classes = [ScopedRateThrottle]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    MAX_PIN_ATTEMPTS = 5
    LOCKOUT_MINUTES = 1

    def send_notifications(self, sender, receiver, amount, transaction_record):
        """Send notifications to both sender and receiver"""
        try:
            # Notification for sender
            Notification.objects.create(
                user=sender,
                title="Money Sent",
                message=f"You sent {amount} to {receiver.email}",
                data={
                    "type": "transaction",
                    "transaction_id": str(transaction_record.reference_id),
                },
            )

            # Notification for receiver
            Notification.objects.create(
                user=receiver,
                title="Money Received",
                message=f"You received {amount} from {sender.email}",
                data={
                    "type": "transaction",
                    "transaction_id": str(transaction_record.reference_id),
                },
            )

        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send notifications: {str(e)}")

    def post(self, request):
        user = request.user
        amount = request.data.get("amount")
        receiver_account_number = request.data.get("receiver_account")
        transaction_pin = request.data.get("transaction_pin")
        narration = request.data.get("narration", "")

        # Input validation
        if not all([amount, receiver_account_number, transaction_pin]):
            return Response(
                {"error": "Amount, receiver account and transaction pin are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if user is locked out
        pin_attempts, _ = TransactionPinAttempt.objects.get_or_create(user=user)

        if pin_attempts.is_locked():
            remaining_time = pin_attempts.remaining_lock_time()
            return Response(
                {
                    "error": f"Account temporarily locked. Try again in {int(remaining_time // 60)} minutes and {int(remaining_time % 60)} seconds",
                    "locked": True,
                    "remaining_time": remaining_time,
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            amount = float(amount)
        except ValueError:
            return Response(
                {"error": "Invalid amount format"}, status=status.HTTP_400_BAD_REQUEST
            )

        if amount <= 0:
            return Response(
                {"error": "Please enter a valid amount greater than 0"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            receiver_account = UserAccount.objects.get(
                account_number=receiver_account_number
            )
        except UserAccount.DoesNotExist:
            return Response(
                {"error": "Receiver account does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verify transaction pin
        if not user.account.transaction_pin or not check_password(
            transaction_pin, user.account.transaction_pin
        ):
            pin_attempts.increment_attempt()
            remaining_attempts = self.MAX_PIN_ATTEMPTS - pin_attempts.attempts

            if pin_attempts.attempts >= self.MAX_PIN_ATTEMPTS:
                return Response(
                    {
                        "error": f"Too many failed attempts. Account locked for {self.LOCKOUT_MINUTES} minutes",
                        "locked": True,
                        "remaining_attempts": 0,
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            return Response(
                {
                    "error": f"Invalid transaction pin. {remaining_attempts} attempts remaining",
                    "remaining_attempts": remaining_attempts,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Reset attempts on successful pin entry
        pin_attempts.reset_attempts()

        # Rest of your transaction logic...
        if user.account.wallet_balance < amount:
            return Response(
                {"error": "Insufficient wallet balance"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.account == receiver_account:
            return Response(
                {"error": "Cannot send money to yourself"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            try:
                user.account.wallet_balance -= amount
                user.account.book_balance -= amount
                user.account.save()

                receiver_account.wallet_balance += amount
                receiver_account.book_balance += amount
                receiver_account.save()

                transaction_record = Transaction.objects.create(
                    sender=user.account,
                    receiver=receiver_account,
                    amount=amount,
                    transaction_type=TransactionType.TRANSFER.value,  # Using Enum value
                    narration=narration if narration else "null",
                )

                # Send notifications
                self.send_notifications(
                    user, receiver_account.user, amount, transaction_record
                )

                return Response(
                    {
                        "message": f"Money sent successfully to {receiver_account.user.get_full_name()}",
                        "transaction_reference": transaction_record.reference_id,
                        "session_id": transaction_record.session_id,
                        "new_balance": user.account.wallet_balance,
                        "narration": transaction_record.narration,
                        "receiver_details": {
                            "account_number": receiver_account.account_number,
                            "name": receiver_account.user.get_full_name(),
                            "email": receiver_account.user.email,
                            "amount_received": amount,
                        },
                    },
                    status=status.HTTP_200_OK,
                )

            except Exception as e:
                return Response(
                    {"error": f"Transaction failed: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
