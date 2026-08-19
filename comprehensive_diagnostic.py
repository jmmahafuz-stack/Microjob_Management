#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive system diagnostic - plain text version
"""
import django
import os
import sys
import codecs

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mjms.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse, NoReverseMatch
from services.models import Service
from workers.models import WorkerProfile
from bookings.models import ServiceRequest, JobApplication, Job, Booking
from payments.models import Payment
from reviews.models import Review

User = get_user_model()
client = Client()

print("=" * 70)
print("COMPREHENSIVE SYSTEM DIAGNOSTIC")
print("=" * 70)

# Test data creation
print("\n[1] CREATING TEST DATA...")
print("-" * 70)

# Create services with required fields
service1, _ = Service.objects.get_or_create(
    name='Electrical Repair',
    defaults={
        'category': 'Electrical', 
        'description': 'Professional electrical repairs and installation',
        'price': 500.00,
        'duration': '1-2 hours',
        'image': 'service_images/default.jpg'
    }
)
service2, _ = Service.objects.get_or_create(
    name='Plumbing Service',
    defaults={
        'category': 'Plumbing', 
        'description': 'Professional plumbing repairs and installation',
        'price': 400.00,
        'duration': '1-2 hours',
        'image': 'service_images/default.jpg'
    }
)
print("OK: Services created: " + service1.name + ", " + service2.name)

# Create customer
customer, _ = User.objects.get_or_create(
    username='testcustomer',
    defaults={'email': 'customer@test.com', 'role': 'customer'}
)
if _:
    customer.set_password('testpass123')
    customer.save()
print("OK: Customer created: " + customer.username)

# Create worker
worker, _ = User.objects.get_or_create(
    username='testworker',
    defaults={'email': 'worker@test.com', 'role': 'worker'}
)
if _:
    worker.set_password('testpass123')
    worker.save()
print("OK: Worker created: " + worker.username)

# Create worker profile
worker_profile, _ = WorkerProfile.objects.get_or_create(
    user=worker,
    defaults={
        'service': service1,
        'service_category': 'Electrical',
        'skills': 'Wiring, Installation',
        'experience_years': 5,
        'hourly_rate': 500,
        'verification_status': 'approved',
        'bkash_number': '01700000000',
        'nagad_number': '01700000000'
    }
)
print("OK: Worker profile created")

# Create admin
admin, _ = User.objects.get_or_create(
    username='testadmin',
    defaults={'email': 'admin@test.com', 'role': 'admin', 'is_staff': True, 'is_superuser': True}
)
if _:
    admin.set_password('testpass123')
    admin.save()
print("OK: Admin created: " + admin.username)

# Test data for workflows
print("\n[2] TESTING CUSTOMER WORKFLOW...")
print("-" * 70)

endpoints = {
    'Home': ('/', 'GET'),
    'Browse Services': ('/services/', 'GET'),
    'Customer Register': ('/accounts/register/', 'GET'),
    'Customer Login': ('/accounts/login/', 'GET'),
    'Service Request List': ('/bookings/requests/', 'GET'),
    'My Bookings': ('/bookings/my-bookings/', 'GET'),
    'Create Service Request': ('/bookings/requests/create/', 'GET'),
    'Customer Profile': ('/accounts/profile/', 'GET'),
}

# Test unauthenticated access
for name, (url, method) in endpoints.items():
    try:
        if method == 'GET':
            response = client.get(url)
            if response.status_code in [200, 301, 302]:
                print("OK: " + name + ": " + str(response.status_code))
            else:
                print("FAIL: " + name + ": " + str(response.status_code))
    except Exception as e:
        print("ERROR: " + name + ": " + str(e)[:50])

# Test customer login and authenticated access
print("\n[3] TESTING CUSTOMER AUTHENTICATED ACCESS...")
print("-" * 70)

client.login(username='testcustomer', password='testpass123')
customer_protected_urls = [
    ('My Bookings', '/bookings/my-bookings/'),
    ('Service Requests', '/bookings/requests/'),
    ('Profile', '/accounts/profile/'),
    ('Create Request', '/bookings/requests/create/'),
]

for name, url in customer_protected_urls:
    response = client.get(url)
    if response.status_code == 200:
        print("OK: " + name + ": Accessible")
    else:
        print("FAIL: " + name + ": Status " + str(response.status_code))

client.logout()

print("\n[4] TESTING WORKER WORKFLOW...")
print("-" * 70)

client.login(username='testworker', password='testpass123')
worker_urls = [
    ('Worker Dashboard', '/workers/dashboard/'),
    ('Available Jobs', '/bookings/jobs/'),
    ('Service Requests', '/bookings/requests/'),
    ('Earnings Detail', '/workers/earnings-detail/'),
    ('Transaction History', '/workers/transaction-history/'),
    ('Payout Requests', '/workers/payout-requests/'),
    ('Payment Methods', '/workers/payment-methods/'),
    ('Profile Edit', '/workers/profile-edit/'),
]

for name, url in worker_urls:
    response = client.get(url)
    if response.status_code == 200:
        print("OK: " + name + ": Accessible")
    elif response.status_code in [301, 302]:
        print("REDIR: " + name + ": Redirect (" + str(response.status_code) + ")")
    else:
        print("FAIL: " + name + ": Status " + str(response.status_code))

client.logout()

print("\n[5] TESTING ADMIN WORKFLOW...")
print("-" * 70)

client.login(username='testadmin', password='testpass123')
admin_urls = [
    ('Admin Dashboard', '/admin/'),
    ('Dashboard Home', '/dashboard/'),
]

for name, url in admin_urls:
    response = client.get(url)
    if response.status_code == 200:
        print("OK: " + name + ": Accessible")
    elif response.status_code in [301, 302]:
        print("REDIR: " + name + ": Redirect")
    else:
        print("FAIL: " + name + ": Status " + str(response.status_code))

client.logout()

print("\n[6] TESTING PAYMENT SYSTEM...")
print("-" * 70)

try:
    payment = Payment.objects.first()
    if payment:
        print("OK: Payment model exists, sample payment: " + str(payment.id))
    else:
        print("OK: Payment model exists, no test data yet")
except Exception as e:
    print("FAIL: Payment model error: " + str(e)[:50])

print("\n[7] TESTING URL ROUTING...")
print("-" * 70)

critical_urls = [
    'home',
    'service_list',
    'login',
    'register',
    'profile',
    'logout',
    'worker_dashboard',
    'service_request_list',
    'my_bookings',
    'dashboard_home',
]

for url_name in critical_urls:
    try:
        url = reverse(url_name)
        print("OK: " + url_name + ": " + url)
    except NoReverseMatch:
        print("FAIL: " + url_name + ": NOT FOUND")

print("\n[8] MODEL INTEGRITY CHECK...")
print("-" * 70)

try:
    user_count = User.objects.count()
    service_count = Service.objects.count()
    worker_profile_count = WorkerProfile.objects.count()
    
    print("OK: Users: " + str(user_count))
    print("OK: Services: " + str(service_count))
    print("OK: Worker Profiles: " + str(worker_profile_count))
except Exception as e:
    print("FAIL: Database error: " + str(e))

print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
