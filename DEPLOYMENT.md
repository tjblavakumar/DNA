# Deployment Guide

This guide covers deploying the Daily News AI Assistant to production environments.

## Production Considerations

### 1. Database

**Current**: SQLite (development only)

**Production Options**:
- PostgreSQL (recommended)
- MySQL
- AWS RDS

**Migration Steps**:
```python
# In database.py, change:
engine = create_engine('sqlite:///news_assistant.db')

# To PostgreSQL:
engine = create_engine('postgresql://user:password@localhost/newsdb')

# Or MySQL:
engine = create_engine('mysql+pymysql://user:password@localhost/newsdb')
```

### 2. Background Processing

**Current**: Threading (simple, but limited)

**Production Options**:
- **Celery** with Redis/RabbitMQ (recommended)
- **AWS Lambda** for scheduled processing
- **APScheduler** for simpler deployments

**Celery Example**:
```python
# celery_app.py
from celery import Celery

celery = Celery('news_assistant', broker='redis://localhost:6379/0')

@celery.task
def fetch_news_task():
    from services import NewsService
    service = NewsService()
    return service.fetch_and_process_news()
```

### 3. Web Server

**Current**: Flask development server

**Production Options**:
- **Gunicorn** (recommended for Linux)
- **uWSGI**
- **Waitress** (Windows-friendly)

**Gunicorn Setup**:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 4. Reverse Proxy

Use **Nginx** or **Apache** as a reverse proxy:

**Nginx Configuration**:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/app/static;
    }
}
```

### 5. Environment Variables

**Never commit .env to version control!**

Use environment-specific configs:
- `.env.development`
- `.env.production`
- `.env.staging`

Or use cloud provider secrets:
- AWS Secrets Manager
- Azure Key Vault
- Google Secret Manager

### 6. Security

**Essential Security Measures**:

1. **HTTPS**: Use SSL/TLS certificates (Let's Encrypt)
2. **Authentication**: Add user login (Flask-Login)
3. **CSRF Protection**: Enable Flask-WTF
4. **Rate Limiting**: Use Flask-Limiter
5. **Input Validation**: Sanitize all user inputs
6. **AWS IAM**: Use least-privilege IAM roles

**Example - Add Authentication**:
```python
from flask_login import LoginManager, login_required

login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/')
@login_required
def dashboard():
    # ... existing code
```

### 7. Monitoring & Logging

**Logging**:
```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('app.log', maxBytes=10000000, backupCount=3)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
```

**Monitoring Tools**:
- **Sentry** for error tracking
- **Prometheus** + **Grafana** for metrics
- **AWS CloudWatch** for AWS-hosted apps
- **New Relic** or **DataDog** for APM

### 8. Performance Optimization

**Caching**:
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@app.route('/')
@cache.cached(timeout=60)
def dashboard():
    # ... existing code
```

**Database Connection Pooling**:
```python
engine = create_engine(
    'postgresql://...',
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

**CDN**: Serve static files via CloudFront or similar

## Deployment Options

### Option 1: Traditional VPS (DigitalOcean, Linode, AWS EC2)

```bash
# 1. Install dependencies
sudo apt update
sudo apt install python3.10 python3-pip nginx

# 2. Clone repository
git clone <your-repo>
cd daily-news-ai-assistant

# 3. Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
nano .env  # Add your credentials

# 5. Setup systemd service
sudo nano /etc/systemd/system/newsai.service
```

**systemd service file**:
```ini
[Unit]
Description=Daily News AI Assistant
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/app
Environment="PATH=/path/to/app/venv/bin"
ExecStart=/path/to/app/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

```bash
# 6. Start service
sudo systemctl start newsai
sudo systemctl enable newsai

# 7. Configure Nginx (see above)
sudo systemctl restart nginx
```

### Option 2: Docker

**Dockerfile**:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  redis:
    image: redis:alpine
    restart: unless-stopped
```

**Deploy**:
```bash
docker-compose up -d
```

### Option 3: AWS Elastic Beanstalk

```bash
# 1. Install EB CLI
pip install awsebcli

# 2. Initialize
eb init -p python-3.10 news-ai-assistant

# 3. Create environment
eb create news-ai-prod

# 4. Deploy
eb deploy

# 5. Open
eb open
```

### Option 4: Heroku

```bash
# 1. Create Procfile
echo "web: gunicorn app:app" > Procfile

# 2. Create runtime.txt
echo "python-3.10.12" > runtime.txt

# 3. Deploy
heroku create news-ai-assistant
git push heroku main

# 4. Set environment variables
heroku config:set AWS_ACCESS_KEY_ID=xxx
heroku config:set AWS_SECRET_ACCESS_KEY=xxx
```

## Scheduled Tasks

### Cron (Linux)

```bash
# Edit crontab
crontab -e

# Add: Run every hour
0 * * * * cd /path/to/app && /path/to/venv/bin/python -c "from services import NewsService; NewsService().fetch_and_process_news()"
```

### AWS EventBridge + Lambda

Create a Lambda function that triggers the news fetch on a schedule.

### Celery Beat

```python
from celery.schedules import crontab

celery.conf.beat_schedule = {
    'fetch-news-every-hour': {
        'task': 'fetch_news_task',
        'schedule': crontab(minute=0, hour='*/1'),
    },
}
```

## Cost Optimization

### AWS Bedrock Costs

- Amazon Nova Pro: ~$0.80 per 1M input tokens, ~$3.20 per 1M output tokens
- Typical article analysis: ~1000 input tokens, ~200 output tokens
- Cost per article: ~$0.001
- 1000 articles/day: ~$1/day or ~$30/month

**Optimization Tips**:
1. Truncate articles to 3000 chars (already implemented)
2. Cache AI results for duplicate content
3. Use lower temperature for faster responses
4. Batch process during off-peak hours
5. Consider Amazon Nova Lite for lower costs

### Infrastructure Costs

**Minimal Setup** (< $20/month):
- DigitalOcean Droplet: $6/month
- AWS Bedrock: ~$30/month (1000 articles/day)
- Domain + SSL: Free (Let's Encrypt)

**Production Setup** (< $100/month):
- AWS EC2 t3.small: ~$15/month
- AWS RDS db.t3.micro: ~$15/month
- AWS Bedrock: ~$30/month
- CloudFront CDN: ~$5/month
- Monitoring: ~$10/month

## Backup Strategy

### Database Backups

```bash
# PostgreSQL
pg_dump newsdb > backup_$(date +%Y%m%d).sql

# Automated daily backups
0 2 * * * /usr/bin/pg_dump newsdb | gzip > /backups/newsdb_$(date +\%Y\%m\%d).sql.gz
```

### AWS Backup

Use AWS Backup for automated RDS snapshots.

## Troubleshooting Production Issues

### High Memory Usage
- Reduce worker count
- Implement connection pooling
- Add memory limits to Docker

### Slow Response Times
- Enable caching
- Optimize database queries
- Use CDN for static files
- Add database indexes

### AWS Throttling
- Implement exponential backoff
- Reduce concurrent requests
- Request limit increase from AWS

### Database Locks
- Use connection pooling
- Optimize long-running queries
- Consider read replicas

## Maintenance

### Regular Tasks

**Daily**:
- Monitor error logs
- Check AWS costs
- Verify article processing

**Weekly**:
- Review and update RSS feeds
- Analyze topic performance
- Check disk space

**Monthly**:
- Update dependencies
- Review security patches
- Optimize database
- Backup verification

### Updates

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Database migrations (if using Alembic)
alembic upgrade head

# Restart service
sudo systemctl restart newsai
```

## Support & Resources

- Flask Documentation: https://flask.palletsprojects.com/
- AWS Bedrock: https://aws.amazon.com/bedrock/
- Gunicorn: https://gunicorn.org/
- Nginx: https://nginx.org/en/docs/

## Checklist Before Going Live

- [ ] Database migrated to production DB
- [ ] Environment variables secured
- [ ] HTTPS enabled
- [ ] Authentication implemented
- [ ] Rate limiting configured
- [ ] Logging and monitoring setup
- [ ] Backups automated
- [ ] Error tracking enabled
- [ ] Performance testing completed
- [ ] Security audit performed
- [ ] Documentation updated
- [ ] Disaster recovery plan documented

Good luck with your deployment! 🚀
