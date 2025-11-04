#!/bin/sh
# wait-for-db.sh

# Environment variables are passed from docker-compose.yml
# DB_HOST: postgres
# DB_PORT: 5432

set -e

host="$DB_HOST"
port="$DB_PORT"
cmd="$@"

echo "Waiting for database connection to $DB_HOST:$DB_PORT (DB: $DB_NAME)..."

# Wait loop: attempt to connect to the specific database ($DB_NAME)
until PGPASSWORD=$DB_PASSWORD psql -h "$host" -p "$port" -U "$DB_USER" -d "$DB_NAME" -c '\q'; do
  echo "Database $DB_NAME is unavailable - sleeping"
  sleep 1
done

echo "Database $DB_NAME is ready!"
# Execute the command passed to the script (e.g., python manage.py migrate ...)
exec $cmd
