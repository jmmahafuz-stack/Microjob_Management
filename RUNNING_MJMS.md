# Running the corrected MJMS project

## 1. Open the project

Extract the ZIP and open the **Micro-Job** folder in VS Code. It is the folder containing `manage.py`.

## 2. Create and activate the virtual environment

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 3. Install dependencies

```powershell
pip install -r requirements.txt
```

## 4. Apply migrations

```powershell
python manage.py migrate
```

## 5. Start the website

```powershell
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

### Wi-Fi / phone testing

```powershell
python manage.py runserver 0.0.0.0:8000
```

Find your PC IP with `ipconfig`, then open:

```text
http://YOUR-PC-IP:8000/
```

Allow Python through Windows Firewall on the Private network if Windows asks.

## Demo accounts

- Customer: `customer` / `Customer12345!`
- Worker: `worker` / `Worker12345!`
- Admin: `admin` / `Admin12345!`

If needed, recreate demo users with:

```powershell
python manage.py create_demo_accounts
```

## What was redesigned

- Complete responsive product-style visual layer across the existing templates.
- Modern marketplace home page with stronger hero, category navigation, feature cards and CTAs.
- Consistent navigation, buttons, forms, cards, tables, status badges and dashboard cards.
- Mobile navigation and responsive grids/tables.
- Existing customer, worker, admin, booking, job, payment, review, complaint and notification workflows were kept intact.
- Added `run_mjms.bat` for a simple Windows startup flow.

## Important

This remains a development Django application. For production deployment, move secrets to environment variables, use HTTPS, configure production hosts, and use a production database/server.
