# 🚀 DEPLOYMENT & MAINTENANCE GUIDE

## 🎯 TỔNG QUAN

Tài liệu này cung cấp hướng dẫn chi tiết để deploy và maintain hệ thống Stock Tracking Data trong môi trường production, bao gồm cả local development và cloud deployment.

## 🏗️ DEPLOYMENT ARCHITECTURE

### **📊 System Components**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   API Gateway   │    │   Monitoring    │
│   (Nginx)       │    │   (FastAPI)     │    │   (Prometheus)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Main API      │    │   SSI Proxy API │    │   Automation    │
│   (Port 8000)   │    │   (Port 8001)   │    │   Service       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │   TimescaleDB   │    │   Redis Cache   │
│   (Port 5434)   │    │   Extension     │    │   (Port 6379)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **🔧 Technology Stack**
- **Containerization**: Docker + Docker Compose
- **Orchestration**: Docker Swarm (optional)
- **Load Balancing**: Nginx
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack (optional)
- **Backup**: pg_dump + S3 (optional)

## 🚀 LOCAL DEVELOPMENT DEPLOYMENT

### **📋 Prerequisites**
```bash
# Required software
- Docker 20.10+
- Docker Compose 2.0+
- Git
- curl (for testing)
- jq (for JSON processing)

# System requirements
- RAM: 4GB minimum, 8GB recommended
- Disk: 10GB free space
- CPU: 2 cores minimum
```

### **🔧 Step-by-Step Deployment**

#### **1. Clone Repository**
```bash
git clone <repository-url>
cd tracking_data
```

#### **2. Environment Setup**
```bash
# Create environment file
cat > .env << EOF
# Database Configuration
POSTGRES_DB=tracking_data
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
POSTGRES_HOST=tracking_data_db
POSTGRES_PORT=5432

# Redis Configuration
REDIS_HOST=tracking_data_redis
REDIS_PORT=6379

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
SSI_PROXY_PORT=8001

# SSI API Configuration
SSI_BASE_URL=https://iboard-api.ssi.com.vn
SSI_QUERY_URL=https://iboard-query.ssi.com.vn

# Automation Configuration
AUTOMATION_MAX_SYMBOLS=100
AUTOMATION_REQUEST_TIMEOUT=30
AUTOMATION_RATE_LIMIT_DELAY=0.1
EOF
```

#### **3. Start System**
```bash
# Make scripts executable
chmod +x ssi_system_manager.sh
chmod +x automation_manager.sh
chmod +x pipeline_manager_extended.sh

# Start all services
./ssi_system_manager.sh start

# Verify system status
./ssi_system_manager.sh status
```

#### **4. Initialize Data**
```bash
# Run automation for VN100
python automation/automation_vn100_direct.py --max-symbols 100

# Verify data
docker exec tracking_data_db psql -U postgres -d tracking_data -c "SELECT COUNT(*) FROM stock_statistics;"
```

## ☁️ PRODUCTION DEPLOYMENT

### **📋 Production Prerequisites**
```bash
# Server requirements
- OS: Ubuntu 20.04+ or CentOS 8+
- RAM: 16GB minimum, 32GB recommended
- Disk: 100GB SSD minimum
- CPU: 4 cores minimum, 8 cores recommended
- Network: Stable internet connection

# Security requirements
- Firewall configured
- SSL certificates
- VPN access (if needed)
- Backup storage
```

### **🔧 Production Setup**

#### **1. Server Preparation**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install additional tools
sudo apt install -y nginx certbot python3-certbot-nginx htop iotop
```

#### **2. Security Configuration**
```bash
# Configure firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Create SSL certificates
sudo certbot --nginx -d your-domain.com

# Configure Nginx
sudo cat > /etc/nginx/sites-available/stock-tracking << EOF
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /ssi/ {
        proxy_pass http://localhost:8001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/stock-tracking /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### **3. Production Docker Compose**
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    restart: unless-stopped
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G

  ssi-proxy:
    build: .
    ports:
      - "8001:8001"
    environment:
      - ENVIRONMENT=production
    restart: unless-stopped
    deploy:
      replicas: 1
      resources:
        limits:
          memory: 1G

  db:
    image: timescale/timescaledb:latest-pg15
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init:/docker-entrypoint-initdb.d
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G

  automation:
    build: .
    command: python automation/automation_vn100_direct.py --max-symbols 100 --production
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
    depends_on:
      - db
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G

volumes:
  postgres_data:
  redis_data:
```

#### **4. Production Deployment**
```bash
# Deploy production system
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment
docker-compose -f docker-compose.prod.yml ps
curl https://your-domain.com/health
```

## 🔧 MAINTENANCE PROCEDURES

### **📅 Daily Maintenance**

#### **Morning Checklist**
```bash
#!/bin/bash
# daily_maintenance.sh

echo "=== Daily Maintenance - $(date) ==="

# 1. Check system status
echo "Checking system status..."
./ssi_system_manager.sh status

# 2. Check disk space
echo "Checking disk space..."
df -h

# 3. Check memory usage
echo "Checking memory usage..."
free -h

# 4. Check Docker containers
echo "Checking Docker containers..."
docker ps

# 5. Check database health
echo "Checking database health..."
docker exec tracking_data_db pg_isready -U postgres

# 6. Check API health
echo "Checking API health..."
curl -s http://localhost:8000/health | jq .

# 7. Run automation
echo "Running daily automation..."
python automation/automation_vn100_direct.py --max-symbols 100

# 8. Check logs for errors
echo "Checking recent errors..."
docker logs tracking_data_api --since 24h | grep -i error | tail -10

echo "=== Daily Maintenance Complete ==="
```

#### **Automated Daily Tasks**
```bash
# Add to crontab
crontab -e

# Add these lines:
0 6 * * * /path/to/tracking_data/daily_maintenance.sh >> /var/log/daily_maintenance.log 2>&1
0 7 * * * /path/to/tracking_data/automation/automation_vn100_direct.py --max-symbols 100 >> /var/log/automation.log 2>&1
```

### **📅 Weekly Maintenance**

#### **Weekly Checklist**
```bash
#!/bin/bash
# weekly_maintenance.sh

echo "=== Weekly Maintenance - $(date) ==="

# 1. Database optimization
echo "Optimizing database..."
docker exec tracking_data_db psql -U postgres -d tracking_data -c "VACUUM ANALYZE;"

# 2. Database backup
echo "Creating database backup..."
docker exec tracking_data_db pg_dump -U postgres -d tracking_data | gzip > backup_$(date +%Y%m%d).sql.gz

# 3. Log rotation
echo "Rotating logs..."
find /var/log -name "*.log" -mtime +7 -delete

# 4. System update
echo "Updating system..."
sudo apt update && sudo apt upgrade -y

# 5. Docker cleanup
echo "Cleaning up Docker..."
docker system prune -f

# 6. Performance check
echo "Checking performance..."
docker stats --no-stream

echo "=== Weekly Maintenance Complete ==="
```

### **📅 Monthly Maintenance**

#### **Monthly Checklist**
```bash
#!/bin/bash
# monthly_maintenance.sh

echo "=== Monthly Maintenance - $(date) ==="

# 1. Full system health check
echo "Running full health check..."
cd test && python3 final_validation.py

# 2. Database maintenance
echo "Database maintenance..."
docker exec tracking_data_db psql -U postgres -d tracking_data -c "REINDEX DATABASE tracking_data;"

# 3. Archive old data
echo "Archiving old data..."
docker exec tracking_data_db psql -U postgres -d tracking_data -c "
DELETE FROM stock_statistics 
WHERE date < CURRENT_DATE - INTERVAL '2 years';"

# 4. Security update
echo "Security updates..."
sudo apt update && sudo apt upgrade -y
sudo certbot renew

# 5. Performance analysis
echo "Performance analysis..."
docker exec tracking_data_db psql -U postgres -d tracking_data -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;"

echo "=== Monthly Maintenance Complete ==="
```

## 📊 MONITORING & ALERTING

### **🔍 System Monitoring**

#### **Prometheus Configuration**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'stock-tracking-api'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:9121']
```

#### **Grafana Dashboard**
```json
{
  "dashboard": {
    "title": "Stock Tracking System",
    "panels": [
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          }
        ]
      },
      {
        "title": "Database Connections",
        "type": "graph",
        "targets": [
          {
            "expr": "pg_stat_database_numbackends"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "container_memory_usage_bytes"
          }
        ]
      }
    ]
  }
}
```

### **🚨 Alerting Rules**

#### **Alert Configuration**
```yaml
# alerts.yml
groups:
  - name: stock-tracking-alerts
    rules:
      - alert: HighAPIResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High API response time"
          description: "API response time is above 1 second"

      - alert: DatabaseDown
        expr: up{job="postgres"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database is down"
          description: "PostgreSQL database is not responding"

      - alert: HighMemoryUsage
        expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Container memory usage is above 80%"
```

## 🔄 BACKUP & RECOVERY

### **📦 Backup Strategy**

#### **Database Backup**
```bash
#!/bin/bash
# backup_database.sh

BACKUP_DIR="/backups/stock-tracking"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="tracking_data_${DATE}.sql.gz"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup
docker exec tracking_data_db pg_dump -U postgres -d tracking_data | gzip > "${BACKUP_DIR}/${BACKUP_FILE}"

# Upload to S3 (optional)
aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}" s3://your-backup-bucket/

# Clean up old backups (keep last 30 days)
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: ${BACKUP_FILE}"
```

#### **Configuration Backup**
```bash
#!/bin/bash
# backup_config.sh

CONFIG_BACKUP_DIR="/backups/config"
DATE=$(date +%Y%m%d_%H%M%S)

# Create config backup
tar -czf "${CONFIG_BACKUP_DIR}/config_${DATE}.tar.gz" \
  docker-compose.yml \
  .env \
  ssi_system_manager.sh \
  automation_manager.sh \
  pipeline_manager_extended.sh \
  ssi_url/tracking_data.json

echo "Configuration backup completed"
```

### **🔄 Recovery Procedures**

#### **Database Recovery**
```bash
#!/bin/bash
# restore_database.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# Stop services
./ssi_system_manager.sh stop

# Restore database
docker exec -i tracking_data_db psql -U postgres -d tracking_data < $BACKUP_FILE

# Start services
./ssi_system_manager.sh start

echo "Database restored from: $BACKUP_FILE"
```

#### **Full System Recovery**
```bash
#!/bin/bash
# full_system_recovery.sh

# 1. Stop all services
docker-compose down -v

# 2. Restore configuration
tar -xzf config_backup.tar.gz

# 3. Restore database
docker-compose up -d db
sleep 30
docker exec -i tracking_data_db psql -U postgres -d tracking_data < database_backup.sql

# 4. Start all services
docker-compose up -d

# 5. Verify system
./ssi_system_manager.sh status
curl http://localhost:8000/health
```

## 🔧 SCALING & OPTIMIZATION

### **📈 Horizontal Scaling**

#### **Load Balancer Configuration**
```nginx
# nginx.conf
upstream api_backend {
    server localhost:8000;
    server localhost:8001;
    server localhost:8002;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

#### **Database Scaling**
```yaml
# docker-compose.scale.yml
services:
  db-master:
    image: timescale/timescaledb:latest-pg15
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_master_data:/var/lib/postgresql/data

  db-replica:
    image: timescale/timescaledb:latest-pg15
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    depends_on:
      - db-master
```

### **⚡ Performance Optimization**

#### **Database Optimization**
```sql
-- Create indexes for better performance
CREATE INDEX CONCURRENTLY idx_stock_statistics_symbol_date ON stock_statistics(symbol, date);
CREATE INDEX CONCURRENTLY idx_stock_statistics_date ON stock_statistics(date);
CREATE INDEX CONCURRENTLY idx_stock_statistics_symbol ON stock_statistics(symbol);

-- Analyze tables
ANALYZE stock_statistics;
ANALYZE companies;
ANALYZE market_indices;
```

#### **API Optimization**
```python
# Add caching to API
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

# Configure Redis caching
FastAPICache.init(RedisBackend(redis), prefix="api-cache")

# Add response caching
@cache(expire=300)  # 5 minutes
@app.get("/stock-statistics")
async def get_stock_statistics(symbol: str):
    # API logic
    pass
```

## 🛡️ SECURITY CONSIDERATIONS

### **🔒 Security Hardening**

#### **Docker Security**
```yaml
# docker-compose.secure.yml
services:
  api:
    build: .
    user: "1000:1000"  # Non-root user
    read_only: true
    tmpfs:
      - /tmp
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
```

#### **Database Security**
```sql
-- Create read-only user
CREATE USER readonly_user WITH PASSWORD 'readonly_password';
GRANT CONNECT ON DATABASE tracking_data TO readonly_user;
GRANT USAGE ON SCHEMA public TO readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;

-- Enable SSL
ALTER SYSTEM SET ssl = on;
ALTER SYSTEM SET ssl_cert_file = '/var/lib/postgresql/server.crt';
ALTER SYSTEM SET ssl_key_file = '/var/lib/postgresql/server.key';
```

## 📋 DEPLOYMENT CHECKLIST

### **✅ Pre-Deployment**
- [ ] Code review completed
- [ ] Tests passing (100%)
- [ ] Documentation updated
- [ ] Security scan completed
- [ ] Performance testing completed
- [ ] Backup strategy verified

### **✅ Deployment**
- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Firewall rules configured
- [ ] Monitoring setup completed
- [ ] Health checks passing
- [ ] Load testing completed

### **✅ Post-Deployment**
- [ ] System monitoring active
- [ ] Backup procedures tested
- [ ] Documentation updated
- [ ] Team training completed
- [ ] Support procedures established
- [ ] Performance baseline established

---

## 🎯 CONCLUSION

Tài liệu này cung cấp hướng dẫn chi tiết để deploy và maintain hệ thống Stock Tracking Data trong môi trường production. Các procedures được thiết kế để đảm bảo:

- ✅ **High Availability**: System uptime 99.9%
- ✅ **Scalability**: Horizontal và vertical scaling
- ✅ **Security**: Comprehensive security measures
- ✅ **Monitoring**: Real-time monitoring và alerting
- ✅ **Backup**: Automated backup và recovery
- ✅ **Maintenance**: Scheduled maintenance procedures

**Hệ thống đã sẵn sàng cho production deployment với đầy đủ monitoring, backup, và maintenance procedures.**
