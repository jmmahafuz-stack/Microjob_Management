from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser
from bookings.models import Job, JobApplication, ServiceRequest
from services.models import Service
from workers.models import WorkerProfile


class WorkerRegistrationTests(TestCase):
    def test_worker_registration_creates_pending_profile(self):
        response = self.client.post(
            reverse('register'),
            {
                'first_name': 'Test',
                'last_name': 'Worker',
                'username': 'newworker',
                'email': 'worker@example.com',
                'phone': '01700000000',
                'address': 'Dhaka',
                'role': 'worker',
                'password1': 'StrongPassword123',
                'password2': 'StrongPassword123',
            },
        )

        self.assertEqual(response.status_code, 302)
        user = CustomUser.objects.get(username='newworker')
        self.assertEqual(user.role, 'worker')
        profile = WorkerProfile.objects.get(user=user)
        self.assertEqual(profile.verification_status, 'Pending')
        self.assertEqual(profile.training_status, 'Pending')

    def test_worker_registration_can_link_a_service(self):
        service = Service.objects.create(
            name='Plumbing',
            category='Plumbing',
            description='Fast plumbing help',
            price='1200.00',
            image='service_images/default.jpg',
            duration='1 hour',
            location='Dhaka',
            is_available=True,
        )

        response = self.client.post(
            reverse('register'),
            {
                'first_name': 'Test',
                'last_name': 'Worker',
                'username': 'newworker2',
                'email': 'worker2@example.com',
                'phone': '01700000001',
                'address': 'Dhaka',
                'role': 'worker',
                'worker_service': service.pk,
                'password1': 'StrongPassword123',
                'password2': 'StrongPassword123',
            },
        )

        self.assertEqual(response.status_code, 302)
        user = CustomUser.objects.get(username='newworker2')
        profile = WorkerProfile.objects.get(user=user)
        self.assertEqual(profile.service, service)

    def test_worker_dashboard_creates_missing_profile(self):
        user = CustomUser.objects.create_user(
            username='profilelessworker',
            email='profilelessworker@example.com',
            password='StrongPassword123',
            role='worker',
            worker_status='APPROVED',
        )

        self.client.login(username='profilelessworker', password='StrongPassword123')
        response = self.client.get(reverse('worker_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(WorkerProfile.objects.filter(user=user).exists())

    def test_pending_worker_can_access_worker_dashboard(self):
        user = CustomUser.objects.create_user(
            username='pendingworker',
            email='pendingworker@example.com',
            password='StrongPassword123',
            role='worker',
            worker_status='PENDING',
        )

        self.client.login(username='pendingworker', password='StrongPassword123')
        response = self.client.get(reverse('worker_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')

    def test_worker_dashboard_shows_only_matching_services(self):
        service_a = Service.objects.create(
            name='Alpha Electric Service',
            category='Electrical',
            description='Electrical work',
            price='1200.00',
            image='service_images/default.jpg',
            duration='2 hours',
            location='Dhaka',
            is_available=True,
        )
        service_b = Service.objects.create(
            name='Beta Drain Service',
            category='Drainage',
            description='Drainage work',
            price='1100.00',
            image='service_images/default.jpg',
            duration='2 hours',
            location='Dhaka',
            is_available=True,
        )

        user = CustomUser.objects.create_user(
            username='specialistworker',
            email='specialistworker@example.com',
            password='StrongPassword123',
            role='worker',
            worker_status='APPROVED',
        )
        WorkerProfile.objects.create(
            user=user,
            service=service_a,
            service_category='Electrical',
            skills='Electrical repair',
            verification_status='Approved',
        )

        self.client.login(username='specialistworker', password='StrongPassword123')
        response = self.client.get(reverse('worker_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, service_a.name)
        self.assertNotContains(response, service_b.name)

    def test_worker_dashboard_does_not_repeat_my_jobs_sections(self):
        user = CustomUser.objects.create_user(
            username='dashboardcleanworker',
            email='dashboardcleanworker@example.com',
            password='StrongPassword123',
            role='worker',
            worker_status='APPROVED',
        )
        WorkerProfile.objects.create(
            user=user,
            verification_status='Approved',
            training_status='Approved',
        )

        self.client.login(username='dashboardcleanworker', password='StrongPassword123')
        response = self.client.get(reverse('worker_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Active Jobs')
        self.assertNotContains(response, 'Your Services')
        self.assertNotContains(response, 'Recent Reviews')

    def test_worker_can_accept_an_assigned_job_from_my_jobs(self):
        customer = CustomUser.objects.create_user(
            username='assignedcustomer',
            email='assignedcustomer@example.com',
            password='StrongPassword123',
            role='customer',
            customer_status='ACTIVE',
        )
        worker = CustomUser.objects.create_user(
            username='assignedworker',
            email='assignedworker@example.com',
            password='StrongPassword123',
            role='worker',
            worker_status='APPROVED',
        )
        WorkerProfile.objects.create(user=worker, verification_status='Approved', training_status='Completed')

        service = Service.objects.create(
            name='Assigned Job Service',
            category='Repair',
            description='Fixing service',
            price='1500.00',
            image='service_images/default.jpg',
            duration='2 hours',
            location='Dhaka',
            is_available=True,
        )

        request_obj = ServiceRequest.objects.create(
            customer=customer,
            service=service,
            title='Assigned Service Request',
            description='Need an urgent repair',
            location='Dhaka',
            address='Road 1',
            preferred_date=date.today() + timedelta(days=2),
            status='OPEN',
            budget_min=Decimal('1000.00'),
            budget_max=Decimal('2000.00'),
        )

        application = JobApplication.objects.create(
            service_request=request_obj,
            worker=worker,
            proposed_price=Decimal('1200.00'),
            estimated_duration=timedelta(hours=2),
            proposal_message='I can handle this task.',
            can_start_date=date.today() + timedelta(days=1),
        )

        application.status = 'ACCEPTED'
        application.save()

        job = Job.objects.create(
            service_request=request_obj,
            job_application=application,
            customer=customer,
            worker=worker,
            title=request_obj.title,
            description=request_obj.description,
            proposed_price=application.proposed_price,
            estimated_duration=timedelta(hours=2),
            scheduled_date=request_obj.preferred_date,
            location=request_obj.location,
            address=request_obj.address,
            status='CONFIRMED',
        )

        self.client.login(username='assignedworker', password='StrongPassword123')
        response = self.client.post(reverse('job_accept', kwargs={'pk': job.pk}), {})

        self.assertEqual(response.status_code, 302)
        job.refresh_from_db()
        self.assertEqual(job.status, 'IN_PROGRESS')
        self.assertContains(self.client.get(reverse('worker_my_jobs')), 'Assigned Service Request')
