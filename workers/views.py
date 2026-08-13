from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import admin_required, worker_required
from bookings.models import Booking
from reviews.models import Review
from .forms import WorkerProfileForm, WorkerVerificationForm
from .models import WorkerProfile
from services.models import Service


@worker_required
def worker_dashboard(request):

    assigned_bookings = Booking.objects.filter(worker=request.user)
    pending_bookings = assigned_bookings.filter(status='Pending')
    in_progress_bookings = assigned_bookings.filter(status='In Progress')
    completed_bookings = assigned_bookings.filter(status='Completed')
    cancelled_bookings = assigned_bookings.filter(status='Cancelled')
    worker_profile, _ = WorkerProfile.objects.get_or_create(user=request.user)
    reviews = Review.objects.filter(worker=request.user)
    total_earnings = sum(booking.service.price for booking in completed_bookings if booking.service.price)
    available_services = Service.objects.filter(is_available=True)

    return render(
        request,
        'workers/worker_dashboard.html',
        {
            'assigned_bookings': assigned_bookings,
            'pending_bookings': pending_bookings,
            'in_progress_bookings': in_progress_bookings,
            'completed_bookings': completed_bookings,
            'cancelled_bookings': cancelled_bookings,
            'worker_profile': worker_profile,
            'reviews': reviews,
            'total_earnings': total_earnings,
            'available_services': available_services,
        }
    )


def worker_profile_detail(request, pk):
    worker_profile = get_object_or_404(WorkerProfile, pk=pk)
    reviews = Review.objects.filter(worker=worker_profile.user).select_related('customer')

    return render(
        request,
        'workers/worker_profile_detail.html',
        {
            'worker_profile': worker_profile,
            'reviews': reviews,
        }
    )


@admin_required
def worker_verification_list(request):

    workers = WorkerProfile.objects.all()
    return render(
        request,
        'workers/worker_verification_list.html',
        {'workers': workers}
    )


@admin_required
def verify_worker(request, pk):

    worker_profile = get_object_or_404(WorkerProfile, pk=pk)

    if request.method == 'POST':
        form = WorkerVerificationForm(request.POST, instance=worker_profile)
        if form.is_valid():
            form.save()
            if worker_profile.verification_status == 'Approved':
                worker_profile.user.worker_status = 'APPROVED'
            elif worker_profile.verification_status == 'Rejected':
                worker_profile.user.worker_status = 'REJECTED'
            worker_profile.user.save(update_fields=['worker_status'])
            messages.success(request, 'Worker verification updated.')
            return redirect('worker_verification_list')
    else:
        form = WorkerVerificationForm(instance=worker_profile)

    return render(
        request,
        'workers/verify_worker.html',
        {'form': form, 'worker_profile': worker_profile}
    )
