from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone

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
        'verification_method',
        'worker_payout_status',
        'payment_date'
    )
    list_filter = ('payment_status', 'worker_payout_status', 'payment_method', 'verification_method', 'payment_date')
    search_fields = ('transaction_id', 'job__id', 'job__customer__username', 'job__worker__username')
    readonly_fields = (
        'platform_commission', 'worker_amount', 'commission_display', 'payment_breakdown',
        'gateway_response', 'gateway_status', 'payment_date', 'verified_date'
    )
    
    fieldsets = (
        ('Job Information', {
            'fields': ('job',)
        }),
        ('Payment Amount', {
            'fields': ('customer_amount',)
        }),
        ('Commission Breakdown', {
            'fields': ('commission_rate', 'platform_commission', 'worker_amount', 'payment_breakdown'),
            'description': 'System automatically calculates: Platform Commission = Customer Amount × Commission Rate%<br/><strong>⚠️ Commission and Worker Amount are READ-ONLY and automatically calculated. Workers cannot modify these values.</strong>'
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'transaction_id', 'receipt', 'payment_status', 'verified_date')
        }),
        ('Gateway Verification', {
            'fields': ('verification_method', 'gateway_status', 'gateway_response'),
            'description': 'Payment gateway verification details. Ensure payment is verified through gateway API before marking as confirmed.',
            'classes': ('collapse',)
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
            '<div style="background:#f5f5f5;padding:10px;border-radius:5px;font-size:14px;">'
            '<strong>Payment Breakdown</strong><br/>'
            'Customer pays: <strong>৳{}</strong><br/>'
            'Platform commission ({}%): <strong>৳{}</strong><br/>'
            'Worker earnings: <strong>৳{}</strong><br/>'
            '<hr style="margin:5px 0;"/>'
            'Total: ৳{}<br/>'
            'Verification: {}<br/>'
            '</div>',
            obj.customer_amount,
            obj.commission_rate,
            obj.platform_commission,
            obj.worker_amount,
            obj.customer_amount,
            'Verified ✓' if obj.payment_status == 'Verified' else 'Pending ⏳',
        )
    payment_breakdown.short_description = "Payment Details"
    
    actions = ['verify_through_gateway', 'mark_as_verified']
    
    def verify_through_gateway(self, request, queryset):
        """Verify payments through gateway API"""
        from payments.payment_service import PaymentGatewayService
        
        updated = 0
        for payment in queryset.filter(payment_status='Pending'):
            is_valid, response = PaymentGatewayService.verify_transaction(
                payment.transaction_id,
                payment.payment_method,
                payment.customer_amount
            )
            
            if is_valid:
                payment.gateway_response = response
                payment.gateway_status = response.get('status', 'success')
                payment.verification_method = 'Gateway'
                payment.payment_status = 'Verified'
                payment.verified_date = timezone.now()
                payment.worker_payout_status = 'Available'
                payment.save()
                
                # Update worker earnings
                if payment.job and payment.job.worker:
                    payment.job.worker.worker_profile.confirm_pending_earnings(payment.worker_amount)
                
                updated += 1
        
        self.message_user(request, f'{updated} payments verified through gateway.')
    verify_through_gateway.short_description = "Verify selected payments through gateway"
    
    def mark_as_verified(self, request, queryset):
        """Manually verify payments (admin action)"""
        updated = 0
        for payment in queryset.filter(payment_status='Pending'):
            payment.verification_method = 'Manual'
            payment.payment_status = 'Verified'
            payment.verified_date = timezone.now()
            payment.worker_payout_status = 'Available'
            payment.save()
            
            # Update worker earnings
            if payment.job and payment.job.worker:
                payment.job.worker.worker_profile.confirm_pending_earnings(payment.worker_amount)
            
            updated += 1
        
        self.message_user(request, f'{updated} payments marked as verified.')
    mark_as_verified.short_description = "Mark selected payments as verified (Manual verification)"


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
