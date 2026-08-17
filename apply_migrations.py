#!/usr/bin/env python
"""
Direct migration runner without Django management command
"""
import os
import django
from django.conf import settings
from django.core.management import call_command

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mjms.settings')
django.setup()

# Run migrations
print("Starting migrations...")
try:
    call_command('migrate', 'bookings', verbosity=2)
    print("\n✓ Bookings migrations applied successfully!")
except Exception as e:
    print(f"\n✗ Error applying bookings migrations: {e}")
    import traceback
    traceback.print_exc()

try:
    call_command('migrate', 'payments', verbosity=2)
    print("\n✓ Payments migrations applied successfully!")
except Exception as e:
    print(f"\n✗ Error applying payments migrations: {e}")
    import traceback
    traceback.print_exc()

print("\nAll migrations completed!")
