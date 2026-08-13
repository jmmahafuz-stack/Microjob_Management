"""
Worker Dashboard Views for earnings, transactions, and payouts management.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from django.contrib import messages
from django.views.decorators.http import require_POST

from datetime import timedelta, datetime
from decimal import Decimal

from accounts.models import CustomUser
from workers.models import WorkerProfile
from payments.models import Payment, PayoutRequest
from bookings.models import Job
from reviews.models import Review


def _get_or_create_worker_profile(user):
    """Ensure a worker always has a profile record for dashboard access."""
    return WorkerProfile.objects.get_or_create(user=user)[0]


def worker_required(view_func):
    """Decorator to check if user is a worker."""
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'worker':
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Access denied. Worker profile required.')
        return redirect('home')
    return wrapper


@login_required
@worker_required
def worker_dashboard(request):
    """Main worker dashboard with earnings overview."""
    
    worker = request.user
    profile = _get_or_create_worker_profile(worker)
    
    # Job statistics
    job_stats = Job.objects.filter(worker=worker).aggregate(
        completed=Count('pk', filter=Q(status='COMPLETED')),
        in_progress=Count('pk', filter=Q(status='IN_PROGRESS')),
        cancelled=Count('pk', filter=Q(status='CANCELLED')),
    )
    
    # Recent jobs
    recent_jobs = Job.objects.filter(worker=worker).order_by('-created_at')[:5]
    
    # Recent payments
    recent_payments = Payment.objects.filter(
        job__worker=worker
    ).select_related('job').order_by('-payment_date')[:5]
    
    # Recent payouts
    recent_payouts = PayoutRequest.objects.filter(
        worker=worker
    ).order_by('-created_at')[:5]
    
    # Pending payout requests
    pending_payouts = PayoutRequest.objects.filter(
        worker=worker,
        status__in=['Requested', 'Approved']
    ).aggregate(
        count=Count('pk'),
        amount=Sum('requested_amount')
    )
    
    context = {
        'profile': profile,
        'job_stats': job_stats,
        'recent_jobs': recent_jobs,
        'recent_payments': recent_payments,
        'recent_payouts': recent_payouts,
        'pending_payouts': pending_payouts,
    }
    
    return render(request, 'workers/dashboard.html', context)


@login_required
@worker_required
def worker_earnings_detail(request):
    """Detailed earnings breakdown and monthly history."""
    
    worker = request.user
    profile = _get_or_create_worker_profile(worker)
    
    # Get all verified payments
    payments = Payment.objects.filter(
        job__worker=worker,
        payment_status='Verified'
    ).order_by('-payment_date')
    
    # Monthly breakdown (last 12 months)
    monthly_breakdown = []
    end_date = timezone.now()
    
    for month_offset in range(12):
        month_start = end_date - timedelta(days=30 * (month_offset + 1))
        month_end = end_date - timedelta(days=30 * month_offset)
        
        month_payments = payments.filter(
            payment_date__range=[month_start, month_end]
        )
        
        earnings = month_payments.aggregate(
            count=Count('pk'),
            total=Sum('worker_amount'),
            commission_deducted=Sum('platform_commission')
        )
        
        monthly_breakdown.append({
            'month': month_start.strftime('%B %Y'),
            'transaction_count': earnings['count'] or 0,
            'earnings': earnings['total'] or Decimal('0'),
            'commission': earnings['commission_deducted'] or Decimal('0'),
        })
    
    context = {
        'profile': profile,
        'payments': payments[:50],  # Last 50 transactions
        'monthly_breakdown': monthly_breakdown,
        'total_verified_payments': payments.count(),
    }
    
    return render(request, 'workers/earnings_detail.html', context)


@login_required
@worker_required
def worker_transaction_history(request):
    """Complete transaction history with filters and search."""
    
    worker = request.user
    
    # Get all payments for this worker
    payments = Payment.objects.filter(
        job__worker=worker
    ).select_related('job').order_by('-payment_date')
    
    # Filters
    status = request.GET.get('status', 'all')
    method = request.GET.get('method', 'all')
    search = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    
    if status != 'all':
        payments = payments.filter(payment_status=status)
    
    if method != 'all':
        payments = payments.filter(payment_method=method)
    
    if search:
        payments = payments.filter(
            Q(transaction_id__icontains=search) |
            Q(job__title__icontains=search)
        )
    
    # Pagination
    per_page = 20
    start = (page - 1) * per_page
    end = start + per_page
    total_pages = (payments.count() + per_page - 1) // per_page
    
    payments_page = payments[start:end]
    
    context = {
        'payments': payments_page,
        'status_selected': status,
        'method_selected': method,
        'search_query': search,
        'page': page,
        'total_pages': total_pages,
        'total_transactions': payments.count(),
    }
    
    return render(request, 'workers/transaction_history.html', context)


@login_required
@worker_required
def worker_payout_requests(request):
    """View and manage payout requests."""
    
    worker = request.user
    profile = _get_or_create_worker_profile(worker)
    
    payouts = PayoutRequest.objects.filter(worker=worker).order_by('-created_at')
    
    # Summary statistics
    payout_stats = payouts.aggregate(
        total_requested=Sum('requested_amount', filter=Q(status='Requested')),
        total_approved=Sum('approved_amount', filter=Q(status='Approved')),
        total_processed=Sum('approved_amount', filter=Q(status='Processed')),
        count_pending=Count('pk', filter=Q(status__in=['Requested', 'Approved'])),
    )
    
    context = {
        'payouts': payouts,
        'payout_stats': payout_stats,
        'available_balance': profile.available_earnings,
    }
    
    return render(request, 'workers/payout_requests.html', context)


@login_required
@worker_required
def create_payout_request(request):
    """Create a new payout request."""
    
    worker = request.user
    profile = _get_or_create_worker_profile(worker)
    
    if request.method == 'POST':
        requested_amount = Decimal(request.POST.get('requested_amount', 0))
        payout_method = request.POST.get('payout_method', profile.payout_method)
        
        # Validation
        if requested_amount <= 0:
            messages.error(request, 'Amount must be greater than zero.')
            return redirect('create_payout_request')
        
        if requested_amount > profile.available_earnings:
            messages.error(
                request, 
                f'Insufficient balance. Available: ৳{profile.available_earnings}'
            )
            return redirect('create_payout_request')
        
        # For mobile money, validate phone number
        if payout_method in ['BKash', 'Nagad', 'Rocket']:
            phone_field = f'{payout_method.lower()}_number'
            phone = getattr(profile, phone_field, None)
            
            if not phone:
                messages.error(
                    request, 
                    f'Please set your {payout_method} number in profile settings.'
                )
                return redirect('worker_payment_methods')
        
        # Create payout request
        payout = PayoutRequest.objects.create(
            worker=worker,
            requested_amount=requested_amount,
            payout_method=payout_method,
            payout_number=getattr(profile, f'{payout_method.lower()}_number', ''),
            payout_account_holder=profile.payout_account_holder,
            payout_account_number=profile.payout_account_number,
            payout_bank_name=profile.payout_bank_name,
            payout_branch=profile.payout_branch,
        )
        
        messages.success(
            request, 
            f'Payout request created for ৳{requested_amount}. Admin will review shortly.'
        )
        return redirect('worker_payout_requests')
    
    context = {
        'profile': profile,
        'available_balance': profile.available_earnings,
    }
    
    return render(request, 'workers/create_payout_request.html', context)


@login_required
@worker_required
def worker_profile_edit(request):
    """Edit worker profile."""
    
    worker = request.user
    profile = _get_or_create_worker_profile(worker)
    
    if request.method == 'POST':
        # Update basic info
        worker.first_name = request.POST.get('first_name', worker.first_name)
        worker.last_name = request.POST.get('last_name', worker.last_name)
        worker.save()
        
        # Update profile
        profile.bio = request.POST.get('bio', profile.bio)
        profile.skills = request.POST.get('skills', profile.skills)
        profile.experience_years = int(request.POST.get('experience_years', profile.experience_years))
        profile.service_area = request.POST.get('service_area', profile.service_area)
        profile.languages = request.POST.get('languages', profile.languages)
        profile.hourly_rate = request.POST.get('hourly_rate', profile.hourly_rate)
        profile.save()
        
        messages.success(request, 'Profile updated successfully.')
        return redirect('worker_dashboard')
    
    context = {
        'worker': worker,
        'profile': profile,
    }
    
    return render(request, 'workers/profile_edit.html', context)


@login_required
@worker_required
def worker_payment_methods(request):
    """Set payment method phone numbers."""
    
    worker = request.user
    profile = _get_or_create_worker_profile(worker)
    
    if request.method == 'POST':
        bkash_number = request.POST.get('bkash_number', '').strip()
        nagad_number = request.POST.get('nagad_number', '').strip()
        rocket_number = request.POST.get('rocket_number', '').strip()
        
        # Validate BD phone numbers if provided
        import re
        bd_phone_pattern = r'^01[0-9]{9}$'
        
        if bkash_number and not re.match(bd_phone_pattern, bkash_number):
            messages.error(request, 'Invalid bKash number. Use format: 01XXXXXXXXX')
            return redirect('worker_payment_methods')
        
        if nagad_number and not re.match(bd_phone_pattern, nagad_number):
            messages.error(request, 'Invalid Nagad number. Use format: 01XXXXXXXXX')
            return redirect('worker_payment_methods')
        
        if rocket_number and not re.match(bd_phone_pattern, rocket_number):
            messages.error(request, 'Invalid Rocket number. Use format: 01XXXXXXXXX')
            return redirect('worker_payment_methods')
        
        # Update profile
        profile.bkash_number = bkash_number or None
        profile.nagad_number = nagad_number or None
        profile.rocket_number = rocket_number or None
        
        # Update payout method and account details if provided
        payout_method = request.POST.get('payout_method', profile.payout_method)
        profile.payout_method = payout_method
        profile.payout_account_holder = request.POST.get('payout_account_holder', '')
        profile.payout_account_number = request.POST.get('payout_account_number', '')
        profile.payout_bank_name = request.POST.get('payout_bank_name', '')
        profile.payout_branch = request.POST.get('payout_branch', '')
        
        profile.save()
        
        messages.success(request, 'Payment methods updated successfully.')
        return redirect('worker_dashboard')
    
    context = {
        'profile': profile,
    }
    
    return render(request, 'workers/payment_methods.html', context)
