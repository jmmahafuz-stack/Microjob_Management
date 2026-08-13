# MJMS - Detailed Gap Analysis

## Executive Summary

Your current implementation is **~35% complete** relative to the specification. The UI/styling work done is excellent, but the backend models need significant restructuring to support proper workflow, approvals, and business logic.

**Critical Blocking Issues** (prevents core functionality):
1. No worker approval workflow
2. No job application system (workers can't bid)
3. Booking conflates 3 separate concepts
4. Payment system incomplete
5. No notification system
6. No notification triggers implemented

---

## Model-by-Model Gap Analysis

### ❌ CustomUser Model (accounts/models.py)

**Current State**:
```python
ROLE_CHOICES = [('customer', 'Customer'), ('worker', 'Worker'), ('admin', 'Admin')]
is_verified_worker = BooleanField  # WRONG: boolean instead of status
# Missing: city, is_blocked
```

**Specification Requires**:
- city: CharField (for job location matching)
- is_blocked: BooleanField (admin can block users)
- worker_status: CharField with choices (PENDING, APPROVED, REJECTED, BLOCKED) ← **NOT boolean**
- customer_status: CharField (ACTIVE, BLOCKED)
- created_at, updated_at: DateTimeField

**Impact**: 
- ❌ Can't track worker approval workflow
- ❌ Can't block users
- ❌ Can't filter jobs by city
- ❌ No audit trail (missing timestamps)

**Fix Priority**: 🔴 CRITICAL - Do this first

---

### ❌ Booking Model (bookings/models.py)

**Current State** (approximate):
```python
class Booking(models.Model):
    customer = FK
    service = FK
    worker = FK
    booking_date = DateField
    status = ['Pending', 'Confirmed', 'In Progress', 'Completed', ...]
```

**Specification Requires**:
Split into 3 models with proper workflow:

**1. ServiceRequest** (customer creates):
```python
class ServiceRequest(models.Model):
    customer = FK(Customer)
    category = FK(Category)  # ← NEW
    title = CharField  # ← NEW
    description = TextField  # ← NEW
    location = CharField
    city = CharField  # ← NEW
    preferred_date = DateField
    preferred_time = TimeField
    budget = DecimalField  # ← NEW (crucial for commission calculation)
    selected_worker = FK(Worker, null=True)  # ← NEW
    status = ['OPEN', 'APPLICATIONS_RECEIVED', 'WORKER_SELECTED', 'WORKER_ACCEPTED',
              'IN_PROGRESS', 'COMPLETED', 'PAYMENT_PENDING', 'PAID', 'CANCELLED', 'DISPUTED']
```

**2. JobApplication** (NEW MODEL - doesn't exist):
```python
class JobApplication(models.Model):
    service_request = FK(ServiceRequest)
    worker = FK(Worker)
    proposed_price = DecimalField  # ← This is how workers bid!
    message = TextField
    status = ['PENDING', 'ACCEPTED', 'REJECTED', 'WITHDRAWN']
```

**3. Job** (NEW MODEL - doesn't exist):
```python
class Job(models.Model):
    service_request = OneToOne
    worker = FK
    status = ['OPEN', 'IN_PROGRESS', 'COMPLETED', 'PAYMENT_PENDING', 'PAID']
    assigned_at, started_at, completed_at = DateTimeField
```

**Current Workflow** (WRONG):
```
Customer books service directly → Worker assigned immediately
(No bidding, no selection, no applications)
```

**Specification Workflow** (CORRECT):
```
ServiceRequest created (OPEN)
    ↓
Workers apply with JobApplication (APPLICATIONS_RECEIVED)
    ↓
Customer selects one worker (WORKER_SELECTED)
    ↓
Selected worker accepts/rejects (WORKER_ACCEPTED)
    ↓
Job created, work begins (IN_PROGRESS)
    ↓
Job completed, payment pending (PAYMENT_PENDING)
    ↓
Payment made (PAID)
```

**Impact**:
- ❌ Workers can't apply/bid for jobs
- ❌ Customers can't see multiple quotes
- ❌ Workers can't withdraw applications
- ❌ No job status tracking
- ❌ Wrong business model (not a "marketplace" without applications)

**Fix Priority**: 🔴 CRITICAL - Core workflow depends on this

---

### ❌ Payment Model (payments/models.py)

**Current State**:
```python
class Payment(models.Model):
    booking = OneToOne
    amount = DecimalField
    payment_method = CharField
    transaction_id = CharField(unique=True)
    payment_status = CharField
    payment_date = DateTimeField
```

**Specification Requires**:
```python
class Payment(models.Model):
    job = OneToOne  # ← CHANGED from booking
    service_request = OneToOne  # ← NEW (for reports)
    customer = FK(Customer)  # ← NEW
    worker = FK(Worker)  # ← NEW
    
    # Amount breakdown ← ALL NEW
    gross_amount = DecimalField  # ← What customer pays (from ServiceRequest budget)
    commission_rate = DecimalField  # ← % at time of payment (e.g., 10.0)
    platform_commission = DecimalField  # ← Calculated: gross * (rate/100)
    worker_amount = DecimalField  # ← Net: gross - commission
    
    transaction_id = CharField(unique=True)
    payment_method = CharField
    payment_status = CharField
    paid_at = DateTimeField  # ← NEW (when payment actually completed)
    created_at = DateTimeField  # ← NEW
```

**Why Commission Tracking Matters**:
- Need to store commission values AT TIME OF PAYMENT for historical accuracy
- If platform rate changes from 10% to 15%, old payments should still show 10%
- Required for: revenue reports, worker earnings reports, audits

**Current Issues**:
- ❌ No customer/worker fields (can't generate reports by user)
- ❌ No commission breakdown (critical for business analytics)
- ❌ Can't generate: "Total revenue", "Total worker payouts", "Platform earnings"
- ❌ If rate changes, historical data becomes meaningless

**Example**:
```python
# Scenario: Customer requests $2000 job, platform takes 10%
Payment.objects.create(
    job=job,
    customer=customer,
    worker=worker,
    gross_amount=2000,
    commission_rate=10.0,
    platform_commission=200,  # 2000 * (10/100)
    worker_amount=1800,       # 2000 - 200
    payment_status='PAID'
)
# Later, if rate changes to 15%, this payment STILL shows 10% historically correct
```

**Fix Priority**: 🔴 CRITICAL - Reports depend on this

---

### ❌ Service Model (services/models.py)

**Current State** (approximate):
```python
class Service(models.Model):
    name = CharField
    category = CharField(choices=['Plumbing', 'Electrical', ...])  # ← WRONG: should be FK
    description = TextField
    price = DecimalField
    image = ImageField
```

**Specification Requires**:
Create separate `Category` model:
```python
class Category(models.Model):
    name = CharField(unique=True)  # Plumbing, Electrical, etc.
    description = TextField
    icon = CharField  # emoji or icon class
    image = ImageField
    is_active = BooleanField
```

Then update Service (optional, or remove if not needed):
```python
class Service(models.Model):
    category = FK(Category)  # ← relationship instead of choices
    name = CharField
    description = TextField
    base_price = DecimalField  # ← Just a reference price
    image = ImageField
```

**Why Separate Category?**:
- WorkerProfile needs ManyToMany relationship to categories
- ServiceRequest needs FK to category
- Can easily add/remove categories from admin
- Easier to manage and query

**Current Issues**:
- ❌ Workers can't be multi-category (if WorkerProfile.service is FK to Service)
- ❌ Jobs are filtered by "Service" not "Category"
- ❌ Hard to add new categories programmatically

**Fix Priority**: 🟡 HIGH - Needed for job filtering

---

### ❌ WorkerProfile Model (workers/models.py)

**Current State**:
```python
class WorkerProfile(models.Model):
    user = OneToOne(CustomUser)
    service_category = CharField  # ← Single string
    service = FK(Service)  # ← Single service
    skills = CharField
    experience = CharField
    bio = TextField
    hourly_rate = DecimalField
    ...
```

**Specification Requires**:
```python
class WorkerProfile(models.Model):
    user = OneToOne(CustomUser)
    categories = ManyToMany(Category)  # ← Multiple categories!
    
    bio = TextField
    skills = TextField
    experience_years = PositiveIntegerField  # ← Proper data type
    service_area = CharField
    languages = CharField
    portfolio_link = URLField
    hourly_rate = DecimalField
    
    # Statistics (cached from queries)
    completed_jobs = PositiveIntegerField  # ← Calculated
    average_rating = DecimalField  # ← Calculated from reviews
    total_earnings = DecimalField  # ← Calculated from payments
    
    created_at, updated_at = DateTimeField
```

**Why ManyToMany Categories?**:
- A plumber might also do "water system maintenance" and "emergency repairs"
- A carpenter might do "furniture repair" and "carpentry"
- Can't handle with single FK

**Current Issues**:
- ❌ Workers limited to one service/category
- ❌ Can't calculate stats (no cached fields)
- ❌ No timestamps for auditing

**Fix Priority**: 🟡 HIGH - Needed for job filtering

---

### ❌ Review Model (reviews/models.py)

**Current State** (probably correct):
```python
class Review(models.Model):
    customer = FK
    worker = FK
    booking = FK
    rating = PositiveSmallInteger
    comment = TextField
```

**Specification Issues**:
- ✅ Model looks good
- ❌ But needs enforcement: only allow after job is PAID (and completed)
- ❌ Needs duplicate prevention: only 1 review per job

**Current Implementation**:
- Likely allows reviews anytime
- Needs view-level enforcement

**Fix Priority**: 🟡 MEDIUM - Logic fix, model mostly OK

---

### ❌❌ MISSING: Notification Model

**Specification Requires**:
```python
class Notification(models.Model):
    user = FK(CustomUser)
    title = CharField
    message = TextField
    notification_type = CharField(choices=[
        'WORKER_APPLIED',
        'WORKER_SELECTED',
        'WORKER_ACCEPTED',
        'JOB_COMPLETED',
        'PAYMENT_RECEIVED',
        'REVIEW_REMINDER',
        'APPROVAL_STATUS',
        'NEW_JOB',
        'COMPLAINT_UPDATE',
    ])
    service_request = FK(null=True)
    job = FK(null=True)
    related_user = FK(null=True)
    is_read = BooleanField
    created_at = DateTimeField
```

**Current Status**: 🔴 DOESN'T EXIST

**Example Usage**:
```python
# When worker applies
Notification.objects.create(
    user=customer,
    title=f"{worker.name} Applied!",
    message=f"Worker applied with price {price}",
    notification_type='WORKER_APPLIED',
    service_request=sr,
    related_user=worker
)

# When worker is selected
Notification.objects.create(
    user=worker,
    title="You're Selected!",
    message=f"Customer selected you for {title}",
    notification_type='WORKER_SELECTED',
    service_request=sr
)
```

**Impact**:
- ❌ No way to notify users of important events
- ❌ Users have no visibility into workflow changes
- ❌ Can't implement "unread notifications" badge

**Fix Priority**: 🔴 CRITICAL - Core user engagement feature

---

### ❌❌ MISSING: CommissionSetting Model

**Specification Requires**:
```python
class CommissionSetting(models.Model):
    platform_commission_rate = DecimalField  # Default: 10.0%
    updated_at = DateTimeField

    @classmethod
    def get_rate(cls):
        setting, _ = cls.objects.get_or_create(pk=1)
        return setting.platform_commission_rate
```

**Current Status**: 🔴 DOESN'T EXIST

**Why Needed**:
- Admin can change commission rate from 10% → 15%
- New payments use new rate
- Old payments show historical rate
- Can audit when changes happened

**Example**:
```python
# At payment time, get current rate
rate = CommissionSetting.get_rate()  # Returns 10.0
payment = Payment.objects.create(
    gross_amount=2000,
    commission_rate=rate,  # Store the exact rate used
    platform_commission=2000 * (rate/100),
)
```

**Fix Priority**: 🟡 HIGH - Needed for payment calculation

---

### ❌❌ MISSING: WorkerAvailability Model

**Specification Requires**:
```python
class WorkerAvailability(models.Model):
    worker = FK(CustomUser)
    day_of_week = IntegerField(choices=[(0, 'Monday'), ..., (6, 'Sunday')])
    start_time = TimeField
    end_time = TimeField
    is_available = BooleanField
    
    class Meta:
        unique_together = ['worker', 'day_of_week']
```

**Current Status**: 🔴 DOESN'T EXIST

**Example**:
```python
# Plumber available Monday-Friday, 9am-5pm
WorkerAvailability.objects.create(worker=plumber, day_of_week=0, start_time='09:00', end_time='17:00')
...
WorkerAvailability.objects.create(worker=plumber, day_of_week=4, start_time='09:00', end_time='17:00')

# Saturday unavailable
WorkerAvailability.objects.create(worker=plumber, day_of_week=5, is_available=False)
```

**Usage**:
- When customer sets preferred date/time, filter workers by availability
- Shows workers "available at that time"

**Fix Priority**: 🟡 MEDIUM - Nice-to-have for UX

---

### ❌❌ MISSING: Complaint Model

**Specification Requires**:
```python
class Complaint(models.Model):
    customer = FK
    worker = FK(null=True)  # May not know worker initially
    service_request = FK
    subject = CharField
    description = TextField
    status = CharField(choices=['OPEN', 'UNDER_REVIEW', 'RESOLVED', 'REJECTED'])
    admin_response = TextField
    created_at, resolved_at = DateTimeField
```

**Current Status**: 🔴 DOESN'T EXIST (or incomplete)

**Example**:
```python
complaint = Complaint.objects.create(
    customer=customer,
    worker=worker,
    service_request=sr,
    subject="Worker didn't complete job",
    description="Only did half the work...",
    status='OPEN'
)

# Admin reviews and responds
complaint.status = 'RESOLVED'
complaint.admin_response = "Refunded customer, blocked worker for 30 days"
complaint.resolved_at = now()
complaint.save()
```

**Fix Priority**: 🟡 HIGH - Important for dispute resolution

---

## Summary Table

| Model/Feature | Current | Spec | Gap | Priority |
|---|---|---|---|---|
| CustomUser | ✅ Basic | Status, city, is_blocked | 🔴 Workflow | CRITICAL |
| Service/Category | ❌ As string | Separate Category model | 🔴 Architecture | CRITICAL |
| Booking | ❌ Single model | ServiceRequest + JobApplication + Job | 🔴 Complete redesign | CRITICAL |
| Payment | ⚠️ Incomplete | + commission breakdown, customer, worker | 🔴 Reports | CRITICAL |
| WorkerProfile | ⚠️ Incomplete | ManyToMany categories, stats | 🟡 Filtering | HIGH |
| Review | ✅ Mostly OK | Enforcement logic | 🟢 Minor | MEDIUM |
| Notification | ❌ MISSING | Complete model | 🔴 Engagement | CRITICAL |
| Complaint | ❌ MISSING | Complete model | 🟡 Disputes | HIGH |
| CommissionSetting | ❌ MISSING | Simple model | 🟡 Settings | HIGH |
| WorkerAvailability | ❌ MISSING | Simple model | 🟢 UX | MEDIUM |

---

## Code Size Impact

**Current Models**: ~500 lines of code
**Specification Models**: ~1500 lines of code
**Additional Views**: ~1000 lines of code
**Additional Templates**: ~50+ new pages

**Total New Code**: ~2000+ lines minimum

---

## Timeline Impact

Given all the gaps, here's realistic timeline:

| Phase | Task | Estimate |
|---|---|---|
| 1 | Update existing models | 3-4 hours |
| 2 | Create new models | 2-3 hours |
| 3 | Create migrations | 1 hour |
| 4 | Update views (10+ views) | 8-10 hours |
| 5 | Create templates (20+ pages) | 12-15 hours |
| 6 | Create notification system | 4-5 hours |
| 7 | Create admin views | 4-5 hours |
| 8 | Write tests | 6-8 hours |
| 9 | Create seed data | 2-3 hours |
| **TOTAL** | | **~50 hours** |

This is realistic for a **production-ready** system, not just a prototype.

---

## Recommendation

### Phase 1 (This Week): Foundation - 8 hours
1. Update CustomUser (worker_status, is_blocked, city)
2. Create Category model
3. Update WorkerProfile (ManyToMany categories)
4. Start migrations

### Phase 2 (Next Week): Core Workflow - 20 hours
1. Rename Booking → ServiceRequest
2. Create JobApplication model
3. Create Job model
4. Update Payment model
5. Update views for new workflow
6. Create 5-10 key templates

### Phase 3 (Week 3): Supporting Systems - 15 hours
1. Create Notification model + triggers
2. Create Complaint model
3. Create CommissionSetting model
4. Create WorkerAvailability model
5. Admin views
6. Seed data

### Phase 4 (Week 4): Testing & Polish - 10 hours
1. Write comprehensive tests
2. Bug fixes
3. Performance optimization
4. Documentation

---

## Critical Path

The order matters. **DON'T** do:
- ❌ Create templates before models are fixed
- ❌ Start views before models are defined
- ❌ Write tests before logic is clear

**DO** follow this order:
1. Models → Migrations → Tests → Views → Templates

This ensures foundation is solid before building on top.

