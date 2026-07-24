from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer',
        'service',
        'worker',
        'booking_date',
        'booking_time',
        'status',
        'created_at'
    )
    list_filter = ('status', 'booking_date', 'service')
    search_fields = ('customer__username', 'worker__username', 'service__name')
    readonly_fields = ('created_at', 'updated_at')
