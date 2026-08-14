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

    def test_pending_worker_cannot_access_worker_dashboard_until_approved(self):
        user = CustomUser.objects.create_user(
            username='pendingworker',
            email='pendingworker@example.com',
            password='StrongPassword123',
            role='worker',
            worker_status='PENDING',
        )

        self.client.login(username='pendingworker', password='StrongPassword123')
        response = self.client.get(reverse('worker_dashboard'))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

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

    def test_worker_dashboard_shows_required_business_flow(self):
        user = CustomUser.objects.create_user(
            username='workerworkflow',
            email='workerworkflow@example.com',
            password='StrongPassword123',
            role='worker',
            worker_status='APPROVED',
        )
        WorkerProfile.objects.create(
            user=user,
            verification_status='Approved',
            training_status='Approved',
        )

        self.client.login(username='workerworkflow', password='StrongPassword123')
        response = self.client.get(reverse('worker_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'See Request → Accept → Start Work → Complete → Receive/Track Earnings')

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

    def test_customer_confirms_payment_and_adds_worker_earnings(self):
        customer = CustomUser.objects.create_user(
            username='payingcustomer',
            email='payingcustomer@example.com',
            password='StrongPassword123',
            role='customer',
            customer_status='ACTIVE',
        )
        worker = CustomUser.objects.create_user(
            username='earningworker',
            email='earningworker@example.com',
            password='StrongPassword123',
            role='worker',
            worker_status='APPROVED',
        )
        profile = WorkerProfile.objects.create(
            user=worker,
            verification_status='Approved',
            training_status='Completed',
            bkash_number='01700000000',
            nagad_number='01800000000',
        )

        service = Service.objects.create(
            name='Paid Repair Service',
            category='Repair',
            description='Repair with payment',
            price='1500.00',
            image='service_images/default.jpg',
            duration='2 hours',
            location='Dhaka',
            is_available=True,
        )

        request_obj = ServiceRequest.objects.create(
            customer=customer,
            service=service,
            title='Paid job request',
            description='Need repair',
            location='Dhaka',
            address='Road 9',
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
            proposal_message='I can do it.',
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
            status='COMPLETED',
        )

        self.client.login(username='payingcustomer', password='StrongPassword123')
        response = self.client.post(
            reverse('make_payment', kwargs={'job_id': job.pk}),
            {
                'payment_method': 'BKash',
                'transaction_id': 'TX-12345',
                'confirm_payment': 'on',
            },
        )

        self.assertEqual(response.status_code, 302)
        payment = job.payment
        self.assertEqual(payment.payment_status, 'Verified')
        self.assertEqual(payment.worker_payout_status, 'Available')
        profile.refresh_from_db()
        self.assertGreater(profile.available_earnings, 0)
        self.assertEqual(profile.pending_earnings, 0)

        self.assertEqual(profile.total_earnings, payment.worker_amount)

    def test_worker_dashboard_uses_real_payment_values_when_profile_is_stale(self):
        customer = CustomUser.objects.create_user(
            username='staleearningscustomer',
            email='staleearningscustomer@example.com',
            password='StrongPassword123',
            role='customer',
            customer_status='ACTIVE',
        )
        worker = CustomUser.objects.create_user(
            username='staleearningsworker',
            email='staleearningsworker@example.com',
            password='StrongPassword123',
            role='worker',
            worker_status='APPROVED',
        )
        profile = WorkerProfile.objects.create(
            user=worker,
            verification_status='Approved',
            training_status='Completed',
            pending_earnings=0,
            available_earnings=0,
            withdrawn_earnings=0,
            total_earnings=0,
        )

        service = Service.objects.create(
            name='Stale Earnings Service',
            category='Repair',
            description='Service with stale profile',
            price='1500.00',
            duration='2 hours',
            location='Dhaka',
            is_available=True,
        )

        request_obj = ServiceRequest.objects.create(
            customer=customer,
            service=service,
            title='Stale earnings job',
            description='Need fix',
            location='Dhaka',
            address='Road 10',
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
            proposal_message='I can do it.',
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
            status='COMPLETED',
        )

        Payment.objects.create(
            job=job,
            customer_amount=Decimal('1200.00'),
            platform_commission=Decimal('120.00'),
            worker_amount=Decimal('1080.00'),
            payment_method='BKash',
            payment_status='Verified',
            worker_payout_status='Available',
            transaction_id='TX-STALE-1',
        )

        refreshed = profile.sync_earnings_from_payments()

        self.assertEqual(refreshed['available'], Decimal('1080.00'))
        self.assertEqual(refreshed['total_earned'], Decimal('1080.00'))
        self.assertEqual(profile.available_earnings, Decimal('1080.00'))

    def test_worker_dashboard_shows_recent_verified_payment_with_service_name_and_amount(self):
        customer = CustomUser.objects.create_user(
            username='dashboardpaycustomer',
            email='dashboardpaycustomer@example.com',
            password='StrongPassword123',
            role='customer',
            customer_status='ACTIVE',
        )
        worker = CustomUser.objects.create_user(
            username='dashboardpayworker',
            email='dashboardpayworker@example.com',
            password='StrongPassword123',
            role='worker',
            worker_status='APPROVED',
        )
        WorkerProfile.objects.create(
            user=worker,
            verification_status='Approved',
            training_status='Completed',
            bkash_number='01700000002',
        )

        service = Service.objects.create(
            name='Dashboard Payment Service',
            category='Repair',
            description='Service with payment summary',
            price='1500.00',
            image='service_images/default.jpg',
            duration='2 hours',
            location='Dhaka',
            is_available=True,
        )

        request_obj = ServiceRequest.objects.create(
            customer=customer,
            service=service,
            title='Dashboard payment request',
            description='Need repair',
            location='Dhaka',
            address='Road 4',
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
            proposal_message='I can do it.',
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
            status='COMPLETED',
        )

        self.client.login(username='dashboardpaycustomer', password='StrongPassword123')
        self.client.post(
            reverse('make_payment', kwargs={'job_id': job.pk}),
            {
                'payment_method': 'BKash',
                'transaction_id': 'TX-DASHBOARD-1',
                'confirm_payment': 'on',
            },
        )

        self.client.login(username='dashboardpayworker', password='StrongPassword123')
        response = self.client.get(reverse('worker_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard Payment Service')
        self.assertContains(response, '৳')

    def test_customer_cannot_pay_before_worker_marks_job_complete(self):
        customer = CustomUser.objects.create_user(
            username='pendingpaycustomer',
            email='pendingpaycustomer@example.com',
            password='StrongPassword123',
            role='customer',
            customer_status='ACTIVE',
        )
        worker = CustomUser.objects.create_user(
            username='pendingpayworker',
            email='pendingpayworker@example.com',
            password='StrongPassword123',
            role='worker',
            worker_status='APPROVED',
        )
        WorkerProfile.objects.create(
            user=worker,
            verification_status='Approved',
            training_status='Completed',
            bkash_number='01700000001',
        )

        service = Service.objects.create(
            name='Pending Payment Service',
            category='Repair',
            description='Service pending payment',
            price='1500.00',
            image='service_images/default.jpg',
            duration='2 hours',
            location='Dhaka',
            is_available=True,
        )

        request_obj = ServiceRequest.objects.create(
            customer=customer,
            service=service,
            title='Pending payment request',
            description='Need service',
            location='Dhaka',
            address='Road 10',
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
            proposal_message='I can do it.',
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
            status='IN_PROGRESS',
        )

        self.client.login(username='pendingpaycustomer', password='StrongPassword123')
        response = self.client.post(
            reverse('make_payment', kwargs={'job_id': job.pk}),
            {
                'payment_method': 'BKash',
                'transaction_id': 'TX-999',
                'confirm_payment': 'on',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('job_detail', kwargs={'pk': job.pk}))
        self.assertFalse(hasattr(job, 'payment'))
