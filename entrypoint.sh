#!/bin/bash
set -e

# Initialize the database (if MongoDB is configured and reachable)
if [ -n "$MONGODB_URI" ] || [ -n "$MONGO_URI" ]; then
  echo "Attempting to initialize database..."
  python -m app.db.init_db || echo "Warning: Could not initialize database; continuing startup..."
fi

# Start the application
echo "Starting application..."
exec "$@"
