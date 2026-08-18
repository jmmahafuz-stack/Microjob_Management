from django.conf import settings
from django.db import models
from django.db.models import Avg

# Create your models here.
from django.urls import reverse


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


class Service(models.Model):
    """
    Service model with ForeignKey to Category.
    Each service belongs to exactly one category (e.g., Electrical, Plumbing, etc.)
    """

    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='services',
        help_text='The category this service belongs to'
    )
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='service_images/')
    duration = models.CharField(max_length=50, help_text='Estimated duration (e.g., "2 hours")')
    location = models.CharField(max_length=100, blank=True, null=True)
    featured = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category__name', 'name']
        indexes = [
            models.Index(fields=['category', 'is_available']),
        ]

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    @property
    def average_rating(self):
        """Calculate average rating from worker reviews for this service"""
        from reviews.models import Review
        from bookings.models import Job
        jobs = Job.objects.filter(service_request__service=self)
        return Review.objects.filter(booking__job__in=jobs).aggregate(avg=Avg('rating'))['avg'] or 0
    
    @property
    def workers_for_this_service(self):
        """Get all approved workers who offer this service category"""
        from workers.models import WorkerProfile
        from accounts.models import CustomUser
        
        # Get workers matching this category
        workers = CustomUser.objects.filter(
            role='worker',
            worker_status='APPROVED',
            is_blocked=False,
            worker_profile__categories=self.category
        ).distinct()
        return workers

    def get_absolute_url(self):
        return reverse('service_detail', kwargs={'pk': self.pk})

