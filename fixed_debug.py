#!/usr/bin/env python3
"""
SuperClaude API Debug Tool - Fixed Version
Comprehensive debugging for DeFiLlama Pro and Velo Data API issues
"""

import requests
import json
import time
from datetime import datetime

def test_defillama_pro_endpoints():
    """Test DeFiLlama Pro API endpoints with correct authentication"""
    
    print("Testing DeFiLlama Pro API Endpoints")
    print("="*50)
    
    api_key = "435722de8920d195d301a595f0c29ed939608c9b1da2d75905e85a68f3ee336d"
    base_url = "https://pro-api.llama.fi"
    
    # Test endpoints with Pro API authentication
    endpoints = [
        {"url": f"{base_url}/protocols", "name": "Protocols List", "description": "All DeFi protocols"},
        {"url": f"{base_url}/protocol/aave", "name": "Protocol TVL", "description": "Specific protocol data"},
        {"url": f"{base_url}/chains", "name": "Chains TVL", "description": "All blockchain networks"},
        {"url": f"{base_url}/yields", "name": "Yields Data", "description": "Yield farming data"},
        {"url": f"{base_url}/pools", "name": "Pools Data", "description": "DeFi pool information"},
        {"url": f"{base_url}/stablecoins", "name": "Stablecoins", "description": "Stablecoin data"},
        {"url": "https://yields.llama.fi/pools", "name": "Alt Yields", "description": "Alternative yields endpoint"},
        {"url": "https://stablecoins.llama.fi/stablecoins", "name": "Alt Stables", "description": "Alternative stablecoins endpoint"}
    ]
    
    results = {"working": [], "failed": [], "details": {}}
    
    for endpoint in endpoints:
        print(f"\nTesting: {endpoint['name']}")
        print(f"URL: {endpoint['url']}")
        print(f"Description: {endpoint['description']}")
        
        # Try different authentication methods
        auth_methods = [
            {"name": "No Auth", "headers": {"Accept": "application/json"}},
            {"name": "API Key Header", "headers": {"Accept": "application/json", "Authorization": f"Bearer {api_key}"}},
            {"name": "X-API-KEY", "headers": {"Accept": "application/json", "X-API-KEY": api_key}},
            {"name": "Query Param", "headers": {"Accept": "application/json"}, "params": {"apikey": api_key}}
        ]
        
        endpoint_working = False
        endpoint_details = []
        
        for auth in auth_methods:
            try:
                print(f"  Trying: {auth['name']}")
                start_time = time.time()
                
                response = requests.get(
                    endpoint["url"], 
                    headers=auth["headers"],
                    params=auth.get("params", {}),
                    timeout=15
                )
                
                response_time = (time.time() - start_time) * 1000
                
                result = {
                    "auth_method": auth["name"],
                    "status_code": response.status_code,
                    "response_time_ms": response_time,
                    "content_size": len(response.content),
                    "success": response.status_code == 200
                }
                
                print(f"    Status: {response.status_code}")
                print(f"    Time: {response_time:.1f}ms") 
                print(f"    Size: {len(response.content)} bytes")
                
                if response.status_code == 200:
                    print("    [PASS] SUCCESS")
                    endpoint_working = True
                    
                    # Analyze response data
                    try:
                        data = response.json()
                        if isinstance(data, list):
                            result["data_type"] = f"array[{len(data)}]"
                            if data and isinstance(data[0], dict):
                                result["sample_keys"] = list(data[0].keys())[:5]
                                print(f"    Data: {len(data)} items")
                                print(f"    Keys: {result['sample_keys']}")
                        elif isinstance(data, dict):
                            result["data_type"] = "object"
                            result["sample_keys"] = list(data.keys())[:5]
                            print(f"    Keys: {result['sample_keys']}")
                        
                        # Success, break out of auth method loop
                        break
                        
                    except json.JSONDecodeError:
                        result["data_type"] = "non-json"
                        print("    [WARN] Non-JSON response")
                        
                elif response.status_code == 401:
                    print("    [AUTH] Unauthorized")
                elif response.status_code == 403:
                    print("    [AUTH] Forbidden")
                elif response.status_code == 404:
                    print("    [NOTFOUND] Endpoint not found")
                else:
                    print(f"    [FAIL] HTTP {response.status_code}")
                    if response.text:
                        print(f"    Error: {response.text[:100]}")
                
                endpoint_details.append(result)
                
            except Exception as e:
                print(f"    [ERROR] {e}")
                endpoint_details.append({
                    "auth_method": auth["name"],
                    "error": str(e),
                    "success": False
                })
        
        # Categorize endpoint result
        if endpoint_working:
            results["working"].append(endpoint["name"])
        else:
            results["failed"].append(endpoint["name"])
            
        results["details"][endpoint["name"]] = endpoint_details
    
    return results

def test_velo_api():
    """Test Velo Data API with official SDK approach"""
    
    print("\nTesting Velo Data API")
    print("="*50)
    
    api_key = "25965dc53c424038964e2f720270bece"
    
    # First, try to install and use the official SDK
    print("Checking for Velo SDK installation...")
    
    try:
        import subprocess
        result = subprocess.run(['pip', 'install', 'velodata'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("[INFO] Velo SDK installed successfully")
        else:
            print(f"[WARN] SDK installation issue: {result.stderr}")
    except Exception as e:
        print(f"[WARN] Could not install SDK: {e}")
    
    # Try to import and use the SDK
    sdk_working = False
    try:
        print("Attempting to use Velo SDK...")
        
        # This would be the proper way according to the GitHub repo
        from velodata import lib as velo
        
        client = velo.client(api_key)
        print("[PASS] Velo client created successfully")
        
        # Test basic functionality
        futures = client.get_futures()
        print(f"[DATA] Retrieved {len(futures)} futures")
        
        columns = client.get_futures_columns()
        print(f"[DATA] Available columns: {len(columns)}")
        
        sdk_working = True
        
    except ImportError:
        print("[INFO] Velo SDK not available, testing direct API calls")
    except Exception as e:
        print(f"[ERROR] SDK error: {e}")
    
    # Test direct API endpoints as fallback
    direct_results = {"working": [], "failed": [], "details": {}}
    
    if not sdk_working:
        print("\nTesting direct API endpoints...")
        
        endpoints = [
            {"url": "https://api.velo.xyz", "name": "Base URL"},
            {"url": "https://api.velo.xyz/health", "name": "Health Check"},
            {"url": "https://api.velo.xyz/api", "name": "API Info"},
            {"url": "https://data.velo.xyz", "name": "Data URL"},
            {"url": "https://pro.velo.xyz/api", "name": "Pro API"},
        ]
        
        for endpoint in endpoints:
            print(f"\nTesting: {endpoint['name']}")
            
            auth_methods = [
                {"name": "No Auth", "headers": {"Accept": "application/json"}},
                {"name": "Bearer Token", "headers": {"Accept": "application/json", "Authorization": f"Bearer {api_key}"}},
                {"name": "API Key Header", "headers": {"Accept": "application/json", "X-API-KEY": api_key}},
            ]
            
            endpoint_working = False
            
            for auth in auth_methods:
                try:
                    response = requests.get(endpoint["url"], headers=auth["headers"], timeout=10)
                    
                    print(f"  {auth['name']}: HTTP {response.status_code}")
                    
                    if response.status_code == 200:
                        print("  [PASS] SUCCESS")
                        direct_results["working"].append(endpoint["name"])
                        endpoint_working = True
                        
                        if response.text:
                            print(f"  Response: {response.text[:100]}")
                        break
                        
                except Exception as e:
                    print(f"  [ERROR] {e}")
            
            if not endpoint_working:
                direct_results["failed"].append(endpoint["name"])
    
    return {
        "sdk_working": sdk_working,
        "direct_api": direct_results,
        "recommendation": "Use official Velo SDK for proper integration" if not sdk_working else "SDK integration successful"
    }

def main():
    """Main debugging execution"""
    
    print("SuperClaude API Debug Tool - Fixed Version")
    print("="*60)
    print(f"Debug started: {datetime.utcnow().isoformat()}")
    
    # Test DeFiLlama Pro API
    print("\n" + "="*60)
    defillama_results = test_defillama_pro_endpoints()
    
    # Test Velo API
    print("\n" + "="*60)  
    velo_results = test_velo_api()
    
    # Generate summary report
    print("\n" + "="*60)
    print("SUMMARY REPORT")
    print("="*30)
    
    print(f"\nDeFiLlama Pro API:")
    print(f"  Working endpoints: {len(defillama_results['working'])}")
    print(f"  Failed endpoints: {len(defillama_results['failed'])}")
    
    if defillama_results["working"]:
        print("  Working:")
        for endpoint in defillama_results["working"]:
            print(f"    - {endpoint}")
    
    if defillama_results["failed"]:
        print("  Failed:")
        for endpoint in defillama_results["failed"]:
            print(f"    - {endpoint}")
    
    print(f"\nVelo Data API:")
    if velo_results["sdk_working"]:
        print("  Status: SDK integration successful")
    else:
        print("  Status: SDK not available, direct API tested")
        print(f"  Working endpoints: {len(velo_results['direct_api']['working'])}")
        print(f"  Failed endpoints: {len(velo_results['direct_api']['failed'])}")
    
    print(f"\nRecommendation: {velo_results['recommendation']}")
    
    # Save detailed results
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    results_file = f"API_DEBUG_FIXED_{timestamp}.json"
    
    full_results = {
        "debug_session": {
            "timestamp": timestamp,
            "tool": "SuperClaude API Debug - Fixed",
            "focus": "DeFiLlama Pro & Velo Data API issues"
        },
        "defillama_pro": defillama_results,
        "velo_data": velo_results
    }
    
    with open(results_file, 'w') as f:
        json.dump(full_results, f, indent=2, default=str)
    
    print(f"\nDetailed results saved to: {results_file}")
    
    return full_results

if __name__ == "__main__":
    results = main()