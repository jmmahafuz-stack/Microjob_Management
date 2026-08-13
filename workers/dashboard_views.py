"""
Worker Dashboard Views
Enhanced worker profile and earnings dashboard with detailed transaction history.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, Q
from django.contrib import messages
from decimal import Decimal
from datetime import datetime, timedelta

from accounts.decorators import worker_required
from accounts.models import CustomUser
from bookings.models import Job
from payments.models import Payment, PayoutRequest
from workers.models import WorkerProfile


@login_required
@worker_required
def worker_dashboard(request):
    """Enhanced worker dashboard with earnings overview."""
    worker_profile = request.user.worker_profile
    
    # Get jobs and payments
    jobs = Job.objects.filter(worker=request.user).order_by('-created_at')
    payments = Payment.objects.filter(
        Q(job__worker=request.user) | Q(booking__worker=request.user)
    ).order_by('-payment_date')
    
    # Calculate statistics
    completed_jobs = jobs.filter(status='COMPLETED').count()
    in_progress_jobs = jobs.filter(status='IN_PROGRESS').count()
    cancelled_jobs = jobs.filter(status='CANCELLED').count()
    
    # Payment statistics
    verified_payments = payments.filter(payment_status='Verified')
    total_verified = verified_payments.aggregate(Sum('worker_amount'))['worker_amount__sum'] or Decimal('0')
    
    pending_payments = payments.filter(payment_status='Pending')
    total_pending = pending_payments.aggregate(Sum('worker_amount'))['worker_amount__sum'] or Decimal('0')
    
    # Payout statistics
    payouts = PayoutRequest.objects.filter(worker=request.user).order_by('-created_at')
    processed_payouts = payouts.filter(status='Processed')
    pending_payout_requests = payouts.filter(status='Requested')
    
    # Average rating
    from reviews.models import Review
    avg_rating = Review.objects.filter(worker=request.user).aggregate(Avg('rating'))['rating__avg'] or 0
    total_reviews = Review.objects.filter(worker=request.user).count()
    
    context = {
        'worker_profile': worker_profile,
        
        # Job statistics
        'completed_jobs': completed_jobs,
        'in_progress_jobs': in_progress_jobs,
        'cancelled_jobs': cancelled_jobs,
        'total_jobs': jobs.count(),
        
        # Earnings
        'pending_earnings': worker_profile.pending_earnings,
        'available_earnings': worker_profile.available_earnings,
        'withdrawn_earnings': worker_profile.withdrawn_earnings,
        'total_earnings': (
            worker_profile.pending_earnings +
            worker_profile.available_earnings +
            worker_profile.withdrawn_earnings
        ),
        
        # Payment info
        'total_verified': total_verified,
        'total_pending': total_pending,
        'verified_payments_count': verified_payments.count(),
        'pending_payments_count': pending_payments.count(),
        
        # Payout info
        'processed_payouts_count': processed_payouts.count(),
        'pending_payout_requests_count': pending_payout_requests.count(),
        'total_payouts': payouts.count(),
        
        # Rating
        'avg_rating': f"{avg_rating:.2f}" if avg_rating else 'No ratings yet',
        'total_reviews': total_reviews,
        
        # Recent activity
        'recent_jobs': jobs[:10],
        'recent_payments': payments[:10],
        'recent_payouts': payouts[:10],
    }
    
    return render(request, 'workers/dashboard.html', context)


@login_required
@worker_required
def worker_earnings_detail(request):
    """Detailed earnings and commission breakdown."""
    worker_profile = request.user.worker_profile
    
    # Get all payments with breakdown
    payments = Payment.objects.filter(
        Q(job__worker=request.user) | Q(booking__worker=request.user)
    ).select_related('job', 'booking').order_by('-payment_date')
    
    # Summary statistics
    verified_payments = payments.filter(payment_status='Verified')
    pending_payments = payments.filter(payment_status='Pending')
    
    verified_summary = verified_payments.aggregate(
        total_customer_amount=Sum('customer_amount'),
        total_commission=Sum('platform_commission'),
        total_worker_amount=Sum('worker_amount'),
        count=Count('id')
    )
    
    pending_summary = pending_payments.aggregate(
        total_customer_amount=Sum('customer_amount'),
        total_commission=Sum('platform_commission'),
        total_worker_amount=Sum('worker_amount'),
        count=Count('id')
    )
    
    # Monthly breakdown
    monthly_earnings = []
    for i in range(12):
        month_date = datetime.now() - timedelta(days=30*i)
        month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if i == 0:
            month_end = datetime.now()
        else:
            if month_date.month == 1:
                month_end = month_date.replace(year=month_date.year-1, month=12, day=31)
            else:
                month_end = month_date.replace(month=month_date.month-1, day=1) - timedelta(days=1)
        
        month_payments = verified_payments.filter(
            verified_date__gte=month_start,
            verified_date__lte=month_end
        )
        
        if month_payments.exists():
            monthly_earnings.append({
                'month': month_start.strftime('%Y-%m'),
                'earnings': month_payments.aggregate(Sum('worker_amount'))['worker_amount__sum'] or Decimal('0'),
                'transactions': month_payments.count(),
                'commission_deducted': month_payments.aggregate(Sum('platform_commission'))['platform_commission__sum'] or Decimal('0'),
            })
    
    context = {
        'worker_profile': worker_profile,
        'payments': payments,
        
        # Earnings breakdown
        'pending_earnings': worker_profile.pending_earnings,
        'available_earnings': worker_profile.available_earnings,
        'withdrawn_earnings': worker_profile.withdrawn_earnings,
        'total_earnings': (
            worker_profile.pending_earnings +
            worker_profile.available_earnings +
            worker_profile.withdrawn_earnings
        ),
        
        # Verified payments summary
        'verified_payments_count': verified_summary.get('count', 0),
        'verified_total_amount': verified_summary.get('total_customer_amount', Decimal('0')),
        'verified_total_commission': verified_summary.get('total_commission', Decimal('0')),
        'verified_total_earnings': verified_summary.get('total_worker_amount', Decimal('0')),
        
        # Pending payments summary
        'pending_payments_count': pending_summary.get('count', 0),
        'pending_total_amount': pending_summary.get('total_customer_amount', Decimal('0')),
        'pending_total_commission': pending_summary.get('total_commission', Decimal('0')),
        'pending_total_earnings': pending_summary.get('total_worker_amount', Decimal('0')),
        
        # Monthly breakdown
        'monthly_earnings': monthly_earnings,
    }
    
    return render(request, 'workers/earnings_detail.html', context)


@login_required
@worker_required
def worker_transaction_history(request):
    """Transaction history with filters and search."""
    # Get all payment transactions
    transactions = Payment.objects.filter(
        Q(job__worker=request.user) | Q(booking__worker=request.user)
    ).select_related('job', 'booking').order_by('-payment_date')
    
    # Filters
    status_filter = request.GET.get('status', 'all')
    method_filter = request.GET.get('method', 'all')
    search = request.GET.get('search', '')
    
    if status_filter != 'all':
        transactions = transactions.filter(payment_status=status_filter)
    
    if method_filter != 'all':
        transactions = transactions.filter(payment_method=method_filter)
    
    if search:
        transactions = transactions.filter(
            Q(transaction_id__icontains=search) |
            Q(job__title__icontains=search) |
            Q(booking__description__icontains=search)
        )
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(transactions, 20)
    page = request.GET.get('page', 1)
    transactions = paginator.get_page(page)
    
    context = {
        'transactions': transactions,
        'status_filter': status_filter,
        'method_filter': method_filter,
        'search': search,
        'payment_statuses': [s[0] for s in Payment.PAYMENT_STATUS_CHOICES],
        'payment_methods': [m[0] for m in Payment.PAYMENT_METHOD_CHOICES],
    }
    
    return render(request, 'workers/transaction_history.html', context)


@login_required
@worker_required
def worker_payout_requests(request):
    """View and manage payout requests."""
    payouts = PayoutRequest.objects.filter(worker=request.user).order_by('-created_at')
    
    # Summary
    processed_total = payouts.filter(status='Processed').aggregate(
        Sum('approved_amount')
    )['approved_amount__sum'] or Decimal('0')
    
    pending_requests = payouts.filter(status='Requested').aggregate(
        total=Sum('requested_amount')
    )['total'] or Decimal('0')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(payouts, 10)
    page = request.GET.get('page', 1)
    payouts = paginator.get_page(page)
    
    context = {
        'payouts': payouts,
        'processed_total': processed_total,
        'pending_requests': pending_requests,
        'available_balance': request.user.worker_profile.available_earnings,
    }
    
    return render(request, 'workers/payout_requests.html', context)


@login_required
@worker_required
def worker_profile_edit(request):
    """Edit worker profile including payment method details."""
    worker_profile = request.user.worker_profile
    
    if request.method == 'POST':
        # Update basic info
        worker_profile.bio = request.POST.get('bio', '')
        worker_profile.skills = request.POST.get('skills', '')
        worker_profile.experience_years = request.POST.get('experience_years', 0)
        worker_profile.service_area = request.POST.get('service_area', '')
        worker_profile.hourly_rate = request.POST.get('hourly_rate', '')
        
        # Update payment method info
        worker_profile.payout_method = request.POST.get('payout_method', 'Bank Account')
        worker_profile.payout_account_holder = request.POST.get('payout_account_holder', '')
        worker_profile.payout_account_number = request.POST.get('payout_account_number', '')
        worker_profile.payout_bank_name = request.POST.get('payout_bank_name', '')
        worker_profile.payout_branch = request.POST.get('payout_branch', '')
        
        # Update bKash/Nagad numbers (for receiving payments)
        worker_profile.bkash_number = request.POST.get('bkash_number', '')
        worker_profile.nagad_number = request.POST.get('nagad_number', '')
        worker_profile.rocket_number = request.POST.get('rocket_number', '')
        
        try:
            worker_profile.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('worker_dashboard')
        except Exception as e:
            messages.error(request, f'Error saving profile: {str(e)}')
    
    context = {
        'worker_profile': worker_profile,
        'payout_methods': [
            ('Bank Account', 'Bank Account'),
            ('BKash', 'bKash'),
            ('Nagad', 'Nagad'),
            ('Rocket', 'Rocket'),
        ]
    }
    
    return render(request, 'workers/profile_edit.html', context)


@login_required
@worker_required
def worker_payment_methods(request):
    """Manage payment methods for receiving payments."""
    worker_profile = request.user.worker_profile
    
    if request.method == 'POST':
        # Validate and save bKash/Nagad numbers
        from payments.payment_service import PaymentGatewayService
        
        bkash = request.POST.get('bkash_number', '').strip()
        nagad = request.POST.get('nagad_number', '').strip()
        rocket = request.POST.get('rocket_number', '').strip()
        
        errors = []
        
        if bkash:
            is_valid, msg = PaymentGatewayService.validate_payment_number('bKash', bkash)
            if not is_valid:
                errors.append(msg)
        
        if nagad:
            is_valid, msg = PaymentGatewayService.validate_payment_number('Nagad', nagad)
            if not is_valid:
                errors.append(msg)
        
        if rocket:
            is_valid, msg = PaymentGatewayService.validate_payment_number('Rocket', rocket)
            if not is_valid:
                errors.append(msg)
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            worker_profile.bkash_number = bkash or None
            worker_profile.nagad_number = nagad or None
            worker_profile.rocket_number = rocket or None
            worker_profile.save()
            messages.success(request, 'Payment methods updated successfully!')
            return redirect('worker_payment_methods')
    
    context = {
        'worker_profile': worker_profile,
    }
    
    return render(request, 'workers/payment_methods.html', context)
