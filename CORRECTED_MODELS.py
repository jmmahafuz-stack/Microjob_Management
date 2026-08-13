# Corrected Models for MJMS

## This file contains the corrected model definitions that should replace
## or complement your existing models.

# ==================================================
# ACCOUNTS APP - CORRECTED CUSTOM USER
# ==================================================

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Corrected Custom User Model with proper status tracking."""
    
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('worker', 'Worker'),
        ('admin', 'Admin'),
    ]
    
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

    # Basic fields
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)  # NEW
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    # Status fields
    is_blocked = models.BooleanField(default=False)  # NEW
    worker_status = models.CharField(  # CHANGED: was is_verified_worker
        max_length=20,
        choices=WORKER_STATUS_CHOICES,
        default='PENDING',
        null=True,
        blank=True,
        help_text="Status for worker accounts only"
    )
    customer_status = models.CharField(  # NEW
        max_length=20,
        choices=CUSTOMER_STATUS_CHOICES,
        default='ACTIVE',
        null=True,
        blank=True,
        help_text="Status for customer accounts only"
    )
    
    # Preferences
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=[('Email', 'Email'), ('SMS', 'SMS')],
        default='Email'
    )
    receive_notifications = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """Auto-set staff/superuser based on role."""
        if self.role == 'admin':
            self.is_staff = True
            self.is_superuser = True
        else:
            self.is_staff = False
            self.is_superuser = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    def get_role_display(self):
        return dict(self.ROLE_CHOICES).get(self.role)
    
    @property
    def is_worker_approved(self):
        """Check if worker is approved."""
        return self.role == 'worker' and self.worker_status == 'APPROVED'
    
    @property
    def is_customer_active(self):
        """Check if customer is active."""
        return self.role == 'customer' and self.customer_status == 'ACTIVE'
    
    class Meta:
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=['role', 'created_at']),
            models.Index(fields=['is_blocked']),
        ]


# ==================================================
# SERVICES APP - CATEGORY MODEL (NEW)
# ==================================================

class Category(models.Model):
    """Service categories like Plumbing, Electrical, etc."""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Emoji or icon class")
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


# ==================================================
# WORKERS APP - UPDATED WORKER PROFILE
# ==================================================

class WorkerProfile(models.Model):
    """Worker Profile with category selection."""
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='worker_profile')
    
    # Services/Categories (ManyToMany)
    categories = models.ManyToManyField(Category, related_name='workers', blank=True)
    
    # Professional info
    bio = models.TextField(blank=True)
    skills = models.TextField(blank=True, help_text="Comma-separated skills")
    experience_years = models.PositiveIntegerField(default=0)
    service_area = models.CharField(max_length=200, blank=True, help_text="Areas of service")
    languages = models.CharField(max_length=150, blank=True)
    portfolio_link = models.URLField(blank=True)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    
    # Documents
    id_verification_document = models.FileField(upload_to='worker_documents/', blank=True)
    
    # Settings
    response_time = models.CharField(max_length=50, default='Within 24 hours')
    default_preferred_contact = models.CharField(
        max_length=20,
        choices=[('Email', 'Email'), ('Phone', 'Phone'), ('SMS', 'SMS')],
        default='Email'
    )
    
    # Stats (calculated/cached)
    completed_jobs = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} (Worker)"
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'average_rating']),
        ]


# ==================================================
# BOOKINGS APP - CORRECTED MODELS
# ==================================================

class ServiceRequest(models.Model):
    """Customer creates a service request (formerly Booking)."""
    
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('APPLICATIONS_RECEIVED', 'Applications Received'),
        ('WORKER_SELECTED', 'Worker Selected'),
        ('WORKER_ACCEPTED', 'Worker Accepted'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('PAYMENT_PENDING', 'Payment Pending'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
        ('DISPUTED', 'Disputed'),
    ]
    
    customer = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='service_requests',
        limit_choices_to={'role': 'customer'}
    )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='service_requests')
    
    # Service details
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    
    # Schedule
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    
    # Budget
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status tracking
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='OPEN')
    selected_worker = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='selected_service_requests',
        limit_choices_to={'role': 'worker'}
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.customer.username}"
    
    @property
    def is_open_for_applications(self):
        return self.status in ['OPEN', 'APPLICATIONS_RECEIVED']
    
    @property
    def can_be_cancelled(self):
        return self.status not in ['PAID', 'DISPUTED']


class JobApplication(models.Model):
    """Worker applies for a service request."""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('WITHDRAWN', 'Withdrawn'),
    ]
    
    service_request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    worker = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='job_applications',
        limit_choices_to={'role': 'worker'}
    )
    
    # Application details
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['service_request', 'worker']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['service_request', 'status']),
            models.Index(fields=['worker', 'status']),
        ]
    
    def __str__(self):
        return f"{self.worker.username} applied for {self.service_request.title}"


class Job(models.Model):
    """Actual job after worker is selected."""
    
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('PAYMENT_PENDING', 'Payment Pending'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    service_request = models.OneToOneField(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name='job'
    )
    worker = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='jobs',
        limit_choices_to={'role': 'worker'}
    )
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='OPEN')
    
    # Timeline
    assigned_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['worker', 'status']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Job: {self.service_request.title}"


# ==================================================
# PAYMENTS APP - CORRECTED PAYMENT MODEL
# ==================================================

from decimal import Decimal

class Payment(models.Model):
    """Payment with commission tracking."""
    
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('MOBILE_BANKING', 'Mobile Banking'),
        ('CARD', 'Card'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]
    
    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name='payment')
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE, related_name='payment', null=True)
    
    customer = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='payments_as_customer',
        limit_choices_to={'role': 'customer'}
    )
    worker = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='payments_as_worker',
        limit_choices_to={'role': 'worker'}
    )
    
    # Amount breakdown
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('10.00'))  # percentage
    platform_commission = models.DecimalField(max_digits=12, decimal_places=2)  # calculated: gross * (rate/100)
    worker_amount = models.DecimalField(max_digits=12, decimal_places=2)  # calculated: gross - commission
    
    # Payment details
    transaction_id = models.CharField(max_length=255, unique=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    receipt = models.FileField(upload_to='payment_receipts/', blank=True)
    
    # Timestamps
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'payment_status']),
            models.Index(fields=['worker', 'payment_status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Payment {self.transaction_id}: {self.gross_amount}"
    
    def save(self, *args, **kwargs):
        """Auto-calculate commission breakdown."""
        if self.gross_amount and self.commission_rate:
            self.platform_commission = self.gross_amount * (self.commission_rate / Decimal('100'))
            self.worker_amount = self.gross_amount - self.platform_commission
        super().save(*args, **kwargs)


# ==================================================
# NOTIFICATIONS APP (NEW)
# ==================================================

class Notification(models.Model):
    """User notifications."""
    
    NOTIFICATION_TYPE_CHOICES = [
        ('WORKER_APPLIED', 'Worker Applied'),
        ('WORKER_SELECTED', 'Worker Selected'),
        ('WORKER_ACCEPTED', 'Worker Accepted'),
        ('JOB_COMPLETED', 'Job Completed'),
        ('PAYMENT_RECEIVED', 'Payment Received'),
        ('REVIEW_REMINDER', 'Review Reminder'),
        ('APPROVAL_STATUS', 'Approval Status'),
        ('NEW_JOB', 'New Job Available'),
        ('COMPLAINT_UPDATE', 'Complaint Update'),
        ('GENERAL', 'General Notification'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES)
    
    # Relations
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.SET_NULL, null=True, blank=True)
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True)
    related_user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications_about_me'
    )
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"


# ==================================================
# COMPLAINTS APP - CORRECTED MODEL
# ==================================================

class Complaint(models.Model):
    """Complaint/Dispute tracking."""
    
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('UNDER_REVIEW', 'Under Review'),
        ('RESOLVED', 'Resolved'),
        ('REJECTED', 'Rejected'),
    ]
    
    customer = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='complaints_filed',
        limit_choices_to={'role': 'customer'}
    )
    worker = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='complaints_against',
        limit_choices_to={'role': 'worker'}
    )
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='complaints')
    
    subject = models.CharField(max_length=200)
    description = models.TextField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    admin_response = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"Complaint: {self.subject}"


# ==================================================
# COMMISSION SETTING MODEL
# ==================================================

class CommissionSetting(models.Model):
    """Global platform commission settings."""
    
    platform_commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('10.00'),
        help_text="Commission percentage (e.g., 10 for 10%)"
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Commission Settings"
    
    def __str__(self):
        return f"Platform Commission: {self.platform_commission_rate}%"
    
    def save(self, *args, **kwargs):
        # Ensure only one record exists
        self.pk = 1
        super().save(*args, **kwargs)
    
    @classmethod
    def get_rate(cls):
        """Get current commission rate."""
        setting, _ = cls.objects.get_or_create(pk=1)
        return setting.platform_commission_rate


# ==================================================
# WORKER AVAILABILITY (NEW)
# ==================================================

class WorkerAvailability(models.Model):
    """Worker availability settings."""
    
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    worker = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='availability')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['worker', 'day_of_week']
        ordering = ['day_of_week']
    
    def __str__(self):
        return f"{self.worker.username} - {self.get_day_of_week_display()}"

