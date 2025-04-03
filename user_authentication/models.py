from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import MinLengthValidator
from django.conf import settings
from datetime import datetime, timedelta
import string, random, uuid


# Random id
# def random_id():
#     return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


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
    is_active = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    
    def token(self):
        pass


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
        max_length=20,
        validators=[MinLengthValidator(11)],
        unique=True,
        blank=True,
        null=True,
    )
    nin = models.CharField(
        max_length=20,
        validators=[MinLengthValidator(11)],
        unique=True,
        blank=True,
        null=True,
    )
    transaction_pin = models.CharField(
        max_length=4, validators=[MinLengthValidator(4)], blank=True, null=True
    )

    # Account Levels as Boolean Fields
    level_1 = models.BooleanField(default=True)  # Default to Level 1
    level_2 = models.BooleanField(default=False)
    level_3 = models.BooleanField(default=False)

    book_balance = models.FloatField(default=0.0)

    def __str__(self):
        return f"UserAccount for ({self.user.email})"
