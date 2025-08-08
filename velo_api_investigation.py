#!/usr/bin/env python3
"""
Velo API Investigation Tool
Comprehensive investigation to understand Velo API authentication and endpoints

Approach:
1. Intercept HTTP requests made by Velo SDK
2. Analyze authentication headers and endpoints
3. Test different authentication methods for direct API access
4. Identify correct API key format and permissions
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import subprocess
import logging
from unittest.mock import patch
import inspect

# Setup HTTP request logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class VeloAPIInvestigator:
    """Comprehensive Velo API investigation"""
    
    def __init__(self, api_key: str = "25965dc53c424038964e2f720270bece"):
        self.api_key = api_key
        self.sdk_available = False
        self.intercepted_requests = []
        self.client = None
        
    def install_and_import_sdk(self):
        """Install Velo SDK and import it"""
        
        print("Installing Velo SDK...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "velodata", "--upgrade"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("[PASS] Velo SDK installed successfully")
                
                # Import and initialize SDK
                try:
                    # Import the SDK
                    from velodata import lib as velo
                    
                    print("SDK imported successfully")
                    print(f"Available methods: {dir(velo)}")
                    
                    # Initialize client
                    self.client = velo.client(self.api_key)
                    self.sdk_available = True
                    
                    print(f"[PASS] SDK client initialized")
                    print(f"Client type: {type(self.client)}")
                    print(f"Client methods: {[m for m in dir(self.client) if not m.startswith('_')]}")
                    
                    return True
                    
                except Exception as e:
                    print(f"[ERROR] SDK import/init failed: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
            else:
                print(f"[ERROR] SDK installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Installation error: {e}")
            return False
    
    def intercept_http_requests(self):
        """Intercept HTTP requests made by the SDK"""
        
        original_request = requests.Session.request
        
        def intercepted_request(self_session, method, url, **kwargs):
            """Intercept and log HTTP requests"""
            print(f"\n[INTERCEPT] HTTP Request:")
            print(f"  Method: {method}")
            print(f"  URL: {url}")
            print(f"  Headers: {kwargs.get('headers', {})}")
            print(f"  Params: {kwargs.get('params', {})}")
            print(f"  Data: {kwargs.get('data', None)}")
            print(f"  JSON: {kwargs.get('json', None)}")
            
            # Store intercepted request
            self.parent.intercepted_requests.append({
                "method": method,
                "url": url,
                "headers": kwargs.get('headers', {}),
                "params": kwargs.get('params', {}),
                "data": kwargs.get('data'),
                "json": kwargs.get('json'),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            # Make the actual request
            response = original_request(self_session, method, url, **kwargs)
            
            print(f"  Response Status: {response.status_code}")
            print(f"  Response Headers: {dict(response.headers)}")
            if response.content and len(response.content) < 1000:
                print(f"  Response Content: {response.text[:500]}")
            else:
                print(f"  Response Size: {len(response.content)} bytes")
            
            return response
        
        # Add parent reference for intercepted function
        intercepted_request.parent = self
        
        # Patch the requests
        requests.Session.request = intercepted_request
        
        return original_request
    
    def restore_http_requests(self, original_request):
        """Restore original HTTP requests"""
        requests.Session.request = original_request
    
    def test_sdk_with_interception(self):
        """Test SDK functionality while intercepting HTTP requests"""
        
        if not self.sdk_available:
            print("[ERROR] SDK not available")
            return {}
        
        print("\n" + "="*60)
        print("TESTING SDK WITH HTTP INTERCEPTION")
        print("="*60)
        
        # Start intercepting
        original_request = self.intercept_http_requests()
        
        try:
            results = {}
            
            # Test 1: Get futures
            print("\n1. Testing get_futures()...")
            try:
                futures = self.client.get_futures()
                results["get_futures"] = {
                    "success": True,
                    "count": len(futures) if futures else 0,
                    "sample": futures[:2] if futures else None
                }
                print(f"   [PASS] Got {len(futures) if futures else 0} futures")
            except Exception as e:
                results["get_futures"] = {"success": False, "error": str(e)}
                print(f"   [ERROR] {e}")
            
            # Test 2: Get columns
            print("\n2. Testing get_futures_columns()...")
            try:
                columns = self.client.get_futures_columns()
                results["get_columns"] = {
                    "success": True,
                    "count": len(columns) if columns else 0,
                    "sample": columns[:5] if columns else None
                }
                print(f"   [PASS] Got {len(columns) if columns else 0} columns")
            except Exception as e:
                results["get_columns"] = {"success": False, "error": str(e)}
                print(f"   [ERROR] {e}")
            
            # Test 3: Try to get some data
            print("\n3. Testing data retrieval...")
            try:
                if results.get("get_futures", {}).get("success") and results.get("get_columns", {}).get("success"):
                    # Basic data request
                    params = {
                        'type': 'futures',
                        'columns': ['close_price'] if results["get_columns"]["sample"] else [],
                        'exchanges': ['binance-futures'],
                        'products': ['BTCUSDT'],
                        'begin': self.client.timestamp() - 1000 * 60 * 60,  # 1 hour ago
                        'end': self.client.timestamp(),
                        'resolution': '1m'
                    }
                    
                    print(f"   Requesting data with params: {params}")
                    data = self.client.get_rows(params)
                    
                    results["get_data"] = {
                        "success": True,
                        "count": len(data) if data else 0,
                        "params_used": params
                    }
                    print(f"   [PASS] Got {len(data) if data else 0} data rows")
                else:
                    results["get_data"] = {"success": False, "error": "Prerequisites failed"}
                    
            except Exception as e:
                results["get_data"] = {"success": False, "error": str(e)}
                print(f"   [ERROR] {e}")
            
        finally:
            # Restore original requests
            self.restore_http_requests(original_request)
        
        return results
    
    def analyze_intercepted_requests(self):
        """Analyze the intercepted HTTP requests to understand authentication"""
        
        print("\n" + "="*60)
        print("ANALYZING INTERCEPTED HTTP REQUESTS")
        print("="*60)
        
        if not self.intercepted_requests:
            print("No requests were intercepted")
            return {}
        
        analysis = {
            "total_requests": len(self.intercepted_requests),
            "unique_urls": set(),
            "authentication_patterns": {},
            "common_headers": {},
            "endpoints": []
        }
        
        for i, req in enumerate(self.intercepted_requests):
            print(f"\n--- Request {i+1} ---")
            print(f"Method: {req['method']}")
            print(f"URL: {req['url']}")
            
            # Extract base URL pattern
            url_parts = req['url'].split('/')
            if len(url_parts) >= 3:
                base_url = '/'.join(url_parts[:3])
                analysis["unique_urls"].add(base_url)
            
            # Analyze authentication headers
            auth_headers = {}
            for header, value in req['headers'].items():
                if any(auth_keyword in header.lower() for auth_keyword in ['auth', 'key', 'token', 'bearer']):
                    auth_headers[header] = value[:20] + "..." if len(str(value)) > 20 else value
            
            if auth_headers:
                analysis["authentication_patterns"][f"request_{i+1}"] = auth_headers
                print(f"Auth Headers: {auth_headers}")
            
            # Common headers
            for header, value in req['headers'].items():
                if header not in analysis["common_headers"]:
                    analysis["common_headers"][header] = []
                analysis["common_headers"][header].append(str(value))
            
            # Store endpoint info
            analysis["endpoints"].append({
                "method": req['method'],
                "url": req['url'],
                "has_auth": bool(auth_headers),
                "params": req['params']
            })
        
        # Summarize common headers
        for header in analysis["common_headers"]:
            analysis["common_headers"][header] = list(set(analysis["common_headers"][header]))
        
        print(f"\n[ANALYSIS SUMMARY]")
        print(f"Total Requests: {analysis['total_requests']}")
        print(f"Unique Base URLs: {list(analysis['unique_urls'])}")
        print(f"Authentication Patterns Found: {len(analysis['authentication_patterns'])}")
        
        return analysis
    
    def test_direct_api_with_discovered_auth(self, analysis):
        """Test direct API calls using discovered authentication patterns"""
        
        print("\n" + "="*60)
        print("TESTING DIRECT API WITH DISCOVERED AUTH")
        print("="*60)
        
        if not analysis.get("authentication_patterns"):
            print("No authentication patterns discovered")
            return {}
        
        results = {}
        
        # Extract authentication method
        auth_pattern = list(analysis["authentication_patterns"].values())[0]
        print(f"Using auth pattern: {auth_pattern}")
        
        # Try the discovered endpoints with discovered auth
        for endpoint_info in analysis.get("endpoints", []):
            endpoint_name = endpoint_info["url"].split('/')[-1] or "root"
            
            print(f"\nTesting endpoint: {endpoint_name}")
            print(f"URL: {endpoint_info['url']}")
            
            # Reconstruct headers from discovered pattern
            headers = {"Accept": "application/json"}
            
            # Add discovered auth headers
            for header, value in auth_pattern.items():
                # Reconstruct full value (remove "..." if truncated)
                if header.lower() == 'authorization' and 'bearer' in value.lower():
                    headers[header] = f"Bearer {self.api_key}"
                elif 'key' in header.lower():
                    headers[header] = self.api_key
                else:
                    headers[header] = value.replace("...", "")
            
            try:
                response = requests.request(
                    method=endpoint_info["method"],
                    url=endpoint_info["url"],
                    headers=headers,
                    params=endpoint_info.get("params", {}),
                    timeout=10
                )
                
                result = {
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "headers_used": headers,
                    "response_size": len(response.content),
                    "response_preview": response.text[:200] if response.text else None
                }
                
                print(f"  Status: {response.status_code}")
                print(f"  Success: {result['success']}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, list):
                            print(f"  Data: {len(data)} items")
                        elif isinstance(data, dict):
                            print(f"  Keys: {list(data.keys())[:5]}")
                    except:
                        print(f"  Raw response: {response.text[:100]}")
                
                results[endpoint_name] = result
                
            except Exception as e:
                results[endpoint_name] = {
                    "success": False,
                    "error": str(e),
                    "headers_used": headers
                }
                print(f"  [ERROR] {e}")
        
        return results
    
    def generate_comprehensive_report(self, sdk_results, analysis, direct_api_results):
        """Generate comprehensive investigation report"""
        
        report = {
            "investigation_summary": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "api_key_format": {
                    "length": len(self.api_key),
                    "format": "hex" if all(c in "0123456789abcdef" for c in self.api_key.lower()) else "mixed",
                    "prefix": self.api_key[:8] + "..."
                },
                "sdk_available": self.sdk_available
            },
            "sdk_functionality": sdk_results,
            "http_interception_analysis": analysis,
            "direct_api_testing": direct_api_results,
            "recommendations": []
        }
        
        # Generate recommendations
        if self.sdk_available and sdk_results:
            report["recommendations"].append("✓ Velo SDK is functional - use as primary integration method")
        
        if analysis.get("authentication_patterns"):
            report["recommendations"].append("✓ Authentication patterns discovered from SDK")
        
        if any(result.get("success") for result in direct_api_results.values()):
            report["recommendations"].append("✓ Some direct API endpoints working")
        else:
            report["recommendations"].append("⚠ Direct API access still failing - may require paid/enterprise API key")
        
        if analysis.get("unique_urls"):
            report["recommendations"].append(f"ℹ Base API URLs identified: {list(analysis['unique_urls'])}")
        
        return report

def main():
    """Main investigation execution"""
    
    print("Velo API Comprehensive Investigation")
    print("="*60)
    
    investigator = VeloAPIInvestigator()
    
    # Step 1: Install and test SDK
    if not investigator.install_and_import_sdk():
        print("Cannot proceed without SDK")
        return
    
    # Step 2: Test SDK with HTTP interception
    sdk_results = investigator.test_sdk_with_interception()
    
    # Step 3: Analyze intercepted requests
    analysis = investigator.analyze_intercepted_requests()
    
    # Step 4: Test direct API with discovered auth
    direct_api_results = investigator.test_direct_api_with_discovered_auth(analysis)
    
    # Step 5: Generate comprehensive report
    report = investigator.generate_comprehensive_report(sdk_results, analysis, direct_api_results)
    
    # Save report
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_file = f"VELO_API_INVESTIGATION_REPORT_{timestamp}.json"
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    # Print summary
    print("\n" + "="*60)
    print("INVESTIGATION COMPLETE")
    print("="*60)
    
    print(f"\nSDK Functionality:")
    for test, result in sdk_results.items():
        status = "[PASS]" if result.get("success") else "[FAIL]"
        print(f"  {status} {test}")
    
    print(f"\nHTTP Analysis:")
    print(f"  Requests Intercepted: {analysis.get('total_requests', 0)}")
    print(f"  Auth Patterns Found: {len(analysis.get('authentication_patterns', {}))}")
    print(f"  Unique URLs: {len(analysis.get('unique_urls', set()))}")
    
    print(f"\nDirect API Testing:")
    for endpoint, result in direct_api_results.items():
        status = "[PASS]" if result.get("success") else "[FAIL]"
        print(f"  {status} {endpoint}")
    
    print(f"\nRecommendations:")
    for rec in report["recommendations"]:
        print(f"  {rec}")
    
    print(f"\nDetailed report saved to: {report_file}")
    
    return report

if __name__ == "__main__":
    report = main()