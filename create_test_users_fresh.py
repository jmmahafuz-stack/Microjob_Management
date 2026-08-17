#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Recreate test users with proper credentials
"""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mjms.settings')
django.setup()

from django.contrib.auth import get_user_model
from services.models import Service
from workers.models import WorkerProfile

User = get_user_model()

# Delete existing test users
User.objects.filter(username__in=['testcustomer', 'testworker', 'testadmin']).delete()
WorkerProfile.objects.filter(user__username='testworker').delete()
print("OK: Deleted existing test users")

# Create services
service, _ = Service.objects.get_or_create(
    name='Electrical Repair',
    defaults={
        'category': 'Electrical', 
        'description': 'Professional electrical repairs',
        'price': 500.00,
        'duration': '1-2 hours',
        'image': 'service_images/default.jpg'
    }
)
print("OK: Services ready")

# Create customer
customer = User.objects.create_user(
    username='testcustomer',
    email='customer@test.com',
    password='testpass123',  # Will be hashed
    role='customer',
    customer_status='ACTIVE',
    is_active=True
)
print("OK: Customer created")

# Create worker
worker = User.objects.create_user(
    username='testworker',
    email='worker@test.com',
    password='testpass123',
    role='worker',
    worker_status='APPROVED',
    is_active=True
)
print("OK: Worker created")

# Create worker profile
worker_profile = WorkerProfile.objects.create(
    user=worker,
    service=service,
    service_category='Electrical',
    skills='Wiring, Installation',
    experience_years=5,
    hourly_rate=500,
    verification_status='approved',
    bkash_number='01700000000',
    nagad_number='01700000000'
)
print("OK: Worker profile created")

# Create admin
admin = User.objects.create_user(
    username='testadmin',
    email='admin@test.com',
    password='testpass123',
    role='admin',
    is_staff=True,
    is_superuser=True,
    is_active=True
)
print("OK: Admin created")

# Test login
from django.test import Client
client = Client()

for username in ['testcustomer', 'testworker', 'testadmin']:
    result = client.login(username=username, password='testpass123')
    print("Login test - " + username + ": " + str(result))
    client.logout()

print("\nAll test users created successfully!")
