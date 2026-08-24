from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.forms import RegisterForm
from accounts.models import CustomUser
from bookings.models import Job, JobApplication, ServiceRequest
from .admin import WorkerProfileAdminForm
from .forms import WorkerProfileForm
from services.models import Service
from workers.models import WorkerProfile
from services.models import Category


class WorkerRegistrationTests(TestCase):
    def test_worker_profile_form_does_not_allow_category_changes(self):
        category = Category.objects.create(name='Electrical', is_active=True)
        user = CustomUser.objects.create_user(
            email='fixedcategory@example.com',
            password='StrongPassword123',
            role='worker',
        )
        profile = WorkerProfile.objects.create(user=user, profession='Electrician')
        profile.categories.add(category)

        form = WorkerProfileForm(instance=profile)

        self.assertNotIn('categories', form.fields)
        self.assertNotIn('service_category', form.fields)

    def test_admin_requires_exactly_one_worker_category(self):
        first = Category.objects.create(name='Electrical', is_active=True)
        second = Category.objects.create(name='Plumbing', is_active=True)
        user = CustomUser.objects.create_user(
            email='admincategory@example.com',
            password='StrongPassword123',
            role='worker',
        )
        profile = WorkerProfile.objects.create(user=user, profession='Technician')

        form = WorkerProfileAdminForm(instance=profile, data={
            'user': user.pk,
            'profession': 'Technician',
            'categories': [first.pk, second.pk],
            'experience_years': 0,
            'response_time': 'Within 24 hours',
            'default_preferred_contact': 'Email',
            'payout_status': 'Pending',
            'training_status': 'Pending',
            'verification_status': 'Pending',
            'payout_method': 'Bank Account',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('categories', form.errors)

    def test_public_worker_profile_shows_profession_and_categories(self):
        category = Category.objects.create(name='Electrical', is_active=True)
        user = CustomUser.objects.create_user(
            email='visibleworker@example.com',
            password='StrongPassword123',
            role='worker',
        )
        profile = WorkerProfile.objects.create(
            user=user,
            profession='Electrician',
            verification_status='Approved',
        )
        profile.categories.add(category)

        response = self.client.get(reverse('worker_profile_detail', args=[profile.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Electrician')
        self.assertContains(response, 'Electrical')

    def test_worker_registration_creates_pending_profile(self):
        category = Category.objects.create(name='Cleaning', is_active=True)
        response = self.client.post(
            reverse('register'),
            {
                'first_name': 'Test',
                'last_name': 'Worker',
                'email': 'worker@example.com',
                'phone': '01700000000',
                'address': 'Dhaka',
                'role': 'worker',
                'worker_categories': category.pk,
                'password1': 'StrongPassword123',
                'password2': 'StrongPassword123',
            },
        )

        self.assertEqual(response.status_code, 302)
        user = CustomUser.objects.get(email='worker@example.com')
        self.assertEqual(user.role, 'worker')
        profile = WorkerProfile.objects.get(user=user)
        self.assertEqual(profile.verification_status, 'Pending')
        self.assertEqual(profile.training_status, 'Pending')
        self.assertEqual(list(profile.categories.values_list('name', flat=True)), ['Cleaning'])

    def test_worker_registration_rejects_unknown_category(self):
        form = RegisterForm(data={
            'email': 'unknowncategory@example.com',
            'role': 'worker',
            'worker_categories': 999999,
            'password1': 'StrongPassword123',
            'password2': 'StrongPassword123',
        })

        self.assertFalse(form.is_valid())
        self.assertIn('worker_categories', form.errors)

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
        user = CustomUser.objects.get(email='worker2@example.com')
        profile = WorkerProfile.objects.get(user=user)
        self.assertEqual(profile.service, service)

    def test_worker_dashboard_creates_missing_profile(self):
        user = CustomUser.objects.create_user(
            email='profilelessworker@example.com',
            password='StrongPassword123',
            role='worker',
            worker_status='APPROVED',
        )

        self.client.login(email=user.email, password='StrongPassword123')
        response = self.client.get(reverse('worker_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(WorkerProfile.objects.filter(user=user).exists())

    def test_pending_worker_can_access_worker_dashboard_before_approval(self):
        user = CustomUser.objects.create_user(
            email='pendingworker@example.com',
            password='StrongPassword123',
            role='worker',
            worker_status='PENDING',
        )

        self.client.login(email=user.email, password='StrongPassword123')
        response = self.client.get(reverse('worker_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Worker Dashboard')

    def test_pending_worker_cannot_apply_for_a_service_request(self):
        category = Category.objects.create(name='Cleaning', is_active=True)
        service = Service.objects.create(
            name='Pending Worker Service',
            category=category,
            description='Cleaning service',
            price='500.00',
            image='service_images/default.jpg',
            duration='1 hour',
            location='Dhaka',
            is_available=True,
        )
        customer = CustomUser.objects.create_user(
            email='pendingapplicationcustomer@example.com',
            password='StrongPassword123',
            role='customer',
        )
        worker = CustomUser.objects.create_user(
            email='pendingapplicationworker@example.com',
            password='StrongPassword123',
            role='worker',
            worker_status='PENDING',
        )
        WorkerProfile.objects.create(user=worker, profession='Cleaning')
        request_obj = ServiceRequest.objects.create(
            customer=customer,
            service=service,
            title='Cleaning request',
            description='Please clean the house',
            location='Dhaka',
            address='Road 1',
            preferred_date=date.today() + timedelta(days=1),
            status='OPEN',
            budget_min=Decimal('400.00'),
            budget_max=Decimal('600.00'),
        )

        self.client.login(email=worker.email, password='StrongPassword123')
        response = self.client.get(reverse(
            'job_application_create',
            kwargs={'service_request_id': request_obj.pk},
        ))

        self.assertRedirects(response, reverse('home'))
        self.assertFalse(JobApplication.objects.filter(worker=worker).exists())

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

        self.client.login(email=user.email, password='StrongPassword123')
        response = self.client.get(reverse('worker_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, service_a.name)
        self.assertNotContains(response, service_b.name)

    def test_worker_dashboard_does_not_repeat_my_jobs_sections(self):
        user = CustomUser.objects.create_user(
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

        self.client.login(email=user.email, password='StrongPassword123')
        response = self.client.get(reverse('worker_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Active Jobs')
        self.assertNotContains(response, 'Your Services')
        self.assertNotContains(response, 'Recent Reviews')

    def test_worker_dashboard_shows_required_business_flow(self):
        user = CustomUser.objects.create_user(
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

        self.client.login(email=user.email, password='StrongPassword123')
        response = self.client.get(reverse('worker_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'See Request → Accept → Start Work → Complete → Receive/Track Earnings')

    def test_worker_can_accept_an_assigned_job_from_my_jobs(self):
        customer = CustomUser.objects.create_user(
            email='assignedcustomer@example.com',
            password='StrongPassword123',
            role='customer',
            customer_status='ACTIVE',
        )
        worker = CustomUser.objects.create_user(
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

        self.client.login(email=user.email, password='StrongPassword123')
        response = self.client.post(reverse('job_accept', kwargs={'pk': job.pk}), {})

        self.assertEqual(response.status_code, 302)
        job.refresh_from_db()
        self.assertEqual(job.status, 'IN_PROGRESS')
        self.assertContains(self.client.get(reverse('worker_my_jobs')), 'Assigned Service Request')

    def test_customer_confirms_payment_and_adds_worker_earnings(self):
        customer = CustomUser.objects.create_user(
            email='payingcustomer@example.com',
            password='StrongPassword123',
            role='customer',
            customer_status='ACTIVE',
        )
        worker = CustomUser.objects.create_user(
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

        self.client.login(email=worker.email, password='StrongPassword123')
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
            email='staleearningscustomer@example.com',
            password='StrongPassword123',
            role='customer',
            customer_status='ACTIVE',
        )
        worker = CustomUser.objects.create_user(
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
            email='dashboardpaycustomer@example.com',
            password='StrongPassword123',
            role='customer',
            customer_status='ACTIVE',
        )
        worker = CustomUser.objects.create_user(
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

        self.client.login(email=customer.email, password='StrongPassword123')
        self.client.post(
            reverse('make_payment', kwargs={'job_id': job.pk}),
            {
                'payment_method': 'BKash',
                'transaction_id': 'TX-DASHBOARD-1',
                'confirm_payment': 'on',
            },
        )

        self.client.login(email=worker.email, password='StrongPassword123')
        response = self.client.get(reverse('worker_dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard Payment Service')
        self.assertContains(response, '৳')

    def test_worker_earnings_report_can_download_pdf(self):
        worker = CustomUser.objects.create_user(
            email='reportworker@example.com',
            password='StrongPassword123',
            role='worker',
            worker_status='APPROVED',
        )
        WorkerProfile.objects.create(
            user=worker,
            verification_status='Approved',
            training_status='Completed',
        )

        self.client.login(email=worker.email, password='StrongPassword123')
        response = self.client.get(reverse('worker_earnings_report') + '?period=monthly&download=pdf')

        self.assertEqual(response.status_code, 200)
        self.assertIn('application/pdf', response['Content-Type'])

    def test_customer_cannot_pay_before_worker_marks_job_complete(self):
        customer = CustomUser.objects.create_user(
            email='pendingpaycustomer@example.com',
            password='StrongPassword123',
            role='customer',
            customer_status='ACTIVE',
        )
        worker = CustomUser.objects.create_user(
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

        self.client.login(email=customer.email, password='StrongPassword123')
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
