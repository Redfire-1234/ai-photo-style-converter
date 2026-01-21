# Deployment Guide

## Table of Contents
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Cloud Platforms](#cloud-platforms)
- [Performance Optimization](#performance-optimization)

---

## Local Development

### Quick Start

1. **Clone and setup:**
```bash
git clone https://github.com/yourusername/ai-photo-style-converter.git
cd ai-photo-style-converter
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
cd backend
pip install -r requirements.txt
```

2. **Download models** (see [MODELS.md](MODELS.md))

3. **Run:**
```bash
python app.py
```

4. **Access:** http://localhost:8000/app

---

## Docker Deployment

### Using Docker Compose (Recommended)

**1. Build and run:**
```bash
docker-compose up -d
```

**2. View logs:**
```bash
docker-compose logs -f
```

**3. Stop:**
```bash
docker-compose down
```

**4. Access:** http://localhost:8000/app

### Using Docker Directly

**Build:**
```bash
docker build -t ai-style-converter .
```

**Run:**
```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/backend/pretrained:/app/backend/pretrained \
  -v $(pwd)/backend/static:/app/backend/static \
  --name ai-style-converter \
  ai-style-converter
```

**Stop:**
```bash
docker stop ai-style-converter
docker rm ai-style-converter
```

---

## Production Deployment

### Prerequisites
- Linux server (Ubuntu 20.04+ recommended)
- 4GB+ RAM
- 10GB+ disk space
- Python 3.10+
- Nginx (reverse proxy)
- SSL certificate (Let's Encrypt)

### Step-by-Step Production Setup

**1. Server Setup:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.10 python3.10-venv nginx certbot python3-certbot-nginx

# Create app directory
sudo mkdir -p /var/www/ai-style-converter
sudo chown $USER:$USER /var/www/ai-style-converter
cd /var/www/ai-style-converter
```

**2. Deploy Application:**
```bash
# Clone repository
git clone https://github.com/yourusername/ai-photo-style-converter.git .

# Setup virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Download models (see MODELS.md)
```

**3. Create Systemd Service:**

Create `/etc/systemd/system/ai-style-converter.service`:

```ini
[Unit]
Description=AI Style Converter
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/ai-style-converter/backend
Environment="PATH=/var/www/ai-style-converter/venv/bin"
ExecStart=/var/www/ai-style-converter/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-style-converter
sudo systemctl start ai-style-converter
sudo systemctl status ai-style-converter
```

**4. Configure Nginx:**

Create `/etc/nginx/sites-available/ai-style-converter`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeouts for video processing
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
        send_timeout 600;
    }
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/ai-style-converter /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**5. Setup SSL (HTTPS):**
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

**6. Firewall:**
```bash
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

---

## Cloud Platforms

### AWS EC2

**1. Launch Instance:**
- AMI: Ubuntu 20.04 LTS
- Instance Type: t3.medium (2 vCPU, 4GB RAM) minimum
- Storage: 20GB EBS
- Security Group: Allow HTTP (80), HTTPS (443), SSH (22)

**2. Connect and deploy:**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
# Follow production deployment steps
```

**3. Elastic IP:**
Assign elastic IP for persistent address

**4. Load Balancer (optional):**
Setup ALB for high availability

### Google Cloud Platform (GCP)

**1. Create VM:**
```bash
gcloud compute instances create ai-style-converter \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=20GB
```

**2. SSH and deploy:**
```bash
gcloud compute ssh ai-style-converter
# Follow production deployment steps
```

**3. Static IP:**
```bash
gcloud compute addresses create ai-style-converter-ip --region=us-central1
gcloud compute instances add-access-config ai-style-converter \
  --address=$(gcloud compute addresses describe ai-style-converter-ip --region=us-central1 --format='get(address)')
```

### Digital Ocean

**1. Create Droplet:**
- Ubuntu 20.04
- 4GB RAM / 2 CPU
- 80GB SSD

**2. Deploy using production steps**

**3. Setup firewall:**
- Inbound: HTTP (80), HTTPS (443), SSH (22)
- Outbound: All

### Heroku

**1. Create `Procfile`:**
```
web: cd backend && uvicorn app:app --host 0.0.0.0 --port $PORT
```

**2. Deploy:**
```bash
heroku create ai-style-converter
git push heroku main
heroku open
```

**Note:** Heroku has limited memory - may timeout on large videos.

---

## Performance Optimization

### 1. Optimize for Speed

**Reduce image size:**
```python
# In config.py
MAX_IMAGE_SIZE = 512  # Faster, lower quality
```

**Limit video frames:**
```python
# In video_processor.py
max_frames = 100  # Process fewer frames
```

**Use OpenCV styles only:**
Remove neural/anime models if not needed.

### 2. Caching

**Add Redis for result caching:**
```python
import redis
from hashlib import md5

cache = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_result(image_hash, style):
    key = f"{image_hash}:{style}"
    return cache.get(key)

def cache_result(image_hash, style, result):
    key = f"{image_hash}:{style}"
    cache.setex(key, 3600, result)  # 1 hour expiry
```

### 3. Queue System

**Add Celery for async processing:**
```python
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task
def process_video(video_path, style):
    # Long-running video processing
    pass
```

### 4. Resource Limits

**Memory management:**
```python
# Limit concurrent requests
from fastapi_limiter import FastAPILimiter

@app.on_event("startup")
async def startup():
    await FastAPILimiter.init()
```

### 5. CDN for Static Files

Use Cloudflare or AWS CloudFront for serving frontend static files.

### 6. GPU Acceleration (Advanced)

**Install CUDA PyTorch:**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**Update model loading:**
```python
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)
```

---

## Monitoring

### Setup Logging

**Add to `app.py`:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ai-style-converter/app.log'),
        logging.StreamHandler()
    ]
)
```

### Health Checks

**Add endpoint:**
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "models_loaded": len(style_loader.neural_models) + len(style_loader.anime_models)
    }
```

### Monitoring Tools

- **Uptime:** UptimeRobot, Pingdom
- **Performance:** New Relic, DataDog
- **Logs:** ELK Stack, Graylog

---

## Backup & Recovery

**Backup models:**
```bash
tar -czf models-backup.tar.gz backend/pretrained/
```

**Backup configuration:**
```bash
cp backend/config.py config.py.backup
```

**Database backup (if added later):**
```bash
# PostgreSQL example
pg_dump dbname > backup.sql
```

---

## Security Best Practices

1. **Environment Variables:**
```python
# Use .env file for secrets
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
```

2. **Rate Limiting:**
```python
from slowapi import Limiter
limiter = Limiter(key_func=lambda: request.client.host)

@app.post("/api/convert")
@limiter.limit("10/minute")
async def convert_style(...):
    pass
```

3. **Input Validation:**
Already implemented - file size, type checking

4. **HTTPS Only:**
Enforce HTTPS in production

5. **Regular Updates:**
```bash
pip list --outdated
pip install --upgrade -r requirements.txt
```

---

## Troubleshooting

**Service won't start:**
```bash
sudo journalctl -u ai-style-converter -n 50
```

**High memory usage:**
```bash
free -h
htop
```

**Slow responses:**
```bash
# Check CPU usage
top
# Check disk I/O
iotop
```

**Nginx errors:**
```bash
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
```

---

## Scaling

**Horizontal Scaling:**
1. Deploy multiple instances
2. Use load balancer (Nginx, HAProxy, AWS ALB)
3. Shared storage for models (NFS, S3)

**Vertical Scaling:**
- Increase RAM/CPU
- Use GPU instances for faster processing

**Auto-scaling (AWS):**
Use Auto Scaling Groups with custom metrics based on queue length.

---

## Cost Estimation

**AWS EC2 (t3.medium):**
- Instance: ~$30/month
- Storage: ~$2/month
- Data transfer: Variable

**Digital Ocean:**
- 4GB Droplet: $24/month
- Backups: +$4.80/month

**GCP:**
- e2-medium: ~$25/month
- Network: Variable

**Heroku:**
- Standard dyno: $25/month
- (May need performance dyno for video: $250/month)

---

For questions or issues, open an issue on GitHub.
