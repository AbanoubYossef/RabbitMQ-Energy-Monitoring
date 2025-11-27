#!/bin/bash

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "PostgreSQL is ready!"

# Wait for RabbitMQ
echo "Waiting for RabbitMQ..."
while ! nc -z $RABBITMQ_HOST $RABBITMQ_PORT; do
  sleep 0.1
done
echo "RabbitMQ is ready!"

# Run migrations
echo "Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Start RabbitMQ consumers in background
echo "Starting RabbitMQ sync consumer in background..."
python manage.py consume_sync &

echo "Starting RabbitMQ message consumer in background..."
python manage.py consume_messages &

# Start Django server
echo "Starting Django server..."
python manage.py runserver 0.0.0.0:8002
