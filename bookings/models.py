from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from services.models import Service


class Booking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Assigned', 'Assigned'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_bookings'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    worker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='worker_bookings'
    )
    booking_date = models.DateField()
    booking_time = models.TimeField()
    address = models.TextField()
    problem_description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer} - {self.service} ({self.status})"

    def clean(self):
        if self.customer_id and self.customer.role != 'customer':
            raise ValidationError('The booking customer must have the customer role.')

        if self.worker_id:
            if self.worker.role != 'worker':
                raise ValidationError('Assigned worker must be a worker role account.')
            if self.worker.is_blocked:
                raise ValidationError('Blocked workers cannot be assigned to bookings.')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('booking_detail', kwargs={'pk': self.pk})


class BookingMessage(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='messages',
        null=True,
        blank=True
    )
    job = models.ForeignKey(
        'Job',
        on_delete=models.CASCADE,
        related_name='messages',
        null=True,
        blank=True
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='booking_messages'
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        if self.job:
            return f"Message from {self.sender.username} on Job #{self.job.id}"
        return f"Message from {self.sender.username} on {self.booking}"


# ===== PHASE 2 MODELS: Core Workflow (ServiceRequest → JobApplication → Job) =====

class ServiceRequest(models.Model):
    """
    Customer creates a ServiceRequest instead of a Booking.
    This is the initial service request that workers can apply for.
    """
    STATUS_CHOICES = [
        ('OPEN', 'Open - Accepting Applications'),
        ('REVIEWING', 'Reviewing Applications'),
        ('ASSIGNED', 'Worker Assigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='service_requests'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='service_requests'
    )
    title = models.CharField(max_length=200, help_text="Brief title of the service needed")
    description = models.TextField()
    location = models.CharField(max_length=255)
    address = models.TextField()
    
    # Scheduling
    preferred_date = models.DateField()
    preferred_time_start = models.TimeField(null=True, blank=True)
    preferred_time_end = models.TimeField(null=True, blank=True)
    
    # Budget
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Status & Workflow
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='OPEN'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['preferred_date']),
        ]

    def __str__(self):
        return f"{self.title} - {self.customer.username} ({self.status})"

    def clean(self):
        if self.customer_id and self.customer.role != 'customer':
            raise ValidationError('ServiceRequest customer must have the customer role.')
        if self.budget_min and self.budget_max and self.budget_min > self.budget_max:
            raise ValidationError('Minimum budget cannot be greater than maximum budget.')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('service_request_detail', kwargs={'pk': self.pk})

    @property
    def application_count(self):
        return self.job_applications.filter(status='PENDING').count()


class JobApplication(models.Model):
    """
    Workers apply for ServiceRequests with their proposed price and details.
    Customer can review all applications and select one.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('WITHDRAWN', 'Withdrawn by Worker'),
    ]

    service_request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name='job_applications'
    )
    worker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_applications'
    )
    
    # Proposal
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_duration = models.DurationField(help_text="Estimated time to complete the job")
    proposal_message = models.TextField(help_text="Why you're the best choice for this job")
    
    # Availability
    can_start_date = models.DateField(help_text="When you can start working")
    
    # Worker stats at time of application
    worker_rating_at_application = models.DecimalField(
        max_digits=3, decimal_places=2, default=0
    )
    worker_completed_jobs = models.PositiveIntegerField(default=0)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['service_request', 'worker']  # Worker can only apply once
        indexes = [
            models.Index(fields=['service_request', 'status']),
            models.Index(fields=['worker', 'status']),
        ]

    def __str__(self):
        return f"{self.worker.username} - {self.service_request.title} (${self.proposed_price})"

    def clean(self):
        if self.worker_id and self.worker.role != 'worker':
            raise ValidationError('Only workers can apply for jobs.')
        if self.worker_id and self.worker.is_blocked:
            raise ValidationError('Blocked workers cannot apply for jobs.')
        if self.proposed_price <= 0:
            raise ValidationError('Proposed price must be greater than 0.')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('job_application_detail', kwargs={'pk': self.pk})


class Job(models.Model):
    """
    The actual job after customer selects a worker's application.
    This is what gets paid for and tracked.
    """
    STATUS_CHOICES = [
        ('CONFIRMED', 'Confirmed'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    # Links to the workflow
    service_request = models.OneToOneField(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name='job'
    )
    job_application = models.OneToOneField(
        JobApplication,
        on_delete=models.CASCADE,
        related_name='job'
    )
    
    # People involved
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='jobs_as_customer'
    )
    worker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='jobs_as_worker'
    )
    
    # Job details (copied from application)
    title = models.CharField(max_length=200)
    description = models.TextField()
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_duration = models.DurationField()
    
    # Scheduling
    scheduled_date = models.DateField()
    scheduled_time_start = models.TimeField(null=True, blank=True)
    scheduled_time_end = models.TimeField(null=True, blank=True)
    
    # Location
    location = models.CharField(max_length=255)
    address = models.TextField()
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='CONFIRMED'
    )
    
    # Completion tracking
    actual_start_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)
    actual_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Final price if different from proposed"
    )
    completion_notes = models.TextField(blank=True, help_text="Notes from worker after completion")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['worker', 'status']),
            models.Index(fields=['scheduled_date']),
        ]

    def __str__(self):
        return f"Job #{self.pk} - {self.worker.username} for {self.title}"

    def clean(self):
        if self.customer_id and self.customer.role != 'customer':
            raise ValidationError('Job customer must have customer role.')
        if self.worker_id and self.worker.role != 'worker':
            raise ValidationError('Job worker must have worker role.')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('job_detail', kwargs={'pk': self.pk})

    @property
    def is_completed(self):
        return str(self.status).upper() == 'COMPLETED'

    @property
    def final_price(self):
        """Return actual price if set, otherwise proposed price"""
        return self.actual_price if self.actual_price else self.proposed_price
