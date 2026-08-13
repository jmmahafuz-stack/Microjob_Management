# MJMS - Quick Reference: What Needs to Change

## 🎯 The Three Critical Workflows to Implement

### 1️⃣ WORKER APPROVAL WORKFLOW
```
New Worker Signs Up
    ↓
Status = PENDING (can't apply for jobs yet)
    ↓
Admin reviews WorkerProfile
    ↓
Admin approves → Status = APPROVED (now can apply!)
    or rejects → Status = REJECTED (can't apply)
    or blocks → Status = BLOCKED (can't do anything)
```

**Implementation**: Change `is_verified_worker` from boolean to proper status field

---

### 2️⃣ JOB REQUEST → APPLICATION → JOB WORKFLOW
```
Customer Creates ServiceRequest
    (Title, Description, Budget, Preferred Date/Time, Category)
    ↓
Status = OPEN → APPLICATIONS_RECEIVED
    ↓
Workers (in that category) Apply with JobApplication
    (Proposed Price, Message)
    ↓
Customer Sees Multiple Quotes
    ↓
Customer Selects One Worker
    (ServiceRequest status = WORKER_SELECTED)
    ↓
Job is Created
    (Job status = OPEN)
    ↓
Worker Accepts/Starts Work
    (Job status = IN_PROGRESS)
    ↓
Work Completes
    (Job status = COMPLETED)
    ↓
Payment Processing
    (Job status = PAYMENT_PENDING → PAID)
    ↓
Customer Can Review
    (Review created only after PAID)
```

**Current Problem**: No JobApplication model - workers are directly assigned instead of applying

---

### 3️⃣ PAYMENT & COMMISSION WORKFLOW
```
Customer Approves Worker Quote
    (ServiceRequest.budget = $2000)
    ↓
Worker Completes Job
    ↓
Payment Created:
    gross_amount = 2000
    commission_rate = 10% (current platform setting)
    platform_commission = 2000 * (10/100) = 200
    worker_amount = 2000 - 200 = 1800
    ↓
Transaction Recorded with ALL values stored
    (So if platform changes to 15%, this payment still shows 10%)
    ↓
Worker Receives 1800
    Platform Keeps 200
    Customer Pays 2000
```

**Current Problem**: Payment model missing commission fields and customer/worker FKs

---

## 📊 Models That Need CRITICAL Changes

### Model 1: CustomUser
```python
# BEFORE (WRONG)
is_verified_worker = BooleanField  # Just yes/no

# AFTER (CORRECT)
WORKER_STATUS_CHOICES = [
    ('PENDING', 'Pending Approval'),
    ('APPROVED', 'Approved'),
    ('REJECTED', 'Rejected'),
    ('BLOCKED', 'Blocked'),
]
worker_status = CharField(choices=WORKER_STATUS_CHOICES)
is_blocked = BooleanField  # Separate from approval
city = CharField  # For job location matching
```

---

### Model 2: Booking → ServiceRequest
```python
# BEFORE (WRONG)
class Booking(models.Model):
    customer = FK
    service = FK        # Should be category
    worker = FK         # Direct assignment (WRONG!)
    booking_date = Date
    status = [...]

# AFTER (CORRECT)
class ServiceRequest(models.Model):
    customer = FK
    category = FK       # ← Changed from service
    title = CharField   # ← NEW
    description = TextField  # ← NEW
    budget = Decimal    # ← NEW (critical!)
    preferred_date = Date
    preferred_time = Time
    location = CharField
    city = CharField    # ← NEW
    selected_worker = FK(null=True)  # ← Changed from direct assignment
    status = ['OPEN', 'APPLICATIONS_RECEIVED', 'WORKER_SELECTED', 
              'WORKER_ACCEPTED', 'IN_PROGRESS', 'COMPLETED', 
              'PAYMENT_PENDING', 'PAID', 'CANCELLED', 'DISPUTED']
```

---

### Model 3 (NEW): JobApplication
```python
# DOESN'T EXIST - NEED TO CREATE!
class JobApplication(models.Model):
    service_request = FK(ServiceRequest)
    worker = FK(CustomUser)
    proposed_price = Decimal  # ← This is the worker's bid!
    message = TextField
    status = ['PENDING', 'ACCEPTED', 'REJECTED', 'WITHDRAWN']
    created_at = DateTime
    updated_at = DateTime
```

**Why Critical**: Without this, workers can't bid/apply for jobs!

---

### Model 4 (NEW): Job
```python
# DOESN'T EXIST - NEED TO CREATE!
class Job(models.Model):
    service_request = OneToOneField  # Link back to request
    worker = FK
    status = ['OPEN', 'IN_PROGRESS', 'COMPLETED', 
              'PAYMENT_PENDING', 'PAID']
    assigned_at = DateTime
    started_at = DateTime
    completed_at = DateTime
```

---

### Model 5: Payment
```python
# BEFORE (INCOMPLETE)
class Payment(models.Model):
    booking = OneToOne
    amount = Decimal           # ← Just one amount
    payment_method = CharField
    transaction_id = CharField
    payment_status = CharField
    payment_date = DateTime

# AFTER (COMPLETE)
class Payment(models.Model):
    job = OneToOne
    service_request = OneToOne  # ← NEW
    customer = FK               # ← NEW (for reports)
    worker = FK                 # ← NEW (for reports)
    
    # All these are NEW - critical for business logic!
    gross_amount = Decimal
    commission_rate = Decimal           # Store the % used
    platform_commission = Decimal       # Store calculated amount
    worker_amount = Decimal             # Store net
    
    transaction_id = CharField
    payment_method = CharField
    payment_status = CharField
    paid_at = DateTime
    created_at = DateTime
```

---

### Model 6 (NEW): Notification
```python
# DOESN'T EXIST - NEED TO CREATE!
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
        'APPROVAL_STATUS',
        ...
    ])
    service_request = FK(null=True)
    job = FK(null=True)
    is_read = BooleanField
    created_at = DateTime
```

---

### Model 7: WorkerProfile
```python
# BEFORE (LIMITED)
service_category = CharField    # Single string
service = FK(Service)          # Single service

# AFTER (FLEXIBLE)
categories = ManyToMany(Category)  # Multiple categories!
completed_jobs = PositiveInt   # ← Cached stats
average_rating = Decimal       # ← Cached stats
total_earnings = Decimal       # ← Cached stats
```

---

### Model 8 (NEW): Category
```python
# DOESN'T EXIST - NEED TO CREATE!
class Category(models.Model):
    name = CharField(unique=True)  # "Plumbing", "Electrical", etc.
    description = TextField
    icon = CharField              # emoji or icon class
    image = ImageField
    is_active = BooleanField
```

---

### Model 9 (NEW): CommissionSetting
```python
# DOESN'T EXIST - NEED TO CREATE!
class CommissionSetting(models.Model):
    platform_commission_rate = Decimal  # Default: 10.0
    updated_at = DateTime
    
    @classmethod
    def get_rate(cls):
        setting, _ = cls.objects.get_or_create(pk=1)
        return setting.platform_commission_rate
```

---

### Model 10 (NEW): WorkerAvailability
```python
# DOESN'T EXIST - NEED TO CREATE!
class WorkerAvailability(models.Model):
    worker = FK(CustomUser)
    day_of_week = Int(0-6)  # 0=Monday, 6=Sunday
    start_time = TimeField
    end_time = TimeField
    is_available = BooleanField
    
    class Meta:
        unique_together = ['worker', 'day_of_week']
```

---

## 🔄 Status Flow Comparisons

### ServiceRequest Status Flow
```
OPEN
  ↓
APPLICATIONS_RECEIVED (workers have applied)
  ↓
WORKER_SELECTED (customer picked one)
  ↓
WORKER_ACCEPTED (worker accepted)
  ↓
IN_PROGRESS (work started)
  ↓
COMPLETED (work done)
  ↓
PAYMENT_PENDING (waiting for payment)
  ↓
PAID (✓ job fully complete)

At any point: CANCELLED or DISPUTED
```

---

### Job Application Status Flow
```
PENDING (worker just applied)
  ↓
ACCEPTED (customer selected this worker)
  OR
REJECTED (customer didn't pick them)
  OR
WITHDRAWN (worker changed mind)
```

---

### Job Status Flow
```
OPEN (freshly created)
  ↓
IN_PROGRESS (work started)
  ↓
COMPLETED (work finished)
  ↓
PAYMENT_PENDING (awaiting payment)
  ↓
PAID (✓ complete)

Can also: CANCELLED
```

---

## 📝 Key Code Examples

### Example 1: Customer Creates ServiceRequest
```python
# CORRECT (after changes)
sr = ServiceRequest.objects.create(
    customer=request.user,
    category=Category.objects.get(name='Plumbing'),
    title='Fix kitchen leak',
    description='Water dripping from under sink',
    budget=Decimal('500.00'),      # ← Customer's max budget
    preferred_date='2024-01-15',
    preferred_time='10:00',
    location='Apt 5, 123 Main St',
    city='Dhaka',
    status='OPEN'  # ← Waiting for applications
)
```

### Example 2: Worker Applies
```python
# CORRECT (after changes)
app = JobApplication.objects.create(
    service_request=sr,
    worker=request.user,           # Logged-in worker
    proposed_price=Decimal('450.00'),  # ← Worker's bid
    message='I can do this Monday morning'
)
# sr.status stays OPEN until more workers apply
# Then sr.status = APPLICATIONS_RECEIVED
```

### Example 3: Customer Selects Worker
```python
# CORRECT (after changes)
sr.selected_worker = worker
sr.status = 'WORKER_SELECTED'
sr.save()

# Reject all other applications
JobApplication.objects.filter(
    service_request=sr,
    worker != worker
).update(status='REJECTED')

# Only accepted app remains
JobApplication.objects.filter(
    service_request=sr,
    worker=worker
).update(status='ACCEPTED')
```

### Example 4: Create Job When Worker Accepts
```python
# CORRECT (after changes)
job = Job.objects.create(
    service_request=sr,
    worker=worker,
    status='OPEN',
    assigned_at=now()
)
sr.status = 'WORKER_ACCEPTED'
sr.save()
```

### Example 5: Create Payment After Job Completes
```python
# CORRECT (after changes)
commission_rate = CommissionSetting.get_rate()
gross_amount = sr.budget  # Customer's budget

payment = Payment.objects.create(
    job=job,
    service_request=sr,
    customer=sr.customer,
    worker=worker,
    gross_amount=gross_amount,
    commission_rate=commission_rate,
    platform_commission=gross_amount * (commission_rate / Decimal('100')),
    worker_amount=gross_amount - (gross_amount * (commission_rate / Decimal('100'))),
    payment_method='CASH',
    payment_status='PENDING'
)

# Save calculation happens in Payment.save()
```

---

## ✅ Implementation Checklist

- [ ] Add to CustomUser: `city`, `is_blocked`, `worker_status` (not boolean)
- [ ] Create Category model
- [ ] Rename Booking → ServiceRequest with new fields/status
- [ ] Create JobApplication model (NEW)
- [ ] Create Job model (NEW)
- [ ] Update Payment with commission fields + customer/worker FKs
- [ ] Update WorkerProfile: categories ManyToMany + stats
- [ ] Create Notification model (NEW)
- [ ] Create CommissionSetting model (NEW)
- [ ] Create WorkerAvailability model (NEW)
- [ ] Create Complaint model (NEW)
- [ ] Run migrations
- [ ] Update all views for new workflow
- [ ] Update all templates with new status flows
- [ ] Create notification triggers in views
- [ ] Write comprehensive tests
- [ ] Create seed data

