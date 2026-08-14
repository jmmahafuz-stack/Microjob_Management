from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Avg

from reviews.models import Review
from services.models import Service, Category


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
    
    # Categories this worker can work in (ManyToMany)
    categories = models.ManyToManyField(Category, related_name='workers', blank=True)
    
    # Keep old fields for backward compatibility
    service_category = models.CharField(max_length=50, blank=True, null=True)
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='workers'
    )
    
    # Professional information
    bio = models.TextField(blank=True, null=True)
    skills = models.TextField(blank=True, help_text="Comma-separated skills")
    experience_years = models.PositiveIntegerField(default=0)
    service_area = models.CharField(max_length=150, blank=True, null=True)
    languages = models.CharField(max_length=150, blank=True, null=True)
    portfolio_link = models.URLField(blank=True, null=True)
    id_verification_document = models.FileField(upload_to='worker_documents/', blank=True, null=True)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    
    # Preferences
    response_time = models.CharField(max_length=50, default='Within 24 hours')
    default_preferred_contact = models.CharField(
        max_length=20,
        choices=[('Email', 'Email'), ('Phone', 'Phone'), ('SMS', 'SMS')],
        default='Email'
    )
    
    # Status fields
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
    
    # Cached statistics
    completed_jobs = models.PositiveIntegerField(default=0)
    average_rating_cached = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Earnings tracking
    pending_earnings = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text="Earnings from completed but unpaid jobs"
    )
    available_earnings = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text="Earnings available for withdrawal after payment is confirmed"
    )
    withdrawn_earnings = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text="Total amount withdrawn by worker"
    )
    
    # Payout preferences
    payout_method = models.CharField(
        max_length=50,
        choices=[
            ('Bank Account', 'Bank Account'),
            ('BKash', 'BKash'),
            ('Nagad', 'Nagad'),
            ('Rocket', 'Rocket'),
        ],
        default='Bank Account',
        blank=True
    )
    payout_account_holder = models.CharField(max_length=255, blank=True)
    payout_account_number = models.CharField(max_length=255, blank=True)
    payout_bank_name = models.CharField(max_length=255, blank=True)
    payout_branch = models.CharField(max_length=255, blank=True)
    
    # Payment method phone numbers (for bKash/Nagad/Rocket)
    bkash_number = models.CharField(
        max_length=20, blank=True, default='',
        help_text="bKash phone number for receiving payments (e.g., 01XXXXXXXXX)"
    )
    nagad_number = models.CharField(
        max_length=20, blank=True, default='',
        help_text="Nagad phone number for receiving payments (e.g., 01XXXXXXXXX)"
    )
    rocket_number = models.CharField(
        max_length=20, blank=True, default='',
        help_text="Rocket phone number for receiving payments (e.g., 01XXXXXXXXX)"
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

    def get_earnings_breakdown(self):
        """Return breakdown of earnings by status"""
        return {
            'pending': self.pending_earnings,
            'available': self.available_earnings,
            'withdrawn': self.withdrawn_earnings,
            'total_earned': self.pending_earnings + self.available_earnings + self.withdrawn_earnings,
        }

    def sync_earnings_from_payments(self):
        """Reconcile worker earnings with actual payment records."""
        from payments.models import Payment

        payments = Payment.objects.filter(job__worker=self.user)

        pending_total = payments.filter(payment_status='Pending').aggregate(
            total=models.Sum('worker_amount')
        )['total'] or Decimal('0.00')

        available_total = payments.filter(
            payment_status='Verified',
            worker_payout_status='Available'
        ).aggregate(total=models.Sum('worker_amount'))['total'] or Decimal('0.00')

        withdrawn_total = payments.filter(
            payment_status='Verified',
            worker_payout_status='Withdrawn'
        ).aggregate(total=models.Sum('worker_amount'))['total'] or Decimal('0.00')

        total_earned = payments.filter(
            payment_status__in=['Pending', 'Verified']
        ).aggregate(total=models.Sum('worker_amount'))['total'] or Decimal('0.00')

        self.pending_earnings = pending_total
        self.available_earnings = available_total
        self.withdrawn_earnings = withdrawn_total
        self.total_earnings = total_earned

        self.save(update_fields=['pending_earnings', 'available_earnings', 'withdrawn_earnings', 'total_earnings'])

        return self.get_earnings_breakdown()

    def update_earnings_from_payment(self, amount, is_confirmed=False):
        """Update worker earnings when payment is processed"""
        if is_confirmed:
            self.available_earnings = models.F('available_earnings') + amount
        else:
            self.pending_earnings = models.F('pending_earnings') + amount
        self.total_earnings = models.F('total_earnings') + amount
        self.save(update_fields=['pending_earnings', 'available_earnings', 'total_earnings'])

    def confirm_pending_earnings(self, amount):
        """Move earnings from pending to available after payment confirmation"""
        self.pending_earnings = models.F('pending_earnings') - amount
        self.available_earnings = models.F('available_earnings') + amount
        self.save(update_fields=['pending_earnings', 'available_earnings'])
