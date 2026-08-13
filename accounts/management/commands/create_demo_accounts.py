from django.core.management.base import BaseCommand
from accounts.models import CustomUser


class Command(BaseCommand):
    help = 'Create the known working demo admin, customer, and worker accounts'

    def handle(self, *args, **options):
        accounts = [
            ('admin', 'admin', 'Admin12345!'),
            ('customer', 'customer', 'Customer12345!'),
            ('worker', 'worker', 'Worker12345!'),
            ('admin', 'testadmin', 'admin123'),
            ('customer', 'testcustomer', 'password123'),
            ('worker', 'testworker', 'password123'),
        ]

        for role, username, password in accounts:
            user, created = CustomUser.objects.get_or_create(
                username=username,
                defaults={
                    'role': role,
                    'email': f'{username}@example.com',
                    'is_staff': role == 'admin',
                    'is_superuser': role == 'admin',
                },
            )
            user.set_password(password)
            user.role = role
            user.is_staff = role == 'admin'
            user.is_superuser = role == 'admin'
            user.email = user.email or f'{username}@example.com'
            if role == 'worker':
                user.worker_status = 'APPROVED'
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'{role}:{username}:{password}:{"created" if created else "exists"}'
                )
            )
