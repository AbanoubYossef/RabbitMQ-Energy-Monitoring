#!/bin/sh

echo "Waiting for PostgreSQL..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
  sleep 1
done
echo "PostgreSQL is ready!"

echo "Waiting for RabbitMQ..."
until python -c "import pika; pika.BlockingConnection(pika.ConnectionParameters('$RABBITMQ_HOST', $RABBITMQ_PORT, '/', pika.PlainCredentials('$RABBITMQ_USER', '$RABBITMQ_PASS')))" 2>/dev/null; do
  echo "RabbitMQ is unavailable - sleeping"
  sleep 2
done
echo "RabbitMQ is ready!"

echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Starting RabbitMQ consumers in background..."
python manage.py consume_messages &
python manage.py consume_sync &

echo "Starting Django server..."
python manage.py runserver 0.0.0.0:8003
