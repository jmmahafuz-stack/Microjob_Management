#!/usr/bin/env python
"""Create demo customer, worker, and admin accounts for local testing."""
import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mjms.settings")
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from accounts.models import CustomUser
from workers.models import WorkerProfile


def create_test_users():
    print("Creating demo users...\n")

    if not CustomUser.objects.filter(username='testcustomer').exists():
        customer = CustomUser.objects.create_user(
            username='testcustomer',
            email='customer@test.com',
            password='password123',
            first_name='John',
            last_name='Customer',
            role='customer',
            phone='01700000001',
            address='123 Main St, Dhaka',
            preferred_contact_method='Email',
            receive_notifications=True,
        )
        customer.customer_status = 'ACTIVE'
        customer.save()
        print('✓ Customer created: testcustomer / password123')
    else:
        print('✓ Customer already exists')

    if not CustomUser.objects.filter(username='testworker').exists():
        worker = CustomUser.objects.create_user(
            username='testworker',
            email='worker@test.com',
            password='password123',
            first_name='Ahmed',
            last_name='Worker',
            role='worker',
            phone='01800000002',
            address='456 Oak Ave, Dhaka',
            preferred_contact_method='Email',
            receive_notifications=True,
            worker_status='APPROVED',
        )
        worker.save()
        WorkerProfile.objects.get_or_create(
            user=worker,
            defaults={
                'service_category': 'Plumbing',
                'skills': 'Plumbing, Pipe repair, Installation',
                'experience': '5+ years',
                'service_area': 'Dhaka Metro',
                'hourly_rate': 500,
                'bio': 'Professional plumber with 5+ years experience',
                'is_verified': True,
                'bkash_number': '01700000002',
                'nagad_number': '01800000002',
            },
        )
        print('✓ Worker created: testworker / password123')
    else:
        print('✓ Worker already exists')

    if not CustomUser.objects.filter(username='admin').exists():
        admin = CustomUser.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            role='admin',
            phone='01900000003',
            address='789 Admin Rd, Dhaka',
            preferred_contact_method='Email',
        )
        admin.save()
        print('✓ Admin created: admin / admin123')
    else:
        print('✓ Admin already exists')

    print('\nDemo accounts ready:')
    print('Customer: testcustomer / password123')
    print('Worker:   testworker / password123')
    print('Admin:    admin / admin123')


if __name__ == '__main__':
    create_test_users()
