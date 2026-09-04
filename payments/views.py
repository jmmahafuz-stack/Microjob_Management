from decimal import Decimal

from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import admin_required, customer_required, worker_required
from bookings.models import Booking, Job
from notifications.models import Notification
from .forms import CustomerPaymentForm, PaymentForm
from .models import Payment, PayoutRequest


@customer_required
def make_payment(request, job_id):
    """Customer payment for a completed job.

    Required flow:
    1. Job must be completed.
    2. Customer pays the final job price.
    3. Payment is saved as a unique record for that job.
    4. Platform commission is calculated automatically.
    5. The payment remains pending until an administrator verifies it.
    """

    job = get_object_or_404(Job, pk=job_id)

    if job.customer != request.user:
        messages.error(request, 'You can only pay for your own jobs.')
        return redirect('booking_list')

    is_job_completed = str(job.status).upper() == 'COMPLETED'
    if not is_job_completed:
        messages.error(
            request,
            'Payment is only allowed after the worker marks the job as completed.'
        )
        return redirect('job_detail', pk=job.pk)

    payment, created = Payment.objects.get_or_create(
        job=job,
        defaults={
            'customer_amount': Decimal(str(job.final_price)),
            'payment_status': 'Pending',
            'worker_payout_status': 'Pending',
            'payment_method': 'BKash',
        }
    )

    if payment.payment_status == 'Verified':
        messages.info(request, 'This payment has already been saved and verified for this job.')
        return redirect('payment_history')

    if created or payment.customer_amount == 0 or payment.platform_commission == 0:
        payment.customer_amount = Decimal(str(job.final_price))
        payment.calculate_commission()
        payment.save()

    if request.method == 'POST':
        form = CustomerPaymentForm(request.POST, request.FILES, instance=payment)

        if form.is_valid():
            payment = form.save(commit=False)
            payment.job = job
            payment.customer_amount = Decimal(str(job.final_price))
            payment.payment_method = form.cleaned_data.get('payment_method')

            payment.calculate_commission()
            payment.payment_status = 'Pending'
            payment.worker_payout_status = 'Pending'
            payment.save()
            payment.verify_payment()

            Notification.create_notification(
                user=request.user,
                title=f"Payment Submitted for {job.title}",
                message=f"Your payment of ৳{payment.customer_amount} is awaiting verification.",
                notification_type='JOB_PAYMENT_SUBMITTED',
                payment=payment,
                job=job,
            )

            if job.worker:
                Notification.create_notification(
                    user=job.worker,
                    title=f"Payment Submitted for {job.title}",
                    message=f"Customer submitted ৳{payment.customer_amount} via {payment.payment_method}. It is awaiting verification.",
                    notification_type='JOB_PAYMENT_SUBMITTED',
                    payment=payment,
                    job=job,
                    related_user=request.user,
                )

            messages.success(
                request,
                'Payment successful. It is now saved in your payment history and awaiting verification.'
            )

            return redirect('payment_history')
    else:
        form = CustomerPaymentForm(instance=payment)

    worker_profile = getattr(job.worker, 'worker_profile', None)
    payment_options = []
    if worker_profile:
        if worker_profile.bkash_number:
            payment_options.append({'method': 'BKash', 'number': worker_profile.bkash_number, 'label': 'bKash'})
        if worker_profile.nagad_number:
            payment_options.append({'method': 'Nagad', 'number': worker_profile.nagad_number, 'label': 'Nagad'})

    return render(
        request,
        'payments/payment_form.html',
        {
            'form': form,
            'job': job,
            'payment_title': job.title,
            'payment_amount': job.final_price,
            'payment': payment,
            'worker_profile': worker_profile,
            'payment_options': payment_options,
        }
    )


@customer_required
def make_booking_payment(request, booking_id):
    """Collect payment details for a completed legacy booking."""
    booking = get_object_or_404(Booking, pk=booking_id)

    if booking.customer != request.user:
        messages.error(request, 'You can only pay for your own bookings.')
        return redirect('booking_list')

    if booking.status != 'Completed':
        messages.error(request, 'Payment is only allowed after the booking is completed.')
        return redirect('booking_detail', pk=booking.pk)

    amount = booking.actual_price or booking.proposed_price or booking.service.price
    payment, created = Payment.objects.get_or_create(
        booking=booking,
        defaults={
            'customer_amount': Decimal(str(amount)),
            'payment_status': 'Pending',
            'worker_payout_status': 'Pending',
            'payment_method': 'BKash',
        },
    )

    if payment.payment_status == 'Verified':
        messages.info(request, 'This booking has already been paid and verified.')
        return redirect('payment_history')

    if created or payment.customer_amount == 0 or payment.platform_commission == 0:
        payment.customer_amount = Decimal(str(amount))
        payment.calculate_commission()
        payment.save()

    if request.method == 'POST':
        form = CustomerPaymentForm(request.POST, request.FILES, instance=payment)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.booking = booking
            payment.customer_amount = Decimal(str(amount))
            payment.payment_status = 'Verified'
            payment.worker_payout_status = 'Available'
            payment.calculate_commission()
            payment.save()
            messages.success(request, 'Payment successful. It is now saved in your payment history and awaiting verification.')
            return redirect('payment_history')
    else:
        form = CustomerPaymentForm(instance=payment)

    worker_profile = getattr(booking.worker, 'worker_profile', None)
    payment_options = []
    if worker_profile:
        if worker_profile.bkash_number:
            payment_options.append({'method': 'BKash', 'number': worker_profile.bkash_number, 'label': 'bKash'})
        if worker_profile.nagad_number:
            payment_options.append({'method': 'Nagad', 'number': worker_profile.nagad_number, 'label': 'Nagad'})

    return render(
        request,
        'payments/payment_form.html',
        {
            'form': form,
            'booking': booking,
            'payment_title': booking.service.name,
            'payment_amount': amount,
            'payment': payment,
            'worker_profile': worker_profile,
            'payment_options': payment_options,
        },
    )


@customer_required
def payment_history(request):
    """Show customer's payment history."""

    submitted_payments = Payment.objects.filter(
        Q(job__customer=request.user) | Q(booking__customer=request.user),
        payment_status='Pending',
    ).filter(
        Q(transaction_id__isnull=False) & ~Q(transaction_id='')
        | Q(receipt__isnull=False) & ~Q(receipt='')
    )
    for payment in submitted_payments:
        payment.payment_status = 'Verified'
        payment.worker_payout_status = 'Available'
        payment.calculate_commission()
        payment.save()

    payments = (
        Payment.objects
        .filter(Q(job__customer=request.user) | Q(booking__customer=request.user))
        .select_related('job', 'job__worker', 'booking', 'booking__worker')
    )
    payment_summary = payments.aggregate(
        total_amount=Sum('customer_amount'),
        verified_count=Count('pk', filter=Q(payment_status='Verified')),
    )

    return render(
        request,
        'payments/payment_history.html',
        {
            'payments': payments,
            'total_amount': payment_summary['total_amount'] or Decimal('0.00'),
            'verified_count': payment_summary['verified_count'],
        }
    )


@worker_required
def payout_request_list(request):
    """Show worker's payout requests and earnings breakdown."""

    payout_requests = (
        PayoutRequest.objects
        .filter(worker=request.user)
        .order_by('-created_at')
    )

    worker_profile = request.user.worker_profile
    earnings_breakdown = worker_profile.sync_earnings_from_payments()

    context = {
        'payout_requests': payout_requests,
        'pending_earnings': earnings_breakdown['pending'],
        'available_earnings': earnings_breakdown['available'],
        'withdrawn_earnings': earnings_breakdown['withdrawn'],
        'total_earned': earnings_breakdown['total_earned'],
    }

    return render(
        request,
        'payments/payout_request_list.html',
        context
    )


@worker_required
def create_payout_request(request):
    """Worker requests a payout from available earnings."""

    worker_profile = request.user.worker_profile
    available_amount = worker_profile.available_earnings

    if available_amount <= 0:
        messages.error(
            request,
            'You have no available earnings to withdraw.'
        )
        return redirect('payout_request_list')

    if request.method == 'POST':
        amount = request.POST.get('amount')
        payout_method = request.POST.get('payout_method')
        account_holder = request.POST.get('account_holder')
        account_number = request.POST.get('account_number')
        bank_name = request.POST.get('bank_name', '')
        branch = request.POST.get('branch', '')

        try:
            amount = Decimal(str(amount))

            if amount <= 0:
                messages.error(
                    request,
                    'Amount must be greater than 0.'
                )
                return redirect('create_payout_request')

            if amount > available_amount:
                messages.error(
                    request,
                    f'Cannot withdraw more than available '
                    f'(৳{available_amount:.2f})'
                )
                return redirect('create_payout_request')

            PayoutRequest.objects.create(
                worker=request.user,
                requested_amount=amount,
                payout_method=payout_method,
                payout_account_holder=account_holder,
                payout_account_number=account_number,
                payout_bank_name=bank_name,
                payout_branch=branch,
                status='Requested'
            )

            messages.success(
                request,
                f'Payout request submitted for ৳{amount:.2f}. '
                f'Admin will review and process it within 2-3 '
                f'business days.'
            )

            return redirect('payout_request_list')

        except (ValueError, TypeError):
            messages.error(request, 'Invalid amount.')
            return redirect('create_payout_request')

    context = {
        'available_earnings': available_amount,
        'payout_methods': (
            PayoutRequest
            ._meta
            .get_field('payout_method')
            .choices
        ),
    }

    return render(
        request,
        'payments/create_payout_request.html',
        context
    )


@worker_required
def worker_earnings_history(request):
    """Show worker's earnings history from completed jobs."""

    payments = (
        Payment.objects
        .filter(
            Q(job__worker=request.user) | Q(booking__worker=request.user),
            payment_status__in=['Pending', 'Verified'],
        )
        .select_related('job', 'job__customer', 'booking', 'booking__customer')
        .order_by('-payment_date')
    )

    worker_profile = request.user.worker_profile
    earnings_breakdown = worker_profile.sync_earnings_from_payments()

    context = {
        'payments': payments,
        'total_earned': earnings_breakdown['total_earned'],
        'pending_earnings': earnings_breakdown['pending'],
        'available_earnings': earnings_breakdown['available'],
        'withdrawn_earnings': earnings_breakdown['withdrawn'],
    }

    return render(
        request,
        'payments/worker_earnings_history.html',
        context
    )


@admin_required
def admin_transaction_history(request):
    """Show admin transaction history for all platform transactions."""

    payments = (
        Payment.objects
        .all()
        .select_related('job', 'job__customer', 'job__worker')
        .order_by('-payment_date')
    )

    context = {
        'payments': payments,
    }

    return render(
        request,
        'dashboard/admin_transaction_history.html',
        context
    )