from django.contrib import admin
from django.utils.html import format_html

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
    search_fields = ('customer__email', 'worker__email', 'service__name')
    readonly_fields = ('created_at', 'updated_at')


# ===== PHASE 2 ADMIN REGISTRATIONS =====

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    
    def service_category(self, obj):
        """Display service category"""
        if obj.service and obj.service.category:
            return obj.service.category.name
        return '-'
    service_category.short_description = 'Category'
    
    def eligible_workers_count(self, obj):
        """Show count of workers eligible for this job"""
        if obj.service:
            return obj.service.workers_for_this_service.count()
        return 0
    eligible_workers_count.short_description = 'Available Workers'
    
    def applications_count(self, obj):
        """Show count of pending applications"""
        return obj.job_applications.filter(status='PENDING').count()
    applications_count.short_description = 'Applications'
    
    list_display = (
        'id',
        'title',
        'customer',
        'service',
        'service_category',
        'status',
        'preferred_date',
        'budget_min',
        'budget_max',
        'eligible_workers_count',
        'applications_count',
    )
    
    list_filter = (
        'status',
        'preferred_date',
        'service__category',
        'service',
        'created_at',
    )
    
    search_fields = (
        'title',
        'description',
        'customer__email',
        'address'
    )
    
    readonly_fields = ('created_at', 'updated_at', 'service_category', 'eligible_workers_count', 'applications_count')
    
    fieldsets = (
        ('Request Information', {
            'fields': ('customer', 'service', 'service_category', 'title', 'description')
        }),
        ('Location & Scheduling', {
            'fields': ('location', 'address', 'preferred_date', 'preferred_time_start', 'preferred_time_end')
        }),
        ('Budget', {
            'fields': ('budget_min', 'budget_max')
        }),
        ('Worker Availability', {
            'fields': ('eligible_workers_count', 'applications_count'),
            'classes': ('collapse',)
        }),
        ('Status & Timestamps', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
    )


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    
    def worker_profession(self, obj):
        """Display worker profession"""
        try:
            return obj.worker.worker_profile.profession
        except:
            return '-'
    worker_profession.short_description = 'Profession'
    
    def worker_rating(self, obj):
        """Display worker rating"""
        rating = obj.worker_rating_at_application
        return f"{rating:.1f} ⭐" if rating > 0 else "No rating"
    worker_rating.short_description = 'Rating'
    
    list_display = (
        'id',
        'worker',
        'worker_profession',
        'service_request',
        'proposed_price',
        'worker_rating',
        'status',
        'created_at'
    )
    
    list_filter = (
        'status',
        'created_at',
        'can_start_date',
        'worker__worker_profile__categories',
    )
    
    search_fields = (
        'worker__email',
        'service_request__title',
        'proposal_message'
    )
    
    readonly_fields = (
        'created_at',
        'updated_at',
        'worker_rating_at_application',
        'worker_completed_jobs',
        'worker_profession',
        'worker_rating'
    )
    
    fieldsets = (
        ('Application Information', {
            'fields': ('service_request', 'worker', 'worker_profession')
        }),
        ('Proposal', {
            'fields': ('proposed_price', 'estimated_duration', 'proposal_message', 'can_start_date')
        }),
        ('Worker Stats at Application', {
            'fields': ('worker_rating', 'worker_completed_jobs'),
        }),
        ('Status & Timestamps', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
    )


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    
    def worker_status_badge(self, obj):
        """Display worker approval status"""
        status = obj.worker.worker_status
        colors = {
            'PENDING': '#FFC107',
            'APPROVED': '#28A745',
            'REJECTED': '#DC3545',
        }
        color = colors.get(status, '#6C757D')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 2px; font-size: 0.9em;">{}</span>',
            color,
            obj.worker.get_worker_status_display()
        )
    worker_status_badge.short_description = 'Worker Status'
    
    def time_conflict_status(self, obj):
        """Check if there are time conflicts"""
        try:
            conflicts = Job.objects.filter(
                worker=obj.worker,
                scheduled_date=obj.scheduled_date,
                status__in=['CONFIRMED', 'IN_PROGRESS']
            ).exclude(pk=obj.pk)
            
            if conflicts.exists():
                return format_html(
                    '<span style="color: #DC3545; font-weight: bold;">⚠️ Conflict Detected</span>'
                )
            return format_html(
                '<span style="color: #28A745;">✓ No Conflicts</span>'
            )
        except:
            return '-'
    time_conflict_status.short_description = 'Availability'
    
    list_display = (
        'id',
        'title',
        'customer',
        'worker',
        'worker_status_badge',
        'status',
        'scheduled_date',
        'time_conflict_status',
        'proposed_price',
        'actual_price',
    )
    
    list_filter = (
        'status',
        'scheduled_date',
        'worker__worker_status',
        'created_at',
    )
    
    search_fields = (
        'title',
        'description',
        'customer__email',
        'worker__email'
    )
    
    readonly_fields = ('created_at', 'updated_at', 'worker_status_badge', 'time_conflict_status')
    
    fieldsets = (
        ('Job Information', {
            'fields': ('service_request', 'job_application', 'title', 'description')
        }),
        ('People Involved', {
            'fields': ('customer', 'worker', 'worker_status_badge')
        }),
        ('Pricing & Duration', {
            'fields': ('proposed_price', 'actual_price', 'estimated_duration')
        }),
        ('Scheduling', {
            'fields': ('scheduled_date', 'scheduled_time_start', 'scheduled_time_end', 'time_conflict_status')
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
