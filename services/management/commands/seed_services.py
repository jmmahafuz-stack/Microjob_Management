from django.core.management.base import BaseCommand
from services.models import Service


class Command(BaseCommand):
    help = 'Seed the database with sample services'

    def handle(self, *args, **options):
        services = [
            {
                'name': 'Emergency Plumbing',
                'category': 'Plumbing',
                'description': 'Fast emergency plumbing services for leaks, clogs, and installations',
                'price': '500.00',
                'duration': '1-2 hours',
                'location': 'Dhaka',
                'featured': True,
            },
            {
                'name': 'Electrical Repair',
                'category': 'Electrical',
                'description': 'Professional electrical repair and maintenance services',
                'price': '400.00',
                'duration': '1-3 hours',
                'location': 'Dhaka',
                'featured': True,
            },
            {
                'name': 'Carpentry Work',
                'category': 'Carpentry',
                'description': 'Custom carpentry, furniture, and wooden installations',
                'price': '600.00',
                'duration': '2-4 hours',
                'location': 'Dhaka',
                'featured': False,
            },
            {
                'name': 'AC Maintenance',
                'category': 'AC Repair',
                'description': 'Air conditioning repair, maintenance, and service',
                'price': '550.00',
                'duration': '1-2 hours',
                'location': 'Dhaka',
                'featured': True,
            },
            {
                'name': 'Home Painting',
                'category': 'Carpentry',
                'description': 'Interior and exterior home painting services',
                'price': '450.00',
                'duration': '4-8 hours',
                'location': 'Dhaka',
                'featured': False,
            },
            {
                'name': 'House Cleaning',
                'category': 'Plumbing',
                'description': 'Professional house cleaning and deep cleaning services',
                'price': '300.00',
                'duration': '2-3 hours',
                'location': 'Dhaka',
                'featured': False,
            },
        ]

        created_count = 0
        for service_data in services:
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults={
                    'category': service_data['category'],
                    'description': service_data['description'],
                    'price': service_data['price'],
                    'duration': service_data['duration'],
                    'location': service_data['location'],
                    'featured': service_data['featured'],
                    'is_available': True,
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created service: {service.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'- Skipped existing service: {service.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Seed complete! Created {created_count} new services.')
        )
