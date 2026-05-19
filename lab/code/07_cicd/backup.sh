#!/usr/bin/env bash
# Backup agent memory JSON as CI artifact
set -euo pipefail

MEMORY_DIR="${1:-lab/code/03_memory/data}"
BACKUP_DIR="${2:-.github/artifacts/memory-backup}"

mkdir -p "$BACKUP_DIR"
if [ -d "$MEMORY_DIR" ]; then
    cp -r "$MEMORY_DIR"/*.json "$BACKUP_DIR/" 2>/dev/null || true
    echo "Memory backed up to $BACKUP_DIR"
else
    echo "No memory data found at $MEMORY_DIR"
fi
