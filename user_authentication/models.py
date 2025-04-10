from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import MinLengthValidator
from django.conf import settings
from datetime import datetime, timedelta
import string, random, uuid
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255, unique=True)
    username = None
    password = models.CharField(max_length=255, validators=[MinLengthValidator(8)])
    phone_number = models.CharField(max_length=20, validators=[MinLengthValidator(11)])
    state = models.CharField(max_length=255, null=False)
    profile_pic = models.URLField(max_length=255, null=False)
    is_verified = models.BooleanField(default=False)
    first_name = models.CharField(max_length=255, null=False)
    last_name = models.CharField(max_length=255, null=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, auto_now=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} {self.first_name} {self.last_name}"

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        
        

class LoginAttempt(models.Model):
    email = models.EmailField()
    failed_attempts = models.PositiveIntegerField(default=0)
    last_attempt_time = models.DateTimeField(auto_now=True)

    def is_locked_out(self):
        if self.failed_attempts >= 5:
            return self.get_remaining_lockout_time() > timedelta(seconds=0)
        return False

    def get_remaining_lockout_time(self):
        lockout_time = self.last_attempt_time + timedelta(minutes=5)
        return lockout_time - timezone.now()

    def reset_attempts(self):
        self.failed_attempts = 0
        self.save()



class UserAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="account"
    )
    wallet_balance = models.FloatField(default=0.0)
    account_number = models.CharField(
        max_length=255, unique=True
    )  # Now an actual account number
    date = models.DateTimeField(auto_now_add=True)
    bvn = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(11)],
        unique=True,
        blank=True,
        null=True,
    )
    nin = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(11)],
        unique=True,
        blank=True,
        null=True,
    )
    transaction_pin = models.CharField(
        max_length=255, validators=[MinLengthValidator(4)], blank=True, null=True
    )

    # Account Levels as Boolean Fields
    level_1 = models.BooleanField(default=True)  # Default to Level 1
    level_2 = models.BooleanField(default=False)
    level_3 = models.BooleanField(default=False)

    book_balance = models.FloatField(default=0.0)

    def __str__(self):
        return f"UserAccount for ({self.user.email})"



class OneTimePassword(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code=models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return f"{self.user} - {self.code}"
    