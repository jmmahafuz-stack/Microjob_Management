from django.db import models
from django.conf import settings


class Payment(models.Model):
    """
    Payment model linking to Job instead of Booking.
    Now includes commission tracking for the platform.
    """

    PAYMENT_METHOD_CHOICES = [
        ('Cash', 'Cash'),
        ('BKash', 'BKash'),
        ('Nagad', 'Nagad'),
        ('Mobile Banking', 'Mobile Banking'),
        ('Card', 'Card'),
        ('Digital Wallet', 'Digital Wallet'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]

    # Link to Job instead of Booking (Phase 2)
    job = models.OneToOneField(
        'bookings.Job',
        on_delete=models.CASCADE,
        related_name='payment',
        null=True,
        blank=True
    )

    # Keep booking link for backward compatibility (deprecated)
    booking = models.OneToOneField(
        'bookings.Booking',
        on_delete=models.CASCADE,
        related_name='payment_legacy',
        null=True,
        blank=True
    )

    # Payment amounts
    customer_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total amount customer pays"
    )

    worker_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Amount worker receives"
    )

    platform_commission = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Platform commission/fee"
    )

    # For backward compatibility - single amount field
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Legacy: single amount field"
    )

    # Payment details
    payment_method = models.CharField(
        max_length=25,
        choices=PAYMENT_METHOD_CHOICES,
        default='Cash'
    )

    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True
    )

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

    # Commission details
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10,
        help_text="Commission percentage (e.g., 10 for 10%)"
    )

    commission_calculated_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # Refund tracking
    refund_reason = models.CharField(
        max_length=255,
        blank=True
    )

    refunded_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-payment_date']
        indexes = [
            models.Index(
                fields=['payment_status', 'payment_date']
            ),
            models.Index(fields=['job']),
        ]

    def __str__(self):
        if self.job:
            return f"Payment for Job #{self.job.pk}"
        return f"Payment for {self.booking}"

    def calculate_commission(self, rate=None):
        """Calculate platform commission based on customer amount and rate"""

        if rate is None:
            rate = self.commission_rate

        self.platform_commission = (
            self.customer_amount * (rate / 100)
        )

        self.worker_amount = (
            self.customer_amount - self.platform_commission
        )

        return self.platform_commission

    def save(self, *args, **kwargs):
        # If customer_amount is set, calculate commission
        if self.customer_amount and not self.platform_commission:
            self.calculate_commission()

        super().save(*args, **kwargs)