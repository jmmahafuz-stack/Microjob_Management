from django.core.management.base import BaseCommand
from services.models import Category


class Command(BaseCommand):
    help = 'Seed the database with sample service categories'

    def handle(self, *args, **options):
        categories = [
            {
                'name': 'Plumbing',
                'description': 'Plumbing services including repairs, installations, and maintenance',
                'icon': '🔧'
            },
            {
                'name': 'Electrical',
                'description': 'Electrical services including wiring, repairs, and installations',
                'icon': '⚡'
            },
            {
                'name': 'Carpentry',
                'description': 'Carpentry services including furniture, doors, and wooden installations',
                'icon': '🪵'
            },
            {
                'name': 'Painting',
                'description': 'Interior and exterior painting services',
                'icon': '🎨'
            },
            {
                'name': 'Cleaning',
                'description': 'House cleaning and janitorial services',
                'icon': '🧹'
            },
            {
                'name': 'Landscaping',
                'description': 'Garden and landscaping services',
                'icon': '🌿'
            },
            {
                'name': 'HVAC',
                'description': 'Heating, ventilation, and air conditioning services',
                'icon': '❄️'
            },
            {
                'name': 'Home Repair',
                'description': 'General home repair and maintenance services',
                'icon': '🏠'
            },
            {
                'name': 'Handyman',
                'description': 'General handyman services for various tasks',
                'icon': '🔨'
            },
            {
                'name': 'Tutoring',
                'description': 'Educational tutoring and coaching services',
                'icon': '📚'
            },
        ]

        created_count = 0
        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'icon': cat_data['icon'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created category: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'- Skipped existing category: {category.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Seed complete! Created {created_count} new categories.')
        )
