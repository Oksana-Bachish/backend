#!/bin/sh

if [ "$POSTGRES_DB" = "electronics_store" ]
then
    echo "Ждем postgres..."

    while ! nc -z "db" $POSTGRES_PORT; do
      sleep 0.5
    done

    echo "PostgreSQL запущен"
fi

python manage.py makemigrations
python manage.py migrate
python manage.py loaddata fixtures/products/categories.json
python manage.py loaddata fixtures/products/brands.json
python manage.py loaddata fixtures/products/products.json
python manage.py loaddata fixtures/products/characteristics.json
python manage.py loaddata fixtures/products/productImage.json
python manage.py collectstatic --noinput
exec "$@"