#!/bin/bash

source /root/backend/backup.config

if [ -z "$BACKUP_DIR" ] || [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_DB" ] || [ -z "$CONTAINER_NAME" ]; then
    echo "Ошибка: Не все переменные окружения настроены!"
    exit 1
fi

mkdir -p "$BACKUP_DIR"

CURRENT_DATE=$(date +%Y-%m-%d)

docker exec "$CONTAINER_NAME" pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "$BACKUP_DIR/backup-$CURRENT_DATE.sql.gz"

find "$BACKUP_DIR" -type f -mtime +3 -delete

echo "Бэкап успешно создан за дату: $CURRENT_DATE"
