from django.contrib import admin

from .models import Booking, ServiceRequest, JobApplication, Job


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


# ===== PHASE 2 ADMIN REGISTRATIONS =====

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'customer',
        'service',
        'status',
        'preferred_date',
        'budget_min',
        'budget_max',
        'created_at'
    )
    list_filter = ('status', 'preferred_date', 'service', 'created_at')
    search_fields = ('title', 'description', 'customer__username', 'address')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Request Information', {
            'fields': ('customer', 'service', 'title', 'description')
        }),
        ('Location & Scheduling', {
            'fields': ('location', 'address', 'preferred_date', 'preferred_time_start', 'preferred_time_end')
        }),
        ('Budget', {
            'fields': ('budget_min', 'budget_max')
        }),
        ('Status & Timestamps', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
    )


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'worker',
        'service_request',
        'proposed_price',
        'status',
        'created_at'
    )
    list_filter = ('status', 'created_at', 'can_start_date')
    search_fields = ('worker__username', 'service_request__title', 'proposal_message')
    readonly_fields = ('created_at', 'updated_at', 'worker_rating_at_application', 'worker_completed_jobs')
    fieldsets = (
        ('Application Information', {
            'fields': ('service_request', 'worker')
        }),
        ('Proposal', {
            'fields': ('proposed_price', 'estimated_duration', 'proposal_message', 'can_start_date')
        }),
        ('Worker Stats at Application', {
            'fields': ('worker_rating_at_application', 'worker_completed_jobs'),
            'classes': ('collapse',)
        }),
        ('Status & Timestamps', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
    )


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'customer',
        'worker',
        'status',
        'scheduled_date',
        'proposed_price',
        'actual_price',
        'created_at'
    )
    list_filter = ('status', 'scheduled_date', 'created_at')
    search_fields = ('title', 'description', 'customer__username', 'worker__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Job Information', {
            'fields': ('service_request', 'job_application', 'title', 'description')
        }),
        ('People Involved', {
            'fields': ('customer', 'worker')
        }),
        ('Pricing & Duration', {
            'fields': ('proposed_price', 'actual_price', 'estimated_duration')
        }),
        ('Scheduling', {
            'fields': ('scheduled_date', 'scheduled_time_start', 'scheduled_time_end')
        }),
        ('Location', {
            'fields': ('location', 'address')
        }),
        ('Completion Tracking', {
            'fields': ('actual_start_time', 'actual_end_time', 'completion_notes')
        }),
        ('Status & Timestamps', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
    )
