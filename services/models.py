from django.conf import settings
from django.db import models
from django.db.models import Avg

# Create your models here.
from django.urls import reverse


class Service(models.Model):
    SERVICE_CHOICES = [
        ('Electrical', 'Electrical'),
        ('Plumbing', 'Plumbing'),
        ('Carpentry', 'Carpentry'),
        ('AC Repair', 'AC Repair'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=SERVICE_CHOICES)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='service_images/')
    duration = models.CharField(max_length=50)
    location = models.CharField(max_length=100, blank=True, null=True)
    featured = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        return self.bookings.aggregate(avg=Avg('reviews__rating'))['avg'] or 0

    def get_absolute_url(self):
        return reverse('service_detail', kwargs={'pk': self.pk})


class FavoriteService(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorite_services'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'service')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.customer.username} favorites {self.service.name}"
