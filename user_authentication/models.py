from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import MinLengthValidator
from django.conf import settings
from datetime import datetime, timedelta




class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)
    
    
    
class User(AbstractUser):
    email=models.EmailField(max_length=255,unique=True)
    username=None
    password=models.CharField(max_length=255,validators=[MinLengthValidator(8)])
    account_number=BigIntegerField(unique=True)
    transaction_pin=BigIntegerField(max_length=4, validators=[MinLengthValidator(4)])
    bvn=BigIntegerField(max_length=20, validators=[MinLengthValidator(11)], unique=True, null=True)
    nin=BigIntegerField(max_length=20, validators=[MinLengthValidator(11)], unique=True, null=True)
    phone_num=BigIntegerField(max_length=20, validators=[MinLengthValidator(11)])
    profile_pic=models.URLField(max_length=255, null=False)
    first_name-models.CharField(max_length=255, null=False)
    last_name=models.CharField(max_length=255, null=False)
    is_active=models.BooleanField(default=True)
    
    objects=CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.email, 
    