from django.db import models

from bookings.models import Booking


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('Cash', 'Cash'),
        ('Mobile Banking', 'Mobile Banking'),
        ('Card', 'Card'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
    ]

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='payment'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(
        max_length=25,
        choices=PAYMENT_METHOD_CHOICES,
        default='Cash'
    )
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='Pending'
    )
    payment_date = models.DateTimeField(auto_now_add=True)
    receipt = models.FileField(
        upload_to='payment_receipts/',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payment for {self.booking}"
