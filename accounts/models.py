from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('worker', 'Worker'),
        ('admin', 'Admin'),
    )
    
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
        return f"{self.get_full_name() or self.username} ({dict(self.ROLE_CHOICES).get(self.role, self.role)})"
    
    @property
    def is_worker_approved(self):
        """Check if worker is approved."""
        return self.role == 'worker' and self.worker_status == 'APPROVED'
    
    @property
    def is_customer_active(self):
        """Check if customer is active."""
        return self.role == 'customer' and self.customer_status == 'ACTIVE'

    class Meta:
        indexes = [
            models.Index(fields=['role', 'created_at']),
            models.Index(fields=['is_blocked']),
        ]