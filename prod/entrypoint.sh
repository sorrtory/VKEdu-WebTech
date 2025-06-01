#!/bin/sh
# This is the entrypoint for django container 
set -e  # Exit immediately if a command exits with a non-zero status

# Here we can wait for the database to be ready
# But I use compose's healthcheck for that

# Clean up database and prepare it
echo "Updating database"
python manage.py flush --no-input
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py fill_db 50
python manage.py update_cache

# Start the Django application
echo "Starting Django application"
exec "$@"  # Execute the command passed to the container