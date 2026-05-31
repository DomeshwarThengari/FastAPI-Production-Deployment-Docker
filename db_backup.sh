#!/bin/bash
# Backup script for PostgreSQL running in Docker
BACKUP_DIR="/home/deployer/backups"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
mkdir -p $BACKUP_DIR

# Using docker compose to execute pg_dump inside the db container
docker compose -f /path/to/your/project/docker-compose.yml exec -t db pg_dump -U jojo production_db > $BACKUP_DIR/db_backup_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -type f -name "*.sql" -mtime +7 -delete

#After this we have to make a cron job in servers system 
# Fir crontab -e run karein aur yeh line add karein (raat 2 baje backup ke liye):
# 0 2 * * * bash /home/deployer/db_backup.sh