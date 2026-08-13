from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import customer_required, worker_required
from bookings.models import Job
from notifications.models import Notification
from .forms import CustomerPaymentForm, PaymentForm
from .models import Payment, PayoutRequest


@customer_required
def make_payment(request, job_id):
    """Customer payment for completed job.
    Flow:
    1. Job must be COMPLETED
    2. Customer pays the service price
    3. System automatically calculates 10% commission
    4. Worker earnings = customer_amount - commission
    5. Worker sees pending earnings until payment is verified
    """
    job = get_object_or_404(Job, pk=job_id)

    if job.customer != request.user:
        messages.error(request, 'You can only pay for your own jobs.')
        return redirect('booking_list')

    if job.status != 'COMPLETED':
        messages.error(request, 'Payment is only allowed after the job is completed.')
        return redirect('job_detail', pk=job.pk)

    # Get or create payment record
    payment, created = Payment.objects.get_or_create(
        job=job,
        defaults={
            'customer_amount': job.final_price,
            'payment_status': 'Pending',
            'worker_payout_status': 'Pending',
        }
    )

    # Auto-calculate commission on first save
    if created and not payment.platform_commission:
        payment.calculate_commission()
        payment.save()

    if request.method == 'POST':
        form = CustomerPaymentForm(request.POST, request.FILES, instance=payment)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.job = job
            payment.customer_amount = Decimal(str(job.final_price))
            payment.payment_method = form.cleaned_data.get('payment_method')

            # When customer provides transaction ID or receipt, mark as pending verification
            if payment.transaction_id or payment.receipt:
                payment.payment_status = 'Pending'  # Awaiting admin verification
                
                # Add pending earnings to worker (not yet available for withdrawal)
                worker_profile = job.worker.worker_profile
                worker_profile.pending_earnings += payment.worker_amount
                worker_profile.total_earnings += payment.worker_amount
                worker_profile.save(update_fields=['pending_earnings', 'total_earnings'])
                
                # Send notification to customer about payment submission
                Notification.create_notification(
                    user=request.user,
                    title=f"Payment Submitted for {job.title}",
                    message=f"Your payment of ৳{payment.customer_amount} has been submitted and is awaiting admin verification.",
                    notification_type='JOB_PAYMENT_SUBMITTED',
                    payment=payment,
                    job=job,
                )
                
                messages.success(
                    request,
                    f'Payment submitted! Your transaction ID is {payment.transaction_id}. '
                    f'Once verified, the worker will receive ৳{payment.worker_amount:.2f}.'
                )
                payment.save()
                return redirect('payment_history')
            else:
                messages.error(request, 'Please provide transaction ID or receipt to proceed.')

        return render(request, 'payments/payment_form.html', {'form': form, 'job': job, 'payment': payment})
    else:
        form = CustomerPaymentForm(instance=payment)

    return render(request, 'payments/payment_form.html', {'form': form, 'job': job, 'payment': payment})


@customer_required
def payment_history(request):
    """Show customer's payment history."""
    # Get payments from Job-based workflow
    payments = Payment.objects.filter(job__customer=request.user).select_related('job', 'job__worker')
    return render(request, 'payments/payment_history.html', {'payments': payments})


@worker_required
def payout_request_list(request):
    """Show worker's payout requests and earnings breakdown."""
    payout_requests = PayoutRequest.objects.filter(worker=request.user).order_by('-created_at')
    worker_profile = request.user.worker_profile
    earnings_breakdown = worker_profile.get_earnings_breakdown()
    
    context = {
        'payout_requests': payout_requests,
        'pending_earnings': earnings_breakdown['pending'],
        'available_earnings': earnings_breakdown['available'],
        'withdrawn_earnings': earnings_breakdown['withdrawn'],
        'total_earned': earnings_breakdown['total_earned'],
    }
    return render(request, 'payments/payout_request_list.html', context)


@worker_required
def create_payout_request(request):
    """Worker requests a payout from available earnings."""
    worker_profile = request.user.worker_profile
    available_amount = worker_profile.available_earnings

    if available_amount <= 0:
        messages.error(request, 'You have no available earnings to withdraw.')
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
                messages.error(request, 'Amount must be greater than 0.')
                return redirect('create_payout_request')
            if amount > available_amount:
                messages.error(request, f'Cannot withdraw more than available (৳{available_amount:.2f})')
                return redirect('create_payout_request')

            payout_request = PayoutRequest.objects.create(
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
                f'Payout request submitted for ৳{amount:.2f}. Admin will review and process it within 2-3 business days.'
            )
            return redirect('payout_request_list')

        except (ValueError, TypeError):
            messages.error(request, 'Invalid amount.')
            return redirect('create_payout_request')

    context = {
        'available_earnings': available_amount,
        'payout_methods': PayoutRequest._meta.get_field('payout_method').choices,
    }
    return render(request, 'payments/create_payout_request.html', context)
