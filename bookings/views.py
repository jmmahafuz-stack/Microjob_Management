from django.shortcuts import render

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import admin_required, customer_required, worker_required
from services.models import Service
from workers.models import WorkerProfile

from .forms import (
    BookingCreateForm,
    BookingAssignForm,
    BookingMessageForm,
    BookingStatusUpdateForm,
    BookingUpdateForm,
)
from .models import Booking, BookingMessage


def _get_related_workers(service):
    category_matches = WorkerProfile.objects.filter(
        user__role='worker',
        user__is_verified_worker=True,
        service_category__icontains=service.category,
    )
    skill_matches = WorkerProfile.objects.filter(
        user__role='worker',
        user__is_verified_worker=True,
        skills__icontains=service.category,
    )
    direct_matches = WorkerProfile.objects.filter(
        user__role='worker',
        user__is_verified_worker=True,
        service=service,
    )

    combined = (category_matches | skill_matches | direct_matches).distinct().select_related('user')[:4]
    return combined


@login_required
def booking_list(request):
    if request.user.role == 'admin':
        bookings = Booking.objects.all().order_by('-created_at')
    elif request.user.role == 'worker':
        bookings = Booking.objects.filter(worker=request.user).order_by('-created_at')
    else:
        bookings = Booking.objects.filter(customer=request.user).order_by('-created_at')

    return render(
        request,
        'bookings/booking_list.html',
        {'bookings': bookings}
    )


@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if request.user.role == 'admin':
        pass
    elif request.user.role == 'worker' and booking.worker != request.user:
        messages.error(request, 'You can only view bookings assigned to you.')
        return redirect('booking_list')
    elif request.user.role == 'customer' and booking.customer != request.user:
        messages.error(request, 'You can only view your own bookings.')
        return redirect('booking_list')

    assign_form = BookingAssignForm(instance=booking)
    status_form = BookingStatusUpdateForm(instance=booking)
    message_form = BookingMessageForm()
    booking_payment = getattr(booking, 'payment', None)

    booking_messages = booking.messages.all()

    if request.method == 'POST' and 'message' in request.POST:
        message_form = BookingMessageForm(request.POST)
        if request.user.role == 'customer' and booking.customer != request.user:
            messages.error(request, 'You can only message for your own booking.')
            return redirect('booking_detail', pk=booking.pk)
        if request.user.role == 'worker' and booking.worker != request.user:
            messages.error(request, 'You can only message for your assigned booking.')
            return redirect('booking_detail', pk=booking.pk)

        if message_form.is_valid():
            message = message_form.save(commit=False)
            message.booking = booking
            message.sender = request.user
            message.save()
            messages.success(request, 'Message sent successfully.')
            return redirect('booking_detail', pk=booking.pk)

    return render(
        request,
        'bookings/booking_detail.html',
        {
            'booking': booking,
            'booking_payment': booking_payment,
            'assign_form': assign_form,
            'status_form': status_form,
            'message_form': message_form,
            'booking_messages': booking_messages,
        }
    )


@customer_required
def create_booking(request):
    selected_service = None
    service_id = request.GET.get('service') or request.POST.get('service')
    if service_id:
        selected_service = get_object_or_404(Service, pk=service_id)
        selected_service.related_workers = _get_related_workers(selected_service)

    if request.method == 'POST':
        form = BookingCreateForm(request.POST, selected_service=selected_service)
        if form.is_valid():
            booking = form.save(commit=False)
            if request.user.role == 'admin' and booking.customer_id:
                booking.customer = booking.customer
            else:
                booking.customer = request.user
            booking.status = 'Pending'
            booking.save()
            messages.success(request, 'Booking request created successfully.')
            return redirect('booking_detail', pk=booking.pk)
    else:
        form = BookingCreateForm(initial={'service': selected_service}, selected_service=selected_service)

    return render(
        request,
        'bookings/create_booking.html',
        {
            'form': form,
            'selected_service': selected_service,
        }
    )


@login_required
def booking_history(request):
    if request.user.role == 'admin':
        bookings = Booking.objects.all().order_by('-created_at')
    elif request.user.role == 'worker':
        bookings = Booking.objects.filter(worker=request.user).order_by('-created_at')
    else:
        bookings = Booking.objects.filter(customer=request.user).order_by('-created_at')

    return render(
        request,
        'bookings/booking_history.html',
        {'bookings': bookings}
    )


@customer_required
def edit_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if booking.customer != request.user:
        messages.error(request, 'You can only edit your own bookings.')
        return redirect('booking_list')

    if booking.status not in ['Pending', 'Confirmed']:
        messages.error(request, 'Only pending or confirmed bookings can be rescheduled.')
        return redirect('booking_detail', pk=booking.pk)

    if request.method == 'POST':
        form = BookingUpdateForm(request.POST, instance=booking)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.status = 'Pending'
            booking.save()
            messages.success(request, 'Booking reschedule request submitted.')
            return redirect('booking_detail', pk=booking.pk)
    else:
        form = BookingUpdateForm(instance=booking)

    return render(
        request,
        'bookings/create_booking.html',
        {'form': form, 'editing': True}
    )


@worker_required
def respond_to_booking(request, pk, action):
    booking = get_object_or_404(Booking, pk=pk)

    if booking.worker != request.user:
        messages.error(request, 'You can only respond to your own assigned bookings.')
        return redirect('booking_list')

    if booking.status != 'Pending':
        messages.error(request, 'Only pending bookings can be accepted or declined.')
        return redirect('booking_detail', pk=booking.pk)

    if action == 'accept':
        booking.status = 'Confirmed'
        messages.success(request, 'Booking accepted successfully.')
    elif action == 'decline':
        booking.status = 'Cancelled'
        messages.success(request, 'Booking declined successfully.')
    else:
        messages.error(request, 'Invalid action.')
        return redirect('booking_detail', pk=booking.pk)

    booking.save(update_fields=['status'])
    return redirect('booking_detail', pk=booking.pk)


@customer_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if booking.customer != request.user:
        messages.error(request, 'You can only cancel your own bookings.')
        return redirect('booking_list')

    if booking.status in ['Completed', 'Cancelled']:
        messages.error(request, 'This booking cannot be cancelled.')
        return redirect('booking_detail', pk=booking.pk)

    if request.method == 'POST':
        booking.status = 'Cancelled'
        booking.save(update_fields=['status'])
        messages.success(request, 'Booking cancelled successfully.')
        return redirect('booking_detail', pk=booking.pk)

    return render(
        request,
        'bookings/booking_detail.html',
        {'booking': booking}
    )


@admin_required
def assign_worker(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if request.method == 'POST':
        form = BookingAssignForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            if booking.worker and booking.status == 'Pending':
                booking.status = 'Assigned'
                booking.save(update_fields=['status'])
            messages.success(request, 'Worker assigned successfully.')
            return redirect('booking_detail', pk=booking.pk)
    else:
        form = BookingAssignForm(instance=booking)

    return render(
        request,
        'bookings/booking_detail.html',
        {'booking': booking, 'assign_form': form}
    )


@login_required
def update_status(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if request.user.role not in ['admin', 'worker']:
        messages.error(request, 'Only workers or admins can update booking status.')
        return redirect('booking_list')

    if request.user.role == 'worker' and booking.worker != request.user:
        messages.error(request, 'You can only update your assigned booking status.')
        return redirect('booking_list')

    if request.method == 'POST':
        form = BookingStatusUpdateForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Booking status updated successfully.')
            return redirect('booking_detail', pk=booking.pk)
    else:
        form = BookingStatusUpdateForm(instance=booking)

    return render(
        request,
        'bookings/booking_detail.html',
        {'booking': booking, 'status_form': form}
    )


@login_required
def invoice(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if request.user.role == 'customer' and booking.customer != request.user:
        messages.error(request, 'You can only view your own invoice.')
        return redirect('booking_list')

    if request.user.role == 'worker' and booking.worker != request.user:
        messages.error(request, 'You can only view invoices for your assigned bookings.')
        return redirect('booking_list')

    return render(
        request,
        'bookings/invoice.html',
        {'booking': booking}
    )
