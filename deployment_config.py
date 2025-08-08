#!/usr/bin/env python3
"""
SuperClaude DevOps - Deployment and Infrastructure Configuration
Production-ready deployment automation with Docker, monitoring, and CI/CD integration
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class DeploymentConfig:
    """Production deployment configuration"""
    
    # Environment Configuration
    environment: str = "production"
    app_name: str = "superclaude-crypto-analytics"
    version: str = "1.0.0"
    
    # API Configuration
    coingecko_api_key: str = os.getenv("COINGECKO_PRO_API_KEY", "CG-MVg68aVqeVyu8fzagC9E1hPj")
    defillama_api_key: str = os.getenv("DEFILLAMA_PRO_API_KEY", "435722de8920d195d301a595f0c29ed939608c9b1da2d75905e85a68f3ee336d")
    velo_api_key: str = os.getenv("VELO_API_KEY", "25965dc53c424038964e2f720270bece")
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8080
    workers: int = 4
    
    # Database Configuration
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Security Configuration
    enable_https: bool = True
    cors_origins: List[str] = None
    
    # Monitoring Configuration
    enable_metrics: bool = True
    log_level: str = "INFO"
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["https://localhost:*"]

# Docker configuration
DOCKERFILE_CONTENT = '''
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run application
CMD ["python", "superclaude_backend.py", "--host", "0.0.0.0", "--port", "8080"]
'''

# Docker Compose configuration
DOCKER_COMPOSE_CONTENT = '''
version: '3.8'

services:
  superclaude-app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - COINGECKO_PRO_API_KEY=${COINGECKO_PRO_API_KEY}
      - DEFILLAMA_PRO_API_KEY=${DEFILLAMA_PRO_API_KEY}
      - VELO_API_KEY=${VELO_API_KEY}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - superclaude-app
    restart: unless-stopped

volumes:
  redis_data:
'''

# Requirements.txt for production
REQUIREMENTS_CONTENT = '''
# Core Framework
Flask==2.3.3
Flask-CORS==4.0.0
Flask-Caching==2.1.0
Flask-Limiter==3.5.0
Werkzeug==2.3.7

# API and HTTP
requests==2.31.0
urllib3==2.0.7

# Data Processing
pandas==2.1.3
numpy==1.25.2

# Security
cryptography==41.0.8
bcrypt==4.1.1
PyJWT==2.8.0

# Caching and Database
redis==5.0.1
cachetools==5.3.2

# Monitoring and Logging
psutil==5.9.6

# Production WSGI Server
gunicorn==21.2.0
'''

def create_deployment_files():
    """Create all deployment configuration files"""
    
    # Create Dockerfile
    with open("Dockerfile", "w") as f:
        f.write(DOCKERFILE_CONTENT)
    
    # Create docker-compose.yml
    with open("docker-compose.yml", "w") as f:
        f.write(DOCKER_COMPOSE_CONTENT)
    
    # Create requirements.txt
    with open("requirements_production.txt", "w") as f:
        f.write(REQUIREMENTS_CONTENT)
    
    print("Deployment configuration files created successfully!")
    print("   - Dockerfile")
    print("   - docker-compose.yml") 
    print("   - requirements_production.txt")

if __name__ == "__main__":
    create_deployment_files()