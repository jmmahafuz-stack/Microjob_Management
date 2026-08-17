#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Investigate redirect destinations
"""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mjms.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()
client = Client()

print("Testing redirect destinations...\n")

# Login as customer
result = client.login(username='testcustomer', password='testpass123')
print("Customer login result:", result)

# Check redirect location for customer endpoints
response = client.get('/bookings/my-bookings/')
print("Customer /bookings/my-bookings/ redirects to:", response.get('Location', 'NO LOCATION HEADER'))
print("Status:", response.status_code)

client.logout()

# Login as worker
result = client.login(username='testworker', password='testpass123')
print("\nWorker login result:", result)

response = client.get('/workers/dashboard/')
print("Worker /workers/dashboard/ redirects to:", response.get('Location', 'NO LOCATION HEADER'))
print("Status:", response.status_code)

client.logout()

# Login as admin
result = client.login(username='testadmin', password='testpass123')
print("\nAdmin login result:", result)

response = client.get('/dashboard/')
print("Admin /dashboard/ redirects to:", response.get('Location', 'NO LOCATION HEADER'))
print("Status:", response.status_code)
