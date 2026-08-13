from django.contrib import admin
from django.utils.html import format_html

from .models import WorkerProfile


@admin.register(WorkerProfile)
class WorkerProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'skills',
        'experience_years',
        'verification_status',
        'earnings_display',
        'payout_method'
    )
    list_filter = ('training_status', 'verification_status', 'payout_method')
    search_fields = ('user__username', 'skills', 'bkash_number', 'nagad_number')
    filter_horizontal = ('categories',)
    readonly_fields = (
        'pending_earnings', 'available_earnings', 'withdrawn_earnings',
        'total_earnings', 'earnings_breakdown_display', 'payment_numbers_display'
    )
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Professional Information', {
            'fields': ('categories', 'bio', 'skills', 'experience_years', 'service_area', 'languages', 'portfolio_link', 'hourly_rate')
        }),
        ('Documents & Verification', {
            'fields': ('id_verification_document', 'verification_status', 'training_status')
        }),
        ('Payment Methods for Receiving Payments', {
            'fields': ('bkash_number', 'nagad_number', 'rocket_number', 'payment_numbers_display'),
            'description': 'Workers register their bKash/Nagad/Rocket phone numbers here to receive payments from customers.'
        }),
        ('Payout / Withdrawal Settings', {
            'fields': ('payout_method', 'payout_account_holder', 'payout_account_number', 'payout_bank_name', 'payout_branch', 'payout_status')
        }),
        ('Earnings & Statistics (READ-ONLY)', {
            'fields': (
                'pending_earnings', 'available_earnings', 'withdrawn_earnings',
                'earnings_breakdown_display', 'completed_jobs', 'average_rating_cached'
            ),
            'description': '<strong style="color:#d9534f;">⚠️ Earnings fields are READ-ONLY and automatically calculated from verified payments. Workers cannot manually change these values.</strong>'
        }),
        ('Preferences', {
            'fields': ('response_time', 'default_preferred_contact')
        }),
        ('Legacy Fields (Backward Compatibility)', {
            'fields': ('service_category', 'service'),
            'classes': ('collapse',)
        })
    )
    
    def earnings_display(self, obj):
        """Display earnings summary in list view"""
        total = obj.pending_earnings + obj.available_earnings + obj.withdrawn_earnings
        return format_html(
            '<span title="Pending: ৳{} | Available: ৳{} | Withdrawn: ৳{}">৳{}</span>',
            obj.pending_earnings,
            obj.available_earnings,
            obj.withdrawn_earnings,
            total
        )
    earnings_display.short_description = "Total Earnings"
    
    def earnings_breakdown_display(self, obj):
        """Display detailed earnings breakdown"""
        return format_html(
            '<div style="background:#f5f5f5;padding:10px;border-radius:5px;font-size:14px;"><strong>Earnings Breakdown</strong><br/>'
            '<strong style="color:#ff9800;">⏳ Pending:</strong> ৳{}<br/>'
            '<strong style="color:#4caf50;">✓ Available:</strong> ৳{}<br/>'
            '<strong style="color:#2196f3;">✔ Withdrawn:</strong> ৳{}<br/>'
            '<hr style="margin:8px 0;"/>'
            '<strong>Total Earned:</strong> ৳{}</div>',
            obj.pending_earnings,
            obj.available_earnings,
            obj.withdrawn_earnings,
            obj.pending_earnings + obj.available_earnings + obj.withdrawn_earnings
        )
    earnings_breakdown_display.short_description = "Detailed Earnings"
    
    def payment_numbers_display(self, obj):
        """Display payment method phone numbers"""
        methods = []
        if obj.bkash_number:
            methods.append(f"<strong>bKash:</strong> {obj.bkash_number}")
        if obj.nagad_number:
            methods.append(f"<strong>Nagad:</strong> {obj.nagad_number}")
        if obj.rocket_number:
            methods.append(f"<strong>Rocket:</strong> {obj.rocket_number}")
        
        if methods:
            return format_html(
                '<div style="background:#e3f2fd;padding:8px;border-left:4px solid #2196f3;"><strong>Payment Numbers Registered:</strong><br/>{}</div>',
                '<br/>'.join(methods)
            )
        else:
            return format_html(
                '<div style="background:#fff3cd;padding:8px;border-left:4px solid #ff9800;"><em>No payment numbers registered yet. Worker should add their bKash/Nagad/Rocket numbers through profile settings.</em></div>'
            )
    payment_numbers_display.short_description = "Payment Numbers"
