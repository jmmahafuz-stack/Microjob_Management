from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AdminDashboardTests(TestCase):
    def test_admin_is_redirected_from_workflow_management_pages(self):
        admin_user = User.objects.create_user(
            username='adminworkflow',
            email='adminworkflow@example.com',
            password='Admin12345!',
            role='admin'
        )
        admin_user.is_staff = True
        admin_user.save()

        self.client.login(username='adminworkflow', password='Admin12345!')

        response = self.client.get(reverse('booking_list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard_home'))

        response = self.client.get(reverse('service_request_list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard_home'))

    def test_admin_dashboard_shows_key_management_summary(self):
        admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='Admin12345!',
            role='admin'
        )
        admin_user.is_staff = True
        admin_user.save()

        self.client.login(username='adminuser', password='Admin12345!')
        response = self.client.get(reverse('dashboard_home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Workers')
        self.assertContains(response, 'Bookings')
        self.assertContains(response, 'Complaints')

    def test_admin_can_approve_worker_and_block_customer(self):
        admin_user = User.objects.create_user(
            username='adminmanager',
            email='adminmanager@example.com',
            password='Admin12345!',
            role='admin'
        )
        admin_user.is_staff = True
        admin_user.save()

        worker = User.objects.create_user(
            username='pendingworker',
            email='pendingworker@example.com',
            password='Worker12345!',
            role='worker',
            worker_status='PENDING',
        )

        customer = User.objects.create_user(
            username='customeruser',
            email='customeruser@example.com',
            password='Customer12345!',
            role='customer',
            customer_status='ACTIVE',
        )

        self.client.login(username='adminmanager', password='Admin12345!')

        response = self.client.post(reverse('admin_user_action', args=[worker.pk]), {'action': 'approve_worker'})
        self.assertEqual(response.status_code, 302)
        worker.refresh_from_db()
        self.assertEqual(worker.worker_status, 'APPROVED')

        response = self.client.post(reverse('admin_user_action', args=[customer.pk]), {'action': 'block_customer'})
        self.assertEqual(response.status_code, 302)
        customer.refresh_from_db()
        self.assertEqual(customer.customer_status, 'BLOCKED')
        self.assertTrue(customer.is_blocked)
