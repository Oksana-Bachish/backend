#!/bin/sh

mkdir -p /app/logs
touch /app/logs/django.log

echo "Ожидание запуска PostgreSQL..."
POSTGRES_PORT=${POSTGRES_PORT:-5432}
while ! nc -z "db" "$POSTGRES_PORT"; do
  echo "Ждём PostgreSQL на db:$POSTGRES_PORT..."
  sleep 0.5
done
echo "PostgreSQL запущен"

python manage.py makemigrations
python manage.py migrate
python manage.py loaddata fixtures/products/categories.json
python manage.py loaddata fixtures/products/brands.json
python manage.py loaddata fixtures/products/products.json
python manage.py loaddata fixtures/products/characteristics.json
python manage.py loaddata fixtures/products/productImage.json
exec "$@"