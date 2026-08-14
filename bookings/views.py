from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db.models import Q, Count
import django.utils.timezone

from accounts.decorators import admin_required, customer_required, worker_required
from services.models import Service
from workers.models import WorkerProfile
from notifications.models import Notification

from .forms import (
    BookingCreateForm,
    BookingAssignForm,
    BookingMessageForm,
    BookingStatusUpdateForm,
    BookingUpdateForm,
    ServiceRequestCreateForm,
    JobApplicationForm,
    JobApplicationReviewForm,
    JobForm,
    JobCompletionForm,
)
from .models import Booking, BookingMessage, ServiceRequest, JobApplication, Job


def _get_related_workers(service):
    category_matches = WorkerProfile.objects.filter(
        user__role='worker',
        user__worker_status='APPROVED',
        service_category__icontains=service.category,
    )
    skill_matches = WorkerProfile.objects.filter(
        user__role='worker',
        user__worker_status='APPROVED',
        skills__icontains=service.category,
    )
    direct_matches = WorkerProfile.objects.filter(
        user__role='worker',
        user__worker_status='APPROVED',
        service=service,
    )

    combined = (category_matches | skill_matches | direct_matches).distinct().select_related('user')[:4]
    return combined


@login_required
def booking_list(request):
    if request.user.role == 'admin':
        messages.warning(request, 'Admin access is limited to reports and user management. Job workflow pages are not available to admins.')
        return redirect('dashboard_home')
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
@customer_required
def my_bookings(request):
    """Show customer's all bookings"""
    bookings = Booking.objects.filter(customer=request.user).select_related('worker', 'service').order_by('-created_at')
    
    return render(
        request,
        'bookings/my_bookings.html',
        {'bookings': bookings}
    )


@login_required
@customer_required
def my_jobs(request):
    """Show customer's active jobs from Phase 2 workflow (ServiceRequest → Job)"""
    jobs = Job.objects.filter(customer=request.user).select_related('worker', 'service_request').order_by('-created_at')
    
    return render(
        request,
        'bookings/my_jobs.html',
        {'jobs': jobs}
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

    if request.user.role == 'admin':
        messages.warning(request, 'Admins cannot view customer or worker invoice pages.')
        return redirect('dashboard_home')

    if request.user.role == 'customer' and booking.customer == request.user:
        return render(request, 'bookings/invoice.html', {'booking': booking})

    if request.user.role == 'worker' and booking.worker == request.user:
        return render(request, 'bookings/invoice.html', {'booking': booking})

    messages.error(request, 'You can only view invoices for your own booking or your assigned booking.')
    return redirect('booking_list')


# ===== PHASE 2 VIEWS: ServiceRequest, JobApplication, Job Workflow =====


@login_required
@customer_required
def service_request_create(request, service_id=None):
    """Customer creates a new service request"""
    service = None
    if service_id:
        service = get_object_or_404(Service, pk=service_id)
    
    if request.method == 'POST':
        form = ServiceRequestCreateForm(request.POST, service=service)
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.customer = request.user
            if service:
                service_request.service = service
            else:
                service_request.service = get_object_or_404(Service, pk=request.POST.get('service'))
            service_request.save()
            messages.success(request, 'Service request created successfully!')
            return redirect('service_request_detail', pk=service_request.pk)
    else:
        form = ServiceRequestCreateForm(service=service)
        if service:
            form.initial['service'] = service
    
    context = {
        'form': form,
        'service': service,
    }
    return render(request, 'bookings/service_request_form.html', context)


@login_required
def service_request_list(request):
    """List service requests based on user role"""
    if request.user.role == 'admin':
        messages.warning(request, 'Admins can view reports and manage users, but they cannot access the customer/worker request workflow.')
        return redirect('dashboard_home')
    if request.user.role == 'customer':
        service_requests = ServiceRequest.objects.filter(customer=request.user)
    elif request.user.role == 'worker':
        service_requests = ServiceRequest.objects.filter(
            status__in=['OPEN', 'REVIEWING']
        )
    else:
        service_requests = ServiceRequest.objects.none()

    service_requests = service_requests.annotate(
        application_count=Count('job_applications')
    ).order_by('-created_at')

    context = {'service_requests': service_requests}
    return render(request, 'bookings/service_request_list.html', context)


@login_required
def service_request_detail(request, pk):
    """View service request details and applications"""
    service_request = get_object_or_404(ServiceRequest, pk=pk)
    
    # Permission check
    if request.user.role == 'customer' and service_request.customer != request.user:
        if request.user.role != 'admin':
            messages.error(request, 'You do not have permission to view this request.')
            return redirect('service_request_list')
    
    # Get applications
    if request.user.role == 'customer' or request.user.role == 'admin':
        applications = service_request.job_applications.all()
    else:
        # Worker can see their own application
        applications = service_request.job_applications.filter(worker=request.user)
    
    context = {
        'service_request': service_request,
        'applications': applications,
    }
    return render(request, 'bookings/service_request_detail.html', context)


@login_required
@worker_required
def job_application_create(request, service_request_id):
    """Worker applies for a service request"""
    service_request = get_object_or_404(ServiceRequest, pk=service_request_id)
    
    # Check if worker already applied
    existing_application = JobApplication.objects.filter(
        service_request=service_request,
        worker=request.user
    ).first()
    
    if existing_application:
        messages.warning(request, 'You have already applied for this request.')
        return redirect('service_request_detail', pk=service_request.pk)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.service_request = service_request
            application.worker = request.user
            
            # Capture worker stats at time of application
            if hasattr(request.user, 'worker_profile'):
                profile = request.user.worker_profile
                application.worker_rating_at_application = profile.average_rating_cached
                application.worker_completed_jobs = profile.completed_jobs
            
            application.save()
            messages.success(request, 'Application submitted successfully!')
            return redirect('service_request_detail', pk=service_request.pk)
    else:
        form = JobApplicationForm()
    
    context = {
        'form': form,
        'service_request': service_request,
    }
    return render(request, 'bookings/job_application_form.html', context)


@login_required
@customer_required
def job_application_review(request, pk):
    """Customer reviews a job application and accepts/rejects"""
    application = get_object_or_404(JobApplication, pk=pk)
    
    # Permission check
    if application.service_request.customer != request.user:
        messages.error(request, 'You do not have permission to review this application.')
        return redirect('service_request_list')
    
    if request.method == 'POST':
        action = request.POST.get('action', '').upper()
        
        if action == 'ACCEPTED':
            # Create a Job from this application
            try:
                job = Job.objects.create(
                    service_request=application.service_request,
                    job_application=application,
                    customer=request.user,
                    worker=application.worker,
                    title=application.service_request.title,
                    description=application.service_request.description,
                    proposed_price=application.proposed_price,
                    estimated_duration=application.estimated_duration,
                    scheduled_date=application.can_start_date,
                    location=application.service_request.location,
                    address=application.service_request.address,
                )
                application.status = 'ACCEPTED'
                application.save()
                
                # Update service request status
                application.service_request.status = 'ASSIGNED'
                application.service_request.save()
                
                # Reject other applications
                JobApplication.objects.filter(
                    service_request=application.service_request
                ).exclude(pk=application.pk).update(status='REJECTED')
                
                messages.success(request, 'Application accepted! Job created successfully!')
                return redirect('job_detail', pk=job.pk)
            except Exception as e:
                messages.error(request, f'Error creating job: {str(e)}')
                return redirect('service_request_detail', pk=application.service_request.pk)
            
        elif action == 'REJECTED':
            application.status = 'REJECTED'
            application.save()
            messages.success(request, 'Application rejected.')
            return redirect('service_request_detail', pk=application.service_request.pk)
    
    context = {'application': application}
    return render(request, 'bookings/job_application_detail.html', context)


@login_required
def job_detail(request, pk):
    """View job details"""
    from django.core.exceptions import ObjectDoesNotExist
    
    try:
        job = Job.objects.get(pk=pk)
    except Job.DoesNotExist:
        messages.error(request, f'Job #{pk} not found. It may have been deleted or the link is invalid.')
        return redirect('my_jobs')
    
    # Permission check
    if request.user != job.customer and request.user != job.worker:
        if request.user.role != 'admin':
            messages.error(request, 'You do not have permission to view this job.')
            return redirect('service_request_list')
    
    context = {'job': job}
    return render(request, 'bookings/job_detail.html', context)


@login_required
@worker_required
def job_complete(request, pk):
    """Worker marks a job as completed"""
    job = get_object_or_404(Job, pk=pk)
    
    if job.worker != request.user:
        messages.error(request, 'Only the assigned worker can mark this job as completed.')
        return redirect('job_detail', pk=job.pk)
    
    if request.method == 'POST':
        form = JobCompletionForm(request.POST, instance=job)
        if form.is_valid():
            job = form.save(commit=False)
            job.status = 'COMPLETED'
            job.actual_end_time = django.utils.timezone.now()
            job.save()
            
            # Send notification to customer
            Notification.create_notification(
                user=job.customer,
                title=f"Job Completed - {job.title}",
                message=f"The worker has marked the job '{job.title}' as completed. Please review and make payment.",
                notification_type='JOB_COMPLETED',
                job=job,
                related_user=job.worker,
            )
            
            messages.success(request, 'Job marked as completed!')
            return redirect('job_detail', pk=job.pk)
    else:
        form = JobCompletionForm(instance=job)
    
    context = {
        'job': job,
        'form': form,
    }
    return render(request, 'bookings/job_completion_form.html', context)


@login_required
@customer_required
def cancel_job(request, pk):
    """Customer cancels a job"""
    job = get_object_or_404(Job, pk=pk)
    
    # Permission check - only customer can cancel
    if job.customer != request.user:
        messages.error(request, 'You can only cancel your own jobs.')
        return redirect('job_detail', pk=job.pk)
    
    # Can only cancel jobs that haven't been completed
    if job.status in ['COMPLETED', 'CANCELLED']:
        messages.error(request, 'This job cannot be cancelled.')
        return redirect('job_detail', pk=job.pk)
    
    if request.method == 'POST':
        cancel_reason = request.POST.get('cancel_reason', 'No reason provided')
        job.status = 'CANCELLED'
        job.save(update_fields=['status', 'updated_at'])
        
        # Send notification to worker
        Notification.create_notification(
            user=job.worker,
            title=f"Job Cancelled - {job.title}",
            message=f"The customer has cancelled the job '{job.title}'. Reason: {cancel_reason}",
            notification_type='JOB_CANCELLED',
            job=job,
            related_user=job.customer,
        )
        
        messages.success(request, 'Job cancelled successfully.')
        return redirect('job_detail', pk=job.pk)
    
    context = {'job': job}
    return render(request, 'bookings/cancel_job.html', context)


@login_required
@worker_required
def worker_my_jobs(request):
    """
    Show worker's all jobs including:
    - Pending applications (customer requests they applied to)
    - Accepted applications (customer requests where they were chosen)
    - Active jobs (jobs in progress or confirmed)
    - Completed jobs
    Includes status and messaging capability
    """
    # Get all pending applications by this worker
    pending_applications = JobApplication.objects.filter(
        worker=request.user,
        status='PENDING'
    ).select_related('service_request', 'service_request__customer').order_by('-created_at')
    
    # Get all accepted applications (but not yet jobs)
    accepted_applications = JobApplication.objects.filter(
        worker=request.user,
        status='ACCEPTED'
    ).select_related('service_request', 'service_request__customer').order_by('-created_at')
    
    # Get all active jobs (confirmed and in progress)
    active_jobs = Job.objects.filter(
        worker=request.user,
        status__in=['CONFIRMED', 'IN_PROGRESS']
    ).select_related('customer', 'service_request').order_by('-created_at')
    
    # Get all completed jobs
    completed_jobs = Job.objects.filter(
        worker=request.user,
        status='COMPLETED'
    ).select_related('customer', 'service_request').order_by('-created_at')
    
    context = {
        'pending_applications': pending_applications,
        'accepted_applications': accepted_applications,
        'active_jobs': active_jobs,
        'completed_jobs': completed_jobs,
        'total_jobs': len(active_jobs),
        'total_completed': len(completed_jobs),
    }
    
    return render(request, 'bookings/worker_my_jobs.html', context)


@login_required
@worker_required
def worker_available_jobs(request):
    """
    Show all jobs assigned to this worker.
    Worker can only see jobs where they are the assigned worker.
    """
    if request.user.worker_status != 'APPROVED':
        messages.error(request, 'You must be approved by admin before viewing available jobs.')
        return redirect('home')
    
    # Get all jobs assigned to this worker
    available_jobs = Job.objects.filter(
        worker=request.user
    ).select_related(
        'customer', 'service_request'
    ).order_by('-created_at')
    
    context = {
        'jobs': available_jobs,
    }
    return render(request, 'bookings/worker_available_jobs.html', context)


@login_required
def job_messages(request, pk):
    """
    View messages between worker and customer for a specific job.
    Both worker and customer can access this.
    """
    job = get_object_or_404(Job, pk=pk)
    
    # Permission check
    if request.user != job.customer and request.user != job.worker:
        if request.user.role != 'admin':
            messages.error(request, 'You do not have permission to view job messages.')
            return redirect('home')
    
    # Get or create a BookingMessage thread (using job as reference)
    # For now, we'll use BookingMessage with a booking-like relationship
    job_messages = BookingMessage.objects.filter(
        Q(sender=job.worker) | Q(sender=job.customer)
    ).filter(
        booking__isnull=True
    ).order_by('created_at')
    
    # Add a way to track job messages by storing them with booking for simplicity
    # Or create a new message for each job interaction
    
    if request.method == 'POST':
        message_text = request.POST.get('message', '').strip()
        
        if message_text:
            # Create a new message
            # We'll store it as a booking message but associate with the job
            # In production, you'd want a JobMessage model
            booking_message = BookingMessage.objects.create(
                booking=None,  # Jobs don't use Booking model
                sender=request.user,
                message=message_text,
            )
            
            # Create a notification for the other party
            recipient = job.customer if request.user == job.worker else job.worker
            Notification.create_notification(
                user=recipient,
                title=f"New message in job: {job.title}",
                message=f"{request.user.username}: {message_text[:50]}...",
                notification_type='JOB_MESSAGE',
                job=job,
                related_user=request.user,
            )
            
            messages.success(request, 'Message sent!')
            return redirect('job_messages', pk=job.pk)
    
    context = {
        'job': job,
        'messages': job_messages,
    }
    return render(request, 'bookings/job_messages.html', context)


@login_required
@customer_required
def initiate_payment(request, job_id):
    """
    Customer initiates payment for a completed job.
    This creates a Payment record and shows payment options.
    """
    job = get_object_or_404(Job, pk=job_id)
    
    # Permission check
    if job.customer != request.user:
        messages.error(request, 'You can only pay for your own jobs.')
        return redirect('my_jobs')
    
    # Check job is completed
    if job.status != 'COMPLETED':
        messages.error(request, 'You can only pay for completed jobs.')
        return redirect('job_detail', pk=job.pk)
    
    # Check if payment already exists
    existing_payment = Payment.objects.filter(job=job).first()
    if existing_payment:
        if existing_payment.payment_status == 'Verified':
            messages.info(request, 'Payment for this job has already been completed.')
            return redirect('job_detail', pk=job.pk)
        else:
            return redirect('make_payment', job_id=job.pk)
    
    # Create payment record
    from payments.models import Payment
    payment = Payment.objects.create(
        job=job,
        customer_amount=job.proposed_price,
        payment_method=request.POST.get('payment_method', 'BKash'),
    )
    
    # Redirect to payment completion
    return redirect('make_payment', job_id=job.pk)
