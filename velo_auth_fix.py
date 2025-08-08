#!/usr/bin/env python3
"""
Velo API Authentication Fix
Based on intercepted HTTP requests, implement proper Velo API authentication

Key Discovery: Velo uses Basic Authentication with base64 encoding
Format: 'Basic ' + base64_encode('api:' + api_key)
"""

import base64
import requests
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

class VeloAPIFixed:
    """Fixed Velo API integration with proper authentication"""
    
    def __init__(self, api_key: str = "25965dc53c424038964e2f720270bece"):
        self.api_key = api_key
        self.base_url = "https://api.velo.xyz/api/v1"
        
        # Decode the intercepted Basic auth to understand the pattern
        intercepted_auth = "YXBpOjI1OTY1ZGM1M2M0MjQwMzg5NjRlMmY3MjAyNzBiZWNl"
        try:
            decoded = base64.b64decode(intercepted_auth).decode('utf-8')
            print(f"Decoded auth pattern: {decoded}")
        except:
            print("Could not decode intercepted auth")
        
        # Generate proper Basic Auth header
        # Pattern appears to be: base64('api:' + api_key)
        auth_string = f"api:{self.api_key}"
        encoded_auth = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
        
        self.headers = {
            'Authorization': f'Basic {encoded_auth}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        print(f"Generated auth header: Basic {encoded_auth}")
        print(f"Auth string used: {auth_string}")
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Make authenticated request to Velo API"""
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        print(f"\n[REQUEST] {url}")
        print(f"Headers: {self.headers}")
        print(f"Params: {params}")
        
        start_time = time.time()
        
        try:
            response = requests.get(
                url=url,
                headers=self.headers,
                params=params or {},
                timeout=15
            )
            
            response_time = (time.time() - start_time) * 1000
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Time: {response_time:.1f}ms")
            print(f"Response Size: {len(response.content)} bytes")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"[PASS] SUCCESS")
                    
                    if isinstance(data, list):
                        print(f"Data: array with {len(data)} items")
                        if data:
                            print(f"Sample item keys: {list(data[0].keys())[:5] if isinstance(data[0], dict) else 'Not dict'}")
                    elif isinstance(data, dict):
                        print(f"Data: object with keys {list(data.keys())[:5]}")
                    
                    return {
                        "success": True,
                        "status_code": response.status_code,
                        "data": data,
                        "response_time_ms": response_time,
                        "error": None
                    }
                    
                except json.JSONDecodeError as e:
                    print(f"[ERROR] Invalid JSON: {e}")
                    print(f"Raw response: {response.text[:200]}")
                    
                    return {
                        "success": False,
                        "status_code": response.status_code,
                        "data": None,
                        "response_time_ms": response_time,
                        "error": f"Invalid JSON: {e}",
                        "raw_response": response.text[:500]
                    }
            
            else:
                print(f"[FAIL] HTTP {response.status_code}")
                print(f"Error response: {response.text}")
                
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "data": None,
                    "response_time_ms": response_time,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "raw_response": response.text
                }
                
        except requests.exceptions.RequestException as e:
            response_time = (time.time() - start_time) * 1000
            print(f"[ERROR] Request failed: {e}")
            
            return {
                "success": False,
                "status_code": 0,
                "data": None,
                "response_time_ms": response_time,
                "error": f"Request error: {e}"
            }
    
    def get_futures(self) -> Dict[str, Any]:
        """Get available futures contracts"""
        return self._make_request("futures")
    
    def get_futures_columns(self) -> Dict[str, Any]:
        """Get available data columns for futures"""
        return self._make_request("futures/columns")
    
    def get_options(self) -> Dict[str, Any]:
        """Get available options contracts"""
        return self._make_request("options")
    
    def get_options_columns(self) -> Dict[str, Any]:
        """Get available data columns for options"""
        return self._make_request("options/columns")
    
    def get_spot(self) -> Dict[str, Any]:
        """Get available spot markets"""
        return self._make_request("spot")
    
    def get_spot_columns(self) -> Dict[str, Any]:
        """Get available data columns for spot"""
        return self._make_request("spot/columns")
    
    def get_status(self) -> Dict[str, Any]:
        """Get API status"""
        return self._make_request("status")
    
    def get_market_overview(self) -> Dict[str, Any]:
        """Get market overview - original failing endpoint"""
        return self._make_request("market/overview")
    
    def get_institutional_flows(self) -> Dict[str, Any]:
        """Get institutional flows - original failing endpoint"""
        return self._make_request("flows/institutional", {"timeframe": "24h"})
    
    def test_all_endpoints(self) -> Dict[str, Any]:
        """Test all discovered endpoints"""
        
        endpoints_to_test = [
            ("futures", "Available futures contracts"),
            ("futures/columns", "Futures data columns"),
            ("options", "Available options contracts"),  
            ("options/columns", "Options data columns"),
            ("spot", "Available spot markets"),
            ("spot/columns", "Spot data columns"),
            ("status", "API status"),
            ("market/overview", "Market overview (original failing)"),
            ("flows/institutional", "Institutional flows (original failing)")
        ]
        
        results = {}
        
        print("="*60)
        print("TESTING ALL VELO API ENDPOINTS WITH FIXED AUTHENTICATION")
        print("="*60)
        
        for endpoint, description in endpoints_to_test:
            print(f"\n--- Testing: {description} ---")
            
            if endpoint == "flows/institutional":
                result = self.get_institutional_flows()
            else:
                result = self._make_request(endpoint)
                
            results[endpoint] = result
        
        return results

def test_velo_basic_auth_variations():
    """Test different Basic Auth variations to find the working one"""
    
    api_key = "25965dc53c424038964e2f720270bece"
    
    # Test different Basic Auth patterns
    auth_patterns = [
        ("api", f"api:{api_key}"),
        ("key", f"key:{api_key}"),
        ("token", f"token:{api_key}"),
        ("plain", api_key),
        ("user", f"user:{api_key}"),
        ("velo", f"velo:{api_key}"),
        ("client", f"client:{api_key}")
    ]
    
    print("Testing Basic Auth Variations")
    print("="*50)
    
    results = {}
    
    for pattern_name, auth_string in auth_patterns:
        print(f"\nTesting pattern '{pattern_name}': {auth_string}")
        
        encoded_auth = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
        headers = {
            'Authorization': f'Basic {encoded_auth}',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.get(
                "https://api.velo.xyz/api/v1/status",
                headers=headers,
                timeout=10
            )
            
            result = {
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "auth_string": auth_string,
                "encoded": encoded_auth
            }
            
            if response.status_code == 200:
                print(f"  [PASS] SUCCESS with pattern '{pattern_name}'")
                try:
                    result["data"] = response.json()
                except:
                    result["data"] = response.text
            else:
                print(f"  [FAIL] HTTP {response.status_code}")
                result["error"] = response.text[:100]
            
            results[pattern_name] = result
            
        except Exception as e:
            print(f"  [ERROR] {e}")
            results[pattern_name] = {"error": str(e), "success": False}
    
    return results

def main():
    """Main testing execution"""
    
    print("Velo API Authentication Fix")
    print("="*60)
    
    # First, test different Basic Auth patterns
    print("\n1. TESTING BASIC AUTH VARIATIONS")
    auth_results = test_velo_basic_auth_variations()
    
    # Find working auth pattern
    working_pattern = None
    for pattern, result in auth_results.items():
        if result.get("success"):
            working_pattern = pattern
            break
    
    if working_pattern:
        print(f"\n[SUCCESS] Working auth pattern found: {working_pattern}")
    else:
        print(f"\n[INFO] No working auth pattern found, proceeding with 'api' pattern")
    
    # Test comprehensive API with fixed auth
    print(f"\n2. COMPREHENSIVE API TESTING")
    velo_api = VeloAPIFixed()
    endpoint_results = velo_api.test_all_endpoints()
    
    # Generate summary
    print(f"\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    
    print(f"\nBasic Auth Pattern Testing:")
    for pattern, result in auth_results.items():
        status = "[PASS]" if result.get("success") else "[FAIL]"
        print(f"  {status} {pattern}: {result.get('auth_string', 'N/A')}")
    
    print(f"\nEndpoint Testing:")
    working_endpoints = 0
    total_endpoints = len(endpoint_results)
    
    for endpoint, result in endpoint_results.items():
        status = "[PASS]" if result.get("success") else "[FAIL]"
        print(f"  {status} {endpoint}")
        if result.get("success"):
            working_endpoints += 1
    
    success_rate = (working_endpoints / total_endpoints * 100) if total_endpoints > 0 else 0
    print(f"\nSuccess Rate: {working_endpoints}/{total_endpoints} ({success_rate:.1f}%)")
    
    # Save detailed results
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    results_file = f"VELO_AUTH_FIX_RESULTS_{timestamp}.json"
    
    full_results = {
        "auth_pattern_testing": auth_results,
        "endpoint_testing": endpoint_results,
        "working_pattern": working_pattern,
        "success_rate": success_rate,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    with open(results_file, 'w') as f:
        json.dump(full_results, f, indent=2, default=str)
    
    print(f"Detailed results saved to: {results_file}")
    
    return full_results

if __name__ == "__main__":
    results = main()