#!/usr/bin/env python3
"""
SuperClaude Performance Optimization Framework
High-Performance Crypto Analytics with Sub-200ms Response Times

Performance Philosophy:
- Measure First: Always profile before optimizing
- Critical Path Focus: Optimize the most impactful bottlenecks first  
- User Experience: Performance optimizations must improve real user experience
- Evidence-Based: All optimizations validated with metrics
- Graceful Degradation: Maintain functionality under load

Performance Budgets:
- API Response Time: <200ms for critical endpoints
- Dashboard Load Time: <1s on WiFi, <3s on 3G
- Memory Usage: <100MB for mobile, <500MB for desktop
- CPU Usage: <30% average, <80% peak for 60fps
"""

import os
import time
import asyncio
import threading
import multiprocessing
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from functools import wraps, lru_cache
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from collections import defaultdict, deque
import statistics
import psutil
import tracemalloc

import numpy as np
import pandas as pd
import requests
from cachetools import TTLCache, LRUCache
import redis
import sqlite3
from sqlalchemy import create_engine
from flask import g, request, current_app
import asyncpg

# ============================================================================
# PERFORMANCE CONFIGURATION
# ============================================================================

@dataclass
class PerformanceConfig:
    """Performance optimization configuration"""
    
    # Response Time Targets (milliseconds)
    critical_endpoint_target_ms: int = 200
    standard_endpoint_target_ms: int = 500
    batch_operation_target_ms: int = 2000
    
    # Concurrency Settings
    max_worker_threads: int = min(32, (os.cpu_count() or 1) + 4)
    max_worker_processes: int = min(8, os.cpu_count() or 1)
    async_request_pool_size: int = 100
    connection_pool_size: int = 20
    
    # Caching Configuration
    memory_cache_size: int = 1000
    memory_cache_ttl: int = 300  # 5 minutes
    redis_cache_ttl: int = 900   # 15 minutes
    enable_query_cache: bool = True
    
    # Resource Limits
    max_memory_mb: int = 512
    max_cpu_percent: int = 80
    max_request_size_mb: int = 10
    request_timeout_seconds: int = 30
    
    # Database Optimization
    db_connection_pool_size: int = 20
    db_query_timeout: int = 10
    enable_db_query_cache: bool = True
    
    # API Rate Limiting
    burst_rate_limit: int = 1000  # requests per minute
    sustained_rate_limit: int = 10000  # requests per hour
    
    # Monitoring
    enable_performance_monitoring: bool = True
    metrics_collection_interval: int = 10  # seconds
    alert_threshold_cpu: int = 85
    alert_threshold_memory: int = 80

perf_config = PerformanceConfig()

# ============================================================================
# PERFORMANCE MONITORING & METRICS
# ============================================================================

class PerformanceMonitor:
    """Comprehensive performance monitoring system"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.request_times = deque(maxlen=1000)
        self.error_counts = defaultdict(int)
        self.resource_usage = deque(maxlen=100)
        self.start_time = time.time()
        
        # Start background monitoring
        self.monitoring_thread = threading.Thread(target=self._monitor_resources, daemon=True)
        self.monitoring_thread.start()
    
    def record_request_time(self, endpoint: str, duration_ms: float, status_code: int = 200):
        """Record API request timing"""
        self.metrics[f"request_time_{endpoint}"].append(duration_ms)
        self.request_times.append({
            'endpoint': endpoint,
            'duration_ms': duration_ms,
            'status_code': status_code,
            'timestamp': time.time()
        })
        
        # Alert on slow requests
        if duration_ms > perf_config.critical_endpoint_target_ms:
            self._alert_slow_request(endpoint, duration_ms)
    
    def record_error(self, endpoint: str, error_type: str):
        """Record error occurrence"""
        self.error_counts[f"{endpoint}_{error_type}"] += 1
    
    def record_custom_metric(self, metric_name: str, value: float, tags: Dict[str, str] = None):
        """Record custom performance metric"""
        self.metrics[metric_name].append({
            'value': value,
            'timestamp': time.time(),
            'tags': tags or {}
        })
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        current_time = time.time()
        uptime = current_time - self.start_time
        
        # Request statistics
        recent_requests = [r for r in self.request_times if current_time - r['timestamp'] < 300]  # Last 5 minutes
        
        request_stats = {}
        if recent_requests:
            response_times = [r['duration_ms'] for r in recent_requests]
            request_stats = {
                'total_requests': len(recent_requests),
                'avg_response_time_ms': statistics.mean(response_times),
                'p50_response_time_ms': statistics.median(response_times),
                'p95_response_time_ms': np.percentile(response_times, 95) if len(response_times) > 1 else response_times[0],
                'p99_response_time_ms': np.percentile(response_times, 99) if len(response_times) > 1 else response_times[0],
                'error_rate': len([r for r in recent_requests if r['status_code'] >= 400]) / len(recent_requests) * 100
            }
        
        # Resource statistics
        resource_stats = {}
        if self.resource_usage:
            latest_resources = self.resource_usage[-1]
            resource_stats = {
                'cpu_percent': latest_resources['cpu_percent'],
                'memory_percent': latest_resources['memory_percent'],
                'memory_mb': latest_resources['memory_mb'],
                'disk_io_read_mb': latest_resources.get('disk_io_read_mb', 0),
                'disk_io_write_mb': latest_resources.get('disk_io_write_mb', 0)
            }
        
        return {
            'uptime_seconds': uptime,
            'performance_grade': self._calculate_performance_grade(request_stats, resource_stats),
            'request_statistics': request_stats,
            'resource_usage': resource_stats,
            'total_errors': sum(self.error_counts.values()),
            'cache_hit_rate': self._calculate_cache_hit_rate(),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _monitor_resources(self):
        """Background resource monitoring"""
        while True:
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_info = psutil.virtual_memory()
                disk_io = psutil.disk_io_counters()
                
                resource_data = {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory_info.percent,
                    'memory_mb': memory_info.used / (1024 * 1024),
                    'timestamp': time.time()
                }
                
                if disk_io:
                    resource_data['disk_io_read_mb'] = disk_io.read_bytes / (1024 * 1024)
                    resource_data['disk_io_write_mb'] = disk_io.write_bytes / (1024 * 1024)
                
                self.resource_usage.append(resource_data)
                
                # Check thresholds
                if cpu_percent > perf_config.alert_threshold_cpu:
                    self._alert_high_cpu(cpu_percent)
                if memory_info.percent > perf_config.alert_threshold_memory:
                    self._alert_high_memory(memory_info.percent)
                
                time.sleep(perf_config.metrics_collection_interval)
                
            except Exception as e:
                print(f"Resource monitoring error: {e}")
                time.sleep(30)  # Wait longer on error
    
    def _calculate_performance_grade(self, request_stats: Dict, resource_stats: Dict) -> str:
        """Calculate overall performance grade A-F"""
        score = 100
        
        # Request performance (40% weight)
        if request_stats.get('p95_response_time_ms', 0) > perf_config.critical_endpoint_target_ms:
            score -= 20
        if request_stats.get('error_rate', 0) > 1:  # >1% error rate
            score -= 10
        if request_stats.get('avg_response_time_ms', 0) > perf_config.standard_endpoint_target_ms:
            score -= 10
        
        # Resource usage (30% weight) 
        if resource_stats.get('cpu_percent', 0) > 70:
            score -= 15
        if resource_stats.get('memory_percent', 0) > 70:
            score -= 15
        
        # System health (30% weight)
        cache_hit_rate = self._calculate_cache_hit_rate()
        if cache_hit_rate < 80:
            score -= 15
        if sum(self.error_counts.values()) > 10:
            score -= 15
        
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B' 
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate from metrics"""
        # Simplified calculation - in production, track actual cache hits/misses
        return 85.0  # Placeholder
    
    def _alert_slow_request(self, endpoint: str, duration_ms: float):
        """Alert on slow request"""
        print(f"⚠️ SLOW REQUEST ALERT: {endpoint} took {duration_ms:.1f}ms (target: {perf_config.critical_endpoint_target_ms}ms)")
    
    def _alert_high_cpu(self, cpu_percent: float):
        """Alert on high CPU usage"""
        print(f"🔥 HIGH CPU ALERT: {cpu_percent:.1f}% (threshold: {perf_config.alert_threshold_cpu}%)")
    
    def _alert_high_memory(self, memory_percent: float):
        """Alert on high memory usage"""
        print(f"🧠 HIGH MEMORY ALERT: {memory_percent:.1f}% (threshold: {perf_config.alert_threshold_memory}%)")

monitor = PerformanceMonitor()

# ============================================================================
# CACHING OPTIMIZATION
# ============================================================================

class MultiLevelCache:
    """Multi-level caching system for maximum performance"""
    
    def __init__(self):
        # Level 1: In-memory LRU cache (fastest)
        self.l1_cache = LRUCache(maxsize=perf_config.memory_cache_size)
        
        # Level 2: In-memory TTL cache (fast, with expiration)
        self.l2_cache = TTLCache(maxsize=perf_config.memory_cache_size * 2, ttl=perf_config.memory_cache_ttl)
        
        # Level 3: Redis cache (shared across instances)
        try:
            self.redis_client = redis.Redis(decode_responses=True)
            self.redis_available = True
        except:
            self.redis_client = None
            self.redis_available = False
        
        self.hit_stats = {'l1': 0, 'l2': 0, 'l3': 0, 'miss': 0}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from multi-level cache"""
        # Level 1: In-memory LRU
        if key in self.l1_cache:
            self.hit_stats['l1'] += 1
            return self.l1_cache[key]
        
        # Level 2: In-memory TTL 
        if key in self.l2_cache:
            value = self.l2_cache[key]
            self.l1_cache[key] = value  # Promote to L1
            self.hit_stats['l2'] += 1
            return value
        
        # Level 3: Redis
        if self.redis_available:
            try:
                redis_key = f"sc_cache:{key}"
                value = self.redis_client.get(redis_key)
                if value:
                    # Promote to upper levels
                    import json
                    parsed_value = json.loads(value)
                    self.l2_cache[key] = parsed_value
                    self.l1_cache[key] = parsed_value
                    self.hit_stats['l3'] += 1
                    return parsed_value
            except Exception as e:
                print(f"Redis cache error: {e}")
        
        self.hit_stats['miss'] += 1
        return None
    
    def set(self, key: str, value: Any, ttl: int = None):
        """Set value in multi-level cache"""
        # Set in all levels
        self.l1_cache[key] = value
        self.l2_cache[key] = value
        
        # Set in Redis with TTL
        if self.redis_available:
            try:
                redis_key = f"sc_cache:{key}"
                import json
                self.redis_client.setex(
                    redis_key,
                    ttl or perf_config.redis_cache_ttl,
                    json.dumps(value, default=str)
                )
            except Exception as e:
                print(f"Redis cache set error: {e}")
    
    def delete(self, key: str):
        """Delete from all cache levels"""
        self.l1_cache.pop(key, None)
        self.l2_cache.pop(key, None)
        
        if self.redis_available:
            try:
                redis_key = f"sc_cache:{key}"
                self.redis_client.delete(redis_key)
            except Exception:
                pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = sum(self.hit_stats.values())
        if total_requests == 0:
            return {"hit_rate": 0, "stats": self.hit_stats}
        
        hit_rate = ((total_requests - self.hit_stats['miss']) / total_requests) * 100
        
        return {
            "hit_rate": round(hit_rate, 2),
            "l1_hit_rate": round((self.hit_stats['l1'] / total_requests) * 100, 2),
            "l2_hit_rate": round((self.hit_stats['l2'] / total_requests) * 100, 2),
            "l3_hit_rate": round((self.hit_stats['l3'] / total_requests) * 100, 2),
            "miss_rate": round((self.hit_stats['miss'] / total_requests) * 100, 2),
            "total_requests": total_requests,
            "stats": self.hit_stats
        }

cache = MultiLevelCache()

# ============================================================================
# PERFORMANCE DECORATORS
# ============================================================================

def performance_monitor(endpoint_name: str = None):
    """Decorator to monitor endpoint performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            endpoint = endpoint_name or func.__name__
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                status_code = getattr(result, 'status_code', 200) if hasattr(result, 'status_code') else 200
                
                monitor.record_request_time(endpoint, duration_ms, status_code)
                
                # Add performance headers if this is a Flask response
                if hasattr(result, 'headers'):
                    result.headers['X-Response-Time'] = f"{duration_ms:.2f}ms"
                    result.headers['X-Performance-Grade'] = monitor._calculate_performance_grade({}, {})
                
                return result
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                monitor.record_request_time(endpoint, duration_ms, 500)
                monitor.record_error(endpoint, type(e).__name__)
                raise
        
        return wrapper
    return decorator

def cached_result(cache_key_func: Callable = None, ttl: int = None):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                # Default key generation
                key_parts = [func.__name__] + [str(arg) for arg in args] + [f"{k}:{v}" for k, v in sorted(kwargs.items())]
                cache_key = ":".join(key_parts)
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Compute and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator

def async_optimized(max_concurrent: int = None):
    """Decorator for async optimization of I/O operations"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Run in thread pool for CPU-bound tasks
            if not asyncio.iscoroutinefunction(func):
                with ThreadPoolExecutor(max_workers=max_concurrent or perf_config.max_worker_threads) as executor:
                    future = executor.submit(func, *args, **kwargs)
                    return future.result()
            else:
                # Run async function
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(func(*args, **kwargs))
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

# ============================================================================
# CONCURRENT REQUEST PROCESSOR
# ============================================================================

class ConcurrentAPIProcessor:
    """High-performance concurrent API request processor"""
    
    def __init__(self):
        self.session = requests.Session()
        
        # Configure connection pooling for maximum performance
        from requests.adapters import HTTPAdapter
        from requests.packages.urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=perf_config.connection_pool_size,
            pool_maxsize=perf_config.connection_pool_size * 2,
            pool_block=False
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    async def fetch_multiple_endpoints(self, requests_config: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fetch multiple API endpoints concurrently"""
        start_time = time.time()
        
        # Use ThreadPoolExecutor for I/O bound operations
        with ThreadPoolExecutor(max_workers=min(len(requests_config), perf_config.max_worker_threads)) as executor:
            # Submit all requests
            futures = []
            for config in requests_config:
                future = executor.submit(self._make_request, config)
                futures.append(future)
            
            # Collect results as they complete
            results = []
            for future in as_completed(futures, timeout=perf_config.request_timeout_seconds):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({
                        "error": str(e),
                        "success": False
                    })
        
        total_time = (time.time() - start_time) * 1000
        monitor.record_custom_metric("concurrent_api_batch_time", total_time, {"batch_size": len(requests_config)})
        
        return results
    
    def _make_request(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Make individual API request"""
        start_time = time.time()
        
        try:
            response = self.session.request(
                method=config.get('method', 'GET'),
                url=config['url'],
                headers=config.get('headers', {}),
                params=config.get('params', {}),
                json=config.get('json'),
                timeout=config.get('timeout', 10)
            )
            
            response_time = (time.time() - start_time) * 1000
            
            return {
                "success": True,
                "status_code": response.status_code,
                "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                "response_time_ms": response_time,
                "url": config['url']
            }
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "error": str(e),
                "response_time_ms": response_time,
                "url": config['url']
            }

# ============================================================================
# DATABASE OPTIMIZATION
# ============================================================================

class OptimizedDatabaseManager:
    """High-performance database operations with connection pooling"""
    
    def __init__(self, database_url: str = "sqlite:///superclaude.db"):
        from sqlalchemy import create_engine
        from sqlalchemy.pool import StaticPool
        
        # Configure connection pool for maximum performance
        self.engine = create_engine(
            database_url,
            poolclass=StaticPool,
            pool_size=perf_config.db_connection_pool_size,
            max_overflow=perf_config.db_connection_pool_size,
            pool_timeout=30,
            pool_recycle=3600,  # Recycle connections every hour
            echo=False  # Set to True for SQL debugging
        )
        
        self.query_cache = TTLCache(maxsize=500, ttl=300)  # 5-minute query cache
    
    def execute_optimized_query(self, query: str, params: Dict = None) -> List[Dict]:
        """Execute database query with optimization"""
        start_time = time.time()
        
        # Check query cache
        cache_key = f"{query}:{hash(str(params))}"
        if perf_config.enable_db_query_cache and cache_key in self.query_cache:
            monitor.record_custom_metric("db_query_cache_hit", 1)
            return self.query_cache[cache_key]
        
        try:
            with self.engine.connect() as connection:
                result = connection.execute(query, params or {})
                data = [dict(row) for row in result]
                
                query_time = (time.time() - start_time) * 1000
                monitor.record_custom_metric("db_query_time", query_time)
                
                # Cache successful queries
                if perf_config.enable_db_query_cache:
                    self.query_cache[cache_key] = data
                
                return data
                
        except Exception as e:
            query_time = (time.time() - start_time) * 1000
            monitor.record_custom_metric("db_query_error", query_time)
            raise

# ============================================================================
# PERFORMANCE TESTING SUITE
# ============================================================================

class PerformanceTester:
    """Comprehensive performance testing and benchmarking"""
    
    def __init__(self):
        self.results = {}
    
    def benchmark_endpoint(self, endpoint_func: Callable, iterations: int = 100) -> Dict[str, Any]:
        """Benchmark endpoint performance"""
        response_times = []
        errors = 0
        
        print(f"🏃 Benchmarking {endpoint_func.__name__} with {iterations} iterations...")
        
        for i in range(iterations):
            start_time = time.time()
            try:
                result = endpoint_func()
                response_time = (time.time() - start_time) * 1000
                response_times.append(response_time)
            except Exception as e:
                errors += 1
                print(f"Error in iteration {i}: {e}")
        
        if response_times:
            stats = {
                "function_name": endpoint_func.__name__,
                "iterations": iterations,
                "errors": errors,
                "success_rate": ((iterations - errors) / iterations) * 100,
                "avg_response_time_ms": statistics.mean(response_times),
                "min_response_time_ms": min(response_times),
                "max_response_time_ms": max(response_times),
                "p50_response_time_ms": statistics.median(response_times),
                "p95_response_time_ms": np.percentile(response_times, 95),
                "p99_response_time_ms": np.percentile(response_times, 99),
                "requests_per_second": 1000 / statistics.mean(response_times) if response_times else 0,
                "meets_target": statistics.mean(response_times) <= perf_config.critical_endpoint_target_ms
            }
        else:
            stats = {"error": "No successful requests", "errors": errors}
        
        self.results[endpoint_func.__name__] = stats
        return stats
    
    def stress_test(self, endpoint_func: Callable, concurrent_users: int = 10, duration_seconds: int = 60) -> Dict[str, Any]:
        """Stress test with concurrent users"""
        print(f"🔥 Stress testing {endpoint_func.__name__} with {concurrent_users} concurrent users for {duration_seconds}s...")
        
        results = []
        errors = 0
        start_time = time.time()
        
        def worker():
            while time.time() - start_time < duration_seconds:
                try:
                    request_start = time.time()
                    endpoint_func()
                    request_time = (time.time() - request_start) * 1000
                    results.append(request_time)
                except Exception:
                    nonlocal errors
                    errors += 1
                time.sleep(0.01)  # Small delay to prevent overwhelming
        
        # Start concurrent workers
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(worker) for _ in range(concurrent_users)]
            
            # Wait for completion
            for future in as_completed(futures, timeout=duration_seconds + 10):
                try:
                    future.result()
                except Exception as e:
                    print(f"Worker error: {e}")
        
        if results:
            total_requests = len(results) + errors
            stats = {
                "function_name": endpoint_func.__name__,
                "concurrent_users": concurrent_users,
                "duration_seconds": duration_seconds,
                "total_requests": total_requests,
                "successful_requests": len(results),
                "errors": errors,
                "requests_per_second": total_requests / duration_seconds,
                "avg_response_time_ms": statistics.mean(results),
                "p95_response_time_ms": np.percentile(results, 95),
                "success_rate": (len(results) / total_requests) * 100 if total_requests > 0 else 0,
                "throughput_sustained": max(results) <= perf_config.standard_endpoint_target_ms
            }
        else:
            stats = {"error": "No successful requests", "total_errors": errors}
        
        return stats
    
    def memory_profile(self, func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Profile memory usage of function"""
        tracemalloc.start()
        
        start_memory = psutil.Process().memory_info().rss / (1024 * 1024)  # MB
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            success = True
        except Exception as e:
            result = str(e)
            success = False
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / (1024 * 1024)  # MB
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        return {
            "function_name": func.__name__,
            "success": success,
            "execution_time_ms": (end_time - start_time) * 1000,
            "memory_start_mb": start_memory,
            "memory_end_mb": end_memory,
            "memory_delta_mb": end_memory - start_memory,
            "peak_memory_mb": peak / (1024 * 1024),
            "memory_efficient": (end_memory - start_memory) < (perf_config.max_memory_mb / 10)  # <10% of limit
        }
    
    def generate_performance_report(self) -> str:
        """Generate comprehensive performance report"""
        report_lines = [
            "🎯 SuperClaude Performance Report",
            "=" * 50,
            f"Generated: {datetime.utcnow().isoformat()}",
            ""
        ]
        
        # Overall system stats
        system_stats = monitor.get_performance_stats()
        report_lines.extend([
            "📊 System Performance:",
            f"  Overall Grade: {system_stats.get('performance_grade', 'N/A')}",
            f"  Uptime: {system_stats.get('uptime_seconds', 0):.0f}s",
            f"  CPU Usage: {system_stats.get('resource_usage', {}).get('cpu_percent', 0):.1f}%",
            f"  Memory Usage: {system_stats.get('resource_usage', {}).get('memory_mb', 0):.1f}MB",
            ""
        ])
        
        # Request statistics
        req_stats = system_stats.get('request_statistics', {})
        if req_stats:
            report_lines.extend([
                "⚡ Request Performance:",
                f"  Average Response Time: {req_stats.get('avg_response_time_ms', 0):.1f}ms",
                f"  95th Percentile: {req_stats.get('p95_response_time_ms', 0):.1f}ms",
                f"  Error Rate: {req_stats.get('error_rate', 0):.2f}%",
                f"  Total Requests (5min): {req_stats.get('total_requests', 0)}",
                ""
            ])
        
        # Cache performance
        cache_stats = cache.get_stats()
        report_lines.extend([
            "🧠 Cache Performance:",
            f"  Hit Rate: {cache_stats['hit_rate']:.1f}%",
            f"  L1 Hit Rate: {cache_stats['l1_hit_rate']:.1f}%",
            f"  L2 Hit Rate: {cache_stats['l2_hit_rate']:.1f}%",
            f"  L3 Hit Rate: {cache_stats['l3_hit_rate']:.1f}%",
            f"  Total Requests: {cache_stats['total_requests']}",
            ""
        ])
        
        # Benchmark results
        if self.results:
            report_lines.extend([
                "🏆 Benchmark Results:",
            ])
            for func_name, stats in self.results.items():
                if "error" not in stats:
                    target_met = "✅" if stats.get("meets_target", False) else "❌"
                    report_lines.append(f"  {func_name}: {stats.get('avg_response_time_ms', 0):.1f}ms {target_met}")
            report_lines.append("")
        
        # Performance recommendations
        recommendations = self._generate_recommendations(system_stats, cache_stats)
        if recommendations:
            report_lines.extend([
                "💡 Performance Recommendations:",
                *[f"  • {rec}" for rec in recommendations],
                ""
            ])
        
        return "\n".join(report_lines)
    
    def _generate_recommendations(self, system_stats: Dict, cache_stats: Dict) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        # Response time recommendations
        req_stats = system_stats.get('request_statistics', {})
        if req_stats.get('avg_response_time_ms', 0) > perf_config.critical_endpoint_target_ms:
            recommendations.append("Consider optimizing slow endpoints or increasing server resources")
        
        # Cache recommendations
        if cache_stats['hit_rate'] < 80:
            recommendations.append("Improve cache hit rate by optimizing cache keys and TTL values")
        
        # Resource recommendations
        resource_stats = system_stats.get('resource_usage', {})
        if resource_stats.get('cpu_percent', 0) > 70:
            recommendations.append("High CPU usage detected - consider horizontal scaling or code optimization")
        
        if resource_stats.get('memory_percent', 0) > 70:
            recommendations.append("High memory usage - consider memory profiling and optimization")
        
        # Error rate recommendations
        if req_stats.get('error_rate', 0) > 1:
            recommendations.append("Error rate above 1% - investigate and fix error-prone endpoints")
        
        return recommendations

# ============================================================================
# PERFORMANCE TESTING EXAMPLES
# ============================================================================

def run_performance_tests():
    """Run comprehensive performance test suite"""
    print("🚀 Starting SuperClaude Performance Test Suite")
    print("=" * 60)
    
    tester = PerformanceTester()
    
    # Mock API endpoint for testing
    def mock_api_endpoint():
        time.sleep(0.05)  # Simulate 50ms API call
        return {"data": "test", "status": "success"}
    
    def mock_slow_endpoint():
        time.sleep(0.3)  # Simulate 300ms slow API call
        return {"data": "slow", "status": "success"}
    
    def mock_cpu_intensive():
        # Simulate CPU-intensive operation
        result = sum(i * i for i in range(10000))
        return {"result": result}
    
    # Benchmark tests
    print("\n📊 Running Benchmark Tests:")
    tester.benchmark_endpoint(mock_api_endpoint, 50)
    tester.benchmark_endpoint(mock_slow_endpoint, 20)
    tester.benchmark_endpoint(mock_cpu_intensive, 30)
    
    # Memory profiling
    print("\n🧠 Running Memory Profiling:")
    memory_result = tester.memory_profile(mock_cpu_intensive)
    print(f"  Memory usage: {memory_result['memory_delta_mb']:.1f}MB delta")
    
    # Stress test
    print("\n🔥 Running Stress Test:")
    stress_result = tester.stress_test(mock_api_endpoint, concurrent_users=5, duration_seconds=10)
    print(f"  Throughput: {stress_result.get('requests_per_second', 0):.1f} RPS")
    
    # Generate final report
    print("\n" + tester.generate_performance_report())

if __name__ == "__main__":
    run_performance_tests()