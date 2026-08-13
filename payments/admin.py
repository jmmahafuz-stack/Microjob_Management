from django.contrib import admin
from django.utils.html import format_html

from .models import Payment, PayoutRequest


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'get_job_display',
        'customer_amount',
        'commission_display',
        'worker_amount_display',
        'payment_method',
        'payment_status',
        'worker_payout_status',
        'payment_date'
    )
    list_filter = ('payment_status', 'worker_payout_status', 'payment_method', 'payment_date')
    search_fields = ('transaction_id', 'job__id', 'job__customer__username', 'job__worker__username')
    readonly_fields = ('platform_commission', 'worker_amount', 'commission_display', 'payment_breakdown')
    
    fieldsets = (
        ('Job Information', {
            'fields': ('job',)
        }),
        ('Payment Amount', {
            'fields': ('customer_amount',)
        }),
        ('Commission Breakdown', {
            'fields': ('commission_rate', 'platform_commission', 'worker_amount', 'payment_breakdown'),
            'description': 'System automatically calculates: Platform Commission = Customer Amount × Commission Rate%'
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'transaction_id', 'receipt', 'payment_status', 'verified_date')
        }),
        ('Worker Payout', {
            'fields': ('worker_payout_status',)
        }),
        ('Refund Information', {
            'fields': ('refund_reason', 'refunded_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_job_display(self, obj):
        """Display job with customer and worker"""
        if obj.job:
            return format_html(
                '<strong>Job #{}</strong><br/>Customer: {}<br/>Worker: {}',
                obj.job.id,
                obj.job.customer.get_full_name() or obj.job.customer.username,
                obj.job.worker.get_full_name() or obj.job.worker.username,
            )
        return "N/A"
    get_job_display.short_description = "Job Details"
    
    def commission_display(self, obj):
        """Display commission amount with percentage"""
        return format_html(
            '{} ({0:.2f}% = {})',
            obj.platform_commission,
            obj.commission_rate,
        )
    commission_display.short_description = "Platform Commission"
    
    def worker_amount_display(self, obj):
        """Display worker earning amount"""
        return format_html('<strong>{}</strong>', obj.worker_amount)
    worker_amount_display.short_description = "Worker Earnings"
    
    def payment_breakdown(self, obj):
        """Display full payment breakdown as HTML"""
        return format_html(
            '<div style="background:#f5f5f5;padding:10px;border-radius:5px;font-size:14px;"'
            '<strong>Payment Breakdown</strong><br/>'
            'Customer pays: <strong>{}</strong><br/>'
            'Platform commission ({}%): <strong>{}</strong><br/>'
            'Worker earnings: <strong>{}</strong><br/>'
            '<hr style="margin:5px 0;"/>'
            'Total: {}<br/>'
            'Verification: {}<br/>'
            '</div>',
            obj.customer_amount,
            obj.commission_rate,
            obj.platform_commission,
            obj.worker_amount,
            obj.customer_amount,
            'Verified' if obj.payment_status == 'Verified' else 'Pending',
        )
    payment_breakdown.short_description = "Payment Details"


@admin.register(PayoutRequest)
class PayoutRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'get_worker_display',
        'requested_amount',
        'approved_amount_display',
        'payout_method',
        'status',
        'created_at'
    )
    list_filter = ('status', 'payout_method', 'created_at')
    search_fields = ('worker__username', 'worker__first_name', 'worker__last_name')
    readonly_fields = ('worker', 'requested_amount', 'created_at')
    
    fieldsets = (
        ('Worker Information', {
            'fields': ('worker',)
        }),
        ('Amount Details', {
            'fields': ('requested_amount', 'approved_amount')
        }),
        ('Payout Details', {
            'fields': ('payout_method', 'payout_account_holder', 'payout_account_number', 'payout_bank_name', 'payout_branch')
        }),
        ('Status', {
            'fields': ('status', 'admin_notes')
        }),
    )
    
    def get_worker_display(self, obj):
        """Display worker information"""
        worker_profile = obj.worker.worker_profile
        return format_html(
            '<strong>{}</strong><br/>Available: {}<br/>Withdrawn: {}',
            obj.worker.get_full_name() or obj.worker.username,
            worker_profile.available_earnings,
            worker_profile.withdrawn_earnings,
        )
    get_worker_display.short_description = "Worker"
    
    def approved_amount_display(self, obj):
        """Display approved amount or requested if not approved yet"""
        return obj.approved_amount or obj.requested_amount
    approved_amount_display.short_description = "Approved Amount"
    
    actions = ['approve_payout', 'process_payout', 'reject_payout']
    
    def approve_payout(self, request, queryset):
        """Admin action to approve payout requests"""
        updated = 0
        for payout_req in queryset.filter(status='Requested'):
            payout_req.approve()
            updated += 1
        self.message_user(request, f'{updated} payout requests approved.')
    approve_payout.short_description = "Approve selected payout requests"
    
    def process_payout(self, request, queryset):
        """Admin action to mark payouts as processed"""
        updated = 0
        for payout_req in queryset.filter(status='Approved'):
            payout_req.process()
            updated += 1
        self.message_user(request, f'{updated} payout requests processed.')
    process_payout.short_description = "Process selected payout requests"
    
    def reject_payout(self, request, queryset):
        """Admin action to reject payout requests"""
        updated = 0
        for payout_req in queryset.filter(status='Requested'):
            payout_req.reject('Rejected by admin')
            updated += 1
        self.message_user(request, f'{updated} payout requests rejected.')
    reject_payout.short_description = "Reject selected payout requests"
