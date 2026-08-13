from decimal import Decimal

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

    if booking.status != 'Completed':
        messages.error(request, 'Payment is allowed only after the service is completed.')
        return redirect('booking_detail', pk=booking.pk)

    payment, created = Payment.objects.get_or_create(
        booking=booking,
        defaults={
            'amount': booking.service.price,
            'customer_amount': booking.service.price,
            'payment_status': 'Pending',
        }
    )

    if request.method == 'POST':
        form = CustomerPaymentForm(request.POST, request.FILES, instance=payment)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.booking = booking
            payment.amount = Decimal(str(booking.service.price))
            payment.customer_amount = Decimal(str(booking.service.price))
            payment.payment_method = form.cleaned_data.get('payment_method')

            if payment.transaction_id or payment.receipt:
                payment.payment_status = 'Paid'
                if payment.customer_amount and not payment.platform_commission:
                    payment.calculate_commission()
            else:
                payment.payment_status = 'Pending'

            payment.save()

            if payment.payment_status == 'Paid':
                messages.success(request, 'Payment completed successfully. The worker can now receive their share.')
                return redirect('payment_history')

            messages.success(request, 'Payment information saved. Complete the payment to confirm.')
            return redirect('payment_history')
    else:
        form = CustomerPaymentForm(instance=payment)

    return render(request, 'payments/payment_form.html', {'form': form, 'booking': booking})


@customer_required
def payment_history(request):
    payments = Payment.objects.filter(booking__customer=request.user)
    return render(request, 'payments/payment_history.html', {'payments': payments})
