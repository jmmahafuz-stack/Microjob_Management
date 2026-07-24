from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('worker', 'Worker'),
        ('admin', 'Admin'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
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

    is_verified_worker = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.role == 'admin':
            self.is_staff = True
            self.is_superuser = True
        else:
            self.is_staff = False
            self.is_superuser = False

        if self.role != 'worker':
            self.is_verified_worker = False

        super().save(*args, **kwargs)

    def __str__(self):
        return self.username