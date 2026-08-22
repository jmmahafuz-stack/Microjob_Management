from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db.models import Exists, OuterRef, Q
import django.utils.timezone

from accounts.decorators import admin_required, customer_required, worker_required
from services.models import Service
from workers.models import WorkerProfile
from notifications.models import Notification
from payments.models import Payment

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
    WorkerResponseForm,
)
from .models import Booking, BookingMessage, ServiceRequest, JobApplication, Job, WorkerResponse


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
    verified_payment = Payment.objects.filter(
        job=OuterRef('pk'),
        payment_status='Verified',
    )
    unread_worker_message = Notification.objects.filter(
        job=OuterRef('pk'),
        user=request.user,
        related_user=OuterRef('worker'),
        notification_type='JOB_MESSAGE',
        is_read=False,
    )
    accepted_jobs = Job.objects.filter(
        customer=request.user,
        status__in=['CONFIRMED', 'IN_PROGRESS', 'COMPLETED'],
    ).annotate(
        payment_completed=Exists(verified_payment),
        has_unread_worker_message=Exists(unread_worker_message),
    ).select_related('worker', 'service_request').order_by('-created_at')
    all_service_requests = ServiceRequest.objects.filter(customer=request.user)
    service_requests = all_service_requests.filter(
        status__in=['OPEN', 'REVIEWING'],
    ).select_related('service').prefetch_related('job_applications').order_by('-created_at')
    total_booked = bookings.count() + all_service_requests.count()
    accepted_count = accepted_jobs.count()
    in_progress_count = accepted_jobs.filter(status='IN_PROGRESS').count()
    completed_count = accepted_jobs.filter(status='COMPLETED').count()
    unread_worker_messages = Notification.objects.filter(
        user=request.user,
        notification_type='JOB_MESSAGE',
        is_read=False,
        job__isnull=False,
    ).select_related('job').order_by('-created_at')
    
    return render(
        request,
        'bookings/my_bookings.html',
        {
            'bookings': bookings,
            'accepted_jobs': accepted_jobs,
            'service_requests': service_requests,
            'total_booked': total_booked,
            'accepted_count': accepted_count,
            'in_progress_count': in_progress_count,
            'completed_count': completed_count,
            'unread_worker_messages': unread_worker_messages,
        }
    )


@login_required
@customer_required
def my_jobs(request):
    """Show the customer's side of the request → accept → work → complete → pay lifecycle."""
    verified_payment = Payment.objects.filter(
        job=OuterRef('pk'),
        payment_status='Verified',
    )
    unread_worker_message = Notification.objects.filter(
        job=OuterRef('pk'),
        user=request.user,
        related_user=OuterRef('worker'),
        notification_type='JOB_MESSAGE',
        is_read=False,
    )
    job_queryset = Job.objects.annotate(
        payment_completed=Exists(verified_payment),
        has_unread_worker_message=Exists(unread_worker_message),
    ).select_related('worker', 'service_request').order_by('-created_at')
    confirmed_jobs = job_queryset.filter(customer=request.user, status='CONFIRMED')
    active_jobs = job_queryset.filter(customer=request.user, status='IN_PROGRESS')
    completed_jobs = job_queryset.filter(customer=request.user, status='COMPLETED')

    context = {
        'confirmed_jobs': confirmed_jobs,
        'active_jobs': active_jobs,
        'completed_jobs': completed_jobs,
        'total_jobs': len(confirmed_jobs) + len(active_jobs),
        'total_completed': len(completed_jobs),
    }

    return render(
        request,
        'bookings/my_jobs.html',
        context
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
    response_form = WorkerResponseForm()
    booking_payment = getattr(booking, 'payment', None)

    booking_messages = booking.messages.all()
    worker_responses = booking.worker_responses.all().order_by('-created_at')
    latest_response = worker_responses.first() if worker_responses.exists() else None

    # Handle worker submitting a response
    if request.method == 'POST' and 'worker_response' in request.POST:
        if request.user.role != 'worker' or booking.worker != request.user:
            messages.error(request, 'Only assigned workers can submit responses.')
            return redirect('booking_detail', pk=booking.pk)

        response_form = WorkerResponseForm(request.POST)
        if response_form.is_valid():
            worker_response = response_form.save(commit=False)
            worker_response.booking = booking
            worker_response.worker = request.user
            worker_response.save()
            messages.success(request, 'Your response has been sent to the customer.')
            return redirect('booking_detail', pk=booking.pk)

    # Handle message posting
    if request.method == 'POST' and 'send_message' in request.POST:
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
            'response_form': response_form,
            'booking_messages': booking_messages,
            'worker_responses': worker_responses,
            'latest_response': latest_response,
        }
    )


@login_required
@customer_required
def accept_worker_response(request, response_id):
    """Customer accepts a worker's response"""
    worker_response = get_object_or_404(WorkerResponse, pk=response_id)
    booking = worker_response.booking

    if booking.customer != request.user:
        messages.error(request, 'You can only accept responses for your own bookings.')
        return redirect('booking_list')

    if request.method == 'POST':
        worker_response.customer_accepted = True
        worker_response.save()
        
        # Update booking status if worker accepted
        if worker_response.status == 'ACCEPTED':
            booking.status = 'Confirmed'
            booking.save()
            messages.success(request, 'You have accepted the worker\'s proposal. The booking is now confirmed!')
        else:
            messages.success(request, 'Your response has been recorded.')
        
        return redirect('booking_detail', pk=booking.pk)

    return render(
        request,
        'bookings/confirm_response.html',
        {'worker_response': worker_response, 'booking': booking}
    )


@login_required
@customer_required
def reject_worker_response(request, response_id):
    """Customer rejects a worker's response"""
    worker_response = get_object_or_404(WorkerResponse, pk=response_id)
    booking = worker_response.booking

    if booking.customer != request.user:
        messages.error(request, 'You can only reject responses for your own bookings.')
        return redirect('booking_list')

    if request.method == 'POST':
        worker_response.delete()
        messages.info(request, 'You have rejected this worker\'s response. They will not be notified.')
        return redirect('booking_detail', pk=booking.pk)

    return render(
        request,
        'bookings/confirm_rejection.html',
        {'worker_response': worker_response, 'booking': booking}
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
            
            # Auto-assign a suitable worker if none selected
            if not booking.worker and booking.service:
                related_workers = _get_related_workers(booking.service)
                if related_workers.exists():
                    booking.worker = related_workers.first().user
                    booking.status = 'Assigned'
            
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
    selected_service_id = service_id or request.GET.get('service') or request.POST.get('service')
    service = get_object_or_404(Service, pk=selected_service_id) if selected_service_id else None
    
    if request.method == 'POST':
        form = ServiceRequestCreateForm(request.POST, service=service)
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.customer = request.user
            if service:
                service_request.service = service
            service_request.save()
            messages.success(request, 'Service request created successfully! Workers can now apply for your request.')
            return redirect('service_request_detail', pk=service_request.pk)
    else:
        initial = {'service': service} if service else {}
        form = ServiceRequestCreateForm(service=service, initial=initial)
    
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
    # Only hide clearly fake demo/test requests. Real work requests from valid customer
    # accounts must remain visible so workers can accept them and complete the workflow.
    demo_test_user_prefixes = ('test', 'demo')
    demo_test_titles = ('test job', 'test request', 'demo', 'house cleaning test', 'sample request')

    if request.user.role == 'customer':
        service_requests = ServiceRequest.objects.filter(customer=request.user)
    elif request.user.role == 'worker':
        if request.user.worker_status != 'APPROVED':
            messages.error(request, 'Your worker account is pending admin approval. You cannot take jobs yet.')
            return redirect('worker_dashboard')
        profile = getattr(request.user, 'worker_profile', None)
        if not profile:
            messages.error(request, 'Please create your worker profile and profession first.')
            return redirect('worker_profile_edit')
        allowed_categories = list(profile.categories.all())
        service_filter = __import__('django.db.models', fromlist=['Q']).Q(service__category__in=allowed_categories)
        if profile.service_id:
            service_filter |= __import__('django.db.models', fromlist=['Q']).Q(service=profile.service)
        if profile.service_category:
            service_filter |= __import__('django.db.models', fromlist=['Q']).Q(service__category__name__icontains=profile.service_category)
        if profile.profession:
            service_filter |= __import__('django.db.models', fromlist=['Q']).Q(service__category__name__icontains=profile.profession)
        service_requests = ServiceRequest.objects.filter(status='OPEN').filter(service_filter).exclude(
            customer__username__istartswith=demo_test_user_prefixes[0]
        ).exclude(
            customer__username__istartswith=demo_test_user_prefixes[1]
        )

        for fake_title in demo_test_titles:
            service_requests = service_requests.exclude(title__icontains=fake_title)
    else:
        service_requests = ServiceRequest.objects.none()

    service_requests = service_requests.order_by('-created_at')

    context = {'service_requests': service_requests}
    return render(request, 'bookings/service_request_list.html', context)


@login_required
def service_request_detail(request, pk):
    """View service request details and applications"""
    service_request = get_object_or_404(ServiceRequest, pk=pk)

    if request.user.role == 'admin':
        messages.warning(request, 'Admins cannot access the customer/worker request workflow.')
        return redirect('dashboard_home')

    # Permission check
    if request.user.role == 'customer' and service_request.customer != request.user:
        messages.error(request, 'You do not have permission to view this request.')
        return redirect('service_request_list')

    # Customers see all applications; each worker sees only their own application.
    if request.user.role == 'customer':
        applications = service_request.job_applications.select_related('worker').all()
        worker_application = None
    else:
        applications = service_request.job_applications.filter(worker=request.user)
        worker_application = applications.first()

    context = {
        'service_request': service_request,
        'applications': applications,
        'worker_application': worker_application,
    }
    return render(request, 'bookings/service_request_detail.html', context)


@login_required
@worker_required
def job_application_create(request, service_request_id):
    """Worker applies for a service request"""
    service_request = get_object_or_404(ServiceRequest, pk=service_request_id)

    if request.user.worker_status != 'APPROVED':
        messages.error(request, 'Your account must be approved by an admin before you can accept jobs.')
        return redirect('worker_dashboard')
    profile = getattr(request.user, 'worker_profile', None)
    if not profile:
        messages.error(request, 'Create your worker profile first.')
        return redirect('worker_profile_edit')
    service = service_request.service
    category_ids = set(profile.categories.values_list('id', flat=True))
    category_name = (service.category.name if service.category else '').lower()
    matches = (
        profile.service_id == service.id
        or service.category_id in category_ids
        or (profile.service_category and profile.service_category.lower() in category_name)
        or (profile.profession and profile.profession.lower() in category_name)
    )
    if not matches:
        messages.error(request, 'This request is not in your profession or service category.')
        return redirect('service_request_list')

    if service_request.status != 'OPEN':
        messages.info(request, 'This request is no longer accepting applications.')
        return redirect('service_request_detail', pk=service_request.pk)
    
    # Check if worker already applied
    existing_application = JobApplication.objects.filter(
        service_request=service_request,
        worker=request.user
    ).first()

    if existing_application:
        if existing_application.status == 'ACCEPTED':
            messages.info(request, 'Your application for this request has already been accepted. Please continue from My Jobs.')
            return redirect('my_jobs')
        if existing_application.status == 'PENDING':
            messages.info(request, 'You already submitted an application for this request. It is waiting for customer review.')
            return redirect('service_request_detail', pk=service_request.pk)
        if existing_application.status == 'REJECTED':
            messages.info(request, 'Your previous application for this request was rejected. Please apply only to open requests.')
            return redirect('service_request_detail', pk=service_request.pk)
        messages.info(request, 'You already have an application for this request.')
        return redirect('service_request_detail', pk=service_request.pk)
    
    if request.method == 'POST':
        form = JobApplicationForm(
            request.POST,
            service_request=service_request,
            worker=request.user,
        )
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
        form = JobApplicationForm(
            service_request=service_request,
            worker=request.user,
            initial={'can_start_date': service_request.preferred_date}
        )
    
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
                    scheduled_time_start=application.service_request.preferred_time_start,
                    scheduled_time_end=application.service_request.preferred_time_end,
                    location=application.service_request.location,
                    address=application.service_request.address,
                )
                application.status = 'ACCEPTED'
                application.save()
                
                # Update service request status
                application.service_request.status = 'ASSIGNED'
                application.service_request.save()

                Notification.create_notification(
                    user=application.worker,
                    title=f"Job Assigned - {job.title}",
                    message=f"The customer selected you for '{job.title}'. Please review the details and accept the job.",
                    notification_type='APPLICATION_ACCEPTED',
                    job=job,
                    related_user=request.user,
                )
                
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

    if request.user.role == 'admin':
        messages.warning(request, 'Admins cannot access the customer/worker job workflow.')
        return redirect('dashboard_home')

    # Permission check
    if request.user != job.customer and request.user != job.worker:
        messages.error(request, 'You do not have permission to view this job.')
        return redirect('service_request_list')

    payment_completed = Payment.objects.filter(
        job=job,
        payment_status='Verified',
    ).exists()
    unread_message_notifications = Notification.objects.filter(
        user=request.user,
        job=job,
        notification_type='JOB_MESSAGE',
        is_read=False,
    ).count()
    payment = Payment.objects.filter(job=job).first()
    price_agreed = BookingMessage.objects.filter(
        job=job,
        sender=request.user,
        message__startswith='I agree to the service price of',
    ).exists()
    context = {
        'job': job,
        'payment_completed': payment_completed,
        'payment': payment,
        'price_agreed': price_agreed,
        'unread_message_notifications': unread_message_notifications,
    }
    return render(request, 'bookings/job_detail.html', context)


@login_required
@worker_required
def job_complete(request, pk):
    """Worker marks a job as completed"""
    job = get_object_or_404(Job, pk=pk)
    
    if job.worker != request.user:
        messages.error(request, 'Only the assigned worker can mark this job as completed.')
        return redirect('job_detail', pk=job.pk)

    if job.status != 'IN_PROGRESS':
        messages.error(request, 'A job must be in progress before it can be completed.')
        return redirect('job_detail', pk=job.pk)
    
    if request.method == 'POST':
        form = JobCompletionForm(request.POST, instance=job)
        if form.is_valid():
            job = form.save(commit=False)
            job.status = 'COMPLETED'
            job.actual_end_time = django.utils.timezone.now()
            job.save()
            job.service_request.status = 'COMPLETED'
            job.service_request.save(update_fields=['status', 'updated_at'])
            
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
    """Show the worker lifecycle clearly: pending applications, accepted work, active jobs, and completed service."""
    pending_applications = JobApplication.objects.filter(
        worker=request.user,
        status='PENDING'
    ).select_related('service_request', 'service_request__customer').order_by('-created_at')

    accepted_applications = JobApplication.objects.filter(
        worker=request.user,
        status='ACCEPTED'
    ).select_related('service_request', 'service_request__customer').order_by('-created_at')

    unread_customer_message = Notification.objects.filter(
        job=OuterRef('pk'),
        user=request.user,
        related_user=OuterRef('customer'),
        notification_type='JOB_MESSAGE',
        is_read=False,
    )
    confirmed_jobs = Job.objects.filter(
        worker=request.user,
        status='CONFIRMED'
    ).annotate(has_unread_customer_message=Exists(unread_customer_message)).select_related('customer', 'service_request').order_by('-created_at')

    active_jobs = Job.objects.filter(
        worker=request.user,
        status='IN_PROGRESS'
    ).annotate(has_unread_customer_message=Exists(unread_customer_message)).select_related('customer', 'service_request').order_by('-created_at')

    completed_jobs = Job.objects.filter(
        worker=request.user,
        status='COMPLETED'
    ).select_related('customer', 'service_request').order_by('-created_at')

    context = {
        'pending_applications': pending_applications,
        'accepted_applications': accepted_applications,
        'confirmed_jobs': confirmed_jobs,
        'active_jobs': active_jobs,
        'completed_jobs': completed_jobs,
        'total_jobs': len(confirmed_jobs) + len(active_jobs),
        'total_completed': len(completed_jobs),
    }

    return render(request, 'bookings/worker_my_jobs.html', context)


@login_required
@worker_required
def job_accept(request, pk):
    """Worker accepts an assigned job and can begin the work."""
    job = get_object_or_404(Job, pk=pk)

    if job.worker != request.user:
        messages.error(request, 'You can only accept jobs assigned to you.')
        return redirect('worker_my_jobs')

    if request.user.worker_status != 'APPROVED':
        messages.error(request, 'Admin approval is required before accepting jobs.')
        return redirect('worker_dashboard')

    if job.status != 'CONFIRMED':
        messages.info(request, 'This job is not waiting for acceptance.')
        return redirect('job_detail', pk=job.pk)

    job.status = 'IN_PROGRESS'
    job.actual_start_time = django.utils.timezone.now()
    job.save(update_fields=['status', 'actual_start_time', 'updated_at'])
    job.service_request.status = 'IN_PROGRESS'
    job.service_request.save(update_fields=['status', 'updated_at'])

    Notification.create_notification(
        user=job.customer,
        title=f"Job Started - {job.title}",
        message=f"The worker has accepted and started the job '{job.title}'.",
        notification_type='JOB_STARTED',
        job=job,
        related_user=job.worker,
    )

    messages.success(request, 'You accepted the job and it is now in progress.')
    return redirect('job_detail', pk=job.pk)


@login_required
@worker_required
def worker_available_jobs(request):
    """
    Show all jobs and bookings assigned to this worker.
    Worker can see:
    1. Jobs where they are the assigned worker
    2. Bookings where customer selected them as preferred/assigned worker
    """
    if getattr(request.user, 'is_blocked', False):
        messages.error(request, 'Your worker account is blocked. Please contact support.')
        return redirect('home')
    
    # Get all jobs assigned to this worker
    unread_customer_message = Notification.objects.filter(
        job=OuterRef('pk'),
        user=request.user,
        related_user=OuterRef('customer'),
        notification_type='JOB_MESSAGE',
        is_read=False,
    )
    available_jobs = Job.objects.filter(
        worker=request.user
    ).select_related(
        'customer', 'service_request'
    ).annotate(has_unread_customer_message=Exists(unread_customer_message)).order_by('-created_at')
    
    # Get all bookings assigned to this worker (Pending/Assigned status)
    assigned_bookings = Booking.objects.filter(
        worker=request.user
    ).exclude(
        status='Cancelled'
    ).select_related(
        'customer', 'service'
    ).order_by('-created_at')
    
    context = {
        'jobs': available_jobs,
        'bookings': assigned_bookings,
    }
    return render(request, 'bookings/worker_available_jobs.html', context)


@login_required
def job_messages(request, pk):
    """
    View messages between worker and customer for a specific job.
    Both worker and customer can access this.
    """
    job = get_object_or_404(Job, pk=pk)

    if request.user.role == 'admin':
        messages.warning(request, 'Admins cannot access the customer/worker job communication flow.')
        return redirect('dashboard_home')

    # Permission check
    if request.user != job.customer and request.user != job.worker:
        messages.error(request, 'You do not have permission to view job messages.')
        return redirect('home')

    payment_completed = Payment.objects.filter(
        job=job,
        payment_status='Verified',
    ).exists()
    Notification.objects.filter(
        user=request.user,
        job=job,
        notification_type='JOB_MESSAGE',
        is_read=False,
    ).update(is_read=True)
    if payment_completed:
        messages.info(request, 'Messaging is closed because payment has been completed for this service.')
        return redirect('job_detail', pk=job.pk)

    if request.method == 'POST' and 'agree_price' in request.POST:
        if request.user != job.customer:
            messages.error(request, 'Only the customer can agree to the job price.')
            return redirect('job_messages', pk=job.pk)
        if job.status in ['COMPLETED', 'CANCELLED']:
            messages.error(request, 'The price cannot be agreed after this job is closed.')
            return redirect('job_messages', pk=job.pk)

        BookingMessage.objects.create(
            job=job,
            sender=request.user,
            message=f'I agree to the service price of ৳{job.final_price}.',
        )
        Notification.create_notification(
            user=job.worker,
            title=f'Price agreed for Job #{job.pk}',
            message=f'{request.user.username} agreed to the service price of ৳{job.final_price}.',
            notification_type='JOB_MESSAGE',
            job=job,
            related_user=request.user,
        )
        messages.success(request, 'You agreed to the current service price.')
        return redirect('job_messages', pk=job.pk)
    
    # Get all messages for this job
    job_messages = BookingMessage.objects.filter(job=job).order_by('created_at')
    price_agreed = job_messages.filter(
        sender=request.user,
        message__startswith='I agree to the service price of',
    ).exists()
    
    if request.method == 'POST':
        message_text = request.POST.get('message', '').strip()
        attachment = request.FILES.get('attachment')
        
        if message_text or attachment:
            # Create a new message associated with the job
            booking_message = BookingMessage.objects.create(
                job=job,
                sender=request.user,
                message=message_text,
                attachment=attachment,
            )
            
            # Create a notification for the other party
            recipient = job.customer if request.user == job.worker else job.worker
            Notification.create_notification(
                user=recipient,
                title=f"New message in job: {job.title}",
                message=(
                    f"{request.user.username}: {message_text[:50]}..."
                    if message_text else
                    f"{request.user.username} sent an attachment."
                ),
                notification_type='JOB_MESSAGE',
                job=job,
                related_user=request.user,
            )
            
            messages.success(request, 'Message sent!')
            return redirect('job_messages', pk=job.pk)
    
    context = {
        'job': job,
        'messages': job_messages,
        'payment_completed': payment_completed,
        'price_agreed': price_agreed,
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
