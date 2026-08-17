# MJMS - Corrections Guide Based on Specification

## Summary of Issues and Fixes

### ❌ ISSUE 1: Incorrect Architecture
**Problem**: Current `Booking` model tries to handle 3 separate workflows:
1. ServiceRequest (customer creates a job request)
2. JobApplication (workers apply with their proposed price)
3. Job (actual job being performed)

**Solution**: Separate into 4 distinct models with proper workflow:
```
ServiceRequest (customer creates)
    ↓
JobApplication (workers apply, status: PENDING/ACCEPTED/REJECTED)
    ↓
Job (created when worker selected, status: OPEN→IN_PROGRESS→COMPLETED→PAYMENT_PENDING→PAID)
    ↓
Payment (tracks money + commission)
```

### ❌ ISSUE 2: Missing Category Model
**Problem**: Services are being used as categories, but they should be separate.

**Solution**: 
- Create `Category` model (Plumbing, Electrical, Carpentry, etc.)
- Make `WorkerProfile` have ManyToMany relationship to `Category`
- Keep `Service` as specific service offerings if needed

### ❌ ISSUE 3: Worker Approval System
**Problem**: Using boolean `is_verified_worker` instead of proper status flow.

**Solution**: Use status choices:
```python
WORKER_STATUS_CHOICES = [
    ('PENDING', 'Pending Approval'),
    ('APPROVED', 'Approved'),
    ('REJECTED', 'Rejected'),
    ('BLOCKED', 'Blocked'),
]
```

### ❌ ISSUE 4: Payment Model Incomplete
**Problem**: Missing commission tracking, customer/worker fields, detailed breakdown.

**Solution**: Add these fields:
- `transaction_id` (unique identifier)
- `customer` (ForeignKey)
- `worker` (ForeignKey)
- `service_request` (ForeignKey)
- `gross_amount` (total customer pays)
- `commission_rate` (10% or custom at time of payment)
- `platform_commission` (calculated: gross * rate)
- `worker_amount` (net: gross - platform_commission)

### ❌ ISSUE 5: Missing Notification System
**Problem**: No Notification model for user alerts.

**Solution**: Create Notification model with:
- user, title, message, notification_type, is_read, created_at

### ❌ ISSUE 6: Missing Complaint System
**Problem**: No proper complaint tracking.

**Solution**: Create Complaint model with:
- customer, worker, service_request, subject, description, status, admin_response

### ❌ ISSUE 7: User Model Issues
**Problem**: 
- Missing `city` field
- Missing `is_blocked` field
- No proper customer status tracking

**Solution**: Add fields to CustomUser

### ❌ ISSUE 8: Status Workflow Issues
**Problem**: Current status flow doesn't match specification.

**Solution**: 

For ServiceRequest:
```
OPEN → APPLICATIONS_RECEIVED → WORKER_SELECTED → WORKER_ACCEPTED → 
IN_PROGRESS → COMPLETED → PAYMENT_PENDING → PAID
(or CANCELLED at any point)
```

For JobApplication:
```
PENDING → ACCEPTED (or REJECTED, WITHDRAWN)
```

---

## Implementation Steps

### Step 1: Update CustomUser Model
- Add `city` field
- Add `is_blocked` field  
- Change `is_verified_worker` to `worker_status` with choices

### Step 2: Create Category Model
- Create new app or add to services app
- Categories: Plumbing, Electrical, Carpentry, House Cleaning, Painting, AC Repair, Gardening, Computer Repair, Appliance Repair

### Step 3: Update WorkerProfile Model
- Change to ManyToMany with Category
- Remove old service_category field
- Add proper approval_status field

### Step 4: Rename Booking Model
- Rename to ServiceRequest
- Update status flow
- Add budget field
- Add city field

### Step 5: Create JobApplication Model
- Link ServiceRequest to Worker
- Track proposed price
- Track application message
- Track status (PENDING, ACCEPTED, REJECTED, WITHDRAWN)

### Step 6: Create Job Model
- Link to ServiceRequest and selected Worker
- Track job progress
- Track timestamps

### Step 7: Update Payment Model
- Add all missing commission fields
- Properly link to service_request and worker

### Step 8: Create Notification Model
- Track all user notifications
- Support different notification types

### Step 9: Create Complaint Model
- Track disputes and complaints
- Support resolution workflow

### Step 10: Create CommissionSetting Model
- Store platform commission percentage
- Default 10%

---

## Database Relationships (Corrected)

```
CustomUser (1)
├── is_staff, is_superuser (for admin)
├── role: CUSTOMER | WORKER | ADMIN
├── is_blocked: bool
├── city: string
└── (Special for workers)
    └── worker_status: PENDING | APPROVED | REJECTED | BLOCKED

WorkerProfile (1 user → 1 profile)
├── user: OneToOne
├── categories: ManyToMany → Category
├── bio, skills, experience
├── average_rating (calculated)
└── completed_jobs (calculated)

Category (many)
├── name
├── description
├── is_active

ServiceRequest (many)
├── customer: ForeignKey → CustomUser
├── category: ForeignKey → Category
├── title, description, location, city
├── preferred_date, preferred_time
├── budget: DecimalField
├── status: OPEN | APPLICATIONS_RECEIVED | WORKER_SELECTED | ...
└── timestamps

JobApplication (many)
├── service_request: ForeignKey
├── worker: ForeignKey → CustomUser
├── proposed_price: DecimalField
├── message: TextField
├── status: PENDING | ACCEPTED | REJECTED | WITHDRAWN
└── timestamps

Job (many)
├── service_request: OneToOne
├── worker: ForeignKey
├── status: OPEN | IN_PROGRESS | COMPLETED | PAYMENT_PENDING | PAID
├── assigned_at, started_at, completed_at
└── timestamps

Payment (one per completed job)
├── job: OneToOne
├── customer: ForeignKey
├── worker: ForeignKey
├── gross_amount: DecimalField
├── commission_rate: DecimalField (e.g., 10)
├── platform_commission: DecimalField (calculated)
├── worker_amount: DecimalField (calculated)
├── transaction_id: string (unique)
├── payment_method: CASH | MOBILE_BANKING | CARD
├── payment_status: PENDING | PAID | FAILED
└── timestamps

Review (many)
├── customer: ForeignKey
├── worker: ForeignKey
├── job: ForeignKey
├── rating: 1-5
├── comment: TextField
└── constraint: unique per job

Complaint (many)
├── customer: ForeignKey
├── worker: ForeignKey (nullable)
├── service_request: ForeignKey
├── subject, description
├── status: OPEN | UNDER_REVIEW | RESOLVED | REJECTED
├── admin_response: TextField
└── timestamps

Notification (many)
├── user: ForeignKey
├── title, message
├── notification_type: NEW_APPLICATION | WORKER_SELECTED | PAYMENT_RECEIVED | ...
├── is_read: bool
└── created_at

CommissionSetting (singleton)
└── platform_commission_rate: DecimalField (default 10.0)

WorkerAvailability (many)
├── worker: ForeignKey
├── day_of_week: (0-6)
├── start_time: TimeField
├── end_time: TimeField
├── is_available: bool
```

---

## Key Business Logic Rules to Implement

1. **Worker Approval**:
   - New workers start with status = PENDING
   - Only ADMIN can change to APPROVED
   - Only APPROVED workers can apply

2. **Service Request Workflow**:
   - Customer creates → status = OPEN
   - Workers apply → status = APPLICATIONS_RECEIVED
   - Customer selects worker → status = WORKER_SELECTED
   - Worker accepts → status = WORKER_ACCEPTED
   - Worker starts → status = IN_PROGRESS
   - Worker completes → status = COMPLETED
   - Payment made → status = PAID
   - Can be CANCELLED anytime

3. **Commission Calculation**:
   ```python
   gross = 2000
   rate = 10  # percent
   platform_commission = gross * (rate / 100)  # 200
   worker_amount = gross - platform_commission  # 1800
   ```
   Store all values in Payment record.

4. **Access Control**:
   - Customers can only view/edit their own requests
   - Workers can only view jobs in their categories
   - Workers can only view their own applications
   - Admins can view everything
   - Blocked users cannot create requests/applications

5. **Reviews**:
   - Only after job is PAID
   - One review per job (unique constraint)
   - Prevent self-reviews (customer ≠ worker)

---

## Testing Checklist

- [ ] Worker can't apply before APPROVED
- [ ] Customer can't see other customers' requests
- [ ] Commission calculated correctly
- [ ] Worker status changes properly
- [ ] Only one worker can be selected per request
- [ ] Other applications rejected after selection
- [ ] Blocked users can't create requests
- [ ] Notifications generated for key events
- [ ] Reports calculate correctly
- [ ] Historical payments don't change if commission % changes

---

## Next Steps

1. Create migrations for new models
2. Update views to use correct models
3. Update templates with new status flows
4. Update admin with approvals
5. Create notification triggers
6. Create report calculations
7. Add comprehensive tests
8. Update seed data command
