#!/bin/sh

if [ "$DEBUG" = "False" ]; then
    echo "Running in production mode — only migrate and collectstatic..."
    python manage.py collectstatic --noinput
    python manage.py migrate --noinput
fi

exec "$@"