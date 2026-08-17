from django.db import models
from django.conf import settings
from django.utils import timezone


class Notification(models.Model):
    """User notification system for job and payment updates."""
    
    NOTIFICATION_TYPE_CHOICES = [
        ('JOB_COMPLETED', 'Job Completed by Worker'),
        ('JOB_PAYMENT_SUBMITTED', 'Payment Submitted for Job'),
        ('PAYMENT_VERIFIED', 'Payment Verified - You Received Payment'),
        ('PAYMENT_PENDING', 'Payment Pending Verification'),
        ('JOB_STARTED', 'Job Started'),
        ('JOB_CANCELLED', 'Job Cancelled'),
        ('WORKER_APPLIED', 'Worker Applied for Your Request'),
        ('APPLICATION_ACCEPTED', 'Your Application Was Accepted'),
        ('APPLICATION_REJECTED', 'Your Application Was Rejected'),
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
        max_length=30,
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
        return f"{self.title} - {self.user.username}"

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
