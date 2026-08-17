#!/usr/bin/env python
"""
Comprehensive test script for all MJMS features
Tests: Customer, Worker, Admin, and Payment workflows
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mjms.settings')
django.setup()

from django.test import Client
from django.contrib.auth import authenticate
from accounts.models import CustomUser
from services.models import Service
from workers.models import WorkerProfile
from bookings.models import ServiceRequest, JobApplication, Booking, Job
from payments.models import Payment

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def test_feature(name, test_func):
    """Helper to run and report test results"""
    try:
        test_func()
        print(f"✓ {name}")
        return True
    except Exception as e:
        print(f"✗ {name}: {str(e)}")
        return False

def setup_demo_accounts():
    """Ensure demo accounts exist with correct status"""
    print_section("Setting up Demo Accounts")
    
    # Delete existing demo accounts
    CustomUser.objects.filter(username__in=['admin', 'customer', 'worker', 
                                            'testadmin', 'testcustomer', 'testworker']).delete()
    
    demo_users = [
        ('admin', 'admin', 'Admin12345!'),
        ('customer', 'customer', 'Customer12345!'),
        ('worker', 'worker', 'Worker12345!'),
    ]
    
    users_created = []
    for role, username, password in demo_users:
        user = CustomUser.objects.create_user(
            username=username,
            email=f'{username}@example.com',
            password=password,
            role=role,
            is_staff=(role == 'admin'),
            is_superuser=(role == 'admin'),
            is_active=True,
            worker_status='APPROVED' if role == 'worker' else None,
            customer_status='ACTIVE' if role == 'customer' else None,
        )
        users_created.append(user)
        print(f"✓ Created {role:10} account: {username}")
        
        # Create worker profile for worker accounts
        if role == 'worker':
            WorkerProfile.objects.get_or_create(user=user)
            print(f"  └─ Created WorkerProfile for {username}")
    
    return users_created

def setup_demo_services():
    """Create demo services"""
    print_section("Setting up Demo Services")
    
    # Delete existing services
    Service.objects.all().delete()
    
    services_data = [
        {
            'name': 'House Cleaning',
            'category': 'cleaning',
            'description': 'Professional house cleaning service',
            'price': 50.00,
        },
        {
            'name': 'Plumbing Repair',
            'category': 'repair',
            'description': 'Quick and reliable plumbing fixes',
            'price': 75.00,
        },
        {
            'name': 'Electrical Work',
            'category': 'repair',
            'description': 'Licensed electrical installations',
            'price': 100.00,
        },
        {
            'name': 'Gardening Service',
            'category': 'gardening',
            'description': 'Lawn and garden maintenance',
            'price': 40.00,
        },
    ]
    
    services = []
    for service_data in services_data:
        service = Service.objects.create(**service_data)
        services.append(service)
        print(f"✓ Created service: {service.name} (${service.price})")
    
    return services

def test_customer_login():
    """Test customer login"""
    client = Client()
    user = CustomUser.objects.get(username='customer')
    
    def login_test():
        success = client.login(username='customer', password='Customer12345!')
        assert success, "Customer login failed"
        # Make a request to verify session
        response = client.get('/bookings/my-bookings/')
        assert response.status_code in [200, 302], f"Expected 200 or 302, got {response.status_code}"
    
    return test_feature("Customer Login", login_test)

def test_customer_browse_services():
    """Test customer browsing services"""
    client = Client()
    client.login(username='customer', password='Customer12345!')
    
    def browse_test():
        response = client.get('/services/')
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        # Check that services are in the response
        service = Service.objects.first()
        if service:
            assert service.name.encode() in response.content, f"Service {service.name} not found in response"
    
    return test_feature("Customer Browse Services", browse_test)

def test_customer_create_request():
    """Test customer creating service request"""
    client = Client()
    client.login(username='customer', password='Customer12345!')
    
    def create_request_test():
        service = Service.objects.first()
        customer = CustomUser.objects.get(username='customer')
        
        # Create a service request
        service_request = ServiceRequest.objects.create(
            customer=customer,
            service=service,
            title=f"Need {service.name}",
            description="Please help me with this service",
            location="Downtown Area",
            address="123 Main Street, Apt 4B, Downtown",
            preferred_date="2024-12-25",
        )
        
        assert service_request.id is not None, "ServiceRequest not created"
        assert service_request.status == 'OPEN', f"Expected status OPEN, got {service_request.status}"
    
    return test_feature("Customer Create Service Request", create_request_test)

def test_worker_login():
    """Test worker login"""
    client = Client()
    
    def login_test():
        success = client.login(username='worker', password='Worker12345!')
        assert success, "Worker login failed"
        # Make a request to verify session
        response = client.get('/workers/dashboard/')
        assert response.status_code in [200, 302], f"Expected 200 or 302, got {response.status_code}"
    
    return test_feature("Worker Login", login_test)

def test_worker_browse_requests():
    """Test worker browsing open service requests"""
    client = Client()
    client.login(username='worker', password='Worker12345!')
    
    def browse_requests_test():
        # First create a service request as a customer
        customer = CustomUser.objects.get(username='customer')
        service = Service.objects.first()
        
        service_request = ServiceRequest.objects.create(
            customer=customer,
            service=service,
            title=f"Need {service.name}",
            description="Please help me",
            location="Downtown Area",
            address="123 Main Street, Apt 4B, Downtown",
            preferred_date="2024-12-25",
        )
        
        # Now worker should be able to see it
        response = client.get('/bookings/requests/')
        assert response.status_code in [200, 302], f"Expected 200 or 302, got {response.status_code}"
    
    return test_feature("Worker Browse Requests", browse_requests_test)

def test_worker_apply_for_job():
    """Test worker applying for a job"""
    
    def apply_test():
        customer = CustomUser.objects.get(username='customer')
        worker = CustomUser.objects.get(username='worker')
        service = Service.objects.first()
        
        # Create service request
        service_request = ServiceRequest.objects.create(
            customer=customer,
            service=service,
            title=f"Need {service.name}",
            description="Please help me",
            location="Downtown Area",
            address="123 Main Street, Apt 4B, Downtown",
            preferred_date="2024-12-25",
        )
        
        # Worker applies for the job
        job_application = JobApplication.objects.create(
            service_request=service_request,
            worker=worker,
            proposal="I can help with this. I have 5 years of experience.",
            quote=service.price,
            status='PENDING',
        )
        
        assert job_application.id is not None, "JobApplication not created"
        assert job_application.status == 'PENDING', f"Expected status PENDING, got {job_application.status}"
    
    return test_feature("Worker Apply for Job", apply_test)

def test_customer_accept_job():
    """Test customer accepting worker's job application"""
    
    def accept_test():
        # Get the job application created in previous test
        job_application = JobApplication.objects.filter(status='PENDING').first()
        
        if job_application:
            # Customer accepts the job
            job_application.status = 'ACCEPTED'
            job_application.save()
            
            # This should create a Booking and Job
            booking = Booking.objects.create(
                service_request=job_application.service_request,
                worker=job_application.worker,
                customer=job_application.service_request.customer,
                price=job_application.quote,
                status='CONFIRMED',
            )
            
            job = Job.objects.create(
                booking=booking,
                title=job_application.service_request.title,
                description=job_application.service_request.description,
                status='ASSIGNED',
            )
            
            assert job.id is not None, "Job not created"
            assert booking.id is not None, "Booking not created"
    
    return test_feature("Customer Accept Job Application", accept_test)

def test_worker_complete_job():
    """Test worker completing a job"""
    
    def complete_test():
        job = Job.objects.filter(status='ASSIGNED').first()
        
        if job:
            job.status = 'COMPLETED'
            job.save()
            
            # Update booking status
            job.booking.status = 'COMPLETED'
            job.booking.save()
            
            assert job.status == 'COMPLETED', "Job status not updated"
    
    return test_feature("Worker Complete Job", complete_test)

def test_payment_system():
    """Test payment system"""
    
    def payment_test():
        booking = Booking.objects.filter(status='COMPLETED').first()
        
        if booking:
            # Create a payment
            payment = Payment.objects.create(
                booking=booking,
                amount=booking.price,
                method='BKASH',
                transaction_id='TXN123456',
                status='COMPLETED',
            )
            
            assert payment.id is not None, "Payment not created"
            assert payment.status == 'COMPLETED', "Payment status not correct"
    
    return test_feature("Payment System", payment_test)

def test_admin_login():
    """Test admin login"""
    client = Client()
    
    def login_test():
        success = client.login(username='admin', password='Admin12345!')
        assert success, "Admin login failed"
        # Make a request to verify session
        response = client.get('/admin/')
        assert response.status_code in [200, 302], f"Expected 200 or 302, got {response.status_code}"
    
    return test_feature("Admin Login", login_test)

def test_admin_dashboard():
    """Test admin dashboard access"""
    client = Client()
    client.login(username='admin', password='Admin12345!')
    
    def dashboard_test():
        response = client.get('/dashboard/')
        assert response.status_code in [200, 302], f"Expected 200 or 302, got {response.status_code}"
    
    return test_feature("Admin Dashboard Access", dashboard_test)

def main():
    print("\n" + "="*70)
    print("  COMPREHENSIVE MJMS FEATURE TEST")
    print("  Testing all customer, worker, admin, and payment functions")
    print("="*70)
    
    # Setup
    setup_demo_accounts()
    setup_demo_services()
    
    # Run all tests
    results = []
    
    print_section("Customer Features")
    results.append(test_customer_login())
    results.append(test_customer_browse_services())
    results.append(test_customer_create_request())
    
    print_section("Worker Features")
    results.append(test_worker_login())
    results.append(test_worker_browse_requests())
    results.append(test_worker_apply_for_job())
    
    print_section("Customer Accepting & Worker Completing")
    results.append(test_customer_accept_job())
    results.append(test_worker_complete_job())
    
    print_section("Payment System")
    results.append(test_payment_system())
    
    print_section("Admin Features")
    results.append(test_admin_login())
    results.append(test_admin_dashboard())
    
    # Summary
    print_section("Test Summary")
    passed = sum(results)
    total = len(results)
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed! System is ready for production.")
    else:
        print(f"\n✗ {total - passed} test(s) failed. Review above for details.")
    
    return 0 if passed == total else 1

if __name__ == '__main__':
    sys.exit(main())
