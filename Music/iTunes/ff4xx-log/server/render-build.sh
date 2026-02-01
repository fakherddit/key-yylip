#!/bin/bash
# render-build.sh - Build script for Render deployment

echo "Installing dependencies..."
apt-get update
apt-get install -y php php-mysqli php-curl php-json

echo "Setting up database tables..."
if [ ! -z "$DB_HOST" ]; then
    mysql -h $DB_HOST -u $DB_USER -p$DB_PASS $DB_NAME < database.sql
fi

echo "Build completed successfully!"
