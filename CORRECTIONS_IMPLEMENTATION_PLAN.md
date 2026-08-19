# Micro-Job Management System - Corrections Implementation Plan

## Overview
This document outlines all the corrections needed to implement your requested features.

---

## Correction 1: Service with Worker Ratings
**Requirement:** When a customer selects a service, show services with worker ratings

**Current Status:**
- Review/Rating system exists ✓
- Worker ratings can be calculated from reviews ✓

**Changes Needed:**
1. Modify Service views to display worker ratings
2. Modify Service detail template to show worker profiles with ratings
3. Add average rating calculation to Service model

**Files to Update:**
- `services/models.py` - Add average_rating property
- `services/views.py` - Pass worker ratings to template
- `templates/services/service_detail.html` - Display ratings

---

## Correction 2: Every Worker Has a Profession
**Requirement:** Every worker will have a profession field

**Current Status:**
- Profession field exists in WorkerProfile ✓
- Field is optional (blank=True) - NEEDS FIX

**Changes Needed:**
1. Make profession field REQUIRED (blank=False, null=False)
2. Update worker registration forms to make profession mandatory
3. Update admin to display profession in list view

**Files to Update:**
- `workers/models.py` - Change profession field (blank=False)
- `accounts/forms.py` - Make profession required in registration
- `workers/admin.py` - Display profession field

---

## Correction 3: Admin Can Create New Services
**Requirement:** Admin can make new services

**Current Status:**
- Service model exists but uses SERVICE_CHOICES (hardcoded)
- Need to link Services to Categories

**Changes Needed:**
1. Modify Service model to use ForeignKey to Category instead of choices
2. Create migration to migrate existing service data
3. Update Service admin interface
4. Create Service creation form for admin

**Files to Update:**
- `services/models.py` - Update Service model
- `services/admin.py` - Update admin interface
- Create migration file
- `services/forms.py` - Create service form

---

## Correction 4: Worker Can Create Profile for Services
**Requirement:** Worker can make profile for services

**Current Status:**
- WorkerProfile has ManyToMany relationship with Category ✓
- Workers can select multiple categories ✓

**Changes Needed:**
1. Update worker profile form to allow selecting multiple categories/services
2. Create/update template for worker to edit their service profile
3. Add view to handle service selection

**Files to Update:**
- `workers/forms.py` - Update profile form
- `workers/views.py` - Add profile management view
- `templates/workers/profile_edit.html` - Add category selection

---

## Correction 5: Admin Approval Workflow
**Requirement:** Admin approves workers; without approval, workers can register but cannot take services

**Current Status:**
- worker_status field exists (PENDING/APPROVED/REJECTED) ✓
- Approval check exists in JobApplication ✓

**Changes Needed:**
1. Ensure registration creates PENDING status
2. Add admin interface to approve/reject workers
3. Add notification when worker is approved/rejected
4. Show approval status in worker profile
5. Prevent PENDING workers from applying to jobs

**Files to Update:**
- `accounts/admin.py` - Add approval interface
- `accounts/views.py` - Handle approval/rejection
- `workers/admin.py` - Display worker status
- `notifications/models.py` - Add approval notifications
- `templates/workers/profile.html` - Show approval status

---

## Correction 6: Customer Can Select Services and View Details
**Requirement:** Customer can select services with details, worker ratings, and worker profiles

**Current Status:**
- Services exist ✓
- Worker profiles exist ✓
- Ratings exist ✓

**Changes Needed:**
1. Update service list/detail view to show workers
2. Display worker ratings prominently
3. Link to worker profile from service detail
4. Add worker portfolio/skills to worker profile view

**Files to Update:**
- `services/views.py` - Add worker data to context
- `templates/services/service_detail.html` - Display workers and ratings
- `templates/workers/profile_view.html` - Create worker profile view

---

## Correction 7: Job Requests Go Only to Matching Workers
**Requirement:** Service requests go only to workers with matching category

**Current Status:**
- JobApplication.clean() validates worker matches job category ✓
- Filtering partially implemented

**Changes Needed:**
1. Ensure ServiceRequest filtering shows only eligible workers
2. Update ServiceRequest admin to show eligible workers count
3. Add validation that prevents wrong workers from seeing requests

**Files to Update:**
- `bookings/views.py` - Filter available jobs by category
- `bookings/admin.py` - Add eligible workers count
- `templates/workers/available_jobs.html` - Show only matching jobs

---

## Correction 8: Customer Provides Job Details
**Requirement:** Customer provides address, time, date, price range, description

**Current Status:**
- ServiceRequest model has most fields ✓
- Need to verify all fields exist

**Changes Needed:**
1. Verify ServiceRequest has all required fields
2. Update service request form
3. Ensure fields are properly displayed

**Fields Needed:**
- address ✓
- scheduled_date ✓
- scheduled_time ✓
- budget/price_range ✓
- description ✓

**Files to Update:**
- `bookings/forms.py` - ServiceRequestForm validation
- `bookings/models.py` - Verify ServiceRequest model
- `templates/bookings/service_request_create.html` - Form layout

---

## Correction 9: Worker Sees Job Requests with Conflict Detection
**Requirement:** Worker can accept jobs; system prevents conflicts; customer sees worker unavailability

**Current Status:**
- Job model has conflict detection in clean() method ✓
- JobApplication allows worker to apply ✓

**Changes Needed:**
1. Enhance conflict detection to include time ranges
2. Add UI notification for conflicts
3. Show worker availability status to customer
4. Create notification when worker is unavailable

**Files to Update:**
- `bookings/models.py` - Enhance Job.clean() for time conflicts
- `bookings/views.py` - Handle conflict detection
- `bookings/admin.py` - Display conflict status
- `notifications/models.py` - Add conflict notification type
- `templates/bookings/job_detail.html` - Show availability status

---

## Correction 10: Payment After Job Completion
**Requirement:** Customer pays fixed price after job completion

**Current Status:**
- Payment system exists ✓
- Payment flow exists ✓

**Changes Needed:**
1. Ensure payment is triggered after job completion
2. Set fixed price from Job model
3. Add payment confirmation workflow
4. Update notifications for payment status

**Files to Update:**
- `payments/views.py` - Payment flow
- `bookings/views.py` - Trigger payment after completion
- `templates/payments/payment.html` - Payment interface
- `notifications/models.py` - Add payment notifications

---

## Implementation Priority

### Phase 1 (Critical - Core Structure)
1. Service model refactoring (Service → Category + ForeignKey)
2. Profession field requirement
3. Worker approval workflow verification

### Phase 2 (Important - User Workflows)
4. Admin service creation interface
5. Worker service profile management
6. Job conflict detection enhancement

### Phase 3 (Enhancement - UI/UX)
7. Worker ratings display
8. Customer service selection with worker info
9. Availability status display
10. Notifications system

---

## Database Migration Strategy

1. Create Category instances for existing services
2. Create migration to add category ForeignKey to Service
3. Migrate existing service data to new category structure
4. Remove SERVICE_CHOICES from Service model

---

## Testing Checklist

- [ ] Admin can create new services
- [ ] Worker profession is required and displayed
- [ ] Worker must be approved before accepting jobs
- [ ] Service request shows only eligible workers (category match)
- [ ] Job prevents worker from accepting overlapping jobs
- [ ] Customer is notified when worker is unavailable
- [ ] Worker sees rating prominently in service details
- [ ] Payment is triggered and fixed after job completion
- [ ] All notifications are sent correctly
- [ ] Admin approval workflow works end-to-end

---

## Files Summary

**Models to Update:**
- `services/models.py`
- `workers/models.py`
- `bookings/models.py`
- `notifications/models.py`

**Views to Update:**
- `services/views.py`
- `workers/views.py`
- `bookings/views.py`
- `accounts/views.py`

**Admin to Update:**
- `services/admin.py`
- `workers/admin.py`
- `accounts/admin.py`
- `bookings/admin.py`

**Templates to Update:**
- `services/service_detail.html`
- `services/service_list.html`
- `workers/profile.html`
- `bookings/service_request_detail.html`
- `bookings/job_detail.html`
- Multiple others

**Forms to Create/Update:**
- `services/forms.py` - ServiceForm
- `workers/forms.py` - WorkerProfileForm
- `bookings/forms.py` - All forms

