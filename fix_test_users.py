#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix test user statuses
"""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mjms.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Update all test users to have proper status
testworker = User.objects.filter(username='testworker').first()
if testworker:
    testworker.worker_status = 'APPROVED'
    testworker.save()
    print("OK: Updated testworker status to APPROVED")

testcustomer = User.objects.filter(username='testcustomer').first()
if testcustomer:
    testcustomer.customer_status = 'ACTIVE'
    testcustomer.save()
    print("OK: Updated testcustomer status to ACTIVE")

testadmin = User.objects.filter(username='testadmin').first()
if testadmin:
    testadmin.is_staff = True
    testadmin.is_superuser = True
    testadmin.save()
    print("OK: Updated testadmin permissions")

# Verify status
testworker = User.objects.filter(username='testworker').first()
if testworker:
    print("\nTestworker details:")
    print("  role:", testworker.role)
    print("  worker_status:", testworker.worker_status)
    print("  is_authenticated would be:", testworker.is_active)
