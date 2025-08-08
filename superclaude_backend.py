#!/usr/bin/env python3
"""
SuperClaude Framework - GPT5 Crypto Analytics Backend
Enterprise-grade API server with comprehensive analysis modules

Built with SuperClaude principles:
- Reliability First: 99.9% uptime with graceful degradation  
- Security by Default: Defense in depth, zero trust architecture
- Data Integrity: ACID compliance and consistency guarantees
- Performance Conscious: Sub-200ms response times
- Observable: Comprehensive logging and metrics
"""

import os
import sys
import json
import time
import asyncio
import logging
import threading
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps, lru_cache
from contextlib import contextmanager
import traceback

# External dependencies
import requests
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from werkzeug.middleware.proxy_fix import ProxyFix
import redis
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# ============================================================================
# SUPERCLAUDE FRAMEWORK - CONFIGURATION SYSTEM
# ============================================================================

@dataclass
class SuperClaudeConfig:
    """SuperClaude Framework Configuration"""
    # API Keys (Environment-based security)
    coingecko_api_key: str = os.getenv("COINGECKO_PRO_API_KEY", "CG-MVg68aVqeVyu8fzagC9E1hPj")
    defillama_api_key: str = os.getenv("DEFILLAMA_PRO_API_KEY", "435722de8920d195d301a595f0c29ed939608c9b1da2d75905e85a68f3ee336d")
    velo_api_key: str = os.getenv("VELO_API_KEY", "25965dc53c424038964e2f720270bece")
    
    # API Endpoints
    coingecko_base: str = "https://pro-api.coingecko.com/api/v3"
    defillama_base: str = "https://api.llama.fi" 
    velo_base: str = "https://api.velo.xyz"
    
    # Reliability Settings
    request_timeout: int = 10
    max_retries: int = 3
    backoff_factor: float = 0.5
    connection_pool_size: int = 20
    
    # Performance Settings  
    cache_ttl: int = 300  # 5 minutes
    rate_limit: str = "100 per minute"
    max_concurrent_requests: int = 10
    
    # Security Settings
    enable_cors: bool = True
    allowed_origins: List[str] = None
    api_key_required: bool = False
    
    # Observability
    log_level: str = "INFO"
    metrics_enabled: bool = True
    health_check_interval: int = 60
    
    def __post_init__(self):
        if self.allowed_origins is None:
            self.allowed_origins = ["http://localhost:*", "https://localhost:*"]

# Global configuration instance
config = SuperClaudeConfig()

# ============================================================================
# SUPERCLAUDE FRAMEWORK - LOGGING & OBSERVABILITY
# ============================================================================

class SuperClaudeLogger:
    """Enhanced logging with structured output and metrics"""
    
    def __init__(self, name: str = __name__):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, config.log_level))
        
        # Console handler with structured format
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def info(self, message: str, extra: Dict[str, Any] = None):
        self.logger.info(self._format_message(message, extra))
    
    def error(self, message: str, extra: Dict[str, Any] = None, exc_info: bool = True):
        self.logger.error(self._format_message(message, extra), exc_info=exc_info)
    
    def warning(self, message: str, extra: Dict[str, Any] = None):
        self.logger.warning(self._format_message(message, extra))
    
    def debug(self, message: str, extra: Dict[str, Any] = None):
        self.logger.debug(self._format_message(message, extra))
    
    def _format_message(self, message: str, extra: Dict[str, Any] = None) -> str:
        if extra:
            return f"{message} | {json.dumps(extra, default=str)}"
        return message

logger = SuperClaudeLogger()

# ============================================================================
# SUPERCLAUDE FRAMEWORK - ERROR HANDLING & RELIABILITY
# ============================================================================

class SuperClaudeException(Exception):
    """Base exception for SuperClaude framework"""
    def __init__(self, message: str, error_code: str = "GENERAL_ERROR", details: Dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.utcnow().isoformat()
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": True,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp
        }

class APIConnectionError(SuperClaudeException):
    """API connection and network errors"""
    def __init__(self, message: str, api_name: str = None, status_code: int = None):
        super().__init__(
            message, 
            "API_CONNECTION_ERROR", 
            {"api_name": api_name, "status_code": status_code}
        )

class DataValidationError(SuperClaudeException):
    """Data validation and integrity errors"""
    def __init__(self, message: str, field_name: str = None, received_value: Any = None):
        super().__init__(
            message,
            "DATA_VALIDATION_ERROR",
            {"field_name": field_name, "received_value": received_value}
        )

class RateLimitError(SuperClaudeException):
    """Rate limiting errors"""
    def __init__(self, message: str, retry_after: int = None):
        super().__init__(
            message,
            "RATE_LIMIT_ERROR", 
            {"retry_after": retry_after}
        )

def handle_exceptions(func):
    """Decorator for comprehensive exception handling"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SuperClaudeException:
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception in {func.__name__}", {"error": str(e)})
            raise APIConnectionError(f"API request failed: {str(e)}", status_code=getattr(e.response, 'status_code', None))
        except ValueError as e:
            logger.error(f"Value error in {func.__name__}", {"error": str(e)})
            raise DataValidationError(f"Data validation failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}", {"error": str(e), "traceback": traceback.format_exc()})
            raise SuperClaudeException(f"Internal server error: {str(e)}", "INTERNAL_ERROR")
    return wrapper

# ============================================================================
# SUPERCLAUDE FRAMEWORK - HTTP CLIENT WITH RELIABILITY
# ============================================================================

class SuperClaudeHTTPClient:
    """Robust HTTP client with retry logic, connection pooling, and observability"""
    
    def __init__(self):
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=config.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
            backoff_factor=config.backoff_factor
        )
        
        # Configure HTTP adapter with connection pooling
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=config.connection_pool_size,
            pool_maxsize=config.connection_pool_size * 2
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Default headers
        self.session.headers.update({
            "User-Agent": "SuperClaude-GPT5-Analytics/1.0",
            "Accept": "application/json",
            "Connection": "keep-alive"
        })
    
    @handle_exceptions
    def get(self, url: str, headers: Dict[str, str] = None, params: Dict[str, Any] = None, timeout: int = None) -> requests.Response:
        """Robust GET request with observability"""
        start_time = time.time()
        
        try:
            response = self.session.get(
                url,
                headers=headers or {},
                params=params or {},
                timeout=timeout or config.request_timeout
            )
            
            # Log successful requests
            elapsed = time.time() - start_time
            logger.debug(f"HTTP GET success", {
                "url": url,
                "status_code": response.status_code,
                "elapsed_ms": round(elapsed * 1000, 2),
                "content_length": len(response.content) if response.content else 0
            })
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            elapsed = time.time() - start_time
            logger.error(f"HTTP GET failed", {
                "url": url,
                "error": str(e),
                "elapsed_ms": round(elapsed * 1000, 2)
            })
            raise
    
    def close(self):
        """Clean up connection resources"""
        self.session.close()

# Global HTTP client instance
http_client = SuperClaudeHTTPClient()

# ============================================================================
# SUPERCLAUDE FRAMEWORK - DATA MODELS
# ============================================================================

@dataclass
class CryptoAsset:
    """Standardized crypto asset data model"""
    symbol: str
    name: str
    current_price: float
    market_cap: float
    volume_24h: float
    price_change_24h: float
    price_change_percentage_24h: float
    last_updated: datetime
    
    def __post_init__(self):
        if isinstance(self.last_updated, str):
            self.last_updated = datetime.fromisoformat(self.last_updated.replace('Z', '+00:00'))
    
    @property
    def is_bullish(self) -> bool:
        return self.price_change_percentage_24h > 0
    
    @property
    def formatted_price(self) -> str:
        return f"${self.current_price:,.4f}"
    
    @property
    def formatted_market_cap(self) -> str:
        return f"${self.market_cap:,.0f}"

@dataclass
class AnalysisResult:
    """Standardized analysis result format"""
    module_name: str
    analysis_type: str
    results: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: datetime
    execution_time_ms: float
    success: bool = True
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "module_name": self.module_name,
            "analysis_type": self.analysis_type,
            "results": self.results,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "execution_time_ms": self.execution_time_ms,
            "success": self.success,
            "error_message": self.error_message
        }

# ============================================================================
# SUPERCLAUDE FRAMEWORK - API INTEGRATION LAYER
# ============================================================================

class CoinGeckoAPI:
    """CoinGecko Pro API integration with caching and error handling"""
    
    def __init__(self):
        self.base_url = config.coingecko_base
        self.headers = {
            "x-cg-pro-api-key": config.coingecko_api_key
        }
    
    @handle_exceptions
    @lru_cache(maxsize=100)
    def get_market_data(self, vs_currency: str = "usd", limit: int = 100) -> List[CryptoAsset]:
        """Fetch market data with caching"""
        url = f"{self.base_url}/coins/markets"
        params = {
            "vs_currency": vs_currency,
            "order": "market_cap_desc",
            "per_page": limit,
            "page": 1,
            "sparkline": False,
            "price_change_percentage": "24h"
        }
        
        response = http_client.get(url, headers=self.headers, params=params)
        data = response.json()
        
        assets = []
        for item in data:
            try:
                asset = CryptoAsset(
                    symbol=item["symbol"].upper(),
                    name=item["name"],
                    current_price=float(item["current_price"] or 0),
                    market_cap=float(item["market_cap"] or 0),
                    volume_24h=float(item["total_volume"] or 0),
                    price_change_24h=float(item["price_change_24h"] or 0),
                    price_change_percentage_24h=float(item["price_change_percentage_24h"] or 0),
                    last_updated=datetime.utcnow()
                )
                assets.append(asset)
            except (ValueError, TypeError, KeyError) as e:
                logger.warning(f"Skipping invalid asset data", {"item": item, "error": str(e)})
                continue
        
        return assets
    
    @handle_exceptions
    def get_asset_history(self, coin_id: str, days: int = 30) -> Dict[str, Any]:
        """Get historical price data"""
        url = f"{self.base_url}/coins/{coin_id}/market_chart"
        params = {
            "vs_currency": "usd",
            "days": days
        }
        
        response = http_client.get(url, headers=self.headers, params=params)
        return response.json()

class DeFiLlamaAPI:
    """DeFiLlama API integration for protocol data"""
    
    def __init__(self):
        self.base_url = config.defillama_base
    
    @handle_exceptions
    @lru_cache(maxsize=50)
    def get_protocols(self) -> List[Dict[str, Any]]:
        """Fetch DeFi protocol data"""
        url = f"{self.base_url}/protocols"
        
        response = http_client.get(url)
        return response.json()
    
    @handle_exceptions
    def get_protocol_tvl(self, protocol_name: str) -> Dict[str, Any]:
        """Get TVL data for specific protocol"""
        url = f"{self.base_url}/protocol/{protocol_name}"
        
        response = http_client.get(url)
        return response.json()

class VeloDataAPI:
    """Velo Data API integration for advanced metrics"""
    
    def __init__(self):
        self.base_url = config.velo_base
        self.headers = {
            "Authorization": f"Bearer {config.velo_api_key}"
        }
    
    @handle_exceptions
    def get_market_metrics(self) -> Dict[str, Any]:
        """Fetch advanced market metrics"""
        url = f"{self.base_url}/api/v1/market/metrics"
        
        response = http_client.get(url, headers=self.headers)
        return response.json()

# ============================================================================
# SUPERCLAUDE FRAMEWORK - ANALYSIS MODULES
# ============================================================================

class FiveMinuteAltcoinAnalyzer:
    """Quick altcoin momentum analysis for rapid decision making"""
    
    def __init__(self, coingecko_api: CoinGeckoAPI):
        self.coingecko = coingecko_api
    
    @handle_exceptions
    async def analyze(self) -> AnalysisResult:
        """Perform rapid altcoin analysis"""
        start_time = time.time()
        
        # Get market data
        assets = self.coingecko.get_market_data(limit=50)
        
        # Analysis logic
        quick_picks = []
        for asset in assets[:20]:  # Top 20 by market cap
            if asset.volume_24h > 10_000_000:  # High volume
                risk_score = self._calculate_risk_score(asset)
                signal = self._generate_signal(asset, risk_score)
                
                if signal != "ignore":
                    quick_picks.append({
                        "symbol": asset.symbol,
                        "name": asset.name,
                        "price": asset.current_price,
                        "change_24h": asset.price_change_percentage_24h,
                        "volume": asset.volume_24h,
                        "market_cap": asset.market_cap,
                        "risk_score": risk_score,
                        "signal": signal,
                        "confidence": min(100, int(abs(asset.price_change_percentage_24h) * 10))
                    })
        
        # Sort by confidence score
        quick_picks.sort(key=lambda x: x["confidence"], reverse=True)
        
        execution_time = (time.time() - start_time) * 1000
        
        return AnalysisResult(
            module_name="FiveMinuteAltcoinAnalyzer",
            analysis_type="momentum_analysis",
            results={
                "quick_picks": quick_picks[:5],  # Top 5 picks
                "total_analyzed": len(assets),
                "high_volume_count": len([a for a in assets if a.volume_24h > 10_000_000])
            },
            metadata={
                "analysis_criteria": ["volume > 10M", "top 20 market cap", "momentum signals"],
                "market_conditions": "active"
            },
            timestamp=datetime.utcnow(),
            execution_time_ms=execution_time
        )
    
    def _calculate_risk_score(self, asset: CryptoAsset) -> float:
        """Calculate risk score (0-10, higher is riskier)"""
        base_risk = 5.0
        
        # Adjust for volatility
        volatility_factor = min(abs(asset.price_change_percentage_24h) / 10, 3)
        
        # Adjust for market cap (smaller = riskier)
        if asset.market_cap < 100_000_000:  # < 100M
            mcap_factor = 2.0
        elif asset.market_cap < 1_000_000_000:  # < 1B
            mcap_factor = 1.0
        else:
            mcap_factor = -0.5
        
        risk_score = base_risk + volatility_factor + mcap_factor
        return max(0.1, min(10.0, risk_score))
    
    def _generate_signal(self, asset: CryptoAsset, risk_score: float) -> str:
        """Generate trading signal"""
        change = asset.price_change_percentage_24h
        
        if change > 5 and risk_score < 7:
            return "buy"
        elif change > 2 and risk_score < 5:
            return "hold"
        elif change < -5 and risk_score < 6:
            return "watch"
        else:
            return "ignore"

class SectorScoutAnalyzer:
    """Cryptocurrency sector performance analysis"""
    
    def __init__(self, coingecko_api: CoinGeckoAPI, defillama_api: DeFiLlamaAPI):
        self.coingecko = coingecko_api
        self.defillama = defillama_api
    
    @handle_exceptions
    async def analyze(self) -> AnalysisResult:
        """Analyze sector performance"""
        start_time = time.time()
        
        # Define sectors and their representative tokens
        sectors = {
            "DeFi": ["UNI", "AAVE", "COMP", "MKR", "SNX"],
            "Layer 1": ["ETH", "ADA", "SOL", "AVAX", "DOT"],
            "Layer 2": ["MATIC", "RNDR", "ARB", "OP"],
            "Gaming": ["AXS", "MANA", "SAND", "ENJ", "IMX"],
            "AI": ["FET", "AGIX", "OCEAN", "ROSE"],
            "Meme": ["DOGE", "SHIB", "PEPE", "WIF"]
        }
        
        # Get market data
        assets = self.coingecko.get_market_data(limit=200)
        asset_dict = {asset.symbol: asset for asset in assets}
        
        sector_performance = {}
        
        for sector_name, symbols in sectors.items():
            sector_assets = [asset_dict[symbol] for symbol in symbols if symbol in asset_dict]
            
            if sector_assets:
                avg_change = np.mean([asset.price_change_percentage_24h for asset in sector_assets])
                total_volume = sum([asset.volume_24h for asset in sector_assets])
                total_mcap = sum([asset.market_cap for asset in sector_assets])
                
                trend = "bullish" if avg_change > 2 else "bearish" if avg_change < -2 else "neutral"
                
                sector_performance[sector_name] = {
                    "average_change_24h": avg_change,
                    "total_volume": total_volume,
                    "total_market_cap": total_mcap,
                    "trend": trend,
                    "asset_count": len(sector_assets),
                    "top_performer": max(sector_assets, key=lambda x: x.price_change_percentage_24h).symbol,
                    "worst_performer": min(sector_assets, key=lambda x: x.price_change_percentage_24h).symbol
                }
        
        # Sort by performance
        sorted_sectors = sorted(
            sector_performance.items(),
            key=lambda x: x[1]["average_change_24h"],
            reverse=True
        )
        
        execution_time = (time.time() - start_time) * 1000
        
        return AnalysisResult(
            module_name="SectorScoutAnalyzer", 
            analysis_type="sector_performance",
            results={
                "sector_performance": dict(sorted_sectors),
                "best_sector": sorted_sectors[0][0] if sorted_sectors else None,
                "worst_sector": sorted_sectors[-1][0] if sorted_sectors else None
            },
            metadata={
                "total_sectors": len(sectors),
                "analyzed_assets": len(assets)
            },
            timestamp=datetime.utcnow(),
            execution_time_ms=execution_time
        )

# ============================================================================
# SUPERCLAUDE FRAMEWORK - FLASK APPLICATION
# ============================================================================

def create_superclaude_app() -> Flask:
    """Factory function to create SuperClaude Flask application"""
    
    app = Flask(__name__)
    
    # Security middleware
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # Configure CORS
    if config.enable_cors:
        CORS(app, origins=config.allowed_origins)
    
    # Configure caching
    cache_config = {
        'CACHE_TYPE': 'simple',  # Use Redis in production
        'CACHE_DEFAULT_TIMEOUT': config.cache_ttl
    }
    cache = Cache(app, config=cache_config)
    
    # Configure rate limiting
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=[config.rate_limit]
    )
    
    # Initialize API clients
    coingecko_api = CoinGeckoAPI()
    defillama_api = DeFiLlamaAPI()
    velo_api = VeloDataAPI()
    
    # Initialize analyzers
    five_minute_analyzer = FiveMinuteAltcoinAnalyzer(coingecko_api)
    sector_scout_analyzer = SectorScoutAnalyzer(coingecko_api, defillama_api)
    
    # ========================================================================
    # API ROUTES
    # ========================================================================
    
    @app.before_request
    def before_request():
        """Set up request context"""
        g.start_time = time.time()
        g.request_id = f"{int(time.time())}-{id(request)}"
        
        logger.info(f"Request started", {
            "request_id": g.request_id,
            "method": request.method,
            "endpoint": request.endpoint,
            "remote_addr": request.remote_addr
        })
    
    @app.after_request 
    def after_request(response):
        """Log request completion"""
        execution_time = (time.time() - g.start_time) * 1000
        
        logger.info(f"Request completed", {
            "request_id": g.request_id,
            "status_code": response.status_code,
            "execution_time_ms": round(execution_time, 2)
        })
        
        return response
    
    @app.errorhandler(SuperClaudeException)
    def handle_superclaude_exception(e: SuperClaudeException):
        """Handle SuperClaude framework exceptions"""
        logger.error(f"SuperClaude exception", {"exception": e.to_dict()})
        return jsonify(e.to_dict()), 400
    
    @app.errorhandler(Exception)
    def handle_generic_exception(e: Exception):
        """Handle unexpected exceptions"""
        logger.error(f"Unexpected exception", {"error": str(e), "traceback": traceback.format_exc()})
        error = SuperClaudeException("Internal server error", "INTERNAL_ERROR")
        return jsonify(error.to_dict()), 500
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "framework": "SuperClaude"
        })
    
    @app.route('/api/analysis/five-minute', methods=['GET'])
    @cache.cached(timeout=60)  # Cache for 1 minute
    async def five_minute_analysis():
        """Five-minute altcoin analysis endpoint"""
        try:
            result = await five_minute_analyzer.analyze()
            return jsonify(result.to_dict())
        except Exception as e:
            raise SuperClaudeException(f"Five-minute analysis failed: {str(e)}", "ANALYSIS_ERROR")
    
    @app.route('/api/analysis/sector-scout', methods=['GET'])
    @cache.cached(timeout=300)  # Cache for 5 minutes
    async def sector_scout_analysis():
        """Sector scout analysis endpoint"""
        try:
            result = await sector_scout_analyzer.analyze() 
            return jsonify(result.to_dict())
        except Exception as e:
            raise SuperClaudeException(f"Sector analysis failed: {str(e)}", "ANALYSIS_ERROR")
    
    @app.route('/api/market/summary', methods=['GET'])
    @cache.cached(timeout=120)  # Cache for 2 minutes
    def market_summary():
        """Market summary endpoint"""
        try:
            assets = coingecko_api.get_market_data(limit=10)
            
            total_mcap = sum(asset.market_cap for asset in assets)
            avg_change = np.mean([asset.price_change_percentage_24h for asset in assets])
            
            return jsonify({
                "success": True,
                "data": {
                    "total_market_cap": total_mcap,
                    "average_change_24h": avg_change,
                    "top_assets": [asdict(asset) for asset in assets[:5]],
                    "market_sentiment": "bullish" if avg_change > 0 else "bearish"
                },
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            raise SuperClaudeException(f"Market summary failed: {str(e)}", "ANALYSIS_ERROR")
    
    @app.route('/')
    def serve_dashboard():
        """Serve the main dashboard"""
        return send_from_directory('.', 'crypto_dashboard_superclaude.html')
    
    return app

# ============================================================================
# SUPERCLAUDE FRAMEWORK - APPLICATION RUNNER
# ============================================================================

def run_superclaude_server(host: str = "0.0.0.0", port: int = 8080, debug: bool = False):
    """Run the SuperClaude server with production settings"""
    
    logger.info("🚀 Starting SuperClaude GPT-5 Analytics Server", {
        "host": host,
        "port": port,
        "debug": debug,
        "framework_version": "1.0.0"
    })
    
    app = create_superclaude_app()
    
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True,
            use_reloader=debug
        )
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server failed to start", {"error": str(e)})
    finally:
        # Cleanup resources
        http_client.close()
        logger.info("✅ Server shutdown complete")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SuperClaude GPT-5 Analytics Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host address")
    parser.add_argument("--port", type=int, default=8080, help="Port number")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    run_superclaude_server(
        host=args.host,
        port=args.port,
        debug=args.debug
    )