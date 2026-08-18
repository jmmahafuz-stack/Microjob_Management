# Requested Workflow Implemented

1. Service pages show approved workers related to the service/category and their profile/rating data.
2. WorkerProfile now has a `profession` field and can also select service categories/services.
3. Admin service management remains available through Django admin and the existing service create/edit pages.
4. Workers can create/edit their professional profile. Verification approval is admin-controlled.
5. Workers may register while pending, but pending/blocked workers cannot browse/take/apply for jobs.
6. Customer service requests contain the admin-created service, service details, address, date, time range, budget range and job description.
7. Worker job visibility/application is filtered by the worker's registered service, category or profession.
8. Job applications require an admin-approved worker and matching profession/category.
9. The Job model checks for overlapping scheduled jobs for the same worker and prevents double assignment. The worker acceptance flow also requires approval.
10. After the worker completes the job, the existing payment workflow can be used by the customer.

## Important setup
Run migrations after installing dependencies:

    python manage.py migrate

Then create/manage service categories and services in the admin panel. Approve a worker by setting the worker account's `worker_status` to `APPROVED` and, if used, the WorkerProfile `verification_status` to `Approved`.
