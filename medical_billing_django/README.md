# Medical Billing & Claims Management (Demo)

A portfolio/demo app with **HTML, CSS, JavaScript + Python Django + MySQL**.

## Features
- Dashboard with fictional patients, claims, and totals
- Insurance payer dropdown populated from the database
- Procedure/claim details and EOB viewing
- Claim form viewing in a modal
- Add account notes and view note history
- Update claim status using a backend POST operation
- Demo-data seeding command

> **Privacy note:** This project uses fictional demo data only. Do not enter real patient/insurance data into an unsecured portfolio demo.

## 1. Setup

Use Python 3.11+ if possible.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

## 2. Create MySQL database

Open MySQL Workbench or a MySQL shell and run:

```sql
CREATE DATABASE medical_billing
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER 'billing_user'@'localhost' IDENTIFIED BY 'change_this_password';
GRANT ALL PRIVILEGES ON medical_billing.* TO 'billing_user'@'localhost';
FLUSH PRIVILEGES;
```

Set environment variables before starting Django. Do not commit real passwords to Git.

**Windows PowerShell:**
```powershell
$env:DB_NAME="medical_billing"
$env:DB_USER="root"
$env:DB_PASSWORD="Tiruchengode"
$env:DB_HOST="127.0.0.1"
$env:DB_PORT="3306"
$env:DJANGO_SECRET_KEY="replace-with-a-long-random-secret"
```

**macOS/Linux:**
```bash
export DB_NAME=medical_billing
export DB_USER=billing_user
export DB_PASSWORD=change_this_password
export DB_HOST=127.0.0.1
export DB_PORT=3306
export DJANGO_SECRET_KEY='replace-with-a-long-random-secret'
```

## 3. Initialize and run

Run from the folder containing `manage.py`:

```bash
python manage.py makemigrations billing
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/

Admin site: http://127.0.0.1:8000/admin/

## 4. Main routes
- `/` — dashboard
- `/claim/<id>/` — claim detail JSON endpoint used by the UI
- `/eob/<id>/` — EOB detail JSON endpoint used by the UI
- `/notes/add/` — add note (POST)
- `/claim/<id>/status/` — update claim status (POST)
- `/admin/` — Django admin

## Project structure

```text
medical_billing_django/
├── manage.py
├── requirements.txt
├── README.md
├── medical_billing/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── billing/
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── admin.py
    ├── apps.py
    ├── templates/billing/dashboard.html
    ├── static/billing/styles.css
    ├── static/billing/app.js
    └── management/commands/seed_demo.py
```

## Before production
This is a learning demo, not a compliant clinical/claims system. Add proper authorization, audit trails, validation, encryption, backups, access controls, secure deployment, and any applicable healthcare privacy/compliance requirements before handling real data.
