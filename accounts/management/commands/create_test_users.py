from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from workers.models import WorkerProfile


class Command(BaseCommand):
    help = 'Create test users for customer, worker, and admin roles'

    def handle(self, *args, **options):
        """Create test users"""
        
        # Create Customer User
        if not CustomUser.objects.filter(username='testcustomer').exists():
            customer = CustomUser.objects.create_user(
                username='testcustomer',
                email='customer@test.com',
                password='password123',
                first_name='John',
                last_name='Customer',
                role='customer',
                phone='01700000001',
                address='123 Main St, Dhaka',
                preferred_contact_method='Email',
                receive_notifications=True
            )
            customer.customer_status = 'ACTIVE'
            customer.save()
            self.stdout.write(self.style.SUCCESS(
                f'✓ Customer created: testcustomer / password123'
            ))
        else:
            self.stdout.write('✓ Customer already exists')

        # Create Worker User
        if not CustomUser.objects.filter(username='testworker').exists():
            worker = CustomUser.objects.create_user(
                username='testworker',
                email='worker@test.com',
                password='password123',
                first_name='Ahmed',
                last_name='Worker',
                role='worker',
                phone='01800000002',
                address='456 Oak Ave, Dhaka',
                preferred_contact_method='Email',
                receive_notifications=True,
                worker_status='APPROVED'  # Set to APPROVED for testing
            )
            worker.save()
            
            # Create worker profile
            WorkerProfile.objects.get_or_create(
                user=worker,
                defaults={
                    'service_category': 'Plumbing',
                    'skills': 'Plumbing, Pipe repair, Installation',
                    'experience': '5+ years',
                    'service_area': 'Dhaka Metro',
                    'hourly_rate': 500,
                    'bio': 'Professional plumber with 5+ years experience',
                    'is_verified': True,
                    'bkash_number': '01700000002',
                    'nagad_number': '01800000002',
                }
            )
            self.stdout.write(self.style.SUCCESS(
                f'✓ Worker created: testworker / password123'
            ))
        else:
            self.stdout.write('✓ Worker already exists')

        # Create Admin User
        if not CustomUser.objects.filter(username='admin').exists():
            admin = CustomUser.objects.create_superuser(
                username='admin',
                email='admin@test.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                role='admin',
                phone='01900000003',
                address='789 Admin Rd, Dhaka',
                preferred_contact_method='Email',
            )
            admin.save()
            self.stdout.write(self.style.SUCCESS(
                f'✓ Admin created: admin / admin123'
            ))
        else:
            self.stdout.write('✓ Admin already exists')

        self.stdout.write(self.style.SUCCESS(
            '\n✅ Test users created successfully!\n'
            'Login credentials:\n'
            '  Customer: testcustomer / password123\n'
            '  Worker:   testworker / password123\n'
            '  Admin:    admin / admin123'
        ))
