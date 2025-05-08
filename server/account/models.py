from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
import uuid
from django.utils import timezone
from django.core.exceptions import ValidationError

class CustomUserManager(BaseUserManager):

    def validate_phone(self, phone):
        """
        Validate and normalize phone number
        Remove non-digit characters and ensure proper formatting
        """
        # Remove all non-digit characters
        cleaned_phone = ''.join(filter(str.isdigit, phone))
        
        # Validate phone number length (adjust as needed)
        if len(cleaned_phone) < 9 or len(cleaned_phone) > 15:
            raise ValidationError("Invalid phone number length")
        
        # Ensure Ethiopian phone number format
        if not cleaned_phone.startswith('251'):
            # If starts with 0, replace with 251
            if cleaned_phone.startswith('0'):
                cleaned_phone = '251' + cleaned_phone[1:]
            else:
                # If no country code, prepend 251
                cleaned_phone = '251' + cleaned_phone
        
        return cleaned_phone

    def create_user(self, username, phone, **extra_fields):
        if not username:
            raise ValueError("The username field must be set")
        if phone:
            try:
                phone = self.validate_phone(phone)
            except ValidationError as e:
                raise ValueError(f"Phone validation error: {str(e)}")
        
        user = self.model(username=username, phone=phone, **extra_fields)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        user = self.create_user(username, None, **extra_fields)
        user.set_password(password)    
        user.save()
        return user
    def get_by_natural_key(self, username):
        return self.get(username=username)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tg_id = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=255, blank=True, default="")
    last_name = models.CharField(max_length=255, blank=True, default="")
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_seen = models.DateTimeField(null = True, blank=True)
    banned_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='banned_users')
    unbanned_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='unbanned_users')
    banned_at = models.DateTimeField(null=True, blank=True)
    unbanned_at = models.DateTimeField(null=True, blank=True)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def natural_key(self):
        return (self.username,)

    def __str__(self):
        return self.username