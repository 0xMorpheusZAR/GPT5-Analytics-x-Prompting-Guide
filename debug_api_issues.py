#!/usr/bin/env python3
"""
SuperClaude API Debug Tool
Comprehensive debugging for DeFiLlama Pro and Velo Data API issues

Debug Focus:
- Detailed error analysis with stack traces
- Authentication mechanism testing
- Alternative endpoint discovery
- Rate limiting and timeout analysis
- Response content inspection
"""

import os
import time
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any
import traceback
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Enable detailed HTTP logging
import logging
import http.client as http_client

# Configure debug logging
logging.basicConfig(level=logging.DEBUG)
http_client.HTTPConnection.debuglevel = 1
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

class APIDebugger:
    """Comprehensive API debugging tool"""
    
    def __init__(self):
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # API Configuration
        self.config = {
            "defillama": {
                "api_key": "435722de8920d195d301a595f0c29ed939608c9b1da2d75905e85a68f3ee336d",
                "base_url": "https://api.llama.fi",
                "alternative_urls": [
                    "https://yields.llama.fi",
                    "https://stablecoins.llama.fi",
                    "https://pro-api.llama.fi"
                ]
            },
            "velo": {
                "api_key": "25965dc53c424038964e2f720270bece", 
                "base_url": "https://api.velo.xyz",
                "alternative_urls": [
                    "https://data.velo.xyz",
                    "https://pro.velo.xyz/api",
                    "https://api-v2.velo.xyz"
                ]
            }
        }
        
    def debug_request(self, method: str, url: str, headers: Dict = None, params: Dict = None, timeout: int = 30) -> Dict[str, Any]:
        """Make a debug request with comprehensive logging"""
        
        print(f"\n{'='*60}")
        print(f"🔍 DEBUG REQUEST: {method} {url}")
        print(f"📝 Headers: {json.dumps(headers, indent=2) if headers else 'None'}")
        print(f"📝 Params: {json.dumps(params, indent=2) if params else 'None'}")
        print(f"⏰ Timeout: {timeout}s")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            response = self.session.request(
                method=method,
                url=url, 
                headers=headers,
                params=params,
                timeout=timeout
            )
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            print(f"\n📊 RESPONSE INFO:")
            print(f"Status Code: {response.status_code}")
            print(f"Response Time: {response_time:.1f}ms")
            print(f"Content Length: {len(response.content)} bytes")
            print(f"Content Type: {response.headers.get('content-type', 'Unknown')}")
            
            # Try to parse response
            response_data = None
            if response.content:
                try:
                    response_data = response.json()
                    print(f"✅ JSON Response: Valid")
                    if isinstance(response_data, dict):
                        print(f"📋 Top-level keys: {list(response_data.keys())[:10]}")
                    elif isinstance(response_data, list):
                        print(f"📋 Array length: {len(response_data)}")
                        if response_data and isinstance(response_data[0], dict):
                            print(f"📋 First item keys: {list(response_data[0].keys())[:10]}")
                except json.JSONDecodeError as e:
                    print(f"❌ JSON Error: {e}")
                    print(f"📝 Raw content preview: {response.text[:200]}...")
            
            # Headers analysis
            print(f"\n📋 RESPONSE HEADERS:")
            for key, value in response.headers.items():
                print(f"  {key}: {value}")
                
            return {
                "success": 200 <= response.status_code < 300,
                "status_code": response.status_code,
                "response_time_ms": response_time,
                "content_length": len(response.content),
                "content_type": response.headers.get('content-type'),
                "data": response_data,
                "raw_text": response.text[:500] if response.text else None,
                "headers": dict(response.headers),
                "error": None
            }
            
        except requests.exceptions.RequestException as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            print(f"\n❌ REQUEST ERROR:")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Message: {str(e)}")
            print(f"Response Time: {response_time:.1f}ms")
            print(f"Stack Trace:")
            traceback.print_exc()
            
            return {
                "success": False,
                "status_code": 0,
                "response_time_ms": response_time,
                "content_length": 0,
                "content_type": None,
                "data": None,
                "raw_text": None,
                "headers": {},
                "error": f"{type(e).__name__}: {str(e)}"
            }
    
    def debug_defillama_issues(self) -> Dict[str, Any]:
        """Debug DeFiLlama API issues"""
        
        print(f"\n🚀 DEBUGGING DEFILLAMA API ISSUES")
        print(f"="*80)
        
        results = {
            "api_name": "DeFiLlama Pro",
            "debug_timestamp": datetime.utcnow().isoformat(),
            "endpoints": {},
            "authentication_tests": {},
            "alternative_urls": {}
        }
        
        base_url = self.config["defillama"]["base_url"]
        api_key = self.config["defillama"]["api_key"]
        
        # Test different authentication methods
        auth_methods = [
            {"name": "No Auth", "headers": {"Accept": "application/json"}},
            {"name": "Bearer Token", "headers": {"Accept": "application/json", "Authorization": f"Bearer {api_key}"}},
            {"name": "API Key Header", "headers": {"Accept": "application/json", "X-API-KEY": api_key}},
            {"name": "API Key Param", "headers": {"Accept": "application/json"}, "params": {"apikey": api_key}}
        ]
        
        # Test problematic endpoints with different auth methods
        problem_endpoints = [
            {"name": "yields_pools", "url": f"{base_url}/pools", "description": "Yield farming pools"},
            {"name": "stablecoins", "url": f"{base_url}/stablecoins", "description": "Stablecoin data"},
            {"name": "yields_alternative", "url": "https://yields.llama.fi/pools", "description": "Alternative yields endpoint"}
        ]
        
        for endpoint in problem_endpoints:
            print(f"\n🔍 Testing endpoint: {endpoint['name']}")
            endpoint_results = {}
            
            for auth_method in auth_methods:
                print(f"\n  🔐 Testing auth method: {auth_method['name']}")
                
                result = self.debug_request(
                    method="GET",
                    url=endpoint["url"],
                    headers=auth_method["headers"],
                    params=auth_method.get("params", {}),
                    timeout=15
                )
                
                endpoint_results[auth_method["name"]] = result
                
                if result["success"]:
                    print(f"  ✅ SUCCESS with {auth_method['name']}")
                    break
                else:
                    print(f"  ❌ FAILED with {auth_method['name']}: HTTP {result['status_code']}")
            
            results["endpoints"][endpoint["name"]] = endpoint_results
        
        # Test alternative base URLs
        for alt_url in self.config["defillama"]["alternative_urls"]:
            print(f"\n🌐 Testing alternative URL: {alt_url}")
            
            result = self.debug_request(
                method="GET", 
                url=f"{alt_url}/pools",
                headers={"Accept": "application/json"},
                timeout=10
            )
            
            results["alternative_urls"][alt_url] = result
            
            if result["success"]:
                print(f"✅ Alternative URL working: {alt_url}")
        
        return results
    
    def debug_velo_issues(self) -> Dict[str, Any]:
        """Debug Velo Data API authentication and access issues"""
        
        print(f"\n🚀 DEBUGGING VELO DATA API ISSUES")
        print(f"="*80)
        
        results = {
            "api_name": "Velo Data API",
            "debug_timestamp": datetime.utcnow().isoformat(),
            "endpoints": {},
            "authentication_tests": {},
            "alternative_urls": {},
            "api_key_analysis": {}
        }
        
        base_url = self.config["velo"]["base_url"]
        api_key = self.config["velo"]["api_key"]
        
        # Analyze API key format
        results["api_key_analysis"] = {
            "key_length": len(api_key),
            "key_format": "hex" if all(c in "0123456789abcdef" for c in api_key.lower()) else "mixed",
            "key_prefix": api_key[:8] + "..." if len(api_key) > 8 else api_key
        }
        
        # Test different authentication methods for Velo
        auth_methods = [
            {"name": "Bearer Token", "headers": {"Accept": "application/json", "Authorization": f"Bearer {api_key}"}},
            {"name": "API Key Header", "headers": {"Accept": "application/json", "X-API-KEY": api_key}},
            {"name": "Velo-API-Key Header", "headers": {"Accept": "application/json", "Velo-API-Key": api_key}},
            {"name": "API Key Param", "headers": {"Accept": "application/json"}, "params": {"api_key": api_key}},
            {"name": "Key Param", "headers": {"Accept": "application/json"}, "params": {"key": api_key}},
            {"name": "Token Param", "headers": {"Accept": "application/json"}, "params": {"token": api_key}}
        ]
        
        # Test different endpoint variations
        velo_endpoints = [
            {"name": "market_overview_v1", "url": f"{base_url}/api/v1/market/overview"},
            {"name": "market_overview_v2", "url": f"{base_url}/api/v2/market/overview"},
            {"name": "market_overview_simple", "url": f"{base_url}/market/overview"},
            {"name": "health_check", "url": f"{base_url}/health"},
            {"name": "api_info", "url": f"{base_url}/api"},
            {"name": "root_endpoint", "url": base_url}
        ]
        
        for endpoint in velo_endpoints:
            print(f"\n🔍 Testing endpoint: {endpoint['name']}")
            endpoint_results = {}
            
            for auth_method in auth_methods:
                print(f"\n  🔐 Testing auth: {auth_method['name']}")
                
                result = self.debug_request(
                    method="GET",
                    url=endpoint["url"],
                    headers=auth_method["headers"],
                    params=auth_method.get("params", {}),
                    timeout=10
                )
                
                endpoint_results[auth_method["name"]] = result
                
                if result["success"]:
                    print(f"  ✅ SUCCESS: {endpoint['name']} with {auth_method['name']}")
                    # If we find a working combination, try other endpoints
                    if endpoint["name"] == "health_check" and result["success"]:
                        print(f"  🎯 Found working auth method, testing other endpoints...")
                elif result["status_code"] == 401:
                    print(f"  🔒 UNAUTHORIZED: Invalid credentials")
                elif result["status_code"] == 403:
                    print(f"  🚫 FORBIDDEN: API key not authorized for this endpoint")
                elif result["status_code"] == 404:
                    print(f"  🔍 NOT FOUND: Endpoint doesn't exist")
                else:
                    print(f"  ❌ ERROR: HTTP {result['status_code']}")
            
            results["endpoints"][endpoint["name"]] = endpoint_results
        
        # Test alternative URLs
        for alt_url in self.config["velo"]["alternative_urls"]:
            print(f"\n🌐 Testing alternative URL: {alt_url}")
            
            result = self.debug_request(
                method="GET",
                url=alt_url,
                headers={"Accept": "application/json", "Authorization": f"Bearer {api_key}"},
                timeout=10
            )
            
            results["alternative_urls"][alt_url] = result
        
        return results
    
    def generate_debug_report(self, defillama_results: Dict, velo_results: Dict) -> str:
        """Generate comprehensive debug report"""
        
        report_lines = [
            "# SuperClaude API Debug Report",
            "",
            f"**Generated:** {datetime.utcnow().isoformat()}",
            "",
            "## Executive Summary",
            "",
            "This report provides detailed debugging analysis for API integration issues",
            "with DeFiLlama Pro and Velo Data APIs.",
            "",
            "## DeFiLlama Pro API Debug Results",
            ""
        ]
        
        # DeFiLlama analysis
        for endpoint_name, auth_results in defillama_results["endpoints"].items():
            report_lines.append(f"### {endpoint_name.replace('_', ' ').title()}")
            report_lines.append("")
            
            success_found = False
            for auth_method, result in auth_results.items():
                if result["success"]:
                    report_lines.append(f"✅ **WORKING**: {auth_method}")
                    report_lines.append(f"- Status: HTTP {result['status_code']}")
                    report_lines.append(f"- Response Time: {result['response_time_ms']:.1f}ms")
                    report_lines.append(f"- Data Size: {result['content_length']} bytes")
                    success_found = True
                    break
            
            if not success_found:
                report_lines.append("❌ **ALL AUTHENTICATION METHODS FAILED**")
                for auth_method, result in auth_results.items():
                    report_lines.append(f"- {auth_method}: HTTP {result['status_code']} - {result.get('error', 'Unknown error')}")
            
            report_lines.append("")
        
        # Velo analysis
        report_lines.extend([
            "## Velo Data API Debug Results",
            ""
        ])
        
        # API key analysis
        key_analysis = velo_results["api_key_analysis"]
        report_lines.extend([
            "### API Key Analysis",
            f"- Key Length: {key_analysis['key_length']} characters",
            f"- Key Format: {key_analysis['key_format']}",
            f"- Key Preview: {key_analysis['key_prefix']}",
            ""
        ])
        
        # Endpoint analysis
        working_endpoints = []
        for endpoint_name, auth_results in velo_results["endpoints"].items():
            success_found = False
            for auth_method, result in auth_results.items():
                if result["success"]:
                    working_endpoints.append(f"{endpoint_name} with {auth_method}")
                    success_found = True
                    break
            
            if not success_found:
                # Find the most informative error
                best_error = None
                for auth_method, result in auth_results.items():
                    if result["status_code"] in [401, 403]:  # Auth-related errors are most informative
                        best_error = result
                        break
                
                if best_error:
                    report_lines.append(f"❌ **{endpoint_name}**: HTTP {best_error['status_code']} - Authentication issue")
                else:
                    report_lines.append(f"❌ **{endpoint_name}**: Multiple failures")
        
        if working_endpoints:
            report_lines.extend([
                "### Working Combinations",
                ""
            ])
            for combo in working_endpoints:
                report_lines.append(f"✅ {combo}")
        else:
            report_lines.append("❌ **NO WORKING ENDPOINT COMBINATIONS FOUND**")
        
        report_lines.extend([
            "",
            "## Recommendations",
            "",
            "### DeFiLlama Pro API",
            "- Several endpoints return HTTP 404, indicating they may have been moved or deprecated",
            "- Try alternative base URLs: yields.llama.fi for yield data",
            "- Check DeFiLlama documentation for current endpoint paths",
            "",
            "### Velo Data API", 
            "- HTTP 403 errors indicate API key is valid but lacks permissions",
            "- Contact Velo support to upgrade API key permissions",
            "- Verify correct API documentation and endpoint URLs",
            "",
            "## Next Steps",
            "1. Update DeFiLlama endpoints to correct URLs",
            "2. Request higher permissions for Velo Data API key",
            "3. Implement fallback mechanisms for failed endpoints",
            "4. Add endpoint health monitoring and alerting"
        ])
        
        return "\n".join(report_lines)

def main():
    """Main debugging execution"""
    
    debugger = APIDebugger()
    
    print("🔍 SuperClaude API Debug Tool")
    print("="*50)
    print("Starting comprehensive API debugging...")
    
    # Debug DeFiLlama issues
    defillama_results = debugger.debug_defillama_issues()
    
    # Debug Velo issues  
    velo_results = debugger.debug_velo_issues()
    
    # Generate comprehensive report
    report = debugger.generate_debug_report(defillama_results, velo_results)
    
    # Save detailed results
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    debug_results = {
        "debug_session": {
            "timestamp": timestamp,
            "duration": "comprehensive",
            "apis_tested": ["DeFiLlama Pro", "Velo Data"]
        },
        "defillama": defillama_results,
        "velo": velo_results
    }
    
    # Save files
    results_file = f"API_DEBUG_RESULTS_{timestamp}.json"
    with open(results_file, 'w') as f:
        json.dump(debug_results, f, indent=2, default=str)
    
    report_file = f"API_DEBUG_REPORT_{timestamp}.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\n{'='*50}")
    print("🎯 API DEBUGGING COMPLETED")
    print("="*50)
    print(f"Results saved to: {results_file}")
    print(f"Report saved to: {report_file}")
    
    # Quick summary
    defillama_working = sum(1 for endpoint in defillama_results["endpoints"].values() 
                           for result in endpoint.values() if result["success"])
    velo_working = sum(1 for endpoint in velo_results["endpoints"].values()
                      for result in endpoint.values() if result["success"])
    
    print(f"\nQuick Summary:")
    print(f"DeFiLlama: {defillama_working} working endpoint/auth combinations found")
    print(f"Velo Data: {velo_working} working endpoint/auth combinations found")
    
    return debug_results

if __name__ == "__main__":
    debug_results = main()