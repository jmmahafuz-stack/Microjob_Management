from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'get_booking_or_job',
        'customer_amount',
        'platform_commission',
        'worker_amount',
        'payment_method',
        'payment_status',
        'payment_date'
    )
    list_filter = ('payment_status', 'payment_method', 'payment_date')
    search_fields = ('transaction_id', 'booking__id', 'job__id')
    readonly_fields = ('created_at', 'updated_at', 'platform_commission', 'worker_amount')
    fieldsets = (
        ('Payment Information', {
            'fields': ('booking', 'job', 'amount', 'customer_amount')
        }),
        ('Commission & Worker Amount', {
            'fields': ('platform_commission', 'commission_rate', 'commission_calculated_at', 'worker_amount')
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'transaction_id', 'payment_status')
        }),
        ('Refund Information', {
            'fields': ('refund_reason', 'refunded_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('payment_date', 'created_at', 'updated_at')
        }),
    )
    
    def get_booking_or_job(self, obj):
        """Display either booking or job depending on which is set"""
        if obj.booking:
            return f"Booking #{obj.booking.id}"
        elif obj.job:
            return f"Job #{obj.job.id}"
        return "N/A"
    get_booking_or_job.short_description = "Associated Booking/Job"
