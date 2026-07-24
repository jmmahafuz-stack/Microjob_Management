from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import admin_required, customer_required
from bookings.models import Booking
from .forms import ComplaintForm, ComplaintReplyForm
from .models import Complaint


@customer_required
def create_complaint(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)

    if booking.customer != request.user:
        messages.error(request, 'You can only complain about your own booking.')
        return redirect('booking_list')

    if request.method == 'POST':
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.customer = request.user
            complaint.booking = booking
            complaint.save()
            messages.success(request, 'Complaint submitted successfully.')
            return redirect('complaint_history')
    else:
        form = ComplaintForm()

    return render(request, 'complaints/complaint_form.html', {'form': form, 'booking': booking})


@customer_required
def complaint_history(request):
    complaints = Complaint.objects.filter(customer=request.user)
    return render(request, 'complaints/complaint_history.html', {'complaints': complaints})


@admin_required
def reply_to_complaint(request, pk):

    complaint = get_object_or_404(Complaint, pk=pk)

    if request.method == 'POST':
        form = ComplaintReplyForm(request.POST, instance=complaint)
        if form.is_valid():
            form.save()
            messages.success(request, 'Complaint reply submitted.')
            return redirect('dashboard_home')
    else:
        form = ComplaintReplyForm(instance=complaint)

    return render(request, 'complaints/reply_complaint.html', {'form': form, 'complaint': complaint})
