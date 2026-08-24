from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AdminDashboardTests(TestCase):
    def test_admin_is_redirected_from_workflow_management_pages(self):
        admin_user = User.objects.create_user(
            email='adminworkflow@example.com',
            password='Admin12345!',
            role='admin'
        )
        admin_user.is_staff = True
        admin_user.save()

        self.client.login(email=admin_user.email, password='Admin12345!')

        response = self.client.get(reverse('booking_list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard_home'))

        response = self.client.get(reverse('service_request_list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard_home'))

    def test_admin_dashboard_shows_key_management_summary(self):
        admin_user = User.objects.create_user(
            email='admin@example.com',
            password='Admin12345!',
            role='admin'
        )
        admin_user.is_staff = True
        admin_user.save()

        self.client.login(email=admin_user.email, password='Admin12345!')
        response = self.client.get(reverse('dashboard_home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Workers')
        self.assertContains(response, 'Bookings')
        self.assertContains(response, 'Complaints')

    def test_customer_dashboard_shows_required_business_flow(self):
        customer = User.objects.create_user(
            email='customerworkflow@example.com',
            password='Customer12345!',
            role='customer',
            customer_status='ACTIVE',
        )

        self.client.login(email=customer.email, password='Customer12345!')
        response = self.client.get(reverse('dashboard_home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Select Service → Select Worker → Request Work → Wait → Pay')

    def test_admin_dashboard_shows_required_business_flow(self):
        admin_user = User.objects.create_user(
            email='adminworkflowsteps@example.com',
            password='Admin12345!',
            role='admin'
        )
        admin_user.is_staff = True
        admin_user.save()

        self.client.login(email=admin_user.email, password='Admin12345!')
        response = self.client.get(reverse('dashboard_home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Manage Users → Manage Services → Monitor Jobs → Manage Commission → Monitor Payments → Generate Reports')

    def test_admin_can_approve_worker_and_block_customer(self):
        admin_user = User.objects.create_user(
            email='adminmanager@example.com',
            password='Admin12345!',
            role='admin'
        )
        admin_user.is_staff = True
        admin_user.save()

        worker = User.objects.create_user(
            email='pendingworker@example.com',
            password='Worker12345!',
            role='worker',
            worker_status='PENDING',
        )

        customer = User.objects.create_user(
            email='customeruser@example.com',
            password='Customer12345!',
            role='customer',
            customer_status='ACTIVE',
        )

        self.client.login(email=admin_user.email, password='Admin12345!')

        response = self.client.post(reverse('admin_user_action', args=[worker.pk]), {'action': 'approve_worker'})
        self.assertEqual(response.status_code, 302)
        worker.refresh_from_db()
        self.assertEqual(worker.worker_status, 'APPROVED')

        response = self.client.post(reverse('admin_user_action', args=[customer.pk]), {'action': 'block_customer'})
        self.assertEqual(response.status_code, 302)
        customer.refresh_from_db()
        self.assertEqual(customer.customer_status, 'BLOCKED')
        self.assertTrue(customer.is_blocked)

    def test_admin_dashboard_shows_trade_worker_summary(self):
        admin_user = User.objects.create_user(
            email='admindashboardtrade@example.com',
            password='Admin12345!',
            role='admin'
        )
        admin_user.is_staff = True
        admin_user.save()

        from services.models import Category
        from workers.models import WorkerProfile

        categories = {
            'Electrical': Category.objects.create(name='Electrical', description='Electrical services', icon='⚡'),
            'Plumbing': Category.objects.create(name='Plumbing', description='Plumbing services', icon='🔧'),
            'Cleaning': Category.objects.create(name='Cleaning', description='Cleaning services', icon='🧼'),
            'Carpentry': Category.objects.create(name='Carpentry', description='Carpentry services', icon='🪚'),
        }

        for idx, (email, category_name) in enumerate([
            ('electrician_demo', 'Electrical'),
            ('plumber_demo', 'Plumbing'),
            ('plumber_demo_2', 'Plumbing'),
            ('cleaner_demo', 'Cleaning'),
        ], start=1):
            worker = User.objects.create_user(
                email=f'{email}@example.com',
                password='Worker12345!',
                role='worker',
                worker_status='APPROVED',
                is_blocked=False,
            )
            profile = WorkerProfile.objects.create(
                user=worker,
                profession=category_name,
                verification_status='Approved',
                training_status='Completed',
                service_area='Dhaka',
                experience_years=3,
            )
            profile.categories.add(categories[category_name])

        self.client.login(email=admin_user.email, password='Admin12345!')
        response = self.client.get(reverse('dashboard_home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Electrical')
        self.assertContains(response, 'Plumbing')
        self.assertContains(response, 'Cleaning')
        self.assertContains(response, 'Carpentry')
        self.assertContains(response, '1')
        self.assertContains(response, '2')
