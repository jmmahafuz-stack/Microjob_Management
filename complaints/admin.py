from django.contrib import admin

from .models import Complaint


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('customer', 'booking', 'subject', 'status', 'created_at')
    list_display_links = ('subject',)
    list_filter = ('status',)
    search_fields = ('customer__username', 'subject', 'description')
