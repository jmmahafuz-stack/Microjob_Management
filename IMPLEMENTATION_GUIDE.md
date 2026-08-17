# MJMS - Step-by-Step Implementation Guide

## Phase 1: Update Existing Models (DO THIS FIRST)

### Step 1.1: Update CustomUser Model
**File**: `accounts/models.py`

Replace the existing `CustomUser` model with the corrected version from `CORRECTED_MODELS.py`.

**Key Changes**:
- Add `city` field (CharField)
- Add `is_blocked` field (BooleanField)
- Change `is_verified_worker` → `worker_status` with choices (PENDING, APPROVED, REJECTED, BLOCKED)
- Add `customer_status` field (new)
- Add created_at, updated_at timestamps

**After Updating**:
```bash
python manage.py makemigrations accounts
python manage.py migrate
```

---

### Step 1.2: Create Category Model
**File**: `services/models.py`

Add the `Category` model from `CORRECTED_MODELS.py`.

This will replace Service-based categories with a dedicated Category model.

**After Adding**:
```bash
python manage.py makemigrations services
python manage.py migrate
```

**Then**: Create sample categories via Django admin or a management command.

---

### Step 1.3: Update WorkerProfile Model
**File**: `workers/models.py`

Replace existing `WorkerProfile` with corrected version:

**Key Changes**:
- Change `service` ForeignKey → `categories` ManyToManyField to Category
- Remove `service_category` field
- Add `experience_years` field (PositiveIntegerField)
- Add `completed_jobs`, `average_rating`, `total_earnings` (for caching stats)
- Add `default_preferred_contact` field
- Add proper indexes

**After Updating**:
```bash
python manage.py makemigrations workers
python manage.py migrate
```

---

## Phase 2: Create New Models

### Step 2.1: Create ServiceRequest Model
**File**: `bookings/models.py` (or rename to `services/models.py`)

**IMPORTANT**: 
- Rename the `Booking` model to `ServiceRequest`
- Use the corrected model from `CORRECTED_MODELS.py`
- Add these new fields: `category` FK, `title`, `budget`, `selected_worker`, proper status flow

**Before**:
```python
class Booking(models.Model):
    customer = ForeignKey
    service = ForeignKey
    worker = ForeignKey
    ...
    status = CHOICES ['Pending', 'Confirmed', 'In Progress', ...]
```

**After**:
```python
class ServiceRequest(models.Model):
    customer = ForeignKey
    category = ForeignKey  # NEW
    title = CharField  # NEW
    budget = DecimalField  # NEW
    selected_worker = ForeignKey  # NEW
    ...
    status = CHOICES ['OPEN', 'APPLICATIONS_RECEIVED', 'WORKER_SELECTED', ...]
```

---

### Step 2.2: Create JobApplication Model
**File**: `bookings/models.py`

**Purpose**: Track worker applications for service requests

```python
class JobApplication(models.Model):
    service_request = ForeignKey(ServiceRequest)
    worker = ForeignKey(CustomUser)
    proposed_price = DecimalField
    message = TextField
    status = CharField(choices=['PENDING', 'ACCEPTED', 'REJECTED', 'WITHDRAWN'])
```

This is a **NEW** workflow that doesn't exist in your current code.

---

### Step 2.3: Create Job Model
**File**: `bookings/models.py`

**Purpose**: Represents the actual job after worker is selected

```python
class Job(models.Model):
    service_request = OneToOneField(ServiceRequest)
    worker = ForeignKey(CustomUser)
    status = CharField(choices=['OPEN', 'IN_PROGRESS', 'COMPLETED', ...])
    assigned_at, started_at, completed_at = DateTimeField
```

This separates the "job in progress" concept from "service request".

---

### Step 2.4: Update Payment Model
**File**: `payments/models.py`

**Current Issues**:
- Missing: transaction_id, customer FK, worker FK, commission fields

**Changes**:
- Add `job` OneToOneField (or keep booking)
- Add `service_request` OneToOneField
- Add `customer` ForeignKey
- Add `worker` ForeignKey
- Rename `amount` → `gross_amount`
- Add `commission_rate` DecimalField
- Add `platform_commission` DecimalField (calculated)
- Add `worker_amount` DecimalField (calculated)
- Add `transaction_id` unique field
- Override `save()` to calculate commission

---

### Step 2.5: Create Notification Model
**File**: Create `notifications/models.py`

**Purpose**: Track all user notifications

```python
class Notification(models.Model):
    user = ForeignKey(CustomUser)
    title, message = CharField, TextField
    notification_type = CharField
    service_request, job, related_user = ForeignKey fields
    is_read = BooleanField
    created_at = DateTimeField
```

**After Creating**:
```bash
python manage.py startapp notifications  # if it doesn't exist
python manage.py makemigrations notifications
python manage.py migrate
```

---

### Step 2.6: Create CommissionSetting Model
**File**: Create in `payments/models.py`

**Purpose**: Store global platform commission rate

```python
class CommissionSetting(models.Model):
    platform_commission_rate = DecimalField(default=10.00)
    
    @classmethod
    def get_rate(cls):
        setting, _ = cls.objects.get_or_create(pk=1)
        return setting.platform_commission_rate
```

---

### Step 2.7: Create WorkerAvailability Model
**File**: Create in `workers/models.py`

**Purpose**: Store worker availability by day/time

```python
class WorkerAvailability(models.Model):
    worker = ForeignKey(CustomUser)
    day_of_week = IntegerField(0-6)
    start_time, end_time = TimeField
    is_available = BooleanField
```

---

## Phase 3: Update Views and Forms

### Step 3.1: Update Service Request Workflow
**File**: `bookings/views.py`

**Current**: Customers book a service directly

**After**: Implement 3-step workflow:
1. Customer creates ServiceRequest
2. Workers apply with JobApplication
3. Customer selects one worker
4. Selected worker accepts → Job is created

**Views to Update**:
- `create_booking()` → `create_service_request()`
- Add `apply_for_job()` view (new)
- Add `select_worker()` view (new)
- Update `booking_detail()` to show applications

---

### Step 3.2: Add Worker Approval View
**File**: Create `workers/views.py` or update

**Purpose**: Allow admin to approve pending workers

```python
@admin_required
def approve_worker(request, worker_id):
    worker = CustomUser.objects.get(id=worker_id, role='worker')
    worker.worker_status = 'APPROVED'
    worker.save()
    # Send notification
    return redirect(...)
```

---

## Phase 4: Migration Strategy

### Create Migrations

```bash
# 1. Update accounts
python manage.py makemigrations accounts
python manage.py migrate

# 2. Update services/categories
python manage.py makemigrations services
python manage.py migrate

# 3. Update workers
python manage.py makemigrations workers
python manage.py migrate

# 4. Update bookings (ServiceRequest + JobApplication + Job)
python manage.py makemigrations bookings
python manage.py migrate

# 5. Update payments
python manage.py makemigrations payments
python manage.py migrate

# 6. Create notifications
python manage.py makemigrations notifications
python manage.py migrate

# 7. Add commission settings and availability
python manage.py makemigrations
python manage.py migrate
```

### Handle Data Migration
If you have existing `Booking` records:

```python
# Create a data migration
python manage.py makemigrations bookings --empty --name migrate_booking_to_service_request

# Edit the migration to:
# 1. Copy Booking → ServiceRequest
# 2. Create Job records for completed bookings
# 3. Delete or archive old Booking records
```

---

## Phase 5: Update Admin

### File: `accounts/admin.py`

```python
from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'role', 'worker_status' if role=='worker' else 'customer_status', 'is_blocked']
    list_filter = ['role', 'worker_status', 'customer_status', 'is_blocked']
    fieldsets = (
        ('User Info', {'fields': ('username', 'email', 'first_name', 'last_name')}),
        ('Contact', {'fields': ('phone', 'address', 'city', 'preferred_contact_method')}),
        ('Role & Status', {'fields': ('role', 'worker_status', 'customer_status', 'is_blocked')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_active')}),
    )
```

### File: `workers/admin.py`

```python
@admin.register(WorkerProfile)
class WorkerProfileAdmin(admin.ModelAdmin):
    filter_horizontal = ['categories']  # ManyToMany select
    
@admin.register(WorkerAvailability)
class WorkerAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['worker', 'day_of_week', 'start_time', 'end_time', 'is_available']
```

### File: `bookings/admin.py`

```python
@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ['customer', 'category', 'title', 'status', 'budget']
    list_filter = ['status', 'category', 'created_at']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['worker', 'service_request', 'proposed_price', 'status']
    list_filter = ['status', 'created_at']

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['service_request', 'worker', 'status']
    list_filter = ['status', 'created_at']
```

---

## Phase 6: Create Seed Data

**File**: Create `management/commands/seed_data.py`

```python
from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from services.models import Category
from workers.models import WorkerProfile

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Create categories
        categories = ['Plumbing', 'Electrical', 'Carpentry', 'Painting', 'AC Repair']
        for cat_name in categories:
            Category.objects.get_or_create(name=cat_name)
        
        # Create admin
        CustomUser.objects.create_superuser(
            username='admin',
            email='admin@mjms.com',
            password='admin123',
            role='admin'
        )
        
        # Create sample customers
        for i in range(5):
            CustomUser.objects.create_user(
                username=f'customer{i}',
                email=f'customer{i}@mjms.com',
                password='pass123',
                role='customer',
                first_name=f'Customer {i}',
                city='Dhaka'
            )
        
        # Create sample workers
        for i in range(5):
            user = CustomUser.objects.create_user(
                username=f'worker{i}',
                email=f'worker{i}@mjms.com',
                password='pass123',
                role='worker',
                first_name=f'Worker {i}',
                worker_status='APPROVED',  # Approve them
                city='Dhaka'
            )
            profile = WorkerProfile.objects.create(user=user, experience_years=3)
            profile.categories.set(Category.objects.all()[:2])
```

Run it:
```bash
python manage.py seed_data
```

---

## Phase 7: Test Business Logic

### Test Checklist

- [ ] Customer can create ServiceRequest
- [ ] Worker sees jobs in their categories
- [ ] Worker can apply with JobApplication
- [ ] Customer sees applications
- [ ] Customer can select a worker
- [ ] Selected application = ACCEPTED
- [ ] Other applications = REJECTED
- [ ] Job is created
- [ ] Worker can start/complete job
- [ ] Payment calculates commission correctly
- [ ] Notification is sent for each event
- [ ] Worker can't apply before APPROVED
- [ ] Blocked users can't create requests
- [ ] Only PAID jobs can be reviewed
- [ ] Reports calculate correctly

---

## Timeline Estimate

1. Update existing models: **2 hours**
2. Create new models: **2 hours**
3. Create migrations & run: **1 hour**
4. Update views: **4 hours**
5. Update templates: **6 hours**
6. Update admin: **2 hours**
7. Create seed data: **1 hour**
8. Testing: **4 hours**

**Total: ~22 hours**

---

## After Implementation

Once complete, your system will have:

✅ Proper ServiceRequest → JobApplication → Job workflow
✅ Worker approval system (PENDING → APPROVED)
✅ Commission tracking with historical records
✅ Notification system
✅ Proper role-based access control
✅ Complaint handling
✅ Worker availability tracking
✅ Category-based job filtering

This will fully match the specification!

