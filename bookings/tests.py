from datetime import timedelta

from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser
from bookings.models import Booking, Job, JobApplication, ServiceRequest
from services.models import Category, Service
from workers.models import WorkerProfile


class BookingCreationTests(TestCase):
    def setUp(self):
        self.customer = CustomUser.objects.create_user(
            email='customer@example.com',
            password='testpass123',
            role='customer',
        )

    def test_my_bookings_exposes_status_counts(self):
        category = Category.objects.create(name='Electrical')
        service = Service.objects.create(
            name='Booking Count Service',
            category=category,
            description='Service for booking count tests.',
            price='120.00',
            image='service_images/test.png',
            duration='2 hours',
            location='Dhaka',
            is_available=True,
        )
        worker = CustomUser.objects.create_user(
            email='countworker@example.com',
            password='testpass123',
            role='worker',
            worker_status='APPROVED',
        )

        Booking.objects.create(
            customer=self.customer,
            service=service,
            worker=worker,
            booking_date='2026-08-11',
            booking_time='11:00:00',
            address='Pending count address',
            problem_description='Pending job',
            status='Pending',
        )
        Booking.objects.create(
            customer=self.customer,
            service=service,
            worker=worker,
            booking_date='2026-08-12',
            booking_time='10:00:00',
            address='Active count address',
            problem_description='Active job',
            status='In Progress',
        )
        Booking.objects.create(
            customer=self.customer,
            service=service,
            worker=worker,
            booking_date='2026-08-13',
            booking_time='13:00:00',
            address='Completed count address',
            problem_description='Completed job',
            status='Completed',
        )
        Booking.objects.create(
            customer=self.customer,
            service=service,
            worker=worker,
            booking_date='2026-08-14',
            booking_time='15:00:00',
            address='Cancelled count address',
            problem_description='Cancelled job',
            status='Cancelled',
        )
        ServiceRequest.objects.create(
            customer=self.customer,
            service=service,
            title='Open request',
            description='Need help',
            location='Dhaka',
            address='Open address',
            preferred_date='2026-08-15',
            status='OPEN',
        )

        self.client.force_login(self.customer)
        response = self.client.get(reverse('my_bookings'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['pending_count'], 2)
        self.assertEqual(response.context['active_count'], 1)
        self.assertEqual(response.context['completed_count'], 1)
        self.assertEqual(response.context['cancelled_count'], 1)

    def test_worker_accept_button_uses_post_form_on_job_detail(self):
        category = Category.objects.create(name='Job Flow Electrical')
        service = Service.objects.create(
            name='Job Flow Service',
            category=category,
            description='Service for job status flow tests.',
            price='250.00',
            image='service_images/test.png',
            duration='3 hours',
            location='Dhaka',
            is_available=True,
        )
        worker = CustomUser.objects.create_user(
            email='flowworker@example.com',
            password='testpass123',
            role='worker',
            worker_status='APPROVED',
        )
        profile = WorkerProfile.objects.create(
            user=worker,
            profession='Electrician',
            experience_years=3,
        )
        profile.categories.add(category)
        service_request = ServiceRequest.objects.create(
            customer=self.customer,
            service=service,
            title='Fix the wiring',
            description='Need a worker for wiring work.',
            location='Dhaka',
            address='Repair lane 2',
            preferred_date='2026-08-15',
            status='ASSIGNED',
        )
        application = JobApplication.objects.create(
            service_request=service_request,
            worker=worker,
            proposed_price='250.00',
            estimated_duration=timedelta(hours=3),
            proposal_message='I can do this job.',
            can_start_date='2026-08-15',
            agreed_to_schedule=True,
            status='ACCEPTED',
        )
        job = Job.objects.create(
            service_request=service_request,
            job_application=application,
            customer=self.customer,
            worker=worker,
            title=service_request.title,
            description=service_request.description,
            proposed_price='250.00',
            estimated_duration=timedelta(hours=3),
            scheduled_date=service_request.preferred_date,
            location=service_request.location,
            address=service_request.address,
            status='CONFIRMED',
        )

        self.client.force_login(worker)
        response = self.client.get(reverse('job_detail', args=[job.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="accept_job"')
        self.assertContains(response, 'method="post"')

    def test_existing_accepted_booking_status_is_visible_in_hubs(self):
        category = Category.objects.create(name='Existing Booking Flow')
        service = Service.objects.create(
            name='Existing Booking Service',
            category=category,
            description='Service for existing booking visibility tests.',
            price='420.00',
            image='service_images/test.png',
            duration='5 hours',
            location='Dhaka',
            is_available=True,
        )
        worker = CustomUser.objects.create_user(
            email='legacyworker@example.com',
            password='testpass123',
            role='worker',
            worker_status='APPROVED',
        )

        booking = Booking.objects.create(
            customer=self.customer,
            service=service,
            worker=worker,
            booking_date='2026-08-18',
            booking_time='09:00:00',
            address='Legacy assigned address',
            problem_description='Existing booking should stay visible.',
            status='Assigned',
        )

        self.client.force_login(worker)
        worker_response = self.client.get(reverse('worker_my_jobs'))
        self.assertEqual(worker_response.status_code, 200)
        self.assertIn(booking, worker_response.context['accepted_bookings'])

        self.client.force_login(self.customer)
        customer_response = self.client.get(reverse('my_bookings'))
        self.assertEqual(customer_response.status_code, 200)
        self.assertIn(booking, customer_response.context['bookings'])
        self.assertContains(customer_response, 'Price can be negotiated')

        self.client.force_login(worker)
        worker_response = self.client.get(reverse('worker_my_jobs'))
        self.assertContains(worker_response, 'Price can be negotiated')

    def test_worker_my_jobs_shows_next_process_buttons_for_direct_booking(self):
        category = Category.objects.create(name='Worker Booking Actions')
        service = Service.objects.create(
            name='Booking Action Service',
            category=category,
            description='Service for direct booking action tests.',
            price='500.00',
            image='service_images/test.png',
            duration='6 hours',
            location='Dhaka',
            is_available=True,
        )
        worker = CustomUser.objects.create_user(
            email='actionworker@example.com',
            password='testpass123',
            role='worker',
            worker_status='APPROVED',
        )

        Booking.objects.create(
            customer=self.customer,
            service=service,
            worker=worker,
            booking_date='2026-08-19',
            booking_time='10:00:00',
            address='Action booking address',
            problem_description='Direct booking should show next-step actions.',
            status='In Progress',
        )

        self.client.force_login(worker)
        response = self.client.get(reverse('worker_my_jobs'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mark completed')
        self.assertContains(response, 'Message')

    def test_my_jobs_and_bookings_show_price_negotiation_status(self):
        category = Category.objects.create(name='Negotiation Flow')
        service = Service.objects.create(
            name='Negotiation Service',
            category=category,
            description='Service for price negotiation tests.',
            price='700.00',
            image='service_images/test.png',
            duration='8 hours',
            location='Dhaka',
            is_available=True,
        )
        worker = CustomUser.objects.create_user(
            email='negotiationworker@example.com',
            password='testpass123',
            role='worker',
            worker_status='APPROVED',
        )
        profile = WorkerProfile.objects.create(
            user=worker,
            profession='Electrician',
            experience_years=4,
        )
        profile.categories.add(category)
        service_request = ServiceRequest.objects.create(
            customer=self.customer,
            service=service,
            title='Install a panel',
            description='Need a worker for electrical panel install.',
            location='Dhaka',
            address='Negotiation lane',
            preferred_date='2026-08-20',
            status='ASSIGNED',
        )
        application = JobApplication.objects.create(
            service_request=service_request,
            worker=worker,
            proposed_price='700.00',
            estimated_duration=timedelta(hours=8),
            proposal_message='Available for this work.',
            can_start_date='2026-08-20',
            agreed_to_schedule=True,
            status='ACCEPTED',
        )
        job = Job.objects.create(
            service_request=service_request,
            job_application=application,
            customer=self.customer,
            worker=worker,
            title=service_request.title,
            description=service_request.description,
            proposed_price='700.00',
            estimated_duration=timedelta(hours=8),
            scheduled_date=service_request.preferred_date,
            location=service_request.location,
            address=service_request.address,
            status='CONFIRMED',
            price_agreed=False,
        )

        self.client.force_login(self.customer)
        customer_response = self.client.get(reverse('my_bookings'))
        self.assertContains(customer_response, 'Price can be negotiated')

        self.client.force_login(worker)
        worker_response = self.client.get(reverse('worker_my_jobs'))
        self.assertContains(worker_response, 'Price can be negotiated')

    def test_direct_booking_price_negotiation_cycle(self):
        category = Category.objects.create(name='Direct Negotiation Flow')
        service = Service.objects.create(
            name='Direct Booking Negotiation Service',
            category=category,
            description='Service for direct booking negotiation tests.',
            price='600.00',
            image='service_images/test.png',
            duration='6 hours',
            location='Dhaka',
            is_available=True,
        )
        worker = CustomUser.objects.create_user(
            email='directnegotiationworker@example.com',
            password='testpass123',
            role='worker',
            worker_status='APPROVED',
        )

        booking = Booking.objects.create(
            customer=self.customer,
            service=service,
            worker=worker,
            booking_date='2026-08-21',
            booking_time='12:00:00',
            address='Direct negotiation address',
            problem_description='Need direct negotiation workflow.',
            status='Accepted',
            proposed_price='600.00',
            actual_price='600.00',
            price_agreed=False,
        )

        self.client.force_login(worker)
        worker_response = self.client.post(
            reverse('booking_detail', args=[booking.pk]),
            {'worker_update_price': '1', 'actual_price': '680.00'},
        )
        booking.refresh_from_db()
        self.assertEqual(worker_response.status_code, 302)
        self.assertEqual(str(booking.actual_price), '680.00')

        self.client.force_login(self.customer)
        customer_response = self.client.post(
            reverse('booking_detail', args=[booking.pk]),
            {'customer_agree_price': '1'},
        )
        booking.refresh_from_db()
        self.assertEqual(customer_response.status_code, 302)
        self.assertTrue(booking.price_agreed)
        self.assertEqual(str(booking.actual_price), '680.00')

    def test_cancel_job_closes_service_request_status(self):
        category = Category.objects.create(name='Cancellation Flow')
        service = Service.objects.create(
            name='Cancellation Service',
            category=category,
            description='Service for cancellation status tests.',
            price='300.00',
            image='service_images/test.png',
            duration='4 hours',
            location='Dhaka',
            is_available=True,
        )
        worker = CustomUser.objects.create_user(
            email='cancelworker@example.com',
            password='testpass123',
            role='worker',
            worker_status='APPROVED',
        )
        profile = WorkerProfile.objects.create(
            user=worker,
            profession='Electrician',
            experience_years=5,
        )
        profile.categories.add(category)
        service_request = ServiceRequest.objects.create(
            customer=self.customer,
            service=service,
            title='Install lights',
            description='Need electrician work.',
            location='Dhaka',
            address='Sample street',
            preferred_date='2026-08-20',
            status='ASSIGNED',
        )
        application = JobApplication.objects.create(
            service_request=service_request,
            worker=worker,
            proposed_price='300.00',
            estimated_duration=timedelta(hours=4),
            proposal_message='I can do this job.',
            can_start_date='2026-08-20',
            agreed_to_schedule=True,
            status='ACCEPTED',
        )
        job = Job.objects.create(
            service_request=service_request,
            job_application=application,
            customer=self.customer,
            worker=worker,
            title=service_request.title,
            description=service_request.description,
            proposed_price='300.00',
            estimated_duration=timedelta(hours=4),
            scheduled_date=service_request.preferred_date,
            location=service_request.location,
            address=service_request.address,
            status='CONFIRMED',
        )

        self.client.force_login(self.customer)
        response = self.client.post(
            reverse('cancel_job', args=[job.pk]),
            {'cancel_reason': 'Customer changed plans.'},
        )

        job.refresh_from_db()
        service_request.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(job.status, 'CANCELLED')
        self.assertEqual(service_request.status, 'CANCELLED')

    def test_admin_cannot_access_customer_invoice(self):
        service = Service.objects.create(
            name='Invoice Service',
            category='Electrical',
            description='A service with invoice access testing.',
            price='150.00',
            image='service_images/test.png',
            duration='2 hours',
            location='Dhaka',
            is_available=True,
        )
        worker = CustomUser.objects.create_user(
            email='workerinvoice@example.com',
            password='testpass123',
            role='worker',
            worker_status='APPROVED',
        )
        booking = Booking.objects.create(
            customer=self.customer,
            service=service,
            worker=worker,
            booking_date='2026-08-11',
            booking_time='11:00:00',
            address='Invoice test address',
            problem_description='Need help',
            status='Completed',
        )
        admin = CustomUser.objects.create_user(
            email='admininvoice@example.com',
            password='testpass123',
            role='admin',
        )

        self.client.force_login(admin)
        response = self.client.get(reverse('invoice', args=[booking.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard_home'))

    def test_preselected_service_can_be_used_to_create_booking(self):
        service = Service.objects.create(
            name='Test Service',
            category='Electrical',
            description='A test service.',
            price='100.00',
            image='service_images/test.png',
            duration='1 hour',
            location='Dhaka',
            is_available=False,
        )

        self.client.force_login(self.customer)

        response = self.client.post(
            reverse('create_booking'),
            {
                'service': service.pk,
                'booking_date': '2026-08-10',
                'booking_time': '10:00:00',
                'address': 'Test address',
                'problem_description': 'Need help with the service.',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Booking.objects.filter(service=service, customer=self.customer).exists())

    def test_customer_can_select_related_worker_for_booking(self):
        category = Category.objects.create(name='Selected Worker Electrical')
        service = Service.objects.create(
            name='Selected Worker Service',
            category=category,
            description='A service with worker selection.',
            price='100.00',
            image='service_images/test.png',
            duration='1 hour',
            location='Dhaka',
            is_available=True,
        )
        worker = CustomUser.objects.create_user(
            email='selected@example.com',
            password='testpass123',
            role='worker',
            worker_status='APPROVED',
        )
        profile = WorkerProfile.objects.create(
            user=worker,
            profession='Electrician',
            experience_years=3,
        )
        profile.categories.add(category)

        self.client.force_login(self.customer)
        response = self.client.post(
            reverse('create_booking'),
            {
                'service': service.pk,
                'worker': worker.pk,
                'booking_date': '2026-08-10',
                'booking_time': '10:00:00',
                'address': 'Selected worker address',
                'problem_description': 'Please assign this worker.',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Booking.objects.filter(service=service, worker=worker).exists())

    def test_service_and_booking_pages_show_related_worker_profiles(self):
        service = Service.objects.create(
            name='Electrical Service',
            category='Electrical',
            description='A test service.',
            price='100.00',
            image='service_images/test.png',
            duration='1 hour',
            location='Dhaka',
            is_available=True,
        )
        worker = CustomUser.objects.create_user(
            email='worker@example.com',
            password='testpass123',
            role='worker',
            is_verified_worker=True,
        )
        WorkerProfile.objects.create(
            user=worker,
            service=service,
            service_category='Electrical',
            skills='Electrical repairs',
            experience_years=5,
            verification_status='Approved',
        )

        self.client.force_login(self.customer)

        detail_response = self.client.get(reverse('service_detail', args=[service.pk]))
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, 'Recommended workers for this service')
        self.assertContains(detail_response, worker.email)

        booking_response = self.client.get(reverse('create_booking'), {'service': service.pk})
        self.assertEqual(booking_response.status_code, 200)
        self.assertContains(booking_response, 'Recommended workers for this service')
        self.assertContains(booking_response, worker.email)

    def test_service_pages_show_workers_matched_by_category(self):
        service = Service.objects.create(
            name='Plumbing Service',
            category='Plumbing',
            description='A test service.',
            price='120.00',
            image='service_images/test.png',
            duration='2 hours',
            location='Dhaka',
            is_available=True,
        )
        worker = CustomUser.objects.create_user(
            email='worker2@example.com',
            password='testpass123',
            role='worker',
            is_verified_worker=True,
        )
        WorkerProfile.objects.create(
            user=worker,
            service_category='Plumbing',
            skills='Plumbing fixes',
            experience_years=4,
            verification_status='Approved',
        )

        self.client.force_login(self.customer)

        response = self.client.get(reverse('service_detail', args=[service.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, worker.email)

    def test_booking_page_uses_compact_worker_card_markup(self):
        service = Service.objects.create(
            name='Cleaning Service',
            category='Cleaning',
            description='A cleaning service.',
            price='80.00',
            image='service_images/test.png',
            duration='30 mins',
            location='Dhaka',
            is_available=True,
        )
        worker = CustomUser.objects.create_user(
            email='worker3@example.com',
            password='testpass123',
            role='worker',
            is_verified_worker=True,
        )
        WorkerProfile.objects.create(
            user=worker,
            service=service,
            service_category='Cleaning',
            skills='Cleaning maintenance',
            experience_years=3,
            verification_status='Approved',
        )

        self.client.force_login(self.customer)

        response = self.client.get(reverse('create_booking'), {'service': service.pk})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'worker-card')
        self.assertContains(response, 'worker-card__image')

    def test_worker_service_request_list_hides_demo_and_test_requests(self):
        worker = CustomUser.objects.create_user(
            email='workerrequestfilter@example.com',
            password='testpass123',
            role='worker',
            worker_status='APPROVED',
        )
        WorkerProfile.objects.create(user=worker, verification_status='Approved')

        demo_customer = CustomUser.objects.create_user(
            email='testcust@example.com',
            password='testpass123',
            role='customer',
        )
        real_customer = CustomUser.objects.create_user(
            email='realcustomer@example.com',
            password='testpass123',
            role='customer',
        )

        service = Service.objects.create(
            name='Cleaning Service',
            category='Cleaning',
            description='Cleaning test service.',
            price='100.00',
            image='service_images/test.png',
            duration='2 hours',
            location='Dhaka',
            is_available=True,
        )

        ServiceRequest.objects.create(
            customer=demo_customer,
            service=service,
            title='Test Request',
            description='Demo request to hide',
            location='Dhaka',
            address='Dhaka',
            preferred_date='2026-08-20',
            budget_min='1000.00',
            budget_max='2000.00',
            status='OPEN',
        )
        real_request = ServiceRequest.objects.create(
            customer=real_customer,
            service=service,
            title='Real Home Repair Request',
            description='This should be shown to workers',
            location='Dhaka',
            address='Dhaka',
            preferred_date='2026-08-21',
            budget_min='800.00',
            budget_max='1200.00',
            status='OPEN',
        )

        self.client.force_login(worker)
        response = self.client.get(reverse('service_request_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Real Home Repair Request')
        self.assertNotContains(response, 'Test Request')
        self.assertContains(response, reverse('service_request_detail', args=[real_request.pk]))

    def test_worker_can_see_customer_requests_created_by_default_customer(self):
        worker = CustomUser.objects.create_user(
            email='visiblecustomerrequestworker@example.com',
            password='testpass123',
            role='worker',
            worker_status='APPROVED',
        )
        WorkerProfile.objects.create(user=worker, verification_status='Approved')

        customer = CustomUser.objects.create_user(
            email='visiblecustomerrequest@example.com',
            password='testpass123',
            role='customer',
        )
        service = Service.objects.create(
            name='Electrical Fix',
            category='Electrical',
            description='Electrical repair.',
            price='1500.00',
            image='service_images/test.png',
            duration='3 hours',
            location='Dhaka',
            is_available=True,
        )
        request_obj = ServiceRequest.objects.create(
            customer=customer,
            service=service,
            title='Customer Request That Must Be Visible',
            description='This request should show to workers.',
            location='Dhaka',
            address='Dhaka',
            preferred_date='2026-08-25',
            budget_min='1200.00',
            budget_max='1800.00',
            status='OPEN',
        )

        self.client.force_login(worker)
        response = self.client.get(reverse('service_request_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Customer Request That Must Be Visible')
        self.assertContains(response, reverse('service_request_detail', args=[request_obj.pk]))

    def test_service_list_adds_example_services_when_database_is_empty(self):
        Service.objects.all().delete()
        self.client.force_login(self.customer)

        response = self.client.get(reverse('service_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Service.objects.exists())
        self.assertContains(response, 'Plumbing')
        self.assertContains(response, 'Electrical')

    def test_service_list_page_uses_compact_worker_card_markup(self):
        service = Service.objects.create(
            name='Laundry Service',
            category='Laundry',
            description='A laundry service.',
            price='70.00',
            image='service_images/test.png',
            duration='45 mins',
            location='Dhaka',
            is_available=True,
        )
        worker = CustomUser.objects.create_user(
            email='worker4@example.com',
            password='testpass123',
            role='worker',
            is_verified_worker=True,
        )
        WorkerProfile.objects.create(
            user=worker,
            service=service,
            service_category='Laundry',
            skills='Laundry care',
            experience_years=2,
            verification_status='Approved',
        )

        self.client.force_login(self.customer)

        response = self.client.get(reverse('service_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'worker-card')
        self.assertContains(response, 'worker-card__image')
