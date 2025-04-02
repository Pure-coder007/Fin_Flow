from django.shortcuts import render
from django.rest_framework.response import Response
from django.rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from user_authentication.models import User
import cloudinary 
import cloudinary.uploader
from rest_framework import generics, permissions
from datetime import datetime, timedelta
from django.utils.timezone import now
import cloudinary.api 
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import os, random, string
from dotenv import load_dotenv
from constants import CLOUD_NAME, API_KEY, API_SECRET

load_dotenv()

import cloudinary
import cloudinary.uploader
import cloudinary.api

cloudinary.config( 
    cloud_name=CLOUD_NAME, 
    api_key=API_KEY, 
    api_secret=API_SECRET
)


def generate_account():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    



class RegisterView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        account_number = generate_account()
        phone_number = request.data.get('phone_number')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        profile_pic = request.data.get('profile_pic')
        bvn = request.data.get('bvn')
        nin = request.data.get('nin')
        transaction_pin = request.data.get('transaction_pin')
        confirm_transaction_pin = request.data.get('confirm_transaction_pin')
        
        try:
            validate_password(password)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if password != confirm_password:
            return Response({'error': 'Passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

        if transaction_pin != confirm_transaction_pin:
            return Response({'error': 'Transaction pins do not match'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        cloudinary_url = None
        
        if profile_pic:
            try:
                upload_result = cloudinary.uploader.upload(profile_pic)
                cloudinary_url = upload_result.get['secure_url']
            except Exception as e:
                return Response({'error': 'Failed to upload profile picture'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            email=email,
            password=password,
            account_number=account_number,
            phone_num=phone_number,
            first_name=first_name,
            last_name=last_name,
            profile_pic=cloudinary_url,
            bvn=bvn,
            nin=nin,
            transaction_pin=transaction_pin,
        )

        return Response({'message': 'User registered successfully', 'email': user.email, 'account_number': user.account_number, 'first_name': user.first_name, 'last_name': user.last_name, 'profile_pic': user.profile_pic}, status=status.HTTP_201_CREATED)