from django.db import models
from django.conf import settings
from decimal import Decimal


class Payment(models.Model):
    """Payment model with automatic commission calculation for platform revenue."""

    PAYMENT_METHOD_CHOICES = [
        ('Cash', 'Cash'),
        ('BKash', 'BKash'),
        ('Nagad', 'Nagad'),
        ('Mobile Banking', 'Mobile Banking'),
        ('Card', 'Card'),
        ('Digital Wallet', 'Digital Wallet'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending - Awaiting Verification'),
        ('Verified', 'Verified - Payment Confirmed'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]

    # Link to Job
    job = models.OneToOneField(
        'bookings.Job',
        on_delete=models.CASCADE,
        related_name='payment',
        null=True,
        blank=True
    )

    # Backward compatibility with old Booking payments
    booking = models.OneToOneField(
        'bookings.Booking',
        on_delete=models.CASCADE,
        related_name='payment_legacy',
        null=True,
        blank=True
    )

    # Payment amounts
    customer_amount = models.DecimalField(
<<<<<<< HEAD
        max_digits=10, decimal_places=2, default=0,
        help_text="Total amount customer pays (e.g., 1500)"
=======
        max_digits=10,
        decimal_places=2,
        help_text="Total amount customer pays"
>>>>>>> 2b9a4033767b5c34cf65e854d204910fc6e11b08
    )

    # Legacy single amount field
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Legacy: single amount field"
    )

    platform_commission = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Platform commission - automatically calculated"
    )

    worker_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Worker earnings after platform commission"
    )

    # Payment details
    payment_method = models.CharField(
        max_length=25,
        choices=PAYMENT_METHOD_CHOICES,
        default='BKash'
    )

    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        help_text="Transaction ID from payment gateway or manual entry"
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='Pending'
    )

    payment_date = models.DateTimeField(auto_now_add=True)

    verified_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When payment was verified/confirmed"
    )

    receipt = models.FileField(
        upload_to='payment_receipts/',
        blank=True,
        null=True,
        help_text="Receipt/proof of payment"
    )

    # Commission settings
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10,
        help_text="Commission percentage (e.g., 10 for 10%)"
    )
<<<<<<< HEAD
    
    # Payment verification (Gateway integration)
    verification_method = models.CharField(
        max_length=20,
        choices=[
            ('Manual', 'Manual - Admin Verified'),
            ('Gateway', 'Gateway - API Verified'),
            ('Receipt', 'Receipt - Uploaded Proof'),
        ],
        default='Manual',
        help_text="How the payment was verified"
    )
    gateway_response = models.JSONField(
        default=dict, blank=True,
        help_text="Raw response from payment gateway"
    )
    gateway_status = models.CharField(
        max_length=50, blank=True, default='',
        help_text="Status returned by payment gateway"
    )
    
=======

    commission_calculated_at = models.DateTimeField(
        null=True,
        blank=True
    )

>>>>>>> 2b9a4033767b5c34cf65e854d204910fc6e11b08
    # Worker payout status
    worker_payout_status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending - Awaiting Payment'),
            ('Available', 'Available - Ready for Withdrawal'),
            ('Withdrawn', 'Withdrawn'),
        ],
        default='Pending'
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
            models.Index(fields=['worker_payout_status']),
        ]

    def __str__(self):
        if self.job:
            return f"Payment #{self.pk} for Job #{self.job.pk} - ৳{self.customer_amount}"
        return f"Payment #{self.pk} - ৳{self.customer_amount}"

    def calculate_commission(self, rate=None):
        """Calculate platform commission and worker amount."""

        if rate is None:
            rate = self.commission_rate

        self.commission_rate = rate

        self.platform_commission = (
            self.customer_amount *
            Decimal(str(rate)) /
            Decimal('100')
        )

        self.worker_amount = (
            self.customer_amount -
            self.platform_commission
        )

        return self.platform_commission, self.worker_amount

    def verify_payment(self):
        """Mark payment as verified and update worker earnings."""

        if self.payment_status != 'Verified':
            self.payment_status = 'Verified'
            self.worker_payout_status = 'Available'

            if self.job and self.job.worker:
                self.job.worker.worker_profile.confirm_pending_earnings(
                    self.worker_amount
                )

            self.save()
            
            # Send notification to worker
            from notifications.models import Notification
            if self.job and self.job.worker:
                Notification.create_notification(
                    user=self.job.worker,
                    title=f"Payment Received for {self.job.title}",
                    message=f"Your payment of ৳{self.worker_amount} has been verified and is now available for withdrawal.",
                    notification_type='PAYMENT_VERIFIED',
                    payment=self,
                    job=self.job,
                    related_user=self.job.customer,
                )
            
            return True

        return False

    def save(self, *args, **kwargs):
        # Auto-calculate commission if customer amount is set
        if self.customer_amount is not None and not self.platform_commission:
            self.calculate_commission()

        super().save(*args, **kwargs)


class PayoutRequest(models.Model):
    """Track worker payout/withdrawal requests."""

    STATUS_CHOICES = [
        ('Requested', 'Requested - Pending Review'),
        ('Approved', 'Approved - Processing'),
        ('Processed', 'Processed - Money Sent'),
        ('Rejected', 'Rejected'),
        ('Cancelled', 'Cancelled by Worker'),
    ]

    worker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payout_requests'
    )

    requested_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Amount worker is requesting to withdraw"
    )

    approved_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Amount approved by admin"
    )

    payout_method = models.CharField(
        max_length=50,
        choices=[
            ('Bank Account', 'Bank Account'),
            ('BKash', 'BKash'),
            ('Nagad', 'Nagad'),
            ('Rocket', 'Rocket'),
        ]
    )

    payout_account_holder = models.CharField(max_length=255)
    payout_account_number = models.CharField(max_length=255)
    payout_bank_name = models.CharField(max_length=255, blank=True)
    payout_branch = models.CharField(max_length=255, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Requested'
    )

    admin_notes = models.TextField(
        blank=True,
        help_text="Reason for approval/rejection"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['worker', 'status']),
            models.Index(fields=['status', '-created_at']),
        ]

    def __str__(self):
        return (
            f"Payout Request #{self.pk} - "
            f"{self.worker.username} - "
            f"৳{self.requested_amount} ({self.status})"
        )

    def approve(self, approved_amount=None):
        """Approve the payout request."""

        if self.status == 'Requested':
            self.status = 'Approved'
            self.approved_amount = (
                approved_amount or self.requested_amount
            )
            self.save()
            return True

        return False

    def process(self):
        """Mark payout as processed."""

        if self.status == 'Approved':
            self.status = 'Processed'
            self.processed_at = models.functions.Now()

            amount_to_deduct = (
                self.approved_amount or self.requested_amount
            )

            worker_profile = self.worker.worker_profile

            worker_profile.available_earnings -= amount_to_deduct
            worker_profile.withdrawn_earnings += amount_to_deduct

            worker_profile.save(
                update_fields=[
                    'available_earnings',
                    'withdrawn_earnings'
                ]
            )

            self.save()
            return True

        return False

    def reject(self, reason=''):
        """Reject the payout request."""

        if self.status == 'Requested':
            self.status = 'Rejected'
            self.admin_notes = reason
            self.save()
            return True

        return False