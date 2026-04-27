# Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#docker-deployment)
4. [Production Deployment](#production-deployment)
5. [Database Management](#database-management)
6. [Monitoring & Health Checks](#monitoring--health-checks)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

- Python 3.10+ (for non-Docker deployment)
- Docker & Docker Compose (for Docker deployment)
- SQLite 3.35+ (usually included with Python)
- Git

## Local Development Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd expense-tracking-system
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

Required environment variables:
- `DATABASE_URL`: SQLite database path (default: `sqlite:///./expense_tracker.db`)
- `JWT_SECRET_KEY`: Secret key for JWT tokens (generate a secure random string)
- `AI_PROVIDER`: AI provider (`ollama`, `openai`, `anthropic`, or `none`)
- `AI_MODEL`: AI model name (e.g., `llama3` for Ollama)
- `AI_API_BASE`: AI API base URL (e.g., `http://localhost:11434` for Ollama)

### 5. Run Database Migrations
```bash
alembic upgrade head
```

### 6. Start Development Server
```bash
uvicorn src.main:app --reload --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Docker Deployment

### Option 1: Docker Compose (Recommended)

#### 1. Configure Environment
```bash
cp .env.example .env
# Edit .env with your production settings
```

#### 2. Build and Start
```bash
docker-compose up -d
```

#### 3. Check Logs
```bash
docker-compose logs -f app
```

#### 4. Stop Services
```bash
docker-compose down
```

### Option 2: Docker Only

#### 1. Build Image
```bash
docker build -t expense-tracker-api .
```

#### 2. Run Container
```bash
docker run -d \
  --name expense-tracker \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e JWT_SECRET_KEY="your-secret-key" \
  -e AI_PROVIDER="ollama" \
  -e AI_MODEL="llama3" \
  -e AI_API_BASE="http://host.docker.internal:11434" \
  expense-tracker-api
```

#### 3. Check Logs
```bash
docker logs -f expense-tracker
```

## Production Deployment

### Security Considerations

1. **Generate Strong JWT Secret**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

2. **Use HTTPS**
   - Deploy behind reverse proxy (Nginx/Traefik)
   - Configure SSL/TLS certificates (Let's Encrypt recommended)

3. **Environment Variables**
   - Never commit `.env` to version control
   - Use secure secret management (e.g., HashiCorp Vault, AWS Secrets Manager)

4. **Database Security**
   - Regular backups (see Database Management section)
   - Restrict file permissions: `chmod 600 expense_tracker.db`
   - Consider encryption at rest for sensitive data

5. **CORS Configuration**
   - Update `CORS_ORIGINS` in settings to only allow your frontend domain
   - Remove wildcard origins in production

### Reverse Proxy Setup (Nginx Example)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Systemd Service (Non-Docker)

Create `/etc/systemd/system/expense-tracker.service`:

```ini
[Unit]
Description=Expense Tracker API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/expense-tracker
Environment="PATH=/opt/expense-tracker/venv/bin"
ExecStart=/opt/expense-tracker/venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable expense-tracker
sudo systemctl start expense-tracker
sudo systemctl status expense-tracker
```

## Database Management

### Backups

#### Automated Backups (Cron)
```bash
# Make backup script executable
chmod +x scripts/backup_database.sh

# Add to crontab (daily at 2 AM)
crontab -e
0 2 * * * /path/to/expense-tracking-system/scripts/backup_database.sh
```

#### Manual Backup
```bash
./scripts/backup_database.sh
```

Backups are stored in `./backups/` directory and automatically compressed.
The script keeps the last 30 backups.

### Restore

#### List Available Backups
```bash
./scripts/restore_database.sh
```

#### Restore from Backup
```bash
./scripts/restore_database.sh backups/expense_tracker_20240426_120000.db.gz
```

**Warning**: This will overwrite the current database. A safety backup is automatically created.

### Migrations

#### Create New Migration
```bash
alembic revision --autogenerate -m "Description of changes"
```

#### Apply Migrations
```bash
alembic upgrade head
```

#### Rollback Migration
```bash
alembic downgrade -1  # Go back one migration
alembic downgrade <revision>  # Go back to specific revision
```

#### Check Current Version
```bash
alembic current
```

## Monitoring & Health Checks

### Health Check Endpoint
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "environment": "production"
}
```

### Docker Health Check
```bash
docker inspect expense-tracker --format='{{.State.Health.Status}}'
```

### Application Logs

#### Docker Compose
```bash
docker-compose logs -f app
```

#### Systemd
```bash
journalctl -u expense-tracker -f
```

### Monitoring Metrics

Consider integrating:
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **Sentry**: Error tracking
- **Uptime Kuma**: Uptime monitoring

## Troubleshooting

### Database Locked Error
SQLite databases can lock under concurrent writes.

**Solution**: Enable WAL mode (already configured):
```python
# In database.py
engine.execute("PRAGMA journal_mode=WAL")
```

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000
# Kill process
kill -9 <PID>
```

### Permission Denied Errors
```bash
# Fix database permissions
chmod 644 expense_tracker.db
chown <user>:<group> expense_tracker.db

# Fix script permissions
chmod +x scripts/*.sh
```

### Docker Cannot Connect to Ollama
If using Ollama on host machine:
- Use `host.docker.internal` instead of `localhost`
- On Linux, add `--add-host=host.docker.internal:host-gateway` to docker run

### Migration Errors
```bash
# Reset migrations (WARNING: destroys data)
rm -rf migrations/
alembic init migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Tests Failing
```bash
# Install test dependencies
pip install -r requirements.txt

# Run tests with verbose output
pytest -v --tb=short

# Check coverage
pytest --cov=src --cov-report=html
```

## Performance Optimization

### Database Optimization
```sql
-- Analyze database
sqlite3 expense_tracker.db "ANALYZE;"

-- Vacuum to reclaim space
sqlite3 expense_tracker.db "VACUUM;"
```

### Application Tuning
- Increase Uvicorn workers: `uvicorn src.main:app --workers 4`
- Enable HTTP/2: Use behind reverse proxy with HTTP/2 support
- Add caching layer (Redis) for frequently accessed data

## Scaling Considerations

SQLite is designed for single-user applications. For multi-user scenarios:

1. **Read-Heavy Workloads**: SQLite with WAL mode handles concurrent reads well
2. **Write-Heavy Workloads**: Consider PostgreSQL or MySQL
3. **High Concurrency**: Migrate to client-server database

## Backup Strategy

Recommended backup schedule:
- **Hourly**: Keep last 24 hours
- **Daily**: Keep last 30 days
- **Weekly**: Keep last 12 weeks
- **Monthly**: Keep last 12 months

Store backups:
- Local storage (for quick recovery)
- Remote storage (cloud backup for disaster recovery)

## Support

For issues and questions:
- Check documentation: `/docs` endpoint
- Review logs for error details
- Check GitHub issues
- Contact support team

---

**Last Updated**: 2026-04-26
