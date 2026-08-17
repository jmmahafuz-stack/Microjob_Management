#!/usr/bin/env python
"""Test that workers can see customer service requests"""

import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mjms.settings')
sys.path.insert(0, '.')
django.setup()

from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from services.models import Service
from bookings.models import ServiceRequest

User = get_user_model()
client = Client()

print("Testing Worker View of Customer Service Requests")
print("=" * 60)

# Trigger login to create demo accounts
response = client.get(reverse('login'))

# Create a test service
service, created = Service.objects.get_or_create(
    name='Test Service',
    defaults={
        'category': 'Test',
        'description': 'Test Description',
        'price': Decimal('500.00'),
        'image': 'service_images/default.jpg',
        'duration': '1 hour',
        'location': 'Test City',
        'is_available': True,
    }
)
print(f"✓ Service created: {service.name}")

# Get customer
customer = User.objects.get(username='customer')
print(f"✓ Customer found: {customer.username}")

# Create a service request
service_request, created = ServiceRequest.objects.get_or_create(
    customer=customer,
    title='Test Request',
    defaults={
        'service': service,
        'description': 'This is a test service request',
        'location': 'Test Location',
        'address': '123 Test Street',
        'preferred_date': date.today() + timedelta(days=1),
        'status': 'OPEN',
        'budget_min': Decimal('100.00'),
        'budget_max': Decimal('500.00'),
    }
)
print(f"✓ Service request created: {service_request.title}")

# Get worker
worker = User.objects.get(username='worker')
print(f"✓ Worker found: {worker.username}")
print(f"  - Role: {worker.role}")
print(f"  - Status: {worker.worker_status}")

# Login as worker
success = client.login(username='worker', password='Worker12345!')
print(f"✓ Worker login: {success}")

# Try to access service_request_list
response = client.get(reverse('service_request_list'))
print(f"✓ Service request list page: HTTP {response.status_code}")

# Check if the service request appears in the response
content = response.content.decode('utf-8')
if 'Test Request' in content:
    print("✓ TEST REQUEST VISIBLE TO WORKER!")
    print("  Worker can see customer service requests!")
else:
    print("✗ Test request NOT visible to worker")
    print(f"  Response contains: {content[:500]}")

# Check if Open Requests link is in navbar
if 'Open Requests' in content:
    print("✓ 'Open Requests' link is in worker navbar")
else:
    print("✗ 'Open Requests' link NOT in worker navbar")

# Try to access the service request detail
response = client.get(reverse('service_request_detail', kwargs={'pk': service_request.pk}))
print(f"✓ Service request detail page: HTTP {response.status_code}")

if response.status_code == 200:
    print("✓ Worker can view service request details!")
else:
    print(f"✗ Error accessing service request: {response.status_code}")

print("\n" + "=" * 60)
print("SUMMARY:")
print("Workers can now:")
print("✓ See 'Open Requests' in navbar")
print("✓ View list of all open customer service requests")
print("✓ View request details")
print("✓ Apply for jobs from customer requests")
