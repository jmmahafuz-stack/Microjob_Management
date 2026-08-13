"""
Admin Dashboard Views
Comprehensive admin dashboard with analytics, reports, and management.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta
from decimal import Decimal

from accounts.models import CustomUser
from bookings.models import Job
from payments.models import Payment, PayoutRequest
from workers.models import WorkerProfile
from reviews.models import Review
from complaints.models import Complaint
from services.models import Service

from payments.report_generator import (
    PaymentReportGenerator, WorkerReportGenerator, JobReportGenerator,
    FinancialReportGenerator
)


@login_required
@staff_member_required
def admin_dashboard(request):
    """Main admin dashboard with key metrics and analytics."""
    
    # Get date range for filtering
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    # ===== PAYMENT METRICS =====
    verified_payments = Payment.objects.filter(
        payment_status='Verified',
        verified_date__gte=start_date
    )
    
    total_transactions = verified_payments.count()
    total_customer_amount = verified_payments.aggregate(
        Sum('customer_amount')
    )['customer_amount__sum'] or Decimal('0')
    total_commission = verified_payments.aggregate(
        Sum('platform_commission')
    )['platform_commission__sum'] or Decimal('0')
    total_worker_earnings = verified_payments.aggregate(
        Sum('worker_amount')
    )['worker_amount__sum'] or Decimal('0')
    
    # ===== JOB METRICS =====
    completed_jobs = Job.objects.filter(
        status='COMPLETED',
        updated_at__gte=start_date
    ).count()
    
    cancelled_jobs = Job.objects.filter(
        status='CANCELLED',
        updated_at__gte=start_date
    ).count()
    
    in_progress_jobs = Job.objects.filter(status='IN_PROGRESS').count()
    
    # ===== USER METRICS =====
    total_customers = CustomUser.objects.filter(role='customer').count()
    total_workers = CustomUser.objects.filter(role='worker').count()
    verified_workers = WorkerProfile.objects.filter(
        verification_status='Approved'
    ).count()
    
    # ===== PAYOUT METRICS =====
    pending_payouts = PayoutRequest.objects.filter(status='Requested').count()
    approved_payouts = PayoutRequest.objects.filter(status='Approved').count()
    processed_payouts = PayoutRequest.objects.filter(status='Processed').count()
    
    pending_payout_amount = PayoutRequest.objects.filter(
        status='Requested'
    ).aggregate(Sum('requested_amount'))['requested_amount__sum'] or Decimal('0')
    
    # ===== RATING & COMPLAINT METRICS =====
    avg_rating = Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0
    total_complaints = Complaint.objects.filter(
        created_at__gte=start_date
    ).count()
    open_complaints = Complaint.objects.filter(
        status__in=['Open', 'Under Review'],
        created_at__gte=start_date
    ).count()
    
    # ===== TOP PERFORMERS =====
    top_workers = WorkerProfile.objects.annotate(
        completed=Count('user__worker_jobs', filter=Q(user__worker_jobs__status='COMPLETED')),
        avg_rating=Avg('user__reviews_received__rating')
    ).order_by('-completed')[:5]
    
    # ===== RECENT PAYMENTS =====
    recent_payments = verified_payments.select_related(
        'job__customer', 'job__worker'
    ).order_by('-verified_date')[:10]
    
    # ===== RECENT PAYOUTS =====
    recent_payouts = PayoutRequest.objects.select_related('worker').order_by('-created_at')[:10]
    
    context = {
        # Payment metrics
        'total_transactions': total_transactions,
        'total_customer_amount': total_customer_amount,
        'total_commission': total_commission,
        'total_worker_earnings': total_worker_earnings,
        'average_transaction': total_customer_amount / total_transactions if total_transactions > 0 else Decimal('0'),
        
        # Job metrics
        'completed_jobs': completed_jobs,
        'cancelled_jobs': cancelled_jobs,
        'in_progress_jobs': in_progress_jobs,
        
        # User metrics
        'total_customers': total_customers,
        'total_workers': total_workers,
        'verified_workers': verified_workers,
        
        # Payout metrics
        'pending_payouts': pending_payouts,
        'approved_payouts': approved_payouts,
        'processed_payouts': processed_payouts,
        'pending_payout_amount': pending_payout_amount,
        
        # Quality metrics
        'avg_rating': f"{avg_rating:.2f}",
        'total_complaints': total_complaints,
        'open_complaints': open_complaints,
        
        # Top performers
        'top_workers': top_workers,
        
        # Recent activity
        'recent_payments': recent_payments,
        'recent_payouts': recent_payouts,
        
        # Filters
        'days': days,
    }
    
    return render(request, 'admin/dashboard.html', context)


@login_required
@staff_member_required
def admin_users_list(request):
    """List all users with filters."""
    role = request.GET.get('role', 'all')
    search = request.GET.get('search', '')
    
    if role == 'customer':
        users = CustomUser.objects.filter(role='customer')
    elif role == 'worker':
        users = CustomUser.objects.filter(role='worker')
    else:
        users = CustomUser.objects.exclude(role='admin')
    
    if search:
        users = users.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    context = {
        'users': users,
        'role': role,
        'search': search,
    }
    
    return render(request, 'admin/users_list.html', context)


@login_required
@staff_member_required
def admin_payments_list(request):
    """List all payments with filters."""
    status = request.GET.get('status', 'all')
    method = request.GET.get('method', 'all')
    
    payments = Payment.objects.select_related(
        'job__customer', 'job__worker'
    ).order_by('-payment_date')
    
    if status != 'all':
        payments = payments.filter(payment_status=status)
    
    if method != 'all':
        payments = payments.filter(payment_method=method)
    
    context = {
        'payments': payments,
        'status': status,
        'method': method,
        'statuses': [s[0] for s in Payment.PAYMENT_STATUS_CHOICES],
        'methods': [m[0] for m in Payment.PAYMENT_METHOD_CHOICES],
    }
    
    return render(request, 'admin/payments_list.html', context)


@login_required
@staff_member_required
def admin_jobs_list(request):
    """List all jobs with filters."""
    status = request.GET.get('status', 'all')
    
    jobs = Job.objects.select_related(
        'customer', 'worker'
    ).order_by('-created_at')
    
    if status != 'all':
        jobs = jobs.filter(status=status)
    
    context = {
        'jobs': jobs,
        'status': status,
        'statuses': ['CONFIRMED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'],
    }
    
    return render(request, 'admin/jobs_list.html', context)


@login_required
@staff_member_required
def admin_workers_earnings(request):
    """View worker earnings and statistics."""
    workers = WorkerProfile.objects.annotate(
        completed_jobs=Count('user__worker_jobs', filter=Q(user__worker_jobs__status='COMPLETED')),
        avg_rating=Avg('user__reviews_received__rating')
    ).order_by('-total_earnings')
    
    context = {
        'workers': workers,
    }
    
    return render(request, 'admin/workers_earnings.html', context)


@login_required
@staff_member_required
def admin_payouts_list(request):
    """List payout requests with status."""
    status = request.GET.get('status', 'all')
    
    payouts = PayoutRequest.objects.select_related('worker').order_by('-created_at')
    
    if status != 'all':
        payouts = payouts.filter(status=status)
    
    context = {
        'payouts': payouts,
        'status': status,
        'statuses': [s[0] for s in PayoutRequest.STATUS_CHOICES],
    }
    
    return render(request, 'admin/payouts_list.html', context)


@login_required
@staff_member_required
def admin_reports(request):
    """Admin reports page."""
    context = {
        'report_types': [
            'payment', 'worker', 'job', 'commission', 'financial', 'daily_revenue'
        ]
    }
    return render(request, 'admin/reports.html', context)


@login_required
@staff_member_required
def download_payment_report(request):
    """Download payment report."""
    format_type = request.GET.get('format', 'csv')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    return PaymentReportGenerator.generate_payment_report(format_type, start_date, end_date)


@login_required
@staff_member_required
def download_worker_report(request):
    """Download worker report."""
    format_type = request.GET.get('format', 'csv')
    return WorkerReportGenerator.generate_worker_report(format_type)


@login_required
@staff_member_required
def download_job_report(request):
    """Download job report."""
    format_type = request.GET.get('format', 'csv')
    status = request.GET.get('status')
    return JobReportGenerator.generate_job_report(format_type, status)


@login_required
@staff_member_required
def download_commission_report(request):
    """Download commission report."""
    format_type = request.GET.get('format', 'csv')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    return FinancialReportGenerator.generate_commission_report(format_type, start_date, end_date)


@login_required
@staff_member_required
def download_financial_report(request):
    """Download comprehensive financial report."""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    summary = FinancialReportGenerator.generate_financial_summary(start_date, end_date)
    
    # Convert to HTML content for PDF
    html_content = f"""
    <h2>Financial Report Summary</h2>
    <p>Period: {summary['period_start']} to {summary['period_end']}</p>
    <table border="1" cellpadding="10">
        <tr>
            <td>Total Transactions</td>
            <td>৳{summary['total_customer_amount']}</td>
        </tr>
        <tr>
            <td>Platform Commission</td>
            <td>৳{summary['total_platform_commission']}</td>
        </tr>
        <tr>
            <td>Worker Earnings</td>
            <td>৳{summary['total_worker_earnings']}</td>
        </tr>
        <tr>
            <td>Completed Jobs</td>
            <td>{summary['completed_jobs']}</td>
        </tr>
        <tr>
            <td>Cancelled Jobs</td>
            <td>{summary['cancelled_jobs']}</td>
        </tr>
    </table>
    """
    
    from payments.report_generator import ReportGenerator
    filename = f"financial_report_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
    return ReportGenerator.generate_pdf_response(filename, 'Financial Report', html_content)


@login_required
@staff_member_required
def get_dashboard_stats_json(request):
    """Return dashboard stats as JSON for dynamic updates."""
    days = int(request.GET.get('days', 30))
    start_date = timezone.now() - timedelta(days=days)
    
    verified_payments = Payment.objects.filter(
        payment_status='Verified',
        verified_date__gte=start_date
    )
    
    stats = {
        'total_transactions': verified_payments.count(),
        'total_revenue': float(
            verified_payments.aggregate(
                Sum('platform_commission')
            )['platform_commission__sum'] or Decimal('0')
        ),
        'total_worker_earnings': float(
            verified_payments.aggregate(
                Sum('worker_amount')
            )['worker_amount__sum'] or Decimal('0')
        ),
        'completed_jobs': Job.objects.filter(
            status='COMPLETED',
            updated_at__gte=start_date
        ).count(),
        'pending_payouts': PayoutRequest.objects.filter(status='Requested').count(),
    }
    
    return JsonResponse(stats)
