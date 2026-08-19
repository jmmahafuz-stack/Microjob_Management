# Admin Dashboard - Quick Reference Guide

## Access the Admin Dashboard

1. Login as an admin user
2. Navigate to Dashboard → Admin Management → User Management
3. URL: `/dashboard/admin/users/`

---

## Managing Workers

### View Worker Profile
1. Click **"View Profile"** button next to any worker
2. See detailed information:
   - Professional background (profession, experience, languages)
   - Current verification status
   - Performance metrics (completed jobs, average rating)
   - Earnings information
   - Service categories assigned

### Worker Status Workflow

```
PENDING → Approve ↓ → APPROVED
           OR ↓
         Reject ↓ → REJECTED

APPROVED → Block ↓ → BLOCKED
BLOCKED ↓→ Unblock ↓ → APPROVED
```

#### Actions by Status:

**PENDING Status:**
- ✅ Approve Worker - Allows them to receive bookings
- ✅ Reject Worker - Blocks them permanently
- ✅ View Profile - See full details before deciding

**APPROVED Status:**
- ✅ Block Worker - Temporarily disable their account
- ✅ View Profile - Check their current performance

**BLOCKED Status:**
- ✅ Unblock Worker - Restore their account
- ✅ View Profile - Review why they were blocked

**REJECTED Status:**
- View Profile only (no actions available)

---

## Managing Customers

### View Customer Profile
1. Click **"View Profile"** button next to any customer
2. See:
   - Account information
   - Activity history (jobs posted, completed jobs)
   - Customer satisfaction metrics
   - Contact preferences

### Customer Status Workflow

```
ACTIVE → Block ↓ → BLOCKED
BLOCKED ↓→ Unblock ↓ → ACTIVE
```

#### Actions by Status:

**ACTIVE Status:**
- ✅ Block Customer - Prevent them from posting jobs
- ✅ View Profile - Check their activity

**BLOCKED Status:**
- ✅ Unblock Customer - Restore their account
- ✅ View Profile - Review previous activity

---

## When Workers Are Approved

When you click "Approve" on a pending worker:

1. ✅ Worker's status changes to APPROVED
2. ✅ Worker immediately appears in service lists
3. ✅ Customers can now see this worker's profile when browsing services
4. ✅ Worker can accept service requests and jobs
5. ✅ Worker appears in "Assign Worker" dropdowns when customers book services

### Service Availability Timeline
- **Before Approval**: Services exist but show no available workers
- **After Approval**: Services show the approved worker's profile and information
- **When Blocked**: Services no longer show the worker (if no other workers in category)

---

## When Workers Are Blocked

When you click "Block" on an approved worker:

1. Worker can no longer accept new jobs
2. Worker does NOT appear in service lists or booking dropdowns
3. Existing jobs continue normally
4. Can be unblocked anytime to restore access

---

## When Customers Are Blocked

When you click "Block" on an active customer:

1. Customer cannot post new service requests
2. Customer cannot book services
3. Existing jobs continue (already in progress)
4. Can be unblocked anytime to restore access

---

## Tips for Management

### Approving New Workers
1. Review their professional information
2. Check if they've completed basic profile setup
3. Verify they're in legitimate service categories
4. Look for red flags (multiple test accounts, etc.)

### Monitoring Performance
- ✅ Check completed jobs count
- ✅ Review average rating
- ✅ Monitor total earnings and payout history
- ✅ Track service category matches

### Blocking Guidance
Block a worker if:
- Multiple customer complaints
- Consistent low ratings
- Service quality issues
- Policy violations

Block a customer if:
- Fraudulent activity
- Abusive behavior toward workers
- Non-payment issues
- Policy violations

---

## Filter & Search

### By Role
- **All users**: View everyone
- **Workers**: Only worker accounts (all statuses)
- **Customers**: Only customer accounts
- **Admins**: Admin accounts

### By Search
- Search by name (first or last)
- Search by email address
- Search by username

### Example: Find all pending workers
1. Select "Workers" from role filter
2. Click "Filter"
3. Scroll to find those with "PENDING" status

---

## Status Indicators

| Status | Badge Color | Worker? | Customer? |
|--------|-----------|---------|-----------|
| PENDING | Blue | Can't work | - |
| APPROVED | Green | Can work | - |
| REJECTED | Gray | Blocked | - |
| BLOCKED | Red | Can't work | - |
| ACTIVE | Green | - | Can book |
| BLOCKED | Red | - | Can't book |

---

## Common Tasks

### "Approve a worker to let customers book their services"
1. Go to User Management
2. Filter by "Workers"
3. Find the pending worker
4. Click "Approve" button
5. Done! Services now show this worker

### "Temporarily suspend a worker"
1. View the worker's profile
2. Click "Block Worker"
3. Services no longer show this worker
4. To restore: Click "Unblock Worker"

### "Prevent a customer from booking"
1. View the customer's profile
2. Click "Block Customer"
3. They cannot book services
4. To restore: Click "Unblock Customer"

### "Review a worker before approving"
1. Click "View Profile" on pending worker
2. Review:
   - Professional qualifications
   - Service categories
   - Verification documents
   - Previous performance (if any)
3. Click "Approve" or "Reject"

---

## Related Pages

- **Dashboard Home**: Main analytics and overview
- **Workers Earnings**: View all worker earnings and payouts
- **Payments**: Monitor transaction history
- **Jobs**: View all posted jobs
- **Payouts**: Manage worker payout requests

---

## Support

For questions or issues:
- Check system logs in Django admin
- Review audit trail (if available)
- Contact system administrator
