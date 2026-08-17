# MJMS — Micro Job Management System

A Django-based local service marketplace connecting customers with workers.

## Main workflows

### Customer
Registration → Login → Browse Services → Create Request/Booking → Review Worker → Payment → Review/Complaint

### Worker
Registration → Admin Approval → Worker Dashboard → Open Requests → Apply/Accept Job → Complete Job → Earnings → Payout

### Admin
Admin Login → Dashboard → Users → Worker Approval → Services → Jobs → Payments → Complaints → Reports

## Local Wi-Fi testing

Run Django so it listens on the local network:

```powershell
python manage.py runserver 0.0.0.0:8000
```

Find your PC IPv4 address:

```powershell
ipconfig
```

Then open this on another device connected to the same Wi-Fi:

```text
http://YOUR-PC-IP:8000/
```

For example:

```text
http://192.168.0.196:8000/
```

If Windows Firewall asks for permission, allow Python on the Private network.

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Demo accounts

If the demo accounts are already present in `db.sqlite3`:

- Customer: `customer` / `Customer12345!`
- Worker: `worker` / `Worker12345!`
- Admin: `admin` / `Admin12345!`

If you need to recreate them, use the provided management command:

```powershell
python manage.py create_demo_accounts
```

## Important

The project uses Django database-backed sessions. A normal PC browser session and a phone browser session are independent, so a customer can remain logged in on the PC while a worker is logged in on the phone.

The included Wi-Fi configuration is for development/LAN testing only. For internet deployment, use HTTPS, a production WSGI/ASGI server, environment-based secrets, and a production database.
