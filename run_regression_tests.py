#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mjms.settings')
django.setup()

from django.core.management import call_command

# Run the two critical tests
try:
    print("Running payment flow regression tests...")
    call_command(
        'test',
        'workers.tests.WorkerRegistrationTests.test_customer_cannot_pay_before_worker_marks_job_complete',
        'workers.tests.WorkerRegistrationTests.test_customer_confirms_payment_and_adds_worker_earnings',
        verbosity=2
    )
    print("\n✓ All regression tests passed!")
except SystemExit as e:
    if e.code == 0:
        print("\n✓ All regression tests passed!")
    else:
        print(f"\n✗ Tests failed with exit code: {e.code}")
        sys.exit(1)
