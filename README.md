# CodeAlpha E-commerce Store

A responsive Django e-commerce MVP built for CodeAlpha Full Stack Development Task 1.

## Features

- Product catalog and detail pages
- Product categories, filtering, and search
- Uploaded product images with remote URL fallback
- Registration, login, and logout
- Session-based shopping cart
- Cart quantity controls
- Authenticated checkout and order creation
- Stock validation and inventory reduction
- Customer order history
- Product and order management in Django admin
- Automated tests for the main shopping flow
- Environment-based production settings and a health endpoint
- Docker deployment configuration with Gunicorn and WhiteNoise

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

## Product images

Open the Django admin, edit a product, and choose a file in the **Image** field. An uploaded image takes priority over the optional remote **Image URL**.

Uploaded media is stored in `media/` locally and is intentionally excluded from Git. A production host must provide persistent storage for this directory or use an object-storage backend.

## Environment settings

Copy `.env.example` values into your deployment platform's environment configuration. Django reads these variables directly from the process environment; the `.env` file is not loaded automatically.

Required in production:

- `DJANGO_DEBUG=false`
- `DJANGO_SECRET_KEY` set to a long, private random value
- `DJANGO_ALLOWED_HOSTS` set to the deployed hostname
- `DJANGO_CSRF_TRUSTED_ORIGINS` set to the full HTTPS origin

Keep `DJANGO_SECURE_HSTS_SECONDS=0` until HTTPS is confirmed. Increase it only after verifying the domain works exclusively over HTTPS.

## Docker deployment

Build and run locally:

```powershell
docker build -t codealpha-store .
docker run --rm -p 8000:8000 `
  -e DJANGO_DEBUG=false `
  -e DJANGO_SECRET_KEY=replace-this-value `
  -e DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1 `
  -e DJANGO_SECURE_SSL_REDIRECT=false `
  codealpha-store
```

The container applies migrations, collects static assets, and starts Gunicorn. The health endpoint is `/health/`.

## Free Render deployment

Create the resources manually in the Render dashboard to remain on the free Hobby plan:

1. Create a free PostgreSQL database named `codealpha-ecommerce-db` in Singapore.
2. Create a free Docker web service from this repository's `main` branch, also in Singapore.
3. Set `DATABASE_URL` to the database's internal URL.
4. Generate `DJANGO_SECRET_KEY`, then set `DJANGO_DEBUG=false`, `DJANGO_SECURE_SSL_REDIRECT=true`, and `DJANGO_SECURE_HSTS_SECONDS=3600`.
5. Set the health check path to `/health/` and create the web service.

The container automatically applies migrations, collects static files, and loads demo products only when the catalog is empty.

Free Render web services have an ephemeral filesystem, so admin-uploaded product images do not survive restarts. The seeded catalog uses remote image URLs and remains fully visible. Use object storage or a paid persistent disk before relying on uploaded images in a long-lived deployment.

Free Render PostgreSQL databases expire after 30 days. Upgrade the database or move to another persistent PostgreSQL provider before that deadline if the demo must remain online longer.

## Production checklist

- Run `python manage.py check --deploy` with production environment variables.
- Use persistent storage for SQLite and uploaded media, or replace them with managed database and object-storage services.
- Back up the database and media directory.
- Do not commit `.env`, `db.sqlite3`, or uploaded media.
