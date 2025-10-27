#!/bin/bash

# Memory Subsystem entrypoint script
# Handles database migrations and service startup

set -e

echo "Starting Memory Subsystem..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
while ! pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER; do
    sleep 2
done
echo "PostgreSQL is ready!"

# Wait for Milvus to be ready
echo "Waiting for Milvus..."
for i in {1..30}; do
    if python -c "from pymilvus import connections; connections.connect(host='$MILVUS_HOST', port=$MILVUS_PORT); print('Connected')"; then
        echo "Milvus is ready!"
        break
    fi
    echo "Milvus not ready yet, retrying in 2 seconds..."
    sleep 2
done

# Run database migrations
echo "Running database migrations..."
cd /app
alembic upgrade head || echo "No migrations to run or Alembic not configured"

# Start the FastAPI application
echo "Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
