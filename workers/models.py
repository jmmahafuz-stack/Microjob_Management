from django.conf import settings
from django.db import models
from django.db.models import Avg

from reviews.models import Review
from services.models import Service


class WorkerProfile(models.Model):
    TRAINING_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Training', 'In Training'),
        ('Completed', 'Completed'),
    ]

    VERIFICATION_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    PAYOUT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='worker_profile'
    )
    service_category = models.CharField(max_length=50, blank=True, null=True)
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='workers'
    )
    skills = models.CharField(max_length=200)
    experience = models.CharField(max_length=100, blank=True, null=True)
    service_area = models.CharField(max_length=150, blank=True, null=True)
    languages = models.CharField(max_length=150, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    portfolio_link = models.URLField(blank=True, null=True)
    id_verification_document = models.FileField(upload_to='worker_documents/', blank=True, null=True)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    response_time = models.CharField(max_length=50, default='Within 24 hours')
    payout_status = models.CharField(
        max_length=20,
        choices=PAYOUT_STATUS_CHOICES,
        default='Pending'
    )
    training_status = models.CharField(
        max_length=20,
        choices=TRAINING_STATUS_CHOICES,
        default='Pending'
    )
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='Pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.verification_status}"

    @property
    def average_rating(self):
        return Review.objects.filter(worker=self.user).aggregate(avg=Avg('rating'))['avg'] or 0

    @property
    def completion_rate(self):
        total = self.user.worker_bookings.count()
        if not total:
            return 0
        completed = self.user.worker_bookings.filter(status='Completed').count()
        return round((completed / total) * 100, 1)

    @property
    def is_verified(self):
        return self.verification_status == 'Approved'

    @property
    def badge_label(self):
        if self.is_verified and self.average_rating >= 4.5:
            return 'Top Rated'
        if self.is_verified:
            return 'Verified Worker'
        return 'Pending Review'
