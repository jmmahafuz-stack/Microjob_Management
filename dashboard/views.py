from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Sum
from django.shortcuts import render
from django.utils import timezone

from accounts.models import CustomUser
from bookings.models import Booking, Job, ServiceRequest
from complaints.models import Complaint
from payments.models import Payment
from reviews.models import Review
from workers.models import WorkerProfile


@login_required
def dashboard_home(request):
    if request.user.role == 'admin':
        bookings = Booking.objects.all()
        complaints = Complaint.objects.all()
        pending_workers = WorkerProfile.objects.filter(verification_status='Pending').count()
        pending_bookings = bookings.filter(status='Pending').count()
        pending_complaints = complaints.filter(status='Pending').count()

        paid_payments = Payment.objects.filter(payment_status='Verified')
        total_revenue = paid_payments.aggregate(total=Sum('customer_amount'))['total'] or 0
        platform_revenue = paid_payments.aggregate(total=Sum('platform_commission'))['total'] or 0
        worker_earnings = paid_payments.aggregate(total=Sum('worker_amount'))['total'] or 0

        total_customers = CustomUser.objects.filter(role='customer').count()
        total_workers = CustomUser.objects.filter(role='worker').count()
        service_requests = ServiceRequest.objects.count()
        completed_jobs = Job.objects.filter(status='COMPLETED').count()
        cancelled_jobs = Job.objects.filter(status='CANCELLED').count()
        paid_transactions = paid_payments.count()
        avg_rating = Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0

        today = timezone.now().date()
        daily_start = today - timedelta(days=1)
        monthly_start = today.replace(day=1)
        yearly_start = today.replace(month=1, day=1)

        report_daily = {
            'revenue': paid_payments.filter(payment_date__date__gte=daily_start).aggregate(total=Sum('customer_amount'))['total'] or 0,
            'jobs': Job.objects.filter(created_at__date__gte=daily_start).count(),
        }
        report_monthly = {
            'revenue': paid_payments.filter(payment_date__date__gte=monthly_start).aggregate(total=Sum('customer_amount'))['total'] or 0,
            'jobs': Job.objects.filter(created_at__date__gte=monthly_start).count(),
        }
        report_yearly = {
            'revenue': paid_payments.filter(payment_date__date__gte=yearly_start).aggregate(total=Sum('customer_amount'))['total'] or 0,
            'jobs': Job.objects.filter(created_at__date__gte=yearly_start).count(),
        }

        context = {
            'bookings': bookings,
            'complaints': complaints,
            'pending_workers': pending_workers,
            'pending_bookings': pending_bookings,
            'pending_complaints': pending_complaints,
            'total_revenue': total_revenue,
            'platform_revenue': platform_revenue,
            'worker_earnings': worker_earnings,
            'total_customers': total_customers,
            'total_workers': total_workers,
            'service_requests': service_requests,
            'completed_jobs': completed_jobs,
            'cancelled_jobs': cancelled_jobs,
            'paid_transactions': paid_transactions,
            'avg_rating': avg_rating,
            'report_daily': report_daily,
            'report_monthly': report_monthly,
            'report_yearly': report_yearly,
        }
        return render(request, 'dashboard/dashboard.html', context)

    if request.user.role == 'worker':
        verified_payments = Payment.objects.filter(
            job__worker=request.user,
            payment_status='Verified'
        )
        completed_jobs = Job.objects.filter(worker=request.user, status='COMPLETED').count()
        total_earnings = verified_payments.aggregate(total=Sum('worker_amount'))['total'] or Decimal('0.00')
        platform_commission = verified_payments.aggregate(total=Sum('platform_commission'))['total'] or Decimal('0.00')
        worker_reviews = Review.objects.filter(worker=request.user)
        average_rating = worker_reviews.aggregate(avg=Avg('rating'))['avg'] or 0

        context = {
            'bookings': Booking.objects.filter(worker=request.user),
            'completed_jobs': completed_jobs,
            'total_earnings': total_earnings,
            'platform_commission': platform_commission,
            'average_rating': average_rating,
            'reviews': worker_reviews,
        }
        return render(request, 'dashboard/dashboard.html', context)

    bookings = Booking.objects.filter(customer=request.user)
    complaints = Complaint.objects.filter(customer=request.user)

    context = {
        'bookings': bookings,
        'complaints': complaints,
    }
    return render(request, 'dashboard/dashboard.html', context)
