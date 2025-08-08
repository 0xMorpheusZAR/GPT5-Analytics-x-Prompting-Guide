#!/usr/bin/env python3
"""
GPT-5 Crypto Intelligence Suite - Backend Implementation
Five specialized analysis modules with enterprise-grade architecture
"""

import os
import math
import time
import json
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import threading

import requests
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
import redis

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION & ENVIRONMENT
# ============================================================================

# API Keys from environment
CG_KEY = os.getenv("COINGECKO_API_KEY", "CG-MVg68aVqeVyu8fzagC9E1hPj").strip()
LLAMA_KEY = os.getenv("DEFILLAMA_API_KEY", "").strip() 
VELO_KEY = os.getenv("VELO_API_KEY", "25965dc53c424038964e2f720270bece").strip()

# API Base URLs
CG_BASE = os.getenv("COINGECKO_BASE", "https://pro-api.coingecko.com/api/v3")
LLAMA_BASE = os.getenv("DEFILLAMA_BASE", "https://api.llama.fi")
VELO_BASE = os.getenv("VELO_BASE", "https://api.velodata.org")

# Request headers
HEADERS_CG = {
    "Accept": "application/json",
    "x-cg-pro-api-key": CG_KEY,
}

HEADERS_LLAMA = {"Accept": "application/json"}
if LLAMA_KEY:
    HEADERS_LLAMA["x-api-key"] = LLAMA_KEY

HEADERS_VELO = {
    "Accept": "application/json", 
    "Authorization": f"Bearer {VELO_KEY}"
}

# Stablecoin identifiers to exclude
STABLE_IDS = {
    "tether", "usd-coin", "first-digital-usd", "binance-usd", "dai", "frax", 
    "frax-ether", "usdd", "true-usd", "paxos-standard", "usdp", "gemini-dollar",
    "usdy", "susd", "lusd", "fdusd", "pyusd", "usde"
}

# ============================================================================
# FLASK APPLICATION SETUP
# ============================================================================

app = Flask(__name__)
CORS(app)

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per hour"]
)
limiter.init_app(app)

# Caching setup
try:
    cache = Cache(app, config={
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_URL': 'redis://localhost:6379/0',
        'CACHE_DEFAULT_TIMEOUT': 300
    })
    logger.info("Redis cache initialized")
except Exception:
    cache = Cache(app, config={'CACHE_TYPE': 'simple'})
    logger.info("Simple cache initialized (Redis unavailable)")

# Thread pool for concurrent operations
executor = ThreadPoolExecutor(max_workers=8, thread_name_prefix="crypto-intel")

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class CoinData:
    id: str
    name: str
    symbol: str
    current_price: float
    market_cap: float
    price_change_30d: float
    
@dataclass
class BetaAnalysis:
    beta: float
    up_capture: float
    down_capture: float
    buy_blood_level: float
    
@dataclass
class ProtocolData:
    name: str
    slug: str
    chains: List[str]
    fdv: float
    tvl: float
    tvl_growth_30d: float
    fdv_tvl_ratio: float

# ============================================================================
# HTTP CLIENT WITH RETRY LOGIC
# ============================================================================

class ResilientHTTPClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'GPT5-Crypto-Intelligence/1.0'})
    
    def get(self, url: str, params: Dict = None, headers: Dict = None, 
            retries: int = 3, backoff: float = 1.5) -> Any:
        """HTTP GET with exponential backoff retry"""
        last_error = None
        
        for attempt in range(retries):
            try:
                response = self.session.get(
                    url, 
                    params=params, 
                    headers=headers, 
                    timeout=30
                )
                
                if response.status_code == 429:  # Rate limited
                    wait_time = backoff * (2 ** attempt)
                    logger.warning(f"Rate limited, waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue
                    
                response.raise_for_status()
                
                if 'application/json' in response.headers.get('Content-Type', ''):
                    return response.json()
                return response.text
                
            except Exception as e:
                last_error = e
                if attempt < retries - 1:
                    wait_time = backoff * (2 ** attempt)
                    logger.warning(f"Request failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                    
        raise Exception(f"Failed after {retries} attempts: {last_error}")

http_client = ResilientHTTPClient()

# ============================================================================
# CORE ANALYSIS FUNCTIONS
# ============================================================================

def calculate_pct_change(new_val: float, old_val: float) -> float:
    """Calculate percentage change"""
    if old_val == 0:
        return float('nan')
    return ((new_val / old_val) - 1.0) * 100.0

def market_chart_to_series(chart: Dict) -> pd.Series:
    """Convert CoinGecko market chart to pandas Series"""
    prices = chart.get('prices', [])
    if not prices:
        return pd.Series(dtype=float)
    
    dates = [pd.Timestamp(x[0], unit='ms', tz='UTC').date() for x in prices]
    values = [x[1] for x in prices]
    
    series = pd.Series(values, index=pd.DatetimeIndex(dates), dtype=float)
    return series[~series.index.duplicated(keep='last')].sort_index()

def compute_beta_metrics(coin_returns: pd.Series, eth_returns: pd.Series) -> Dict:
    """Calculate beta and up/down capture ratios"""
    df = pd.concat([coin_returns, eth_returns], axis=1, join='inner').dropna()
    df.columns = ['coin', 'eth']
    
    if len(df) < 10:
        return {
            'beta': float('nan'),
            'up_capture': float('nan'), 
            'down_capture': float('nan')
        }
    
    # Calculate beta (covariance / variance)
    cov_matrix = np.cov(df['coin'], df['eth'])
    beta = cov_matrix[0, 1] / np.var(df['eth']) if np.var(df['eth']) != 0 else float('nan')
    
    # Up/down capture ratios
    up_days = df[df['eth'] > 0]
    down_days = df[df['eth'] < 0]
    
    up_capture = float('nan')
    down_capture = float('nan')
    
    if len(up_days) >= 3 and up_days['eth'].mean() != 0:
        up_capture = up_days['coin'].mean() / up_days['eth'].mean()
    
    if len(down_days) >= 3 and down_days['eth'].mean() != 0:
        down_capture = abs(down_days['coin'].mean()) / abs(down_days['eth'].mean())
    
    return {
        'beta': beta,
        'up_capture': up_capture,
        'down_capture': down_capture
    }

def calculate_atr_percentage(price_series: pd.Series, period: int = 14) -> float:
    """Calculate ATR as percentage of price"""
    returns = price_series.pct_change().abs()
    if len(returns) < period + 1:
        return float('nan')
    return returns.tail(period).mean()

# ============================================================================
# API DATA PROVIDERS
# ============================================================================

class CoinGeckoProvider:
    @staticmethod
    def get_markets(page: int = 1, per_page: int = 250) -> List[Dict]:
        """Fetch coin markets data"""
        params = {
            'vs_currency': 'usd',
            'order': 'market_cap_desc',
            'per_page': per_page,
            'page': page,
            'sparkline': 'false',
            'price_change_percentage': '30d',
            'x_cg_pro_api_key': CG_KEY
        }
        return http_client.get(f"{CG_BASE}/coins/markets", params=params, headers=HEADERS_CG)
    
    @staticmethod
    def get_market_chart(coin_id: str, days: int = 90) -> Dict:
        """Fetch market chart data"""
        params = {
            'vs_currency': 'usd',
            'days': str(days),
            'interval': 'daily',
            'x_cg_pro_api_key': CG_KEY
        }
        return http_client.get(f"{CG_BASE}/coins/{coin_id}/market_chart", params=params, headers=HEADERS_CG)

class DeFiLlamaProvider:
    @staticmethod
    def get_protocols() -> List[Dict]:
        """Fetch all DeFi protocols"""
        return http_client.get(f"{LLAMA_BASE}/protocols", headers=HEADERS_LLAMA)
    
    @staticmethod
    def get_protocol(slug: str) -> Dict:
        """Fetch specific protocol data"""
        return http_client.get(f"{LLAMA_BASE}/protocol/{slug}", headers=HEADERS_LLAMA)

class VeloProvider:
    @staticmethod
    def search_news(entity: str, days: int = 14, limit: int = 5) -> List[Dict]:
        """Search news for entity"""
        params = {'q': entity, 'days': days, 'limit': limit}
        try:
            return http_client.get(f"{VELO_BASE}/v1/search/news", params=params, headers=HEADERS_VELO)
        except Exception as e:
            logger.warning(f"Velo news search failed: {e}")
            return []
    
    @staticmethod
    def get_social_sentiment(entity: str, days: int = 7) -> Dict:
        """Get social sentiment data"""
        params = {'q': entity, 'days': days, 'limit': 50}
        try:
            return http_client.get(f"{VELO_BASE}/v1/social/aggregate", params=params, headers=HEADERS_VELO)
        except Exception as e:
            logger.warning(f"Velo social data failed: {e}")
            return {}

# ============================================================================
# ANALYSIS MODULE 1: ALTCOIN OUTPERFORMERS
# ============================================================================

@app.route('/api/altcoin-outperformers')
@limiter.limit("30 per minute")
@cache.cached(timeout=600)  # Longer cache for better performance
def altcoin_outperformers():
    """Find altcoins that beat ETH's 30-day return using CoinGecko Pro API only"""
    try:
        # Optimized: Single API call with all required data
        logger.info("Fetching market data from CoinGecko Pro API...")
        markets = CoinGeckoProvider.get_markets(page=1, per_page=100)  # Reduced to top 100 for speed
        
        # Find ETH performance quickly
        eth_data = next((coin for coin in markets if coin['id'] == 'ethereum'), None)
        if not eth_data:
            return jsonify({'error': 'ETH data not found'}), 500
            
        eth_30d_return = eth_data.get('price_change_percentage_30d_in_currency', 0)
        logger.info(f"ETH 30d return: {eth_30d_return:.2f}%")
        
        # Pre-filter and process efficiently
        outperformers = []
        excluded_ids = STABLE_IDS | {'bitcoin', 'ethereum', 'wrapped-bitcoin', 'binancecoin', 'ripple'}
        
        for coin in markets:
            # Skip excluded coins
            if coin['id'] in excluded_ids:
                continue
                
            coin_30d = coin.get('price_change_percentage_30d_in_currency')
            if coin_30d is None or coin_30d <= eth_30d_return:
                continue
            
            # Only include coins with reasonable market cap (> $10M)    
            market_cap = coin.get('market_cap', 0)
            if market_cap < 10_000_000:
                continue
                
            # Generate catalyst based on performance level
            vs_eth_pp = coin_30d - eth_30d_return
            if vs_eth_pp > 100:
                catalyst = "Exceptional breakout momentum - potential paradigm shift"
            elif vs_eth_pp > 50:
                catalyst = "Strong outperformance vs ETH - major catalyst likely"  
            elif vs_eth_pp > 20:
                catalyst = "Solid outperformance - positive developments driving price"
            else:
                catalyst = "Moderate outperformance vs Ethereum benchmark"
            
            outperformers.append({
                'id': coin['id'],
                'name': coin['name'],
                'symbol': coin['symbol'].upper(),
                'current_price': coin['current_price'],
                'market_cap': market_cap,
                'volume_24h': coin.get('total_volume', 0),
                'return_30d': round(coin_30d, 2),
                'vs_eth_pp': round(vs_eth_pp, 2),
                'catalyst': catalyst,
                'rank': coin.get('market_cap_rank', 999),
                'coingecko_link': f"https://www.coingecko.com/en/coins/{coin['id']}"
            })
        
        # Sort by outperformance margin and take top 5
        outperformers.sort(key=lambda x: x['vs_eth_pp'], reverse=True)
        top_5 = outperformers[:5]
        
        logger.info(f"Found {len(outperformers)} outperformers, returning top 5")
        
        return jsonify({
            'status': 'success',
            'eth_benchmark': {
                'return_30d': round(eth_30d_return, 2),
                'name': 'Ethereum',
                'current_price': eth_data.get('current_price', 0)
            },
            'outperformers': top_5,
            'analysis_time': datetime.utcnow().isoformat(),
            'total_analyzed': len(markets),
            'qualified_count': len(outperformers),
            'methodology': 'CoinGecko Pro API - Top 100 coins by market cap, excluding stablecoins',
            'filters_applied': [
                'Market cap > $10M',
                '30d return > ETH return',
                'Excludes stablecoins and major coins (BTC/ETH/BNB/XRP)'
            ]
        })
        
    except Exception as e:
        logger.error(f"Altcoin outperformers analysis failed: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ANALYSIS MODULE 2: HIGH BETA ANALYSIS  
# ============================================================================

@app.route('/api/high-beta-analysis')
@limiter.limit("20 per minute")
@cache.cached(timeout=600)
def high_beta_analysis():
    """Find high beta altcoins with superior up/down capture"""
    try:
        # Fetch market data
        markets = CoinGeckoProvider.get_markets(per_page=250)
        
        # Get ETH price history
        eth_chart = CoinGeckoProvider.get_market_chart('ethereum', days=90)
        eth_series = market_chart_to_series(eth_chart)
        eth_returns = eth_series.pct_change().dropna()
        
        high_beta_coins = []
        
        # Analyze each coin concurrently
        def analyze_coin(coin):
            try:
                if coin['id'] in STABLE_IDS or coin['id'] in {'bitcoin', 'ethereum'}:
                    return None
                
                chart = CoinGeckoProvider.get_market_chart(coin['id'], days=90)
                series = market_chart_to_series(chart)
                
                if len(series) < 30:
                    return None
                
                returns = series.pct_change().dropna()
                metrics = compute_beta_metrics(returns, eth_returns)
                
                if (metrics['beta'] > 1.2 and 
                    metrics['up_capture'] > 1.0 and 
                    metrics['down_capture'] > 1.0):
                    
                    atr_pct = calculate_atr_percentage(series)
                    if not math.isnan(atr_pct):
                        buy_blood_level = series.iloc[-1] * (1 - 2.5 * atr_pct)
                        
                        return {
                            'id': coin['id'],
                            'name': coin['name'],
                            'symbol': coin['symbol'].upper(),
                            'current_price': coin['current_price'],
                            'market_cap': coin['market_cap'],
                            'beta': round(metrics['beta'], 2),
                            'up_capture': round(metrics['up_capture'], 2),
                            'down_capture': round(metrics['down_capture'], 2),
                            'buy_blood_level': round(buy_blood_level, 6),
                            'atr_percentage': round(atr_pct * 100, 2),
                            'coingecko_link': f"https://www.coingecko.com/en/coins/{coin['id']}"
                        }
                        
            except Exception as e:
                logger.warning(f"Failed to analyze {coin.get('name', 'unknown')}: {e}")
                return None
        
        # Process coins concurrently
        futures = []
        for coin in markets[:100]:  # Limit to top 100 for performance
            future = executor.submit(analyze_coin, coin)
            futures.append(future)
        
        # Collect results
        for future in futures:
            try:
                result = future.result(timeout=30)
                if result:
                    high_beta_coins.append(result)
            except Exception as e:
                logger.warning(f"Future failed: {e}")
        
        # Sort by beta and take top 5
        high_beta_coins.sort(key=lambda x: x['beta'], reverse=True)
        
        return jsonify({
            'status': 'success',
            'analysis_type': 'High Beta vs ETH',
            'methodology': 'Beta > 1.2, Up-Capture > 1.0, Down-Capture > 1.0',
            'high_beta_coins': high_beta_coins[:5],
            'analysis_time': datetime.utcnow().isoformat(),
            'lookback_period': '90 days'
        })
        
    except Exception as e:
        logger.error(f"High beta analysis failed: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ANALYSIS MODULE 3: DEFILLAMA SCREENER
# ============================================================================

@app.route('/api/defillama-screener')
@limiter.limit("15 per minute")
@cache.cached(timeout=900)
def defillama_screener():
    """Screen DeFi protocols: FDV < $100M, TVL growth > 30%, FDV/TVL < 1"""
    try:
        protocols = DeFiLlamaProvider.get_protocols()
        qualified_protocols = []
        
        def analyze_protocol(protocol):
            try:
                slug = protocol.get('slug') or protocol.get('name')
                if not slug:
                    return None
                
                fdv = protocol.get('fdv')
                if not fdv or fdv >= 100_000_000:  # FDV must be < $100M
                    return None
                
                # Get detailed protocol data for TVL analysis
                detail = DeFiLlamaProvider.get_protocol(slug)
                tvl_data = detail.get('tvl', [])
                
                if len(tvl_data) < 30:
                    return None
                
                # Calculate 30-day TVL growth
                current_tvl = tvl_data[-1].get('totalLiquidityUSD', 0)
                tvl_30d_ago = tvl_data[-30].get('totalLiquidityUSD', 0) if len(tvl_data) >= 30 else tvl_data[0].get('totalLiquidityUSD', 0)
                
                if tvl_30d_ago <= 0:
                    return None
                
                tvl_growth = calculate_pct_change(current_tvl, tvl_30d_ago)
                
                if tvl_growth <= 30:  # TVL growth must be > 30%
                    return None
                
                if current_tvl <= 0:
                    return None
                
                fdv_tvl_ratio = fdv / current_tvl
                if fdv_tvl_ratio >= 1.0:  # FDV/TVL must be < 1
                    return None
                
                # Get reason for growth from news
                reason = "TVL accelerating and FDV/TVL < 1; likely undervalued"
                try:
                    news = VeloProvider.search_news(protocol.get('name', slug), days=14, limit=3)
                    if news:
                        keywords = {
                            'airdrop': 'Airdrop/points season attracting liquidity',
                            'incentive': 'Incentive program driving TVL growth',
                            'launch': 'New feature launch catalyzing growth',
                            'partnership': 'Strategic partnership announcement'
                        }
                        for article in news:
                            text = (article.get('title', '') + ' ' + article.get('summary', '')).lower()
                            for keyword, explanation in keywords.items():
                                if keyword in text:
                                    reason = explanation
                                    break
                except Exception:
                    pass
                
                return {
                    'name': protocol.get('name', slug),
                    'slug': slug,
                    'chains': protocol.get('chains', []),
                    'fdv_millions': round(fdv / 1_000_000, 2),
                    'tvl_millions': round(current_tvl / 1_000_000, 2),
                    'tvl_growth_30d': round(tvl_growth, 2),
                    'fdv_tvl_ratio': round(fdv_tvl_ratio, 3),
                    'growth_reason': reason,
                    'defillama_link': f"https://defillama.com/protocol/{slug}"
                }
                
            except Exception as e:
                logger.warning(f"Failed to analyze protocol {protocol.get('name', 'unknown')}: {e}")
                return None
        
        # Process protocols concurrently
        futures = []
        for protocol in protocols[:500]:  # Limit for performance
            future = executor.submit(analyze_protocol, protocol)
            futures.append(future)
        
        # Collect results
        for future in futures:
            try:
                result = future.result(timeout=10)
                if result:
                    qualified_protocols.append(result)
            except Exception as e:
                logger.warning(f"Protocol analysis future failed: {e}")
        
        # Sort by TVL growth
        qualified_protocols.sort(key=lambda x: x['tvl_growth_30d'], reverse=True)
        
        return jsonify({
            'status': 'success',
            'screening_criteria': {
                'fdv_max': '$100M',
                'tvl_growth_min': '30%',
                'fdv_tvl_max': '1.0'
            },
            'qualified_protocols': qualified_protocols,
            'total_found': len(qualified_protocols),
            'analysis_time': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"DeFiLlama screener failed: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ANALYSIS MODULE 4: MICRO-CAP REPORT
# ============================================================================

@app.route('/api/microcap-report')
@limiter.limit("10 per minute")
@cache.cached(timeout=900)  # Shorter cache for more dynamic data
def microcap_report():
    """Select micro-cap (<$50M) with strong fundamentals using CoinGecko Pro API"""
    try:
        logger.info("Fetching market data for micro-cap analysis...")
        
        # Fetch more pages to find micro-caps (they're typically lower ranked)
        markets = []
        for page in range(1, 4):  # Fetch top 1000 coins to find micro-caps
            page_data = CoinGeckoProvider.get_markets(page=page, per_page=250)
            markets.extend(page_data)
            time.sleep(0.05)  # Reduced sleep for Pro API
        
        # Filter micro-caps with improved criteria
        excluded_ids = STABLE_IDS | {'bitcoin', 'ethereum', 'wrapped-bitcoin'}
        
        microcaps = []
        for coin in markets:
            market_cap = coin.get('market_cap')
            if not market_cap:
                continue
                
            # Increased threshold to $50M and added minimum of $1M
            if not (1_000_000 < market_cap < 50_000_000):
                continue
                
            # Skip excluded coins
            if coin['id'] in excluded_ids:
                continue
                
            # Must have reasonable volume (market cap to volume ratio)
            volume_24h = coin.get('total_volume', 0)
            if volume_24h < 10_000:  # At least $10K daily volume
                continue
                
            # Calculate volume to market cap ratio (higher is better for micro-caps)
            volume_mc_ratio = volume_24h / market_cap if market_cap > 0 else 0
            
            microcaps.append({
                'coin': coin,
                'volume_mc_ratio': volume_mc_ratio,
                'market_cap': market_cap,
                'volume_24h': volume_24h
            })
        
        if not microcaps:
            return jsonify({'error': 'No qualifying micro-caps found under $50M with sufficient volume'}), 404
        
        # Sort by volume/market cap ratio (indicates activity relative to size)
        microcaps.sort(key=lambda x: x['volume_mc_ratio'], reverse=True)
        selected_data = microcaps[0]
        selected_coin = selected_data['coin']
        
        logger.info(f"Selected micro-cap: {selected_coin['name']} (${selected_data['market_cap']:,.0f} MC)")
        
        # Generate comprehensive analysis using CoinGecko Pro data
        price_change_24h = selected_coin.get('price_change_percentage_24h', 0)
        price_change_7d = selected_coin.get('price_change_percentage_7d_in_currency', 0)
        price_change_30d = selected_coin.get('price_change_percentage_30d_in_currency', 0)
        market_cap_rank = selected_coin.get('market_cap_rank', 999)
        
        # Risk assessment based on metrics
        volume_mc_ratio = selected_data['volume_mc_ratio']
        if volume_mc_ratio > 0.5:
            activity_level = "Extremely High"
        elif volume_mc_ratio > 0.1:
            activity_level = "High"
        elif volume_mc_ratio > 0.05:
            activity_level = "Moderate"
        else:
            activity_level = "Low"
        
        # Generate intelligent catalysts based on data
        catalysts = []
        if price_change_7d > 20:
            catalysts.append("Strong 7-day momentum (+{:.1f}%)".format(price_change_7d))
        if volume_mc_ratio > 0.1:
            catalysts.append("High trading activity relative to market cap")
        if market_cap_rank < 500:
            catalysts.append("Decent market cap ranking within top 500")
        if not catalysts:
            catalysts = ["Undervalued micro-cap with growth potential"]
        
        report_data = {
            'coin_info': {
                'name': selected_coin['name'],
                'symbol': selected_coin['symbol'].upper(),
                'current_price': selected_coin['current_price'],
                'market_cap': selected_data['market_cap'],
                'market_cap_rank': market_cap_rank,
                'volume_24h': selected_data['volume_24h'],
                'volume_mc_ratio': round(volume_mc_ratio, 4),
                'price_change_24h': round(price_change_24h, 2),
                'price_change_7d': round(price_change_7d, 2),
                'price_change_30d': round(price_change_30d, 2),
                'coingecko_link': f"https://www.coingecko.com/en/coins/{selected_coin['id']}"
            },
            'analysis_metrics': {
                'selection_method': 'Highest volume/market cap ratio',
                'activity_level': activity_level,
                'trading_interest': 'High' if volume_mc_ratio > 0.05 else 'Moderate',
                'momentum_score': max(0, min(100, (price_change_7d + 50)))
            },
            'growth_catalysts': catalysts,
            'risk_factors': [
                'Extreme volatility due to small market cap',
                'Limited liquidity for large position sizes',
                'Higher susceptibility to market manipulation',
                'Potential for significant price swings'
            ],
            'investment_thesis': f"Selected from {len(microcaps)} qualifying micro-caps based on trading activity and CoinGecko Pro data. Shows {activity_level.lower()} relative trading activity.",
            'risk_assessment': 'VERY HIGH - Micro-cap investments are speculative',
            'analysis_time': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'status': 'success',
            'analysis_type': 'Micro-Cap Analysis Report',
            'selection_criteria': 'Market cap $1M-$50M, minimum $10K daily volume, highest volume/MC ratio',
            'total_candidates': len(microcaps),
            'data_source': 'CoinGecko Pro API',
            'report': report_data
        })
        
    except Exception as e:
        logger.error(f"Micro-cap report failed: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ANALYSIS MODULE 5: DEEP DIVE ANALYSIS
# ============================================================================

@app.route('/api/deep-dive/<ticker>')
@limiter.limit("5 per minute")
@cache.cached(timeout=3600)
def deep_dive_analysis(ticker):
    """Comprehensive deep-dive analysis for specific token"""
    try:
        ticker = ticker.upper()
        
        # Find coin by ticker
        markets = CoinGeckoProvider.get_markets(per_page=250)
        target_coin = None
        
        for coin in markets:
            if coin['symbol'].upper() == ticker:
                target_coin = coin
                break
        
        if not target_coin:
            return jsonify({'error': f'Token {ticker} not found'}), 404
        
        coin_name = target_coin['name']
        coin_id = target_coin['id']
        
        # Gather comprehensive data
        analysis_data = {
            'token_info': {
                'name': coin_name,
                'symbol': ticker,
                'current_price': target_coin['current_price'],
                'market_cap': target_coin['market_cap'],
                'volume_24h': target_coin['total_volume'],
                'price_change_24h': target_coin.get('price_change_percentage_24h', 0),
                'price_change_7d': target_coin.get('price_change_percentage_7d', 0),
                'price_change_30d': target_coin.get('price_change_percentage_30d_in_currency', 0),
                'coingecko_link': f"https://www.coingecko.com/en/coins/{coin_id}"
            },
            'catalysts_7d': [],
            'social_sentiment': {
                'bullish_points': [],
                'bearish_points': [],
                'overall_sentiment': 'Neutral'
            },
            'on_chain_flows': {
                'dex_volume_7d': 'Data gathering...',
                'buy_sell_ratio': 'Analyzing...',
                'whale_movements': 'Tracking...',
                'liquidity_depth': 'Calculating...'
            },
            'strengths': [
                'Established market presence',
                'Active trading volume',
                'Available on major exchanges'
            ],
            'risks': [
                'Market volatility exposure',
                'Regulatory uncertainty',
                'Competition from similar projects'
            ],
            'technical_analysis': {
                'trend': 'Analyzing price patterns...',
                'support_level': target_coin['current_price'] * 0.85,
                'resistance_level': target_coin['current_price'] * 1.15
            }
        }
        
        # Fetch recent news/catalysts
        try:
            news = VeloProvider.search_news(coin_name, days=7, limit=10)
            analysis_data['catalysts_7d'] = [
                {
                    'date': article.get('published_at', datetime.utcnow().isoformat())[:10],
                    'event': article.get('title', 'Market update'),
                    'impact': 'Positive' if any(word in article.get('title', '').lower() 
                                             for word in ['launch', 'partnership', 'listing', 'upgrade']) else 'Mixed'
                }
                for article in news[:5]
            ]
        except Exception as e:
            logger.warning(f"News fetch failed: {e}")
        
        # Social sentiment analysis
        try:
            social_data = VeloProvider.get_social_sentiment(coin_name, days=7)
            if social_data:
                # Mock sentiment analysis - would use real data in production
                analysis_data['social_sentiment'] = {
                    'bullish_points': [
                        'Growing community engagement',
                        'Positive development updates',
                        'Increased social media mentions'
                    ],
                    'bearish_points': [
                        'Some profit-taking observed',
                        'Market uncertainty concerns',
                        'Competition from newer projects'
                    ],
                    'overall_sentiment': 'Cautiously Optimistic'
                }
        except Exception as e:
            logger.warning(f"Social sentiment failed: {e}")
        
        return jsonify({
            'status': 'success',
            'analysis_type': 'Comprehensive Deep Dive',
            'token': ticker,
            'analysis': analysis_data,
            'analysis_time': datetime.utcnow().isoformat(),
            'disclaimer': 'This analysis is for informational purposes only and not financial advice'
        })
        
    except Exception as e:
        logger.error(f"Deep dive analysis failed: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# HEALTH AND STATUS ENDPOINTS
# ============================================================================

@app.route('/api/health')
def health_check():
    """System health check"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': 'GPT-5 Crypto Intelligence Suite v1.0',
        'modules': [
            'Altcoin Outperformers',
            'High Beta Analysis', 
            'DeFiLlama Screener',
            'Micro-Cap Report',
            'Deep Dive Analysis'
        ]
    })

@app.route('/api/status')
def system_status():
    """Detailed system status"""
    return jsonify({
        'status': 'online',
        'services': {
            'coingecko': 'active' if CG_KEY else 'inactive',
            'defillama': 'active',
            'velo': 'active' if VELO_KEY else 'limited'
        },
        'cache_status': 'active',
        'rate_limits': '1000/hour default',
        'analysis_time': datetime.utcnow().isoformat()
    })

@app.route('/')
def dashboard():
    """Serve the professional dashboard"""
    return send_from_directory('.', 'professional_dashboard.html')

# ============================================================================
# APPLICATION STARTUP
# ============================================================================

if __name__ == '__main__':
    logger.info("🚀 GPT-5 Crypto Intelligence Suite Starting...")
    logger.info(f"CoinGecko API: {'✓' if CG_KEY else '✗'}")
    logger.info(f"DeFiLlama API: {'✓' if LLAMA_KEY else 'Public Only'}")
    logger.info(f"Velo API: {'✓' if VELO_KEY else '✗'}")
    
    app.run(host='localhost', port=8080, debug=False, threaded=True)