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
    problem_photo = models.ImageField(
        upload_to='booking_problem_photos/',
        blank=True,
        null=True,
    )
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
    attachment = models.FileField(
        upload_to='message_attachments/',
        blank=True,
        null=True,
        help_text='Optional photo or document'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        if self.job:
            return f"Message from {self.sender.email} on Job #{self.job.id}"
        return f"Message from {self.sender.email} on {self.booking}"


class WorkerResponse(models.Model):
    """
    Worker's response to a booking.
    Allows worker to accept, reject, or propose completion status with messaging.
    """
    RESPONSE_STATUS_CHOICES = [
        ('PENDING', 'Pending - Considering the job'),
        ('REJECTED', 'Rejected - Cannot do this job'),
        ('ACCEPTED', 'Accepted - Ready to work'),
        ('IN_PROGRESS', 'In Progress - Working on it'),
        ('COMPLETED', 'Completed - Job finished'),
    ]

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='worker_responses'
    )
    worker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='booking_responses'
    )
    
    # Worker's response status
    status = models.CharField(
        max_length=20,
        choices=RESPONSE_STATUS_CHOICES,
        default='PENDING'
    )
    
    # Worker's message to customer
    message = models.TextField(help_text="Your response message to the customer")
    
    # Customer acceptance
    customer_accepted = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['booking', 'worker']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Response from {self.worker.email} on Booking #{self.booking.id} - {self.status}"

    def clean(self):
        if self.worker_id and self.worker.role != 'worker':
            raise ValidationError('Only workers can create responses.')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


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
    problem_photo = models.ImageField(
        upload_to='service_request_photos/',
        blank=True,
        null=True,
        help_text='Optional photo showing the problem'
    )
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
        return f"{self.title} - {self.customer.email} ({self.status})"

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
    proposal_message = models.TextField(
        blank=True,
        help_text="Optional message explaining why you're the best choice for this job"
    )
    
    # Availability
    can_start_date = models.DateField(help_text="When you can start working")
    agreed_to_schedule = models.BooleanField(
        default=False,
        help_text="Worker agrees to the customer's requested date and time"
    )
    
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
        return f"{self.worker.email} - {self.service_request.title} (${self.proposed_price})"

    def clean(self):
        if self.worker_id and self.worker.role != 'worker':
            raise ValidationError('Only workers can apply for jobs.')
        if self.worker_id and (self.worker.is_blocked or self.worker.worker_status != 'APPROVED'):
            raise ValidationError('Only admin-approved workers can apply for jobs.')
        if self.worker_id:
            try:
                profile = self.worker.worker_profile
                service = self.service_request.service
                category_ids = set(profile.categories.values_list('id', flat=True))
                category_name = (service.category.name if service.category else '').lower()
                matches = (
                    profile.service_id == service.id
                    or service.category_id in category_ids
                    or (profile.service_category and profile.service_category.lower() in category_name)
                    or (profile.profession and profile.profession.lower() in category_name)
                )
                if not matches:
                    raise ValidationError('This job is outside your registered profession/category.')
            except AttributeError:
                raise ValidationError('Create your worker profile before applying for jobs.')
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
        return f"Job #{self.pk} - {self.worker.email} for {self.title}"

    def clean(self):
        if self.customer_id and self.customer.role != 'customer':
            raise ValidationError('Job customer must have customer role.')
        if self.worker_id and self.worker.role != 'worker':
            raise ValidationError('Job worker must have worker role.')
        
        # Check for time conflicts
        if self.worker_id and self.scheduled_date and self.scheduled_time_start:
            # Get all non-cancelled jobs for this worker on the same date
            conflict = Job.objects.filter(
                worker=self.worker, 
                scheduled_date=self.scheduled_date, 
                status__in=['CONFIRMED', 'IN_PROGRESS']
            ).exclude(pk=self.pk)
            
            if conflict.exists():
                # Check if there's a time overlap
                for existing_job in conflict:
                    # If both jobs have time ranges, check for overlap
                    if existing_job.scheduled_time_end and self.scheduled_time_end:
                        # Check if time ranges overlap
                        if (self.scheduled_time_start < existing_job.scheduled_time_end and 
                            self.scheduled_time_end > existing_job.scheduled_time_start):
                            raise ValidationError(
                                f'Worker is already assigned to another job at this date and time. '
                                f'Existing job: {existing_job.scheduled_time_start} - {existing_job.scheduled_time_end}'
                            )
                    # If new job has end time but existing doesn't, assume 4-hour duration
                    elif existing_job.scheduled_time_end is None and self.scheduled_time_end:
                        existing_end = existing_job.get_estimated_end_time()
                        if (self.scheduled_time_start < existing_end and 
                            self.scheduled_time_end > existing_job.scheduled_time_start):
                            raise ValidationError(
                                f'Worker is already assigned to another job at this date and time.'
                            )
                    # If new job has no end time but existing does, assume 4-hour duration for new
                    elif existing_job.scheduled_time_end and self.scheduled_time_end is None:
                        new_end = self.get_estimated_end_time()
                        if (self.scheduled_time_start < existing_job.scheduled_time_end and 
                            new_end > existing_job.scheduled_time_start):
                            raise ValidationError(
                                f'Worker is already assigned to another job at this date and time.'
                            )
                    # Both have no end times - check if start times are on same date
                    else:
                        raise ValidationError(
                            f'Worker is already assigned to another job on this date. '
                            f'Please specify time ranges to avoid conflicts.'
                        )

    def get_estimated_end_time(self):
        """Get estimated end time, defaulting to 4 hours if not set"""
        from datetime import time, datetime, timedelta
        if self.scheduled_time_end:
            return self.scheduled_time_end
        # Default to 4 hours from start time
        start = datetime.combine(datetime.today(), self.scheduled_time_start)
        end = start + timedelta(hours=4)
        return end.time()

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
