#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check user details
"""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mjms.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()

for username in ['testcustomer', 'testworker', 'testadmin']:
    user = User.objects.filter(username=username).first()
    if user:
        print("User:", username)
        print("  is_active:", user.is_active)
        print("  role:", user.role)
        if username == 'testworker':
            print("  worker_status:", user.worker_status)
        print()

# Test actual login
print("Testing login with test client...")
client = Client()
result = client.login(username='testcustomer', password='testpass123')
print("testcustomer login result:", result)

# After login, check if we're authenticated
response = client.get('/')
print("After login, can access /:", response.status_code)
