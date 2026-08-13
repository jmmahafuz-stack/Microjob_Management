from django.test import TestCase
from django.urls import reverse

from .forms import RegisterForm
from .models import CustomUser


class AuthenticationRoleTests(TestCase):
    def test_customer_registration_creates_customer_account(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'customer1',
                'email': 'customer1@example.com',
                'first_name': 'Customer',
                'last_name': 'One',
                'phone': '1234567890',
                'address': 'Test address',
                'password1': 'StrongPassword123',
                'password2': 'StrongPassword123',
            },
        )

        self.assertEqual(response.status_code, 302)
        user = CustomUser.objects.get(username='customer1')
        self.assertEqual(user.role, 'customer')
        self.assertFalse(user.is_verified_worker)

    def test_worker_self_registration_is_not_allowed(self):
        form = RegisterForm(
            data={
                'username': 'worker1',
                'email': 'worker1@example.com',
                'first_name': 'Worker',
                'last_name': 'One',
                'phone': '0987654321',
                'address': 'Worker address',
                'password1': 'StrongPassword123',
                'password2': 'StrongPassword123',
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.role, 'customer')
        self.assertFalse(user.is_verified_worker)

    def test_authenticated_admin_is_redirected_to_dashboard_from_login_page(self):
        admin_user = CustomUser.objects.create_user(
            username='adminuser',
            password='StrongPassword123',
            role='admin',
        )
        self.client.force_login(admin_user)

        response = self.client.get(reverse('login'))

        self.assertRedirects(response, reverse('dashboard_home'))

    def test_admin_role_grants_staff_access(self):
        admin_user = CustomUser.objects.create_user(
            username='adminstaff',
            password='StrongPassword123',
            role='admin',
        )

        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_unverified_worker_cannot_login(self):
        worker_user = CustomUser.objects.create_user(
            username='workeruser',
            password='StrongPassword123',
            role='worker',
            is_verified_worker=False,
        )

        response = self.client.post(
            reverse('login'),
            {'username': 'workeruser', 'password': 'StrongPassword123'},
            follow=True,
        )

        self.assertContains(response, 'pending verification')
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertTrue(CustomUser.objects.get(pk=worker_user.pk).is_authenticated)

    def test_verified_worker_is_redirected_to_worker_dashboard(self):
        worker_user = CustomUser.objects.create_user(
            username='workerverified',
            password='StrongPassword123',
            role='worker',
            is_verified_worker=True,
        )

        response = self.client.post(
            reverse('login'),
            {'username': 'workerverified', 'password': 'StrongPassword123'},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
        self.assertIn('_auth_user_id', self.client.session)
