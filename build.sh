#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install production dependencies
pip install -r requirements.txt

# Run migrations
cd ecomm
python manage.py migrate

# Collect static files with WhiteNoise
python manage.py collectstatic --no-input

# Auto-create or ensure admin superuser if env variables exist
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser from environment variables..."
    python manage.py createsuperuser --noinput || true
fi
