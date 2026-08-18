from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import customer_required
from bookings.models import Booking, Job
from .forms import ReviewForm
from .models import Review


@customer_required
def create_review(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)

    if booking.customer != request.user:
        messages.error(request, 'You can only review your own booking.')
        return redirect('booking_list')

    if Review.objects.filter(customer=request.user, booking=booking).exists():
        messages.info(request, 'You already reviewed this booking.')
        return redirect('review_history')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.customer = request.user
            review.worker = booking.worker
            review.booking = booking
            review.save()
            messages.success(request, 'Review submitted successfully.')
            return redirect('review_history')
    else:
        form = ReviewForm()

    return render(request, 'reviews/review_form.html', {'form': form, 'booking': booking})


@customer_required
def create_job_review(request, job_id):
    job = get_object_or_404(Job, pk=job_id)

    if job.customer != request.user:
        messages.error(request, 'You can only review your own service.')
        return redirect('my_bookings')
    if job.status != 'COMPLETED':
        messages.error(request, 'You can review the worker after the service is completed.')
        return redirect('job_detail', pk=job.pk)
    if Review.objects.filter(customer=request.user, job=job).exists():
        messages.info(request, 'You already reviewed this service.')
        return redirect('review_history')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.customer = request.user
            review.worker = job.worker
            review.job = job
            review.save()
            messages.success(request, 'Your rating was submitted successfully.')
            return redirect('review_history')
    else:
        form = ReviewForm()

    return render(request, 'reviews/review_form.html', {'form': form, 'job': job})


@customer_required
def review_history(request):
    reviews = Review.objects.filter(customer=request.user).select_related('worker', 'job', 'booking')
    return render(request, 'reviews/review_history.html', {'reviews': reviews})
