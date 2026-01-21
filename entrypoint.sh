#!/bin/bash

# Wait for MongoDB to be ready
echo "Waiting for MongoDB..."
while ! nc -z mongo 27017; do
  sleep 0.1
done
echo "MongoDB started"

# Initialize the database
echo "Initializing database..."
python app/db/init_db.py

# Start the application
echo "Starting application..."
exec "$@"
