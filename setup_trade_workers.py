import os
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mjms.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from services.models import Category, Service
from workers.models import WorkerProfile
from bookings.models import ServiceRequest

User = get_user_model()

trade_configs = [
    {
        'username': 'electrician_worker',
        'email': 'electrician@example.com',
        'password': 'Worker12345!',
        'profession': 'Electrician',
        'category_name': 'Electrical',
        'service_name': 'Electrical Repair',
        'skills': 'Wiring, Lighting, Panel Repair',
        'experience_years': 6,
        'service_area': 'Dhaka',
        'hourly_rate': '550.00',
    },
    {
        'username': 'plumber_worker',
        'email': 'plumber@example.com',
        'password': 'Worker12345!',
        'profession': 'Plumber',
        'category_name': 'Plumbing',
        'service_name': 'Pipe Fix',
        'skills': 'Pipe Fitting, Leakage Repair',
        'experience_years': 5,
        'service_area': 'Dhaka',
        'hourly_rate': '500.00',
    },
    {
        'username': 'cleaner_worker',
        'email': 'cleaner@example.com',
        'password': 'Worker12345!',
        'profession': 'House Cleaner',
        'category_name': 'Cleaning',
        'service_name': 'House Cleaning',
        'skills': 'Deep Cleaning, Kitchen Cleaning',
        'experience_years': 4,
        'service_area': 'Chattogram',
        'hourly_rate': '350.00',
    },
    {
        'username': 'carpenter_worker',
        'email': 'carpenter@example.com',
        'password': 'Worker12345!',
        'profession': 'Carpenter',
        'category_name': 'Carpentry',
        'service_name': 'Furniture Repair',
        'skills': 'Cabinet Making, Door Fixing',
        'experience_years': 7,
        'service_area': 'Sylhet',
        'hourly_rate': '600.00',
    },
]

# Create admin + customer
admin_user, _ = User.objects.get_or_create(
    username='admin1',
    defaults={
        'email': 'admin1@example.com',
        'role': 'admin',
        'is_staff': True,
        'is_superuser': True,
    },
)
admin_user.set_password('Admin12345!')
admin_user.save()

customer_user, _ = User.objects.get_or_create(
    username='customer01',
    defaults={
        'email': 'customer01@example.com',
        'role': 'customer',
    },
)
customer_user.set_password('Customer12345!')
customer_user.save()

# Create categories
category_map = {}
for config in trade_configs:
    category, _ = Category.objects.get_or_create(
        name=config['category_name'],
        defaults={'description': config['profession'], 'icon': '🛠️', 'is_active': True},
    )
    category_map[config['category_name']] = category

# Create service entries for each trade
service_map = {}
for config in trade_configs:
    category = category_map[config['category_name']]
    service, _ = Service.objects.get_or_create(
        name=config['service_name'],
        defaults={
            'category': category,
            'description': f'{config["profession"]} service for homes and businesses.',
            'price': Decimal(config['hourly_rate']),
            'image': 'service_images/default.jpg',
            'duration': '2-4 hours',
            'location': config['service_area'],
            'is_available': True,
        },
    )
    service_map[config['category_name']] = service

# Create approved worker profiles
created_workers = []
for config in trade_configs:
    user, created = User.objects.get_or_create(
        username=config['username'],
        defaults={
            'email': config['email'],
            'role': 'worker',
            'worker_status': 'APPROVED',
            'is_blocked': False,
        },
    )
    user.set_password(config['password'])
    user.save()

    profile, _ = WorkerProfile.objects.get_or_create(
        user=user,
        defaults={
            'profession': config['profession'],
            'bio': f'{config["profession"]} with {config["experience_years"]} years of experience.',
            'skills': config['skills'],
            'experience_years': config['experience_years'],
            'service_area': config['service_area'],
            'languages': 'English, Bengali',
            'hourly_rate': Decimal(config['hourly_rate']),
            'verification_status': 'Approved',
            'training_status': 'Completed',
            'response_time': 'Within 24 hours',
            'service_category': config['category_name'],
            'service': service_map[config['category_name']],
        },
    )

    if profile.service is None:
        profile.service = service_map[config['category_name']]
    if not profile.service_category:
        profile.service_category = config['category_name']
    profile.profession = config['profession']
    profile.skills = config['skills']
    profile.experience_years = config['experience_years']
    profile.service_area = config['service_area']
    profile.hourly_rate = Decimal(config['hourly_rate'])
    profile.verification_status = 'Approved'
    profile.training_status = 'Completed'
    profile.save()
    profile.categories.set([category_map[config['category_name']]])
    created_workers.append({'user': user, 'profile': profile})

# Create sample open requests for each trade so the worker can see matching requests
request_titles = [
    ('Need electrician for wiring', 'Electrical', 'Electrical Repair'),
    ('Need plumber for bathroom leak', 'Plumbing', 'Pipe Fix'),
    ('Need house cleaning this weekend', 'Cleaning', 'House Cleaning'),
    ('Need carpenter for wardrobe repair', 'Carpentry', 'Furniture Repair'),
]

for title, category_name, service_name in request_titles:
    service = service_map[category_name]
    ServiceRequest.objects.get_or_create(
        customer=customer_user,
        title=title,
        defaults={
            'service': service,
            'description': f'Looking for a qualified {category_name.lower()} professional for this job.',
            'location': 'Dhaka',
            'address': 'House 12, Road 5, Dhaka',
            'preferred_date': timezone.now().date(),
            'status': 'OPEN',
            'budget_min': Decimal('200.00'),
            'budget_max': Decimal('800.00'),
        },
    )

print('==============================')
print('Admin account: admin1 / Admin12345!')
print('Customer account: customer01 / Customer12345!')
print('Worker accounts:')
for config in trade_configs:
    print(f"- {config['username']} / {config['password']} -> {config['profession']} ({config['category_name']})")
print('==============================')
print('Services created:')
for key, service in service_map.items():
    print(f'- {key}: {service.name}')
print('==============================')
print('Approved worker totals by category:')
for category_name in ['Electrical', 'Plumbing', 'Cleaning', 'Carpentry']:
    count = WorkerProfile.objects.filter(categories__name=category_name, user__worker_status='APPROVED').distinct().count()
    print(f'- {category_name}: {count}')
print('==============================')
print('Setup complete. Open request flow is ready for validation.')
