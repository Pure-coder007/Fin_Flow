from django.db import transaction, IntegrityError
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import ScopedRateThrottle
from user_authentication.models import User, UserAccount
import cloudinary.uploader
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
import random, re
import string
import logging
from constants import CLOUD_NAME, API_KEY, API_SECRET

logger = logging.getLogger(__name__)

cloudinary.config(
    api_key=API_KEY,
    cloud_name=CLOUD_NAME,
    api_secret=API_SECRET
)

class RegisterView(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "register"

    def post(self, request):
        try:
            data = request.data
            
            # Validate required fields
            required_fields = [
                'email', 'password', 'confirm_password',
                'phone_number', 'transaction_pin',
                'confirm_transaction_pin', 'profile_pic'
            ]
            
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                return Response(
                    {"error": f"Missing required fields: {', '.join(missing_fields)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate email format
            if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
                return Response(
                    {"error": "Invalid email format"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Password validation
            if data['password'] != data['confirm_password']:
                return Response(
                    {"error": "Passwords do not match"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                validate_password(data['password'])
            except ValidationError as e:
                return Response(
                    {"error": ", ".join(e.messages)},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Transaction PIN validation
            if data['transaction_pin'] != data['confirm_transaction_pin']:
                return Response(
                    {"error": "Transaction pins do not match"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if len(data['transaction_pin']) != 4 or not data['transaction_pin'].isdigit():
                return Response(
                    {"error": "Transaction pin must be 4 digits"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Phone number validation (Nigeria)
            if not data['phone_number'].startswith('+234') or len(data['phone_number']) != 14:
                return Response(
                    {"error": "Phone must be in +234XXXXXXXXXX format (13 digits total)"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if user exists
            if User.objects.filter(email=data['email']).exists():
                return Response(
                    {"error": "Email already registered"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Handle profile picture upload
            try:
                upload_result = cloudinary.uploader.upload(data['profile_pic'])
                profile_pic_url = upload_result["secure_url"]
            except Exception as e:
                logger.error(f"Profile picture upload failed: {str(e)}")
                return Response(
                    {"error": "Profile picture upload failed"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get NIN and BVN values from data (convert empty strings to None)
            nin_value = data.get('nin') or None
            bvn_value = data.get('bvn') or None

            # Validate NIN length if provided
            if nin_value and len(nin_value) < 11:
                return Response(
                    {"error": "NIN must be 11 digits if provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Validate BVN length if provided
            if bvn_value and len(bvn_value) < 11:
                return Response(
                    {"error": "BVN must be 11 digits if provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create user and account
            with transaction.atomic():
                user = User.objects.create_user(
                    email=data['email'],
                    password=data['password'],
                    phone_number=data['phone_number'],
                    first_name=data.get('first_name', ''),
                    last_name=data.get('last_name', ''),
                    profile_pic=profile_pic_url,
                    state=data.get('state', ''),
                )

                # Only hash NIN/BVN if they exist
                hashed_bvn = make_password(bvn_value) if bvn_value else None
                hashed_nin = make_password(nin_value) if nin_value else None

                account = UserAccount.objects.create(
                    user=user,
                    bvn=hashed_bvn,
                    nin=hashed_nin,
                    transaction_pin=make_password(data['transaction_pin']),
                    account_number=self.generate_account_number(),
                    wallet_balance=100000,
                    book_balance=100000,
                )

                return Response(
                    {
                        "success": True,
                        "message": "Registration successful",
                        "data": {
                            "account_number": account.account_number,
                            "email": user.email,
                            "full_name": f"{user.first_name} {user.last_name}",
                            "phone_number": user.phone_number,
                            "profile_pic": user.profile_pic,
                            "state": user.state
                        }
                    },
                    status=status.HTTP_201_CREATED
                )

        except IntegrityError as e:
            logger.error(f"Registration integrity error: {str(e)}")
            if 'nin' in str(e):
                return Response(
                    {"error": "This NIN is already registered"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif 'bvn' in str(e):
                return Response(
                    {"error": "This BVN is already registered"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {"error": "Registration failed due to data conflict"},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred during registration"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def generate_account_number(self):
        """Generate random 10-digit account number that doesn't exist"""
        while True:
            account_number = ''.join(random.choices(string.digits, k=10))
            if not UserAccount.objects.filter(account_number=account_number).exists():
                return account_number