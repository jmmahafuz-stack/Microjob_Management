from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AdminDashboardTests(TestCase):
    def test_admin_dashboard_shows_key_management_summary(self):
        User = get_user_model()
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
