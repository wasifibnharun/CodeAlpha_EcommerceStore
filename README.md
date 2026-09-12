# CodeAlpha E-commerce Store

A responsive Django e-commerce MVP built for CodeAlpha Full Stack Development Task 1.

## Features

- Product catalog and detail pages
- Product categories, filtering, and search
- Registration, login, and logout
- Session-based shopping cart
- Cart quantity controls
- Authenticated checkout and order creation
- Stock validation and inventory reduction
- Customer order history
- Product and order management in Django admin
- Automated tests for the main shopping flow

## Local setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_products
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. The admin area is at `http://127.0.0.1:8000/admin/`.

## Tests

```powershell
python manage.py test
```

## Production note

Before deployment, move the secret key and environment-specific settings into environment variables, set `DEBUG = False`, configure `ALLOWED_HOSTS`, and use production-grade static file and database services.
