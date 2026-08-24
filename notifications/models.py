from django.db import models
from django.conf import settings
from django.utils import timezone


class Notification(models.Model):
    """User notification system for job and payment updates."""
    
    NOTIFICATION_TYPE_CHOICES = [
        # Job related
        ('JOB_COMPLETED', 'Job Completed by Worker'),
        ('JOB_STARTED', 'Job Started'),
        ('JOB_CANCELLED', 'Job Cancelled'),
        ('JOB_WORKER_UNAVAILABLE', 'Worker Unavailable at Requested Time'),
        ('JOB_CONFLICT', 'Job Time Conflict'),
        
        # Application related
        ('WORKER_APPLIED', 'Worker Applied for Your Request'),
        ('APPLICATION_ACCEPTED', 'Your Application Was Accepted'),
        ('APPLICATION_REJECTED', 'Your Application Was Rejected'),
        
        # Payment related
        ('JOB_PAYMENT_SUBMITTED', 'Payment Submitted for Job'),
        ('PAYMENT_VERIFIED', 'Payment Verified - You Received Payment'),
        ('PAYMENT_PENDING', 'Payment Pending Verification'),
        
        # Worker approval/status
        ('WORKER_APPROVED', 'Your Worker Account Has Been Approved'),
        ('WORKER_REJECTED', 'Your Worker Account Application Was Rejected'),
        ('WORKER_PROFILE_UPDATED', 'Your Worker Profile Was Updated'),
        
        # General
        ('GENERAL', 'General Notification'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPE_CHOICES,
        default='GENERAL'
    )
    is_read = models.BooleanField(default=False)
    
    # Optional relations to track what the notification is about
    job = models.ForeignKey(
        'bookings.Job',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    payment = models.ForeignKey(
        'payments.Payment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    
    # Related user (the person who triggered the notification)
    related_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications_about_me'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.email}"

    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read', 'updated_at'])
            return True
        return False

    @staticmethod
    def create_notification(user, title, message, notification_type, job=None, payment=None, related_user=None):
        """Helper method to create and save a notification."""
        return Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            job=job,
            payment=payment,
            related_user=related_user,
        )
