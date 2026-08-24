from django.contrib import admin
from django import forms
from django.utils.html import format_html

from services.models import Category
from .models import WorkerProfile


class WorkerProfileAdminForm(forms.ModelForm):
    class Meta:
        model = WorkerProfile
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        active_categories = Category.objects.filter(is_active=True)
        assigned_categories = (
            Category.objects.filter(workers=self.instance)
            if self.instance.pk else Category.objects.none()
        )
        self.fields['categories'].queryset = (active_categories | assigned_categories).distinct()

    def clean_categories(self):
        categories = self.cleaned_data['categories']
        if categories.count() != 1:
            raise forms.ValidationError('Assign exactly one category to each worker.')
        return categories


@admin.register(WorkerProfile)
class WorkerProfileAdmin(admin.ModelAdmin):
    form = WorkerProfileAdminForm
    
    def worker_approval_status(self, obj):
        """Display worker approval status from CustomUser"""
        status = obj.user.worker_status
        colors = {
            'PENDING': '#FFC107',   # Yellow
            'APPROVED': '#28A745',  # Green
            'REJECTED': '#DC3545',  # Red
            'BLOCKED': '#6C757D',   # Gray
        }
        color = colors.get(status, '#6C757D')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.user.get_worker_status_display()
        )
    worker_approval_status.short_description = 'Approval Status'
    
    def worker_email(self, obj):
        """Display worker email"""
        return obj.user.email
    worker_email.short_description = 'Email'
    
    def worker_categories(self, obj):
        """Display worker categories"""
        cats = ', '.join([c.name for c in obj.categories.all()])
        return cats if cats else '-'
    worker_categories.short_description = 'Categories'
    
    list_display = (
        'user',
        'profession',
        'worker_categories',
        'experience_years',
        'worker_approval_status',
        'verification_status',
        'average_rating_cached',
    )
    
    list_filter = (
        'training_status', 
        'verification_status',
        'categories',
        'user__worker_status',
        'created_at',
    )
    
    search_fields = (
        'user__email',
        'user__email',
        'profession',
        'skills',
    )
    
    filter_horizontal = ('categories',)
    readonly_fields = (
        'completed_jobs',
        'average_rating_cached',
        'total_earnings',
        'pending_earnings',
        'available_earnings',
        'withdrawn_earnings',
        'worker_email',
        'worker_approval_status',
        'worker_categories',
    )
    
    fieldsets = (
        ('User', {
            'fields': ('user', 'worker_email', 'worker_approval_status')
        }),
        ('Professional Information', {
            'fields': (
                'profession',
                'categories',
                'bio',
                'skills',
                'experience_years',
                'service_area',
                'languages',
            )
        }),
        ('Documents & Verification', {
            'fields': ('id_verification_document', 'verification_status')
        }),
        ('Status & Preferences', {
            'fields': ('training_status', 'payout_status', 'response_time', 'default_preferred_contact')
        }),
        ('Earnings & Statistics', {
            'fields': (
                'completed_jobs',
                'average_rating_cached',
                'total_earnings',
                'pending_earnings',
                'available_earnings',
                'withdrawn_earnings',
            ),
            'classes': ('collapse',)
        }),
        ('Payout Information', {
            'fields': (
                'payout_method',
                'payout_account_holder',
                'payout_account_number',
                'payout_bank_name',
                'payout_branch',
                'bkash_number',
                'nagad_number',
                'rocket_number',
            ),
            'classes': ('collapse',)
        }),
        ('Legacy Fields (Backward Compatibility)', {
            'fields': ('service_category', 'service'),
            'classes': ('collapse',)
        })
    )
