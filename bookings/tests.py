from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser
from bookings.models import Booking, ServiceRequest
from services.models import Service
from workers.models import WorkerProfile


class BookingCreationTests(TestCase):
    def setUp(self):
        self.customer = CustomUser.objects.create_user(
            username='customer1',
            email='customer@example.com',
            password='testpass123',
            role='customer',
        )

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
            username='workerinvoice',
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
            username='admininvoice',
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
            username='worker1',
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
        self.assertContains(detail_response, worker.username)

        booking_response = self.client.get(reverse('create_booking'), {'service': service.pk})
        self.assertEqual(booking_response.status_code, 200)
        self.assertContains(booking_response, 'Recommended workers for this service')
        self.assertContains(booking_response, worker.username)

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
            username='worker2',
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
        self.assertContains(response, worker.username)

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
            username='worker3',
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
            username='workerrequestfilter',
            email='workerrequestfilter@example.com',
            password='testpass123',
            role='worker',
            worker_status='APPROVED',
        )
        WorkerProfile.objects.create(user=worker, verification_status='Approved')

        demo_customer = CustomUser.objects.create_user(
            username='testcust',
            email='testcust@example.com',
            password='testpass123',
            role='customer',
        )
        real_customer = CustomUser.objects.create_user(
            username='real_customer',
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
            username='visiblecustomerrequestworker',
            email='visiblecustomerrequestworker@example.com',
            password='testpass123',
            role='worker',
            worker_status='APPROVED',
        )
        WorkerProfile.objects.create(user=worker, verification_status='Approved')

        customer = CustomUser.objects.create_user(
            username='customer',
            email='customer@example.com',
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
            username='worker4',
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
