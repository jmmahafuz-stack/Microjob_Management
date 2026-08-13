from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Sum
from django.shortcuts import render

from bookings.models import Booking
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
        total_revenue = Payment.objects.filter(payment_status='Paid').aggregate(
            total=Sum('amount')
        )['total'] or 0
        avg_rating = Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0

        context = {
            'bookings': bookings,
            'complaints': complaints,
            'pending_workers': pending_workers,
            'pending_bookings': pending_bookings,
            'pending_complaints': pending_complaints,
            'total_revenue': total_revenue,
            'avg_rating': avg_rating,
        }
        return render(request, 'dashboard/dashboard.html', context)

    if request.user.role == 'worker':
        bookings = Booking.objects.filter(worker=request.user)
        completed_jobs = bookings.filter(status='Completed').count()
        total_earnings = sum(
            booking.service.price for booking in bookings.filter(status='Completed')
        )
        worker_reviews = Review.objects.filter(worker=request.user)
        average_rating = worker_reviews.aggregate(avg=Avg('rating'))['avg'] or 0

        context = {
            'bookings': bookings,
            'completed_jobs': completed_jobs,
            'total_earnings': total_earnings,
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
