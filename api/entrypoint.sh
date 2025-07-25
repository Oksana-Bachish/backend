#!/bin/sh

if [ "$DEBUG" = "True" ]; then
    echo "Running in DEBUG mode — makemigrations and migrate with --fake..."
    python manage.py makemigrations --noinput
    python manage.py migrate --noinput --fake
else
    echo "Running in production mode — only migrate and collectstatic..."
    python manage.py collectstatic --noinput
    python manage.py migrate --noinput
fi

exec "$@"