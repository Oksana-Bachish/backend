#!/bin/sh

if [ "$DEBUG" = "False" ]; then
    python manage.py collectstatic --noinput
fi

python manage.py migrate --noinput

exec "$@"