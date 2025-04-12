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

from enum import Enum

class TransactionType(Enum):
    TRANSFER = 'Transfer'
    DEPOSIT = 'Deposit'
    WITHDRAWAL = 'Withdrawal'




def reference_code_generator(size=15, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def session_id_generator(size=15, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))




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
    
    

class TransactionPinAttempt(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="pin_attempts"
    )
    attempts = models.PositiveIntegerField(default=0)
    last_attempt = models.DateTimeField(auto_now=True)
    locked_until = models.DateTimeField(null=True, blank=True)

    def is_locked(self):
        if self.locked_until:
            if timezone.now() < self.locked_until:
                return True
            else:
                # Auto-reset when lock expires
                self.reset_attempts()
                return False
        return False

    def remaining_lock_time(self):
        if self.locked_until:
            remaining = self.locked_until - timezone.now()
            return max(remaining.total_seconds(), 0)
        return 0

    def reset_attempts(self):
        self.attempts = 0
        self.locked_until = None
        self.save()

    def increment_attempt(self):  # NOW PROPERLY INDENTED INSIDE THE CLASS
        self.attempts += 1
        self.last_attempt = timezone.now()
        
        # Lock for 5 minutes after 3 failed attempts
        if self.attempts >= 3:
            self.locked_until = timezone.now() + timedelta(minutes=5)
        self.save()
    
    

class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name="receiver")
    amount = models.FloatField()
    reference_id = models.CharField(max_length=255, unique=True, default=reference_code_generator)
    session_id = models.CharField(max_length=255, unique=True, default=session_id_generator)
    date = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(
        max_length=20,
        choices=[(tag.value, tag.name) for tag in TransactionType]
    )
    narration = models.CharField(max_length=255, null=True)
    
    
    def __str__(self):
        return f"Transaction for {self.transaction_type} - {self.amount}"
    
    
    
    

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    message = models.TextField()
    data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    