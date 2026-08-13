from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser
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
