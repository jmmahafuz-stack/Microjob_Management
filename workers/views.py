from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import admin_required, worker_required
from bookings.models import Booking, Job
from payments.models import Payment
from reviews.models import Review
from .forms import WorkerProfileForm, WorkerVerificationForm
from .models import WorkerProfile
from services.models import Service


def _get_worker_earnings_data(user, period='monthly'):
    now = timezone.now()

    if period == 'daily':
        start_date = now.date() - timedelta(days=1)
        label = 'Daily earnings'
    elif period == 'yearly':
        start_date = now.date().replace(month=1, day=1)
        label = 'Yearly earnings'
    else:
        start_date = now.date().replace(day=1)
        label = 'Monthly earnings'

    payments = Payment.objects.filter(
        job__worker=user,
        payment_status='Verified'
    ).select_related('job', 'job__customer', 'job__service_request', 'job__service_request__service').order_by('-payment_date')

    if start_date:
        payments = payments.filter(payment_date__date__gte=start_date)

    job_entries = []
    total_earnings = Decimal('0.00')

    for payment in payments:
        job = payment.job
        if not job:
            continue

        amount = Decimal(str(payment.worker_amount or Decimal('0.00')))
        total_earnings += amount
        service_name = getattr(job.service_request.service, 'name', None) or job.title
        job_entries.append({
            'job': job,
            'date': payment.payment_date.date(),
            'customer': job.customer.get_full_name() or job.customer.username,
            'service_title': service_name,
            'amount': amount,
        })

    return {
        'label': label,
        'start_date': start_date,
        'jobs': job_entries,
        'total_earnings': total_earnings,
    }


@worker_required
def worker_dashboard(request):

    # Show message if worker is pending approval
    if request.user.worker_status == 'PENDING':
        from django.contrib import messages as django_messages
        django_messages.warning(
            request,
            "Your account is awaiting admin approval. You can browse the platform, but you won't appear in service listings until approved. "
            "Once approved, customers will be able to see your profile and request your services."
        )
    elif request.user.worker_status == 'REJECTED':
        from django.contrib import messages as django_messages
        django_messages.error(
            request,
            "Your worker account has been rejected. Please contact support for more information."
        )

    assigned_bookings = Booking.objects.filter(worker=request.user)
    pending_bookings = assigned_bookings.filter(status='Pending')
    in_progress_bookings = assigned_bookings.filter(status='In Progress')
    completed_bookings = assigned_bookings.filter(status='Completed')
    cancelled_bookings = assigned_bookings.filter(status='Cancelled')
    worker_profile, _ = WorkerProfile.objects.get_or_create(user=request.user)
    reviews = Review.objects.filter(worker=request.user)
    
    from payments.models import Payment
    from bookings.models import Job
    
    active_jobs = Job.objects.filter(worker=request.user).exclude(status='CANCELLED').order_by('-created_at')[:5]
    pending_earnings = worker_profile.pending_earnings
    available_earnings = worker_profile.available_earnings
    withdrawn_earnings = worker_profile.withdrawn_earnings
    total_earnings = (pending_earnings + available_earnings + withdrawn_earnings)

    relevant_services = Service.objects.filter(is_available=True)
    if worker_profile.service:
        relevant_services = relevant_services.filter(pk=worker_profile.service.pk)
    elif worker_profile.service_category:
        relevant_services = relevant_services.filter(category__name__icontains=worker_profile.service_category)
    elif worker_profile.categories.exists():
        relevant_services = relevant_services.filter(category__in=worker_profile.categories.all())
    else:
        relevant_services = relevant_services.none()

    report_daily = _get_worker_earnings_data(request.user, 'daily')
    report_monthly = _get_worker_earnings_data(request.user, 'monthly')
    report_yearly = _get_worker_earnings_data(request.user, 'yearly')

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
            'pending_earnings': pending_earnings,
            'available_earnings': available_earnings,
            'withdrawn_earnings': withdrawn_earnings,
            'available_services': relevant_services,
            'active_jobs': active_jobs,
            'report_daily': report_daily,
            'report_monthly': report_monthly,
            'report_yearly': report_yearly,
        }
    )


@worker_required
def worker_earnings_report(request):
    period = request.GET.get('period', 'monthly')
    download = request.GET.get('download', '').lower()
    data = _get_worker_earnings_data(request.user, period)

    if download in {'csv', 'excel', 'pdf'}:
        rows = [
            [entry['date'].strftime('%Y-%m-%d'), entry['customer'], entry['service_title'], str(entry['amount'])]
            for entry in data['jobs']
        ]
        filename = f'worker_earnings_{period}_{timezone.now().strftime("%Y%m%d")}.{download}'

        if download == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            import csv
            writer = csv.writer(response)
            writer.writerow(['Date', 'Customer', 'Service', 'Amount'])
            writer.writerows(rows)
            return response

        if download == 'excel':
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            import openpyxl
            from io import BytesIO
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            sheet.title = 'Worker Earnings'
            sheet.append(['Date', 'Customer', 'Service', 'Amount'])
            for row in rows:
                sheet.append(row)
            buffer = BytesIO()
            workbook.save(buffer)
            response.write(buffer.getvalue())
            return response

        if download == 'pdf':
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
            from io import BytesIO

            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            elements = [
                Paragraph(f'Worker Earnings Report - {data["label"]}', styles['Title']),
                Paragraph(f'Total Earnings: ৳{data["total_earnings"]}', styles['Normal']),
                Spacer(1, 12),
            ]
            table_data = [['Date', 'Customer', 'Service', 'Amount']] + rows
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ]))
            elements.append(table)
            doc.build(elements)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            response.write(buffer.getvalue())
            return response

    return render(
        request,
        'workers/worker_earnings_report.html',
        {
            'period': period,
            'report_label': data['label'],
            'total_earnings': data['total_earnings'],
            'job_entries': data['jobs'],
            'start_date': data['start_date'],
        }
    )


def worker_profile_detail(request, pk):
    worker_profile = get_object_or_404(WorkerProfile, pk=pk)
    reviews = Review.objects.filter(worker=worker_profile.user).select_related('customer')
    categories = worker_profile.categories.all()

    return render(
        request,
        'workers/worker_profile_detail.html',
        {
            'worker_profile': worker_profile,
            'categories': categories,
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
