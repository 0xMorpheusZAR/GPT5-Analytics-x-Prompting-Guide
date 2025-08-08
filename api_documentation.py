#!/usr/bin/env python3
"""
SuperClaude API Documentation & Testing Suite
Comprehensive documentation and stress testing for all integrated APIs

APIs Covered:
- CoinGecko Pro API: Market data, price feeds, historical analysis
- DeFiLlama Pro API: Protocol TVL, yields, treasury data  
- Velo Data API: Advanced DeFi metrics and institutional data

Testing Philosophy:
- Evidence-Based: All endpoints tested with real requests
- Systematic Validation: Comprehensive test coverage
- Performance Verification: Stress testing under load
- Documentation Accuracy: Live API validation
"""

import os
import time
import json
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

import requests
import pandas as pd
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# ============================================================================
# API CONFIGURATION & CREDENTIALS
# ============================================================================

@dataclass
class APIConfig:
    """API configuration and credentials"""
    
    # CoinGecko Pro API
    coingecko_api_key: str = "CG-MVg68aVqeVyu8fzagC9E1hPj"
    coingecko_base_url: str = "https://pro-api.coingecko.com/api/v3"
    coingecko_rate_limit: int = 500  # requests per minute
    
    # DeFiLlama Pro API  
    defillama_api_key: str = "435722de8920d195d301a595f0c29ed939608c9b1da2d75905e85a68f3ee336d"
    defillama_base_url: str = "https://api.llama.fi"
    defillama_rate_limit: int = 300  # requests per minute
    
    # Velo Data API
    velo_api_key: str = "25965dc53c424038964e2f720270bece"
    velo_base_url: str = "https://api.velo.xyz"
    velo_rate_limit: int = 100  # requests per minute
    
    # Testing Configuration
    stress_test_duration: int = 30  # seconds
    concurrent_users: int = 5
    max_retries: int = 3
    request_timeout: int = 10

config = APIConfig()

# ============================================================================
# API ENDPOINT DEFINITIONS
# ============================================================================

@dataclass
class APIEndpoint:
    """API endpoint definition with testing parameters"""
    name: str
    method: str
    url: str
    headers: Dict[str, str]
    params: Dict[str, Any]
    description: str
    expected_fields: List[str]
    rate_limit_per_minute: int
    critical: bool = False  # Critical endpoints need < 200ms response time
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

# ============================================================================
# COINGECKO PRO API ENDPOINTS
# ============================================================================

class CoinGeckoProAPI:
    """CoinGecko Pro API endpoint definitions and testing"""
    
    def __init__(self):
        self.base_headers = {
            "Accept": "application/json",
            "x-cg-pro-api-key": config.coingecko_api_key
        }
        
        self.endpoints = [
            APIEndpoint(
                name="market_data",
                method="GET",
                url=f"{config.coingecko_base_url}/coins/markets",
                headers=self.base_headers,
                params={
                    "vs_currency": "usd",
                    "order": "market_cap_desc", 
                    "per_page": 100,
                    "page": 1,
                    "sparkline": False,
                    "price_change_percentage": "24h"
                },
                description="Get cryptocurrency market data with prices, market cap, volume",
                expected_fields=["id", "symbol", "name", "current_price", "market_cap", "total_volume"],
                rate_limit_per_minute=config.coingecko_rate_limit,
                critical=True
            ),
            
            APIEndpoint(
                name="price_history",
                method="GET",
                url=f"{config.coingecko_base_url}/coins/bitcoin/market_chart",
                headers=self.base_headers,
                params={
                    "vs_currency": "usd",
                    "days": 30,
                    "interval": "daily"
                },
                description="Get historical price data for specific cryptocurrency",
                expected_fields=["prices", "market_caps", "total_volumes"],
                rate_limit_per_minute=config.coingecko_rate_limit
            ),
            
            APIEndpoint(
                name="global_data",
                method="GET", 
                url=f"{config.coingecko_base_url}/global",
                headers=self.base_headers,
                params={},
                description="Get global cryptocurrency market statistics",
                expected_fields=["active_cryptocurrencies", "total_market_cap", "total_volume"],
                rate_limit_per_minute=config.coingecko_rate_limit
            ),
            
            APIEndpoint(
                name="trending_coins",
                method="GET",
                url=f"{config.coingecko_base_url}/search/trending",
                headers=self.base_headers,
                params={},
                description="Get trending cryptocurrencies",
                expected_fields=["coins", "nfts"],
                rate_limit_per_minute=config.coingecko_rate_limit
            ),
            
            APIEndpoint(
                name="coin_details",
                method="GET",
                url=f"{config.coingecko_base_url}/coins/ethereum",
                headers=self.base_headers,
                params={
                    "localization": False,
                    "tickers": False,
                    "market_data": True,
                    "community_data": False,
                    "developer_data": False
                },
                description="Get detailed information about specific cryptocurrency",
                expected_fields=["id", "symbol", "name", "market_data"],
                rate_limit_per_minute=config.coingecko_rate_limit
            )
        ]

# ============================================================================
# DEFILLAMA PRO API ENDPOINTS  
# ============================================================================

class DeFiLlamaProAPI:
    """DeFiLlama Pro API endpoint definitions and testing"""
    
    def __init__(self):
        self.base_headers = {
            "Accept": "application/json"
        }
        
        # Note: DeFiLlama Pro may require different authentication
        if config.defillama_api_key:
            self.base_headers["Authorization"] = f"Bearer {config.defillama_api_key}"
        
        self.endpoints = [
            APIEndpoint(
                name="protocols_list",
                method="GET",
                url=f"{config.defillama_base_url}/protocols",
                headers=self.base_headers,
                params={},
                description="Get list of all DeFi protocols with TVL data",
                expected_fields=["name", "symbol", "tvl", "chain", "category"],
                rate_limit_per_minute=config.defillama_rate_limit,
                critical=True
            ),
            
            APIEndpoint(
                name="protocol_tvl",
                method="GET",
                url=f"{config.defillama_base_url}/protocol/aave",
                headers=self.base_headers,
                params={},
                description="Get detailed TVL data for specific protocol",
                expected_fields=["tvl", "tokensInUsd", "tokens"],
                rate_limit_per_minute=config.defillama_rate_limit
            ),
            
            APIEndpoint(
                name="chains_tvl",
                method="GET",
                url=f"{config.defillama_base_url}/chains",
                headers=self.base_headers,
                params={},
                description="Get TVL data for all blockchain networks",
                expected_fields=["name", "tvl", "tokenSymbol"],
                rate_limit_per_minute=config.defillama_rate_limit
            ),
            
            APIEndpoint(
                name="yields_pools",
                method="GET",
                url=f"{config.defillama_base_url}/pools",
                headers=self.base_headers,
                params={},
                description="Get yield farming pool data",
                expected_fields=["pool", "chain", "project", "apy", "tvlUsd"],
                rate_limit_per_minute=config.defillama_rate_limit
            ),
            
            APIEndpoint(
                name="stablecoins",
                method="GET",
                url=f"{config.defillama_base_url}/stablecoins",
                headers=self.base_headers,
                params={
                    "includePrices": True
                },
                description="Get stablecoin market data and circulating supply",
                expected_fields=["name", "symbol", "circulating", "price"],
                rate_limit_per_minute=config.defillama_rate_limit
            )
        ]

# ============================================================================
# VELO DATA API ENDPOINTS
# ============================================================================

class VeloDataAPI:
    """Velo Data API endpoint definitions and testing"""
    
    def __init__(self):
        self.base_headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {config.velo_api_key}",
            "Content-Type": "application/json"
        }
        
        self.endpoints = [
            APIEndpoint(
                name="market_overview",
                method="GET", 
                url=f"{config.velo_base_url}/api/v1/market/overview",
                headers=self.base_headers,
                params={},
                description="Get comprehensive market overview and metrics",
                expected_fields=["market_cap", "volume", "dominance", "sentiment"],
                rate_limit_per_minute=config.velo_rate_limit,
                critical=True
            ),
            
            APIEndpoint(
                name="institutional_flows",
                method="GET",
                url=f"{config.velo_base_url}/api/v1/flows/institutional",
                headers=self.base_headers,
                params={
                    "timeframe": "24h"
                },
                description="Get institutional money flows and activity",
                expected_fields=["inflows", "outflows", "net_flow", "volume"],
                rate_limit_per_minute=config.velo_rate_limit
            ),
            
            APIEndpoint(
                name="options_flow", 
                method="GET",
                url=f"{config.velo_base_url}/api/v1/options/flow",
                headers=self.base_headers,
                params={
                    "asset": "BTC",
                    "timeframe": "1d"
                },
                description="Get options flow and derivatives data",
                expected_fields=["calls", "puts", "volume", "open_interest"],
                rate_limit_per_minute=config.velo_rate_limit
            ),
            
            APIEndpoint(
                name="sentiment_analysis",
                method="GET",
                url=f"{config.velo_base_url}/api/v1/sentiment/analysis",
                headers=self.base_headers,
                params={},
                description="Get market sentiment and social metrics",
                expected_fields=["sentiment_score", "social_volume", "mentions"],
                rate_limit_per_minute=config.velo_rate_limit
            ),
            
            APIEndpoint(
                name="whale_activity",
                method="GET", 
                url=f"{config.velo_base_url}/api/v1/whale/activity",
                headers=self.base_headers,
                params={
                    "min_value": 1000000,  # $1M minimum
                    "timeframe": "24h"
                },
                description="Get large transaction and whale activity data",
                expected_fields=["transactions", "total_value", "addresses"],
                rate_limit_per_minute=config.velo_rate_limit
            )
        ]

# ============================================================================
# API TESTING FRAMEWORK
# ============================================================================

@dataclass
class TestResult:
    """API test result data structure"""
    endpoint_name: str
    success: bool
    status_code: int
    response_time_ms: float
    data_size_bytes: int
    expected_fields_found: List[str]
    missing_fields: List[str]
    error_message: Optional[str]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "timestamp": self.timestamp.isoformat()
        }

class APITester:
    """Comprehensive API testing and validation framework"""
    
    def __init__(self):
        self.session = requests.Session()
        
        # Configure robust retry strategy
        retry_strategy = Retry(
            total=config.max_retries,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.test_results = []
        self.performance_metrics = {}
    
    def test_endpoint(self, endpoint: APIEndpoint) -> TestResult:
        """Test single API endpoint comprehensively"""
        print(f"Testing {endpoint.name}...")
        
        start_time = time.time()
        
        try:
            response = self.session.request(
                method=endpoint.method,
                url=endpoint.url,
                headers=endpoint.headers,
                params=endpoint.params,
                timeout=config.request_timeout
            )
            
            response_time_ms = (time.time() - start_time) * 1000
            
            # Validate status code
            if response.status_code != 200:
                return TestResult(
                    endpoint_name=endpoint.name,
                    success=False,
                    status_code=response.status_code,
                    response_time_ms=response_time_ms,
                    data_size_bytes=0,
                    expected_fields_found=[],
                    missing_fields=endpoint.expected_fields,
                    error_message=f"HTTP {response.status_code}: {response.text[:200]}",
                    timestamp=datetime.utcnow()
                )
            
            # Parse JSON response
            try:
                data = response.json()
                data_size_bytes = len(response.content)
            except ValueError as e:
                return TestResult(
                    endpoint_name=endpoint.name,
                    success=False,
                    status_code=response.status_code,
                    response_time_ms=response_time_ms,
                    data_size_bytes=len(response.content),
                    expected_fields_found=[],
                    missing_fields=endpoint.expected_fields,
                    error_message=f"Invalid JSON response: {str(e)}",
                    timestamp=datetime.utcnow()
                )
            
            # Validate expected fields
            expected_fields_found, missing_fields = self._validate_response_fields(data, endpoint.expected_fields)
            
            success = len(missing_fields) == 0
            
            result = TestResult(
                endpoint_name=endpoint.name,
                success=success,
                status_code=response.status_code,
                response_time_ms=response_time_ms,
                data_size_bytes=data_size_bytes,
                expected_fields_found=expected_fields_found,
                missing_fields=missing_fields,
                error_message=None,
                timestamp=datetime.utcnow()
            )
            
            # Log performance for critical endpoints
            if endpoint.critical and response_time_ms > 200:
                print(f"WARNING: Critical endpoint {endpoint.name} exceeded 200ms target: {response_time_ms:.1f}ms")
            
            return result
            
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return TestResult(
                endpoint_name=endpoint.name,
                success=False,
                status_code=0,
                response_time_ms=response_time_ms,
                data_size_bytes=0,
                expected_fields_found=[],
                missing_fields=endpoint.expected_fields,
                error_message=str(e),
                timestamp=datetime.utcnow()
            )
    
    def stress_test_endpoint(self, endpoint: APIEndpoint, duration_seconds: int = 30, concurrent_requests: int = 5) -> Dict[str, Any]:
        """Stress test endpoint with concurrent requests"""
        print(f"Stress testing {endpoint.name} for {duration_seconds}s with {concurrent_requests} concurrent requests...")
        
        results = []
        errors = []
        start_time = time.time()
        
        def make_request():
            """Make a single request"""
            try:
                request_start = time.time()
                response = self.session.request(
                    method=endpoint.method,
                    url=endpoint.url,
                    headers=endpoint.headers,
                    params=endpoint.params,
                    timeout=config.request_timeout
                )
                request_time = (time.time() - request_start) * 1000
                
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "response_time_ms": request_time,
                    "data_size_bytes": len(response.content)
                }
            except Exception as e:
                request_time = (time.time() - request_start) * 1000
                return {
                    "success": False,
                    "error": str(e),
                    "response_time_ms": request_time,
                    "data_size_bytes": 0
                }
        
        def worker():
            """Worker function for concurrent requests"""
            while time.time() - start_time < duration_seconds:
                result = make_request()
                if result["success"]:
                    results.append(result)
                else:
                    errors.append(result)
                time.sleep(60 / endpoint.rate_limit_per_minute)  # Respect rate limits
        
        # Start concurrent workers
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = [executor.submit(worker) for _ in range(concurrent_requests)]
            
            for future in as_completed(futures, timeout=duration_seconds + 10):
                try:
                    future.result()
                except Exception as e:
                    print(f"Worker error: {e}")
        
        # Calculate statistics
        if results:
            response_times = [r["response_time_ms"] for r in results]
            data_sizes = [r["data_size_bytes"] for r in results]
            
            stats = {
                "endpoint_name": endpoint.name,
                "duration_seconds": duration_seconds,
                "total_requests": len(results) + len(errors),
                "successful_requests": len(results),
                "failed_requests": len(errors),
                "success_rate": len(results) / (len(results) + len(errors)) * 100,
                "requests_per_second": len(results) / duration_seconds,
                "avg_response_time_ms": statistics.mean(response_times),
                "min_response_time_ms": min(response_times),
                "max_response_time_ms": max(response_times),
                "p50_response_time_ms": statistics.median(response_times),
                "p95_response_time_ms": sorted(response_times)[int(len(response_times) * 0.95)] if len(response_times) > 1 else response_times[0],
                "avg_data_size_bytes": statistics.mean(data_sizes) if data_sizes else 0,
                "total_data_transferred_mb": sum(data_sizes) / (1024 * 1024),
                "rate_limit_respected": len(results) <= (duration_seconds * endpoint.rate_limit_per_minute / 60),
                "performance_grade": self._calculate_performance_grade(statistics.mean(response_times), len(results) / (len(results) + len(errors)) * 100)
            }
        else:
            stats = {
                "endpoint_name": endpoint.name,
                "error": "No successful requests",
                "total_errors": len(errors)
            }
        
        return stats
    
    def test_all_apis(self) -> Dict[str, Any]:
        """Test all API endpoints systematically"""
        print("Starting comprehensive API testing...")
        
        apis = {
            "coingecko": CoinGeckoProAPI(),
            "defillama": DeFiLlamaProAPI(), 
            "velo": VeloDataAPI()
        }
        
        all_results = {
            "test_summary": {
                "start_time": datetime.utcnow().isoformat(),
                "total_endpoints": 0,
                "successful_endpoints": 0,
                "failed_endpoints": 0
            },
            "api_results": {},
            "performance_summary": {}
        }
        
        for api_name, api_instance in apis.items():
            print(f"\nTesting {api_name.upper()} API endpoints...")
            
            api_results = []
            for endpoint in api_instance.endpoints:
                # Basic functionality test
                result = self.test_endpoint(endpoint)
                api_results.append(result.to_dict())
                
                all_results["test_summary"]["total_endpoints"] += 1
                if result.success:
                    all_results["test_summary"]["successful_endpoints"] += 1
                else:
                    all_results["test_summary"]["failed_endpoints"] += 1
                
                # Stress test critical endpoints
                if result.success and endpoint.critical:
                    stress_stats = self.stress_test_endpoint(endpoint, duration_seconds=config.stress_test_duration)
                    result.stress_test_results = stress_stats
                
                time.sleep(1)  # Brief pause between tests
            
            all_results["api_results"][api_name] = api_results
        
        # Generate performance summary
        all_results["performance_summary"] = self._generate_performance_summary(all_results["api_results"])
        all_results["test_summary"]["end_time"] = datetime.utcnow().isoformat()
        
        return all_results
    
    def _validate_response_fields(self, data: Any, expected_fields: List[str]) -> Tuple[List[str], List[str]]:
        """Validate that response contains expected fields"""
        found_fields = []
        missing_fields = []
        
        def check_nested_fields(obj, field_path=""):
            """Recursively check nested object fields"""
            if isinstance(obj, dict):
                for key in obj.keys():
                    full_path = f"{field_path}.{key}" if field_path else key
                    if key in expected_fields or full_path in expected_fields:
                        found_fields.append(key)
                    check_nested_fields(obj[key], full_path)
            elif isinstance(obj, list) and len(obj) > 0:
                check_nested_fields(obj[0], field_path)  # Check first item in array
        
        check_nested_fields(data)
        
        for field in expected_fields:
            if field not in found_fields:
                missing_fields.append(field)
        
        return found_fields, missing_fields
    
    def _calculate_performance_grade(self, avg_response_time: float, success_rate: float) -> str:
        """Calculate performance grade for endpoint"""
        score = 100
        
        if avg_response_time > 500:  # > 500ms
            score -= 30
        elif avg_response_time > 200:  # > 200ms
            score -= 15
        
        if success_rate < 95:
            score -= 20
        elif success_rate < 99:
            score -= 10
        
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        else:
            return "F"
    
    def _generate_performance_summary(self, api_results: Dict[str, List]) -> Dict[str, Any]:
        """Generate comprehensive performance summary"""
        summary = {
            "total_apis_tested": len(api_results),
            "api_performance": {},
            "overall_stats": {
                "avg_response_time_ms": 0,
                "fastest_endpoint": {"name": "", "time_ms": float('inf')},
                "slowest_endpoint": {"name": "", "time_ms": 0},
                "highest_success_rate": {"name": "", "rate": 0},
                "lowest_success_rate": {"name": "", "rate": 100}
            }
        }
        
        all_response_times = []
        
        for api_name, results in api_results.items():
            api_times = [r["response_time_ms"] for r in results if r["success"]]
            api_success_rate = len([r for r in results if r["success"]]) / len(results) * 100 if results else 0
            
            if api_times:
                avg_time = statistics.mean(api_times)
                all_response_times.extend(api_times)
                
                summary["api_performance"][api_name] = {
                    "avg_response_time_ms": avg_time,
                    "success_rate": api_success_rate,
                    "total_endpoints": len(results),
                    "successful_endpoints": len([r for r in results if r["success"]]),
                    "performance_grade": self._calculate_performance_grade(avg_time, api_success_rate)
                }
                
                # Track overall fastest/slowest
                fastest_in_api = min(api_times)
                slowest_in_api = max(api_times)
                
                if fastest_in_api < summary["overall_stats"]["fastest_endpoint"]["time_ms"]:
                    summary["overall_stats"]["fastest_endpoint"] = {
                        "name": f"{api_name} (fastest endpoint)",
                        "time_ms": fastest_in_api
                    }
                
                if slowest_in_api > summary["overall_stats"]["slowest_endpoint"]["time_ms"]:
                    summary["overall_stats"]["slowest_endpoint"] = {
                        "name": f"{api_name} (slowest endpoint)", 
                        "time_ms": slowest_in_api
                    }
        
        if all_response_times:
            summary["overall_stats"]["avg_response_time_ms"] = statistics.mean(all_response_times)
        
        return summary

# ============================================================================
# DOCUMENTATION GENERATOR
# ============================================================================

class APIDocumentationGenerator:
    """Generate comprehensive API documentation from test results"""
    
    def __init__(self, test_results: Dict[str, Any]):
        self.test_results = test_results
    
    def generate_markdown_documentation(self) -> str:
        """Generate comprehensive markdown documentation"""
        doc_lines = [
            "# SuperClaude API Documentation & Testing Report",
            "",
            "Comprehensive documentation and stress testing results for all integrated APIs in the SuperClaude GPT-5 Analytics framework.",
            "",
            f"**Generated:** {datetime.utcnow().isoformat()}",
            "",
            "## Test Summary",
            "",
            f"- **Total Endpoints Tested:** {self.test_results['test_summary']['total_endpoints']}",
            f"- **Successful Tests:** {self.test_results['test_summary']['successful_endpoints']}",
            f"- **Failed Tests:** {self.test_results['test_summary']['failed_endpoints']}",
            f"- **Success Rate:** {(self.test_results['test_summary']['successful_endpoints'] / self.test_results['test_summary']['total_endpoints'] * 100):.1f}%",
            "",
            "## Performance Overview",
            "",
        ]
        
        # Add performance summary
        perf_summary = self.test_results.get("performance_summary", {})
        if perf_summary:
            doc_lines.extend([
                f"- **Average Response Time:** {perf_summary.get('overall_stats', {}).get('avg_response_time_ms', 0):.1f}ms",
                f"- **Fastest Endpoint:** {perf_summary.get('overall_stats', {}).get('fastest_endpoint', {}).get('name', 'N/A')} ({perf_summary.get('overall_stats', {}).get('fastest_endpoint', {}).get('time_ms', 0):.1f}ms)",
                f"- **Slowest Endpoint:** {perf_summary.get('overall_stats', {}).get('slowest_endpoint', {}).get('name', 'N/A')} ({perf_summary.get('overall_stats', {}).get('slowest_endpoint', {}).get('time_ms', 0):.1f}ms)",
                ""
            ])
        
        # Document each API
        for api_name, results in self.test_results.get("api_results", {}).items():
            doc_lines.extend(self._generate_api_documentation(api_name, results))
        
        return "\n".join(doc_lines)
    
    def _generate_api_documentation(self, api_name: str, results: List[Dict]) -> List[str]:
        """Generate documentation for specific API"""
        api_title = api_name.replace("_", " ").title()
        
        doc_lines = [
            f"## {api_title} API",
            "",
            f"**Base URL:** {self._get_base_url(api_name)}",
            f"**Rate Limit:** {self._get_rate_limit(api_name)} requests/minute",
            f"**Authentication:** {'API Key Required' if self._requires_auth(api_name) else 'Public API'}",
            "",
            "### Endpoints",
            ""
        ]
        
        for result in results:
            status_emoji = "[PASS]" if result["success"] else "[FAIL]"
            performance_indicator = "[FAST]" if result["response_time_ms"] < 200 else "[MEDIUM]" if result["response_time_ms"] < 500 else "[SLOW]"
            
            doc_lines.extend([
                f"#### {status_emoji} {result['endpoint_name'].replace('_', ' ').title()}",
                "",
                f"- **Status:** {'PASS' if result['success'] else 'FAIL'}",
                f"- **Response Time:** {performance_indicator} {result['response_time_ms']:.1f}ms",
                f"- **Data Size:** {result['data_size_bytes']} bytes",
                f"- **HTTP Status:** {result['status_code']}",
            ])
            
            if result["expected_fields_found"]:
                doc_lines.extend([
                    f"- **Fields Found:** {', '.join(result['expected_fields_found'][:5])}{'...' if len(result['expected_fields_found']) > 5 else ''}",
                ])
            
            if result["missing_fields"]:
                doc_lines.extend([
                    f"- **Missing Fields:** {', '.join(result['missing_fields'])}",
                ])
            
            if result["error_message"]:
                doc_lines.extend([
                    f"- **Error:** {result['error_message'][:100]}{'...' if len(result['error_message']) > 100 else ''}",
                ])
            
            # Add stress test results if available
            if hasattr(result, 'stress_test_results'):
                stress_results = result.stress_test_results
                doc_lines.extend([
                    "",
                    "**Stress Test Results:**",
                    f"- Requests/Second: {stress_results.get('requests_per_second', 0):.1f}",
                    f"- Success Rate: {stress_results.get('success_rate', 0):.1f}%",
                    f"- P95 Response Time: {stress_results.get('p95_response_time_ms', 0):.1f}ms",
                    f"- Performance Grade: {stress_results.get('performance_grade', 'N/A')}",
                ])
            
            doc_lines.append("")
        
        return doc_lines
    
    def _get_base_url(self, api_name: str) -> str:
        """Get base URL for API"""
        urls = {
            "coingecko": config.coingecko_base_url,
            "defillama": config.defillama_base_url,
            "velo": config.velo_base_url
        }
        return urls.get(api_name, "Unknown")
    
    def _get_rate_limit(self, api_name: str) -> int:
        """Get rate limit for API"""
        limits = {
            "coingecko": config.coingecko_rate_limit,
            "defillama": config.defillama_rate_limit,
            "velo": config.velo_rate_limit
        }
        return limits.get(api_name, 0)
    
    def _requires_auth(self, api_name: str) -> bool:
        """Check if API requires authentication"""
        return api_name in ["coingecko", "velo"]  # DeFiLlama may be public

# ============================================================================
# MAIN TESTING EXECUTION
# ============================================================================

def run_comprehensive_api_testing():
    """Run comprehensive API testing and generate documentation"""
    print("SuperClaude Comprehensive API Testing Suite")
    print("=" * 60)
    
    # Initialize tester
    tester = APITester()
    
    # Run all tests
    test_results = tester.test_all_apis()
    
    # Generate documentation
    doc_generator = APIDocumentationGenerator(test_results)
    documentation = doc_generator.generate_markdown_documentation()
    
    # Save results
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    # Save test results as JSON
    results_filename = f"api_test_results_{timestamp}.json"
    with open(results_filename, 'w') as f:
        json.dump(test_results, f, indent=2, default=str)
    
    # Save documentation as Markdown
    doc_filename = f"API_DOCUMENTATION_{timestamp}.md"
    with open(doc_filename, 'w') as f:
        f.write(documentation)
    
    print(f"\nTesting completed successfully!")
    print(f"Test results saved to: {results_filename}")
    print(f"Documentation saved to: {doc_filename}")
    
    # Print summary
    summary = test_results["test_summary"]
    print(f"\nSummary:")
    print(f"  Total endpoints: {summary['total_endpoints']}")
    print(f"  Successful: {summary['successful_endpoints']}")
    print(f"  Failed: {summary['failed_endpoints']}")
    print(f"  Success rate: {(summary['successful_endpoints'] / summary['total_endpoints'] * 100):.1f}%")
    
    return test_results, documentation

if __name__ == "__main__":
    # Run the comprehensive API testing suite
    results, docs = run_comprehensive_api_testing()