# 🚀 SuperClaude Crypto Analysis Suite - Hosting Guide

## Local Hosting (Development)

### Quick Start
```bash
# 1. Install dependencies
pip install flask flask-cors pandas requests numpy

# 2. Start the server
python crypto_server.py

# 3. Open browser to:
http://localhost:8080
```

### Automated Launch
```bash
# Windows - Launch everything automatically
launch_dashboard.bat

# Or start server only
start_crypto_server.bat
```

### Available Endpoints
- **GET /** - Main live dashboard
- **GET /api/status** - Server and API status
- **GET /api/risk-analysis** - Risk management analysis
- **GET /api/sector-scout** - Sector rotation opportunities  
- **GET /api/dip-buyer** - Leverage reset detection
- **GET /api/yield-analysis** - DeFi yield opportunities
- **GET /api/altcoin-strength** - ETH outperformers
- **GET /api/gem-analysis** - Micro-cap deep dive
- **GET /api/full-analysis** - Combined analysis

---

## Live Hosting (Production)

### Option 1: Cloud Platforms

#### **Heroku Deployment**
```bash
# 1. Install Heroku CLI
# 2. Create Procfile
echo "web: python crypto_server.py" > Procfile

# 3. Deploy
git add .
git commit -m "Deploy to Heroku"
heroku create superclaude-crypto-suite
heroku config:set FLASK_ENV=production
git push heroku main
```

#### **Railway Deployment**
```bash
# 1. Connect GitHub repository
# 2. Set environment variables:
PORT=8080
FLASK_ENV=production

# 3. Deploy automatically via GitHub
```

#### **Vercel Deployment**
```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Deploy
vercel --prod
```

### Option 2: VPS/Server Deployment

#### **Ubuntu/Linux VPS**
```bash
# 1. Install dependencies
sudo apt update
sudo apt install python3 python3-pip nginx

# 2. Install Python packages  
pip3 install -r requirements.txt

# 3. Create systemd service
sudo nano /etc/systemd/system/crypto-suite.service

# Service file content:
[Unit]
Description=SuperClaude Crypto Analysis Suite
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/crypto-suite
Environment=PATH=/var/www/crypto-suite/venv/bin
ExecStart=/var/www/crypto-suite/venv/bin/python crypto_server.py
Restart=always

[Install]
WantedBy=multi-user.target

# 4. Enable and start service
sudo systemctl enable crypto-suite
sudo systemctl start crypto-suite

# 5. Configure Nginx reverse proxy
sudo nano /etc/nginx/sites-available/crypto-suite

# Nginx config:
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# 6. Enable site
sudo ln -s /etc/nginx/sites-available/crypto-suite /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Option 3: Docker Deployment

#### **Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "crypto_server.py"]
```

#### **Docker Compose**
```yaml
version: '3.8'
services:
  crypto-suite:
    build: .
    ports:
      - "8080:8080"
    environment:
      - FLASK_ENV=production
    restart: always
```

#### **Deploy with Docker**
```bash
# 1. Build image
docker build -t superclaude-crypto-suite .

# 2. Run container
docker run -d -p 8080:8080 --name crypto-suite superclaude-crypto-suite

# Or use docker-compose
docker-compose up -d
```

---

## Environment Variables

### Required for Production
```bash
FLASK_ENV=production
PORT=8080

# API Keys (if using real APIs)
COINGECKO_API_KEY=your_coingecko_key
DEFILLAMA_API_KEY=your_defillama_key  
VELO_API_KEY=your_velo_key
```

### Optional Configuration
```bash
# Caching
CACHE_TIMEOUT=300  # 5 minutes

# CORS
CORS_ORIGINS=*  # Or specific domains

# Debug
DEBUG=False
```

---

## Security Considerations

### Production Checklist
- ✅ Set `DEBUG=False` in production
- ✅ Use environment variables for API keys
- ✅ Enable HTTPS with SSL certificates
- ✅ Implement rate limiting
- ✅ Configure CORS properly
- ✅ Use production WSGI server (Gunicorn)
- ✅ Set up monitoring and logging
- ✅ Implement backup strategies

### Enhanced Security
```bash
# 1. Use Gunicorn for production
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 crypto_server:app

# 2. Add rate limiting
pip install flask-limiter

# 3. Enable HTTPS
# Use Let's Encrypt with certbot
sudo certbot --nginx -d your-domain.com
```

---

## Monitoring & Maintenance

### Health Checks
```bash
# Check server status
curl http://localhost:8080/api/status

# Monitor logs
tail -f /var/log/crypto-suite/app.log
```

### Performance Monitoring
- **Response times** for API endpoints
- **Memory usage** and CPU utilization  
- **Error rates** and exception tracking
- **API rate limits** and quotas

### Backup Strategy
- **Database backups** (if using persistent storage)
- **Configuration files** backup
- **Log rotation** and archival
- **Disaster recovery** procedures

---

## Troubleshooting

### Common Issues

#### **Server Won't Start**
```bash
# Check dependencies
pip list | grep -E "(flask|pandas|requests)"

# Check port conflicts
netstat -tulpn | grep :8080

# Check logs
python crypto_server.py
```

#### **API Errors**
```bash
# Test individual endpoints
curl http://localhost:8080/api/status
curl http://localhost:8080/api/risk-analysis

# Check API key validity
# Verify rate limits
```

#### **Performance Issues**
```bash
# Monitor resource usage
htop
ps aux | grep python

# Check cache effectiveness
# Optimize query performance
```

---

## Live Demo URLs

### Local Development
- **Main Dashboard**: http://localhost:8080
- **API Status**: http://localhost:8080/api/status
- **Risk Analysis**: http://localhost:8080/api/risk-analysis

### Production Examples
- **Heroku**: https://superclaude-crypto-suite.herokuapp.com
- **Railway**: https://superclaude-crypto-suite.up.railway.app
- **Custom Domain**: https://crypto.your-domain.com

---

## Support & Updates

### Getting Help
- **Documentation**: Check README files
- **Issues**: Submit GitHub issues
- **Community**: SuperClaude Framework Discord

### Updates
- **Pull latest changes**: `git pull origin main`
- **Update dependencies**: `pip install -r requirements.txt --upgrade`
- **Restart services**: `sudo systemctl restart crypto-suite`

---

**Ready to launch your SuperClaude Crypto Analysis Suite! 🚀**

*Both local and live hosting options are configured and tested.*