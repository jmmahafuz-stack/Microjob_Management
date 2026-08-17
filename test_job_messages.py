#!/usr/bin/env python
"""Test BookingMessage with job field"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mjms.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from accounts.models import CustomUser
from bookings.models import Job, ServiceRequest, JobApplication, BookingMessage
from services.models import Service
from workers.models import WorkerProfile

# Get or create test data
customer, _ = CustomUser.objects.get_or_create(
    username='test_customer_msg',
    defaults={
        'email': 'customer_msg@example.com',
        'role': 'customer',
        'first_name': 'Test',
        'last_name': 'Customer'
    }
)
customer.set_password('TestPass123')
customer.save()

service, _ = Service.objects.get_or_create(
    name='Cleaning',
    defaults={
        'category': 'Cleaning',
        'description': 'Professional cleaning service',
        'price': '1000.00',
        'duration': '2 hours',
        'location': 'Dhaka',
        'is_available': True
    }
)

worker_user, _ = CustomUser.objects.get_or_create(
    username='test_worker_msg',
    defaults={
        'email': 'worker_msg@example.com',
        'role': 'worker',
        'first_name': 'Test',
        'last_name': 'Worker',
        'worker_status': 'APPROVED'
    }
)
worker_user.set_password('TestPass123')
worker_user.save()

worker_profile, _ = WorkerProfile.objects.get_or_create(
    user=worker_user,
    defaults={
        'service': service,
        'bio': 'Professional cleaner',
        'verification_status': 'Approved'
    }
)

sr, _ = ServiceRequest.objects.get_or_create(
    title='House Cleaning Test',
    customer=customer,
    defaults={
        'service': service,
        'description': 'Clean my house',
        'location': 'Dhaka',
        'address': 'House #123, Dhaka',
        'preferred_date': timezone.now().date(),
        'budget_min': '900.00',
        'budget_max': '1100.00',
        'status': 'OPEN'
    }
)

app, _ = JobApplication.objects.get_or_create(
    service_request=sr,
    worker=worker_user,
    defaults={
        'proposed_price': '1000.00',
        'estimated_duration': timedelta(hours=2),
        'proposal_message': 'I am a professional cleaner with 5 years experience',
        'can_start_date': timezone.now().date(),
        'status': 'ACCEPTED'
    }
)

job, _ = Job.objects.get_or_create(
    service_request=sr,
    customer=customer,
    worker=worker_user,
    defaults={
        'job_application': app,
        'title': 'House Cleaning Test',
        'description': 'Professional house cleaning',
        'proposed_price': '1000.00',
        'estimated_duration': timedelta(hours=2),
        'location': 'Dhaka',
        'address': 'House #123, Dhaka',
        'scheduled_date': timezone.now().date(),
        'status': 'IN_PROGRESS'
    }
)

# Test message creation
msg, created = BookingMessage.objects.get_or_create(
    job=job,
    sender=customer,
    defaults={
        'message': 'I need the house cleaned today'
    }
)

if created:
    print("✓ Message created successfully")
else:
    print("✓ Message already exists")
print(f"  - Job: {job.title}")
print(f"  - Sender: {customer.username}")
print(f"  - Message: {msg.message}")

# Test retrieval
messages = BookingMessage.objects.filter(job=job)
print(f"✓ Retrieved {messages.count()} message(s) for job")

print("\n✓ BookingMessage job field works correctly!")
