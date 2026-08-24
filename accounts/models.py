from django.db import models

# Create your models here.
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('worker', 'Worker'),
        ('admin', 'Admin'),
    )

    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=False, null=True)

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __init__(self, *args, **kwargs):
        legacy_verified = kwargs.pop('is_verified_worker', None)
        if legacy_verified is not None:
            kwargs['worker_status'] = 'APPROVED' if legacy_verified else 'PENDING'
        super().__init__(*args, **kwargs)
    
    WORKER_STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('BLOCKED', 'Blocked'),
    ]
    
    CUSTOMER_STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('BLOCKED', 'Blocked'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True
    )
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=(
            ('Email', 'Email'),
            ('SMS', 'SMS'),
        ),
        default='Email'
    )
    receive_notifications = models.BooleanField(default=True)

    # Status fields
    is_blocked = models.BooleanField(default=False)
    worker_status = models.CharField(
        max_length=20,
        choices=WORKER_STATUS_CHOICES,
        default='PENDING',
        null=True,
        blank=True,
        help_text="Status for worker accounts only"
    )
    customer_status = models.CharField(
        max_length=20,
        choices=CUSTOMER_STATUS_CHOICES,
        default='ACTIVE',
        null=True,
        blank=True,
        help_text="Status for customer accounts only"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.role == 'admin':
            self.is_staff = True
            self.is_superuser = True
        else:
            self.is_staff = False
            self.is_superuser = False

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_full_name() or self.email} ({dict(self.ROLE_CHOICES).get(self.role, self.role)})"

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    @property
    def is_verified_worker(self):
        """Backward-compatible alias for the worker approval status."""
        return self.role == 'worker' and self.worker_status == 'APPROVED'

    @is_verified_worker.setter
    def is_verified_worker(self, value):
        self.worker_status = 'APPROVED' if value else 'PENDING'

    @property
    def is_worker_approved(self):
        """Check if worker is approved."""
        return self.is_verified_worker

    @property
    def is_customer_active(self):
        """Check if customer is active."""
        return self.role == 'customer' and self.customer_status == 'ACTIVE'

    class Meta:
        indexes = [
            models.Index(fields=['role', 'created_at']),
            models.Index(fields=['is_blocked']),
        ]