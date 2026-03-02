#!/bin/bash

# Only wait for local MongoDB (skip when using Atlas or external URI)
if [[ "${MONGO_URI:-mongodb://localhost:27017}" == *"localhost"* ]] || \
   [[ "${MONGO_URI:-mongodb://localhost:27017}" == *"mongo:27017"* ]]; then
    echo "Waiting for local MongoDB..."
    while ! nc -z ${MONGO_HOST:-mongo} 27017; do
      sleep 0.1
    done
    echo "MongoDB started"
else
    echo "Using external MongoDB (Atlas) — skipping wait"
fi

# Initialize the database (non-fatal: Atlas may already have collections)
echo "Initializing database..."
python app/db/init_db.py || echo "DB init skipped or already initialized"

# Start the application
echo "Starting application..."
exec "$@"
