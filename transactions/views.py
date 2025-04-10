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
        return Response({
            "account_number": user_wallet.account_number,
            "wallet_balance": user_wallet.wallet_balance,
            "book_balance": user_wallet.book_balance,
            "account_opening_date": user_wallet.date,
            "user": user_details
        }, status=status.HTTP_200_OK)




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
            return Response({"error": "Amount is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            amount = float(amount)
        except ValueError:
            return Response({"error": "Invalid amount format"}, status=status.HTTP_400_BAD_REQUEST)
        
        if amount <= 0:
            return Response({"error": "Please enter a valid amount greater than 0"}, status=status.HTTP_400_BAD_REQUEST)
        
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

            
        return Response({"message": "Wallet funded successfully, a confirmation mail has been sent to your email. Thank you for using Fin flow to manage your finances", "amount": amount, 
        "wallet_balance": user.account.wallet_balance,
        "book_balance": user.account.book_balance}, status=status.HTTP_200_OK)
        
        
    