#!/usr/bin/env python
"""Direct test of payment flow without Django test framework."""
import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mjms.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from accounts.models import CustomUser
from services.models import Service
from bookings.models import ServiceRequest, JobApplication, Job
from workers.models import WorkerProfile
from payments.models import Payment

print("=" * 80)
print("TESTING PAYMENT FLOW: Job Completion Before Payment")
print("=" * 80)

try:
    # Cleanup
    CustomUser.objects.filter(username__in=['testcust', 'testworker']).delete()
    
    # Setup
    customer = CustomUser.objects.create_user(
        username='testcust',
        email='testcust@example.com',
        password='Pass123!',
        role='customer',
        customer_status='ACTIVE'
    )
    worker = CustomUser.objects.create_user(
        username='testworker',
        email='testworker@example.com',
        password='Pass123!',
        role='worker',
        worker_status='APPROVED'
    )
    WorkerProfile.objects.create(
        user=worker,
        verification_status='Approved',
        training_status='Completed',
        bkash_number='01700000000'
    )
    
    service = Service.objects.create(
        name='Test Service',
        category='Repair',
        description='Test',
        price='1500.00',
        image='service_images/default.jpg',
        duration='2 hours',
        location='Dhaka',
        is_available=True
    )
    
    request_obj = ServiceRequest.objects.create(
        customer=customer,
        service=service,
        title='Test Request',
        description='Test',
        location='Dhaka',
        address='Test Rd',
        preferred_date=date.today() + timedelta(days=2),
        status='OPEN',
        budget_min=Decimal('1000.00'),
        budget_max=Decimal('2000.00')
    )
    
    application = JobApplication.objects.create(
        service_request=request_obj,
        worker=worker,
        proposed_price=Decimal('1200.00'),
        estimated_duration=timedelta(hours=2),
        proposal_message='I can do it',
        can_start_date=date.today() + timedelta(days=1)
    )
    application.status = 'ACCEPTED'
    application.save()
    
    job = Job.objects.create(
        service_request=request_obj,
        job_application=application,
        customer=customer,
        worker=worker,
        title='Test Job',
        description='Test',
        proposed_price=Decimal('1200.00'),
        estimated_duration=timedelta(hours=2),
        scheduled_date=request_obj.preferred_date,
        location='Dhaka',
        address='Test Rd',
        status='IN_PROGRESS'
    )
    
    # TEST 1: Customer tries to pay while job is IN_PROGRESS
    print("\n[TEST 1] Customer tries to pay before completion...")
    client = Client()
    client.force_login(customer)
    response = client.post(
        reverse('make_payment', kwargs={'job_id': job.pk}),
        {'payment_method': 'BKash', 'transaction_id': 'TX-001', 'confirm_payment': 'on'}
    )
    
    if response.status_code == 302:
        print(f"✓ Payment blocked (redirected to {response.url})")
        payment_exists = Payment.objects.filter(job=job).exists()
        if not payment_exists:
            print("✓ No payment record created (correct)")
        else:
            print("✗ Payment record was created (should not exist)")
    else:
        print(f"✗ Expected redirect, got {response.status_code}")
    
    # TEST 2: Worker completes job
    print("\n[TEST 2] Worker marks job as complete...")
    client.force_login(worker)
    response = client.post(
        reverse('job_complete', kwargs={'pk': job.pk}),
        {'actual_price': '1200.00', 'completion_notes': 'Done'}
    )
    print(f"  Job completion response: {response.status_code}")
    
    job.refresh_from_db()
    if job.status == 'COMPLETED':
        print("✓ Job status is COMPLETED")
    else:
        print(f"✗ Job status is {job.status}, expected COMPLETED")
    
    # TEST 3: Customer pays after completion
    print("\n[TEST 3] Customer pays after completion...")
    client.force_login(customer)
    response = client.post(
        reverse('make_payment', kwargs={'job_id': job.pk}),
        {'payment_method': 'BKash', 'transaction_id': 'TX-002', 'confirm_payment': 'on'}
    )
    print(f"  Payment response: {response.status_code}")
    
    payment = Payment.objects.filter(job=job).first()
    if payment:
        print(f"✓ Payment created: {payment.pk}")
        print(f"  - Status: {payment.payment_status}")
        print(f"  - Customer amount: {payment.customer_amount}")
        print(f"  - Worker amount: {payment.worker_amount}")
        print(f"  - Worker payout status: {payment.worker_payout_status}")
        
        worker.worker_profile.refresh_from_db()
        print(f"✓ Worker profile updated:")
        print(f"  - Available earnings: {worker.worker_profile.available_earnings}")
        print(f"  - Pending earnings: {worker.worker_profile.pending_earnings}")
        print(f"  - Total earnings: {worker.worker_profile.total_earnings}")
    else:
        print("✗ Payment was not created")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

except Exception as e:
    import traceback
    print(f"\n✗ ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)
