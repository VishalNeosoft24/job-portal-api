#!/bin/bash

# Exit on errors
set -e

echo "Starting startup script..."

# Step 0: Wait for the database to be ready
echo "Waiting for the database to be ready..."
until nc -z -v -w30 db 3306
do
  echo "Waiting for MySQL database connection..."
  sleep 5
done

# Step 1: Apply migrations
echo "Applying migrations..."
python manage.py migrate

# Step 2: Create superuser
echo "Creating superuser..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
username = "admin"
email = "admin@example.com"
password = "admin"
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' created successfully.")
else:
    print(f"Superuser '{username}' already exists.")
EOF

# Step 3: Start the server
echo "Starting Django server..."
# For development:
python manage.py runserver 0.0.0.0:8000

# For production (e.g., using Gunicorn):
# gunicorn your_project_name.wsgi:application --bind 0.0.0.0:8000 --workers 3
