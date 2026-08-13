from django.contrib import admin

from .models import WorkerProfile


@admin.register(WorkerProfile)
class WorkerProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'skills',
        'experience_years',
        'training_status',
        'verification_status'
    )
    list_filter = ('training_status', 'verification_status')
    search_fields = ('user__username', 'skills')
    filter_horizontal = ('categories',)
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Professional Information', {
            'fields': ('categories', 'bio', 'skills', 'experience_years', 'service_area', 'languages', 'portfolio_link', 'hourly_rate')
        }),
        ('Documents & Verification', {
            'fields': ('id_verification_document', 'verification_status')
        }),
        ('Status & Preferences', {
            'fields': ('training_status', 'payout_status', 'response_time', 'default_preferred_contact')
        }),
        ('Statistics', {
            'fields': ('completed_jobs', 'average_rating_cached', 'total_earnings')
        }),
        ('Legacy Fields (Backward Compatibility)', {
            'fields': ('service_category', 'service'),
            'classes': ('collapse',)
        })
    )
