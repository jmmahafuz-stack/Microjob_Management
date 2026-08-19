# Database Migration & Setup Guide

## Overview
This guide explains how to apply the database changes and run the system with all corrections implemented.

---

## Step 1: Create Migrations

### 1.1 Create Migration for Service Model Changes

The Service model has been changed from using `CharField` with choices to using a `ForeignKey` to Category.

```bash
python manage.py makemigrations services
```

**What this does:**
- Creates migration to change `category` field from CharField to ForeignKey
- You may need to provide a default category for existing services

### 1.2 Create Migration for WorkerProfile Changes

The `profession` field is now required (blank=False).

```bash
python manage.py makemigrations workers
```

### 1.3 Create Migration for Notification Changes

New notification types have been added.

```bash
python manage.py makemigrations notifications
```

### 1.4 Create Migration for Job Model Changes

The Job model's `clean()` method has been enhanced, but no schema changes.

---

## Step 2: Handle Data Migration for Service Category

Since we're changing from CharField to ForeignKey, we need to migrate existing data:

### 2.1 Create Data Migration

```bash
python manage.py makemigrations services --empty --name migrate_service_categories
```

This creates an empty migration file you can fill in.

### 2.2 Create Categories First

If you don't have categories yet, create them through Django shell or admin:

```bash
python manage.py shell

from services.models import Category

categories_to_create = [
    {'name': 'Electrical', 'description': 'Electrical services'},
    {'name': 'Plumbing', 'description': 'Plumbing services'},
    {'name': 'Carpentry', 'description': 'Carpentry services'},
    {'name': 'AC Repair', 'description': 'AC Repair services'},
]

for cat_data in categories_to_create:
    Category.objects.get_or_create(**cat_data)

exit()
```

### 2.3 Handle Profession Field

For existing workers without profession, set a default:

```bash
python manage.py shell

from workers.models import WorkerProfile

# Set default profession for workers who don't have one
WorkerProfile.objects.filter(profession__isnull=True).update(profession='General Services')
WorkerProfile.objects.filter(profession='').update(profession='General Services')

exit()
```

---

## Step 3: Apply Migrations

```bash
python manage.py migrate
```

This applies all migrations in order:
- services: Category field change
- workers: Profession requirement
- notifications: New notification types
- bookings: Enhanced validation (no schema changes)

---

## Step 4: Verify Installation

Run these checks to ensure everything is working:

```bash
# Check for any migration issues
python manage.py migrate --check

# Test Django shell
python manage.py shell -c "from django.apps import apps; print('✓ Apps loaded successfully')"

# Run tests
python manage.py test
```

---

## Step 5: Create Sample Data (Optional)

If you want to test the system:

```bash
python manage.py shell

from django.contrib.auth import get_user_model
from services.models import Category, Service
from workers.models import WorkerProfile

User = get_user_model()

# Create categories
categories = []
for cat_name in ['Electrical', 'Plumbing', 'Carpentry']:
    cat, _ = Category.objects.get_or_create(
        name=cat_name,
        defaults={'description': f'{cat_name} services', 'is_active': True}
    )
    categories.append(cat)

# Create services
services = [
    {'name': 'Electrical Wiring', 'category': categories[0], 'price': 100, 'duration': '2 hours'},
    {'name': 'Pipe Repair', 'category': categories[1], 'price': 80, 'duration': '1.5 hours'},
    {'name': 'Furniture Making', 'category': categories[2], 'price': 150, 'duration': '4 hours'},
]

for service_data in services:
    Service.objects.get_or_create(**service_data)

print("✓ Sample data created!")
exit()
```

---

## Step 6: Run Development Server

```bash
python manage.py runserver
```

---

## Common Issues & Solutions

### Issue 1: "Column does not exist" error
**Solution:** Make sure you ran `python manage.py migrate` after creating migrations.

### Issue 2: Service.category ValueError during migration
**Solution:** Create categories first, then run migration with default category selection.

### Issue 3: WorkerProfile has workers without profession
**Solution:** Run the shell command to update existing workers with default profession.

### Issue 4: Import errors in notifications.utils
**Solution:** Make sure all models are imported correctly and EMAIL settings are configured in settings.py.

---

## Admin Interface Setup

After migrations, the admin interface has been enhanced:

### 1. Go to Django Admin
```
http://localhost:8000/admin/
```

### 2. Manage Services
- **Services** → Create new services through admin
- Each service is linked to a category
- See available workers for each service

### 3. Approve Workers
- **Users** → Select pending workers
- Use action: "Approve selected workers"
- Workers automatically get approval notification

### 4. View Jobs & Applications
- **ServiceRequests** → See all requests
- **JobApplications** → Review worker applications
- **Jobs** → Monitor active jobs, check for conflicts

---

## Testing the Workflow

### 1. Admin Creates Service
1. Go to Admin → Services → Add Service
2. Select Category, add details
3. Save

### 2. Worker Registers
1. Go to Registration → Select "Worker"
2. Fill profile with profession (required)
3. Select categories they work in
4. Status: PENDING

### 3. Admin Approves Worker
1. Go to Admin → Users
2. Find pending worker
3. Action: "Approve selected workers"
4. Worker gets approval notification

### 4. Customer Creates Request
1. Customer logs in
2. Selects service
3. Fills job details (address, date, time, budget)
4. Request created

### 5. Worker Sees Request
1. Worker goes to "Available Jobs"
2. Only sees jobs matching their categories
3. Can apply for job

### 6. Customer Reviews Applications
1. Views all worker applications
2. Selects preferred worker
3. Job is created

### 7. System Checks Conflicts
1. Job is confirmed
2. System checks if worker has time conflict
3. If conflict exists, shows notification
4. Customer is notified if worker unavailable

### 8. Job Completion & Payment
1. Worker marks job complete
2. Customer gets payment notification
3. Customer makes payment
4. Payment confirmation sent to worker

---

## Environment Configuration

Make sure your `settings.py` has:

```python
# Email Configuration (for notifications)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # or your email service
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'

# Media Files (for uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

---

## Next Steps

1. ✅ Apply all migrations
2. ✅ Create sample categories and services through admin
3. ✅ Test user registration flow
4. ✅ Test worker approval workflow
5. ✅ Test job request and application flow
6. ✅ Verify notifications are sent
7. ✅ Test payment integration
8. ✅ Deploy to production

---

## Rollback (If Needed)

If you need to rollback changes:

```bash
# See migration history
python manage.py showmigrations

# Rollback to specific migration
python manage.py migrate services 0001  # Go to first migration
python manage.py migrate workers 0001
```

---

## Verification Checklist

- [ ] Migrations created successfully
- [ ] Migrations applied without errors
- [ ] Admin interface loads
- [ ] Can create services in admin
- [ ] Can approve workers in admin
- [ ] Services show available workers
- [ ] Jobs prevent time conflicts
- [ ] Notifications are created
- [ ] Email notifications configured (optional)
- [ ] All tests pass

