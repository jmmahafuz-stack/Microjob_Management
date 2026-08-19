#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mjms.settings')
django.setup()

from django.core.management import call_command

# Run specific tests
sys.exit(call_command(
    'test',
    'workers.tests.WorkerRegistrationTests.test_customer_cannot_pay_before_worker_marks_job_complete',
    'workers.tests.WorkerRegistrationTests.test_customer_confirms_payment_and_adds_worker_earnings',
    verbosity=2
))
