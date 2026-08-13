import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mjms.settings')
import django
django.setup()
from accounts.models import CustomUser

accounts = [
    ('admin', 'admin', 'Admin12345!'),
    ('customer', 'customer', 'Customer12345!'),
    ('worker', 'worker', 'Worker12345!'),
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
    user.is_verified_worker = role == 'worker'
    user.save()
    print(f"{role}:{username}:{password}:{'created' if created else 'exists'}")
