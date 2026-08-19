# MJMS — Micro Job Management System

A full-stack **Micro Job Management System (MJMS)** built with **Django** that connects customers with service providers/workers through a structured service marketplace.

The platform allows customers to discover services, create service requests, receive worker applications, select workers, track jobs, make payments, submit reviews, and raise complaints. Workers can create profiles, get verified by administrators, browse suitable jobs, submit applications, manage assigned work, track earnings, and request payouts.

Administrators have centralized control over users, workers, services, jobs, payments, payouts, complaints, and system reports.

---

## 📌 Overview

MJMS is designed as a role-based service marketplace with three primary user roles:

* **Customer** — Finds services and hires workers.
* **Worker** — Provides services and earns money from completed jobs.
* **Administrator** — Manages and monitors the entire platform.

The system follows a structured workflow from service discovery and job requests to worker assignment, job completion, payment verification, worker earnings, and payout.

---

## ✨ Key Features

### 👤 Customer Features

* Customer registration and authentication
* Customer profile management
* Browse available services
* Browse services by category
* View detailed service information
* Create service requests
* Specify:

  * Service
  * Job title
  * Description
  * Location
  * Address
  * Preferred date
  * Preferred time
  * Budget range
* View submitted service requests
* Receive applications from workers
* Review worker applications
* Select a suitable worker
* Track job status
* Communicate through job/booking messages
* View booking and job history
* Submit payments
* View payment history
* Review and rate workers
* Submit complaints
* Receive system notifications

---

### 🧑‍🔧 Worker Features

* Worker registration
* Worker profile creation
* Worker verification workflow
* Admin approval/rejection
* Professional/service category information
* Worker profile management
* Browse available job requests
* Apply for suitable jobs
* Submit:

  * Proposed price
  * Estimated duration
  * Proposal message
  * Starting date
  * Schedule agreement
* Track application status
* View assigned jobs
* Update job progress
* Communicate with customers
* View completed jobs
* View ratings and reviews
* View earnings
* Earnings breakdown
* Request payouts
* Select payout methods
* Track payout request status
* Receive payment and job notifications

---

### 🛠️ Service Management

The platform supports structured service management through categories and individual services.

Each service can contain:

* Service name
* Category
* Description
* Price
* Service image
* Estimated duration
* Location
* Featured status
* Availability status
* Creation/update timestamps

Service categories can also contain:

* Category name
* Description
* Icon
* Image
* Active/inactive status

---

### 📋 Job & Service Request Workflow

MJMS provides a structured workflow instead of simply connecting customers and workers.

```text
Customer
   │
   ▼
Create Service Request
   │
   ▼
Workers Browse Available Requests
   │
   ▼
Workers Submit Applications
   │
   ▼
Customer Reviews Applications
   │
   ▼
Customer Selects Worker
   │
   ▼
Job Created
   │
   ▼
Worker Performs Job
   │
   ▼
Job Completed
   │
   ▼
Customer Makes Payment
   │
   ▼
Payment Verification
   │
   ▼
Worker Earnings Updated
   │
   ▼
Worker Requests Payout
   │
   ▼
Admin Processes Payout
```

### Job Statuses

The system supports job states such as:

* Confirmed
* In Progress
* Completed
* Cancelled

Service requests can progress through:

* Open
* Reviewing
* Assigned
* In Progress
* Completed
* Cancelled

---

## 💳 Payment & Payout System

MJMS includes a payment management system designed to track customer payments and worker earnings.

### Payment Features

* Payment creation
* Multiple payment methods
* Transaction ID tracking
* Payment status tracking
* Payment receipt upload
* Payment verification
* Payment/refund tracking
* Platform commission calculation
* Worker earnings calculation
* Payment history
* Payment verification notifications

### Supported Payment Methods

* Cash
* bKash
* Nagad
* Mobile Banking
* Card
* Digital Wallet

> Payment gateway/API integration depends on the configured deployment environment. The project includes payment verification and gateway-related fields for integration.

### Platform Commission

The system automatically calculates the platform commission.

```text
Customer Payment
       │
       ├── Platform Commission
       │
       └── Worker Earnings
```

For example, with a 10% commission:

```text
Customer Payment = ৳1,000

Platform Commission = ৳100
Worker Earnings     = ৳900
```

The commission rate is configurable through the payment model.

---

## 💰 Worker Earnings & Payouts

Workers can track different stages of their earnings:

* Pending earnings
* Available earnings
* Withdrawn earnings
* Total earnings

Workers can submit payout requests using supported methods such as:

* Bank Account
* bKash
* Nagad
* Rocket

Administrators can review payout requests and:

* Approve
* Reject
* Process
* Add administrative notes

---

## ⭐ Reviews & Ratings

After completing a job, customers can review workers.

The review system supports:

* Star ratings
* Written comments
* Customer-to-worker reviews
* Worker rating calculation
* Review history

Worker profiles can display performance information such as:

* Average rating
* Completed jobs
* Completion rate
* Verification status
* Worker badge

---

## 🚨 Complaint Management

Customers can submit complaints related to their service experience.

Complaint features include:

* Complaint subject
* Complaint description
* Optional booking reference
* Complaint status
* Administrator response
* Complaint history

Complaint statuses include:

```text
Pending
   ↓
Processing
   ↓
Resolved
```

---

## 🔔 Notification System

MJMS includes an internal notification system for important platform events.

Notifications can be generated for events including:

* Worker applications
* Application acceptance/rejection
* Job completion
* Job cancellation
* Payment submission
* Payment verification
* Worker approval/rejection
* Worker profile updates
* Payment availability
* General system messages

Users can view notifications and mark them as read.

---

## 👨‍💼 Administrator Features

The administrator has centralized management capabilities through the Django admin and custom dashboard.

### Admin Dashboard

Administrators can manage and monitor:

* Users
* Customers
* Workers
* Worker verification
* Services
* Service categories
* Jobs
* Bookings
* Payments
* Payout requests
* Complaints
* Reviews
* Reports
* Transactions
* Worker earnings

### Worker Verification

New workers can go through an administrative verification process.

```text
Worker Registration
        │
        ▼
Worker Profile
        │
        ▼
Admin Review
     ┌──┴──┐
     ▼     ▼
 Approved  Rejected
     │
     ▼
Can Apply for Jobs
```

Only approved and eligible workers can apply for jobs.

---

## 🏗️ Project Architecture

The project follows a modular Django application architecture.

```text
Micro-Job/
│
├── accounts/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
│
├── services/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── management/
│
├── bookings/
│   ├── models.py
│   ├── views.py
│   └── urls.py
│
├── workers/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
│
├── payments/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── payment_service.py
│   └── report_generator.py
│
├── reviews/
│   ├── models.py
│   ├── views.py
│   └── forms.py
│
├── complaints/
│   ├── models.py
│   ├── views.py
│   └── forms.py
│
├── notifications/
│   ├── models.py
│   ├── views.py
│   └── utils.py
│
├── dashboard/
│   ├── views.py
│   ├── admin_views.py
│   └── urls.py
│
├── core/
│   ├── views.py
│   └── urls.py
│
├── mjms/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── templates/
│
├── static/
│
├── media/
│
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🧩 Django Applications

| Application     | Responsibility                                    |
| --------------- | ------------------------------------------------- |
| `accounts`      | User authentication, roles and profiles           |
| `services`      | Services and service categories                   |
| `bookings`      | Bookings, service requests, applications and jobs |
| `workers`       | Worker profiles, verification and earnings        |
| `payments`      | Payments, commissions and payouts                 |
| `reviews`       | Worker reviews and ratings                        |
| `complaints`    | Customer complaints and admin responses           |
| `notifications` | User notifications                                |
| `dashboard`     | Admin and user dashboards                         |
| `core`          | Home and core website functionality               |

---

## 🛠️ Technology Stack

### Backend

* **Python**
* **Django 5.2**
* Django Authentication
* Django ORM
* Django Admin
* Django REST Framework
* Simple JWT

### Database

The project is configured for:

* SQLite for local development
* MySQL/PostgreSQL support through the installed database packages

### Frontend

* HTML5
* CSS3
* JavaScript
* Django Templates

### Media & Static Files

* Pillow
* Django Static Files
* WhiteNoise

### Additional Technologies

* Django CORS Headers
* Python Dotenv
* REST APIs
* JWT Authentication support

---

## 📦 Requirements

The project uses Python dependencies defined in:

```text
requirements.txt
```

Important packages include:

```text
Django==5.2.15
djangorestframework==3.17.1
djangorestframework_simplejwt==5.5.1
Pillow==12.2.0
django-cors-headers==4.9.0
whitenoise==6.12.0
python-dotenv==1.2.2
```

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/jmmahafuz-stack/Microjob_Management.git
cd Microjob_Management
```

---

### 2. Create a Virtual Environment

#### Windows PowerShell

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

#### Windows CMD

```cmd
python -m venv .venv
.venv\Scripts\activate
```

#### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Apply Database Migrations

```bash
python manage.py migrate
```

---

### 5. Create a Superuser

```bash
python manage.py createsuperuser
```

Follow the terminal instructions to create the administrator account.

---

### 6. Start the Development Server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

## 🌐 Local Network / Wi-Fi Testing

To access the application from another device on the same Wi-Fi network:

```bash
python manage.py runserver 0.0.0.0:8000
```

Find your computer's local IP address:

```powershell
ipconfig
```

Then access:

```text
http://YOUR-PC-IP:8000/
```

For example:

```text
http://192.168.0.196:8000/
```

If Windows Firewall requests permission, allow Python/Django on the appropriate private network.

> The Wi-Fi configuration is intended for development and local testing, not production deployment.

---

## 👥 User Roles

### Customer

Customers can:

```text
Register
   ↓
Login
   ↓
Browse Services
   ↓
Create Service Request
   ↓
Receive Worker Applications
   ↓
Select Worker
   ↓
Track Job
   ↓
Make Payment
   ↓
Review Worker
```

### Worker

Workers can:

```text
Register
   ↓
Create Worker Profile
   ↓
Admin Verification
   ↓
Browse Jobs
   ↓
Apply for Jobs
   ↓
Get Selected
   ↓
Complete Job
   ↓
Receive Earnings
   ↓
Request Payout
```

### Administrator

Administrators can:

```text
Admin Login
   ↓
Dashboard
   ├── Users
   ├── Workers
   ├── Services
   ├── Jobs
   ├── Payments
   ├── Payouts
   ├── Complaints
   └── Reports
```

---

## 🗃️ Database

The default development configuration uses SQLite:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

For production, a managed database such as **PostgreSQL** or **MySQL** is recommended.

### Important

The local `db.sqlite3` database should generally **not be committed to GitHub** for a production project.

Instead:

* Keep database credentials in environment variables.
* Run migrations on the deployment server.
* Use a production database.
* Never commit sensitive production data.

---

## 🔐 Security Considerations

Before deploying the project publicly, configure production security settings.

Recommended settings include:

```text
DEBUG=False
```

Use environment variables for:

* Django `SECRET_KEY`
* Database credentials
* API keys
* Payment gateway credentials
* Email credentials
* Other sensitive configuration

Production deployment should also use:

* HTTPS
* Secure cookies
* CSRF protection
* Allowed hosts configuration
* Production WSGI/ASGI server
* Production database
* Proper static file handling
* Proper media file storage

Never expose secret keys or payment credentials in the Git repository.

---

## 🧪 Testing

The repository contains multiple test and diagnostic scripts covering areas such as:

* Authentication
* Job workflow
* Job completion
* Job messaging
* Payment flow
* Redirects
* Worker job visibility
* General system functionality

Django tests can be executed with:

```bash
python manage.py test
```

Additional project-specific test scripts are also available in the repository.

---

## 📁 Static & Media Files

Static resources are stored in:

```text
static/
```

Uploaded media files are stored in:

```text
media/
```

Examples include:

* Service images
* Category images
* Worker profile pictures
* Payment receipts

For production, media files should preferably use reliable persistent storage rather than relying on the local filesystem.

---

## 🔄 Development Workflow

A typical development workflow is:

```bash
git pull origin main
```

Make your changes, then:

```bash
git status
git add .
git commit -m "Describe your changes"
git push origin main
```

Before pushing major changes, it is recommended to run:

```bash
python manage.py check
python manage.py test
```

---

## 📌 Project Status

The project currently contains the core components required for a functional micro-job/service marketplace, including:

* Role-based user management
* Service marketplace
* Worker verification
* Service request workflow
* Worker job applications
* Job management
* Messaging
* Payment management
* Platform commission calculation
* Worker earnings
* Payout requests
* Reviews and ratings
* Complaint management
* Notifications
* Administrative dashboard

Further production hardening, deployment configuration, external payment gateway integration, and infrastructure configuration may be required before operating the system as a public production service.

---

## 🔮 Future Improvements

Potential future enhancements include:

* Real-time chat using WebSockets
* Real-time notifications
* Production payment gateway integration
* Advanced service search and filtering
* Location-based worker matching
* Worker availability calendar
* Automated worker recommendation
* Email/SMS notifications
* Advanced analytics
* REST API expansion
* Mobile application
* Cloud media storage
* PostgreSQL production deployment
* Automated CI/CD pipeline
* Docker containerization
* Automated security and code-quality checks

---

## 🤝 Contributing

Contributions are welcome.

To contribute:

1. Fork the repository.
2. Create a feature branch.

```bash
git checkout -b feature/your-feature
```

3. Make your changes.
4. Test the application.
5. Commit your changes.

```bash
git commit -m "Add your feature"
```

6. Push the branch.

```bash
git push origin feature/your-feature
```

7. Open a Pull Request.

---

## 📄 License

This project currently does not specify a license.

If you intend to distribute or allow others to reuse the project, add an appropriate license such as MIT, Apache-2.0, or another license that matches your requirements.

---

## 👨‍💻 Author

**Md Mahafuz Islam**

GitHub: [@jmmahafuz-stack](https://github.com/jmmahafuz-stack)

---

## ⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub.

---

### MJMS

**A structured platform for connecting customers with skilled workers and managing the complete service lifecycle — from request to completion, payment, review, and payout.**

