"""
Admin Dashboard Views for comprehensive analytics and reporting.
Shows payments, workers, jobs, earnings, payouts, and more.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta, datetime

from accounts.models import CustomUser
from workers.models import WorkerProfile
from payments.models import Payment, PayoutRequest
from bookings.models import Job
from reviews.models import Review
from complaints.models import Complaint
from payments.report_generator import (
    PaymentReportGenerator, 
    WorkerReportGenerator, 
    JobReportGenerator, 
    FinancialReportGenerator
)


@staff_member_required
def admin_dashboard(request):
    """Main admin dashboard with key metrics and analytics."""
    
    # Date range filter (default 30 days)
    days_param = int(request.GET.get('days', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days_param)
    
    # Payment Analytics
    total_payments = Payment.objects.filter(
        payment_date__range=[start_date, end_date],
        payment_status='Verified'
    )
    
    payment_stats = total_payments.aggregate(
        total_revenue=Sum('customer_amount'),
        total_commission=Sum('platform_commission'),
        total_worker_earnings=Sum('worker_amount'),
        transaction_count=Count('pk'),
        avg_transaction=Avg('customer_amount'),
    )
    
    # Job Metrics
    job_stats = Job.objects.filter(
        created_at__range=[start_date, end_date]
    ).aggregate(
        completed=Count('pk', filter=Q(status='COMPLETED')),
        in_progress=Count('pk', filter=Q(status='IN_PROGRESS')),
        cancelled=Count('pk', filter=Q(status='CANCELLED')),
        total=Count('pk'),
    )
    
    # User Metrics
    user_stats = {
        'total_customers': CustomUser.objects.filter(role='customer').count(),
        'total_workers': CustomUser.objects.filter(role='worker').count(),
        'verified_workers': WorkerProfile.objects.filter(verification_status='Approved').count(),
        'pending_verification': WorkerProfile.objects.filter(verification_status='Pending').count(),
    }
    
    # Payout Metrics
    payout_stats = PayoutRequest.objects.filter(
        created_at__range=[start_date, end_date]
    ).aggregate(
        pending=Count('pk', filter=Q(status='Requested')),
        approved=Count('pk', filter=Q(status='Approved')),
        processed=Count('pk', filter=Q(status='Processed')),
        pending_amount=Sum('requested_amount', filter=Q(status='Requested')),
    )
    
    # Quality Metrics
    quality_stats = {
        'avg_rating': Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0,
        'total_complaints': Complaint.objects.filter(
            created_at__range=[start_date, end_date]
        ).count(),
        'open_complaints': Complaint.objects.filter(
            created_at__range=[start_date, end_date],
            status__in=['Open', 'In Progress']
        ).count(),
    }
    
    # Top Performers (Workers)
    top_workers = CustomUser.objects.filter(
        role='worker'
    ).annotate(
        completed_jobs=Count('jobs_completed', filter=Q(jobs_completed__status='COMPLETED')),
        avg_rating=Avg('reviews_received__rating')
    ).order_by('-completed_jobs')[:5]
    
    # Recent Payments
    recent_payments = total_payments.select_related(
        'job__customer', 'job__worker'
    ).order_by('-payment_date')[:10]
    
    # Recent Payouts
    recent_payouts = PayoutRequest.objects.filter(
        created_at__range=[start_date, end_date]
    ).select_related('worker').order_by('-created_at')[:10]
    
    context = {
        'payment_stats': payment_stats,
        'job_stats': job_stats,
        'user_stats': user_stats,
        'payout_stats': payout_stats,
        'quality_stats': quality_stats,
        'top_workers': top_workers,
        'recent_payments': recent_payments,
        'recent_payouts': recent_payouts,
        'date_range': f"{start_date.date()} to {end_date.date()}",
        'days': days_param,
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)


@staff_member_required
def admin_users_list(request):
    """List all users with filtering options."""
    
    role = request.GET.get('role', 'all')
    search = request.GET.get('search', '')
    
    users = CustomUser.objects.all()
    
    if role != 'all':
        users = users.filter(role=role)
    
    if search:
        users = users.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(username__icontains=search)
        )
    
    users = users.order_by('-date_joined')
    
    context = {
        'users': users,
        'role_selected': role,
        'search_query': search,
    }
    
    return render(request, 'dashboard/admin_users_list.html', context)


@staff_member_required
def admin_user_action(request, user_id):
    """Approve, reject, block, or unblock users from the admin dashboard."""
    user = CustomUser.objects.get(pk=user_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve_worker' and user.role == 'worker':
            user.worker_status = 'APPROVED'
            if hasattr(user, 'worker_profile'):
                user.worker_profile.verification_status = 'Approved'
                user.worker_profile.save(update_fields=['verification_status'])
            user.save(update_fields=['worker_status'])
            messages.success(request, f'{user.username} approved as a worker.')

        elif action == 'reject_worker' and user.role == 'worker':
            user.worker_status = 'REJECTED'
            if hasattr(user, 'worker_profile'):
                user.worker_profile.verification_status = 'Rejected'
                user.worker_profile.save(update_fields=['verification_status'])
            user.save(update_fields=['worker_status'])
            messages.warning(request, f'{user.username} rejected as a worker.')

        elif action == 'block_worker' and user.role == 'worker':
            user.worker_status = 'BLOCKED'
            user.is_blocked = True
            user.save(update_fields=['worker_status', 'is_blocked'])
            messages.warning(request, f'{user.username} has been blocked as a worker.')

        elif action == 'unblock_worker' and user.role == 'worker':
            user.worker_status = 'APPROVED'
            user.is_blocked = False
            user.save(update_fields=['worker_status', 'is_blocked'])
            messages.success(request, f'{user.username} has been unblocked and restored.')

        elif action == 'block_customer' and user.role == 'customer':
            user.customer_status = 'BLOCKED'
            user.is_blocked = True
            user.save(update_fields=['customer_status', 'is_blocked'])
            messages.warning(request, f'{user.username} has been blocked as a customer.')

        elif action == 'unblock_customer' and user.role == 'customer':
            user.customer_status = 'ACTIVE'
            user.is_blocked = False
            user.save(update_fields=['customer_status', 'is_blocked'])
            messages.success(request, f'{user.username} has been unblocked as a customer.')

    return redirect('admin_users_list')


@staff_member_required
def admin_view_user_profile(request, user_id):
    """View user profile (worker or customer) from admin dashboard."""
    user = get_object_or_404(CustomUser, pk=user_id)
    
    context = {
        'user': user,
        'is_worker': user.role == 'worker',
        'is_customer': user.role == 'customer',
    }
    
    if user.role == 'worker':
        # Get worker profile details
        worker_profile = getattr(user, 'worker_profile', None)
        context['worker_profile'] = worker_profile
        
        # Get worker stats
        if worker_profile:
            completed_jobs = Job.objects.filter(
                worker=user,
                status='COMPLETED'
            ).count()
            
            avg_rating = Review.objects.filter(
                booking__worker=user
            ).aggregate(avg_rating=Avg('rating'))['avg_rating']
            
            context['completed_jobs'] = completed_jobs
            context['avg_rating'] = avg_rating or 0
    
    elif user.role == 'customer':
        # Get customer stats
        total_jobs = Job.objects.filter(customer=user).count()
        completed_jobs = Job.objects.filter(customer=user, status='COMPLETED').count()
        
        avg_rating_given = Review.objects.filter(
            booking__customer=user
        ).aggregate(avg_rating=Avg('rating'))['avg_rating']
        
        context['total_jobs'] = total_jobs
        context['completed_jobs'] = completed_jobs
        context['avg_rating_given'] = avg_rating_given or 0
    
    return render(request, 'dashboard/admin_view_profile.html', context)


@staff_member_required
def admin_payments_list(request):
    """List all payments with filtering."""
    
    status = request.GET.get('status', 'all')
    method = request.GET.get('method', 'all')
    page = int(request.GET.get('page', 1))
    
    payments = Payment.objects.select_related(
        'job__customer', 'job__worker'
    ).order_by('-payment_date')
    
    if status != 'all':
        payments = payments.filter(payment_status=status)
    
    if method != 'all':
        payments = payments.filter(payment_method=method)
    
    # Pagination
    per_page = 20
    start = (page - 1) * per_page
    end = start + per_page
    total_pages = (payments.count() + per_page - 1) // per_page
    
    payments = payments[start:end]
    
    context = {
        'payments': payments,
        'status_selected': status,
        'method_selected': method,
        'page': page,
        'total_pages': total_pages,
    }
    
    return render(request, 'dashboard/admin_payments_list.html', context)


@staff_member_required
def admin_jobs_list(request):
    """List all jobs with filtering."""
    
    status = request.GET.get('status', 'all')
    page = int(request.GET.get('page', 1))
    
    jobs = Job.objects.select_related(
        'customer', 'worker'
    ).order_by('-created_at')
    
    if status != 'all':
        jobs = jobs.filter(status=status)
    
    # Pagination
    per_page = 20
    start = (page - 1) * per_page
    end = start + per_page
    total_pages = (jobs.count() + per_page - 1) // per_page
    
    jobs = jobs[start:end]
    
    context = {
        'jobs': jobs,
        'status_selected': status,
        'page': page,
        'total_pages': total_pages,
    }
    
    return render(request, 'dashboard/admin_jobs_list.html', context)


@staff_member_required
def admin_workers_earnings(request):
    """View all workers and their earnings."""
    
    order_by = request.GET.get('order_by', 'total_earnings')
    page = int(request.GET.get('page', 1))
    
    workers = CustomUser.objects.filter(
        role='worker'
    ).select_related('worker_profile').annotate(
        completed_jobs=Count('jobs_completed', filter=Q(jobs_completed__status='COMPLETED')),
        avg_rating=Avg('reviews_received__rating')
    )
    
    # Sorting
    if order_by == 'total_earnings':
        workers = workers.order_by('-worker_profile__total_earnings')
    elif order_by == 'jobs_completed':
        workers = workers.order_by('-completed_jobs')
    elif order_by == 'rating':
        workers = workers.order_by('-avg_rating')
    
    # Pagination
    per_page = 20
    start = (page - 1) * per_page
    end = start + per_page
    total_pages = (workers.count() + per_page - 1) // per_page
    
    workers = workers[start:end]
    
    context = {
        'workers': workers,
        'order_by': order_by,
        'page': page,
        'total_pages': total_pages,
    }
    
    return render(request, 'dashboard/admin_workers_earnings.html', context)


@staff_member_required
def admin_payouts_list(request):
    """View and manage payout requests."""
    
    status = request.GET.get('status', 'all')
    page = int(request.GET.get('page', 1))
    
    payouts = PayoutRequest.objects.select_related('worker').order_by('-created_at')
    
    if status != 'all':
        payouts = payouts.filter(status=status)
    
    # Pagination
    per_page = 20
    start = (page - 1) * per_page
    end = start + per_page
    total_pages = (payouts.count() + per_page - 1) // per_page
    
    payouts = payouts[start:end]
    
    context = {
        'payouts': payouts,
        'status_selected': status,
        'page': page,
        'total_pages': total_pages,
    }
    
    return render(request, 'dashboard/admin_payouts_list.html', context)


@staff_member_required
def admin_reports(request):
    """Reports page for downloading various reports."""
    
    context = {}
    return render(request, 'dashboard/admin_reports.html', context)


@staff_member_required
def admin_report_download(request, report_type):
    """Download reports in specified format."""
    
    format_type = request.GET.get('format', 'excel')
    start_date_str = request.GET.get('start_date', '')
    end_date_str = request.GET.get('end_date', '')
    
    # Parse dates
    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            start_date = timezone.make_aware(start_date)
        else:
            start_date = None
        
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            end_date = timezone.make_aware(end_date.replace(hour=23, minute=59, second=59))
        else:
            end_date = None
    except:
        start_date = None
        end_date = None
    
    try:
        if report_type == 'payment':
            gen = PaymentReportGenerator('Payment Report', start_date, end_date)
            return gen.generate(format_type)
        
        elif report_type == 'worker':
            gen = WorkerReportGenerator('Worker Report', start_date, end_date)
            return gen.generate(format_type)
        
        elif report_type == 'job':
            gen = JobReportGenerator('Job Report', start_date, end_date)
            return gen.generate(format_type)
        
        elif report_type == 'commission':
            gen = FinancialReportGenerator('Commission Report', start_date, end_date)
            return gen.generate_commission_report(format_type)
        
        elif report_type == 'financial':
            gen = FinancialReportGenerator('Financial Summary', start_date, end_date)
            return gen.generate_financial_summary(format_type)
        
        else:
            return redirect('admin_reports')
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@staff_member_required
def admin_api_stats(request):
    """API endpoint for real-time stats (AJAX)."""
    
    days = int(request.GET.get('days', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Payment stats
    payments = Payment.objects.filter(
        payment_date__range=[start_date, end_date],
        payment_status='Verified'
    )
    
    stats = payments.aggregate(
        total_revenue=Sum('customer_amount'),
        total_commission=Sum('platform_commission'),
        transaction_count=Count('pk'),
    )
    
    return JsonResponse({
        'total_revenue': float(stats['total_revenue'] or 0),
        'total_commission': float(stats['total_commission'] or 0),
        'transactions': stats['transaction_count'] or 0,
    })
