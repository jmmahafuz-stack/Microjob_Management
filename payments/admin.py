from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'booking',
        'amount',
        'payment_method',
        'transaction_id',
        'payment_status',
        'payment_date'
    )
    list_filter = ('payment_status', 'payment_method')
    search_fields = ('transaction_id', 'booking__id')
