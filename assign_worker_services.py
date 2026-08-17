#!/usr/bin/env python
"""Assign services to test workers."""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mjms.settings")
django.setup()

from services.models import Service
from workers.models import WorkerProfile
from accounts.models import CustomUser

# Assign to testworker
worker = CustomUser.objects.filter(username='testworker').first()
if worker:
    prof, _ = WorkerProfile.objects.get_or_create(user=worker)
    service = Service.objects.filter(name='Emergency Plumbing').first()
    if service:
        prof.service = service
        prof.service_category = service.category
        prof.save()
        print(f'✓ Assigned {service.name} to {worker.username}')
    else:
        print('Service not found')
else:
    print('Worker testworker not found')

# Assign to worker
worker = CustomUser.objects.filter(username='worker').first()
if worker:
    prof, _ = WorkerProfile.objects.get_or_create(user=worker)
    service = Service.objects.filter(name='Electrical Repair').first()
    if service:
        prof.service = service
        prof.service_category = service.category
        prof.save()
        print(f'✓ Assigned {service.name} to {worker.username}')
else:
    print('Worker not found')

print('\n✓ All workers assigned services!')
