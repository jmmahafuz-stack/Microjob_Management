from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import customer_required
from bookings.models import Booking
from .forms import CustomerPaymentForm, PaymentForm
from .models import Payment


@customer_required
def make_payment(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if booking.customer != request.user:
        messages.error(request, 'You can only pay for your own booking.')
        return redirect('booking_list')

    payment, created = Payment.objects.get_or_create(
        booking=booking,
        defaults={
            'amount': booking.service.price,
            'payment_status': 'Pending',
        }
    )

    if request.method == 'POST':
        form = CustomerPaymentForm(request.POST, request.FILES, instance=payment)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.booking = booking
            payment.amount = booking.service.price
            if payment.transaction_id or payment.receipt:
                payment.payment_status = 'Paid'
            else:
                payment.payment_status = 'Pending'
            payment.save()
            if payment.payment_status == 'Paid':
                messages.success(request, 'Payment completed successfully.')
            else:
                messages.success(request, 'Payment information saved. Complete the payment to confirm.')
            return redirect('payment_history')
    else:
        form = CustomerPaymentForm(instance=payment)

    return render(request, 'payments/payment_form.html', {'form': form, 'booking': booking})


@customer_required
def payment_history(request):
    payments = Payment.objects.filter(booking__customer=request.user)
    return render(request, 'payments/payment_history.html', {'payments': payments})
