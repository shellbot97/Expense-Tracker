#!/bin/bash
# Database backup script for SQLite expense tracker database

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DB_FILE="${PROJECT_ROOT}/expense_tracker.db"
BACKUP_DIR="${PROJECT_ROOT}/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/expense_tracker_${TIMESTAMP}.db"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Check if database exists
if [ ! -f "$DB_FILE" ]; then
    echo "Error: Database file not found at $DB_FILE"
    exit 1
fi

# Perform backup
echo "Backing up database to $BACKUP_FILE..."
sqlite3 "$DB_FILE" ".backup '$BACKUP_FILE'"

if [ $? -eq 0 ]; then
    echo "Backup completed successfully!"
    
    # Compress backup
    gzip "$BACKUP_FILE"
    echo "Backup compressed to ${BACKUP_FILE}.gz"
    
    # Keep only last 30 backups
    echo "Cleaning up old backups (keeping last 30)..."
    ls -t "${BACKUP_DIR}"/expense_tracker_*.db.gz | tail -n +31 | xargs -r rm
    
    echo "Backup process complete."
else
    echo "Error: Backup failed"
    exit 1
fi
