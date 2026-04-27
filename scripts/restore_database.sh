#!/bin/bash
# Database restore script for SQLite expense tracker database

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DB_FILE="${PROJECT_ROOT}/expense_tracker.db"
BACKUP_DIR="${PROJECT_ROOT}/backups"

# Check if backup file is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file>"
    echo ""
    echo "Available backups:"
    ls -lh "$BACKUP_DIR"/expense_tracker_*.db.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Create backup of current database before restoring
if [ -f "$DB_FILE" ]; then
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    PRE_RESTORE_BACKUP="${BACKUP_DIR}/pre_restore_${TIMESTAMP}.db"
    echo "Creating safety backup of current database..."
    cp "$DB_FILE" "$PRE_RESTORE_BACKUP"
    gzip "$PRE_RESTORE_BACKUP"
    echo "Safety backup created: ${PRE_RESTORE_BACKUP}.gz"
fi

# Decompress and restore
if [[ "$BACKUP_FILE" == *.gz ]]; then
    echo "Decompressing backup..."
    TEMP_FILE="${BACKUP_FILE%.gz}"
    gunzip -c "$BACKUP_FILE" > "$TEMP_FILE"
    BACKUP_TO_RESTORE="$TEMP_FILE"
    CLEANUP_TEMP=true
else
    BACKUP_TO_RESTORE="$BACKUP_FILE"
    CLEANUP_TEMP=false
fi

# Perform restore
echo "Restoring database from $BACKUP_FILE..."
cp "$BACKUP_TO_RESTORE" "$DB_FILE"

# Cleanup temporary file
if [ "$CLEANUP_TEMP" = true ]; then
    rm "$BACKUP_TO_RESTORE"
fi

echo "Database restored successfully!"
echo "Note: You may need to restart the application."
