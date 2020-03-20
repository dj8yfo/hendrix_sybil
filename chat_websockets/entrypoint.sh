#!/bin/bash
echo "Waiting for postgres..."

while ! nc -z $SQL_HOST $SQL_PORT; do
sleep 0.1
done
echo "PostgreSQL started"

echo "Waiting for redis..."
REDIS_HOST=redis
REDIS_PORT=6379

while ! nc -z $REDIS_HOST $REDIS_PORT; do
sleep 0.1
done
echo "redis started"

python manage.py flush --no-input
python manage.py migrate

exec "$@"
