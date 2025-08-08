#!/usr/bin/env python3
"""
Simple API Debug Tool
Quick diagnosis of DeFiLlama and Velo API issues
"""

import requests
import json
import time
from datetime import datetime

def test_defillama_endpoints():
    """Test DeFiLlama endpoints with different approaches"""
    
    print("Testing DeFiLlama API Endpoints")
    print("="*50)
    
    # Test working endpoints
    working_endpoints = [
        "https://api.llama.fi/protocols",
        "https://api.llama.fi/protocol/aave", 
        "https://api.llama.fi/chains"
    ]
    
    # Test problematic endpoints
    problem_endpoints = [
        "https://api.llama.fi/pools",
        "https://api.llama.fi/stablecoins",
        "https://yields.llama.fi/pools",
        "https://stablecoins.llama.fi/stablecoins"
    ]
    
    results = {"working": [], "failed": []}
    
    for url in working_endpoints + problem_endpoints:
        try:
            print(f"\nTesting: {url}")
            start_time = time.time()
            
            response = requests.get(url, timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            print(f"Status: {response.status_code}")
            print(f"Response Time: {response_time:.1f}ms")
            print(f"Content Size: {len(response.content)} bytes")
            
            if response.status_code == 200:
                print("[PASS] SUCCESS")
                results["working"].append(url)
                
                # Try to parse JSON
                try:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        print(f"📊 Data: {len(data)} items")
                        if isinstance(data[0], dict):
                            print(f"📋 Keys: {list(data[0].keys())[:5]}")
                    elif isinstance(data, dict):
                        print(f"📋 Keys: {list(data.keys())[:5]}")
                except:
                    print("⚠️ Non-JSON response")
            else:
                print(f"❌ FAILED: HTTP {response.status_code}")
                results["failed"].append(url)
                print(f"Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results["failed"].append(url)
    
    return results

def test_velo_api():
    """Test Velo API with different authentication methods"""
    
    print("\nTesting Velo Data API")
    print("="*50)
    
    api_key = "25965dc53c424038964e2f720270bece"
    base_url = "https://api.velo.xyz"
    
    # Test different endpoints and auth methods
    test_configs = [
        {"url": f"{base_url}", "auth": None, "name": "Base URL"},
        {"url": f"{base_url}/health", "auth": None, "name": "Health Check"},
        {"url": f"{base_url}/api", "auth": None, "name": "API Info"},
        {"url": f"{base_url}/api/v1/market/overview", "auth": f"Bearer {api_key}", "name": "Market Overview v1"},
        {"url": f"https://data.velo.xyz", "auth": f"Bearer {api_key}", "name": "Alternative URL"},
    ]
    
    results = {"working": [], "failed": []}
    
    for config in test_configs:
        try:
            print(f"\nTesting: {config['name']}")
            print(f"URL: {config['url']}")
            
            headers = {"Accept": "application/json"}
            if config["auth"]:
                headers["Authorization"] = config["auth"]
                print(f"Auth: {config['auth'][:20]}...")
            
            start_time = time.time()
            response = requests.get(config["url"], headers=headers, timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            print(f"Status: {response.status_code}")
            print(f"Response Time: {response_time:.1f}ms")
            print(f"Content Size: {len(response.content)} bytes")
            
            if response.status_code == 200:
                print(f"✅ SUCCESS")
                results["working"].append(config["name"])
                
                try:
                    data = response.json()
                    print(f"📊 JSON Response: {type(data)}")
                    if isinstance(data, dict):
                        print(f"📋 Keys: {list(data.keys())[:5]}")
                except:
                    print(f"📝 Text Response: {response.text[:100]}")
                    
            elif response.status_code == 403:
                print(f"🔒 FORBIDDEN: API key not authorized")
                results["failed"].append(config["name"])
            elif response.status_code == 401:
                print(f"🔑 UNAUTHORIZED: Invalid credentials")
                results["failed"].append(config["name"])
            else:
                print(f"❌ FAILED: HTTP {response.status_code}")
                results["failed"].append(config["name"])
                print(f"Response: {response.text[:100]}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results["failed"].append(config["name"])
    
    return results

def main():
    """Main debugging function"""
    
    print("SuperClaude API Quick Debug")
    print("="*60)
    
    # Test DeFiLlama
    defillama_results = test_defillama_endpoints()
    
    # Test Velo
    velo_results = test_velo_api()
    
    # Summary
    print(f"\n📊 SUMMARY")
    print("="*30)
    print(f"DeFiLlama Working: {len(defillama_results['working'])}")
    print(f"DeFiLlama Failed: {len(defillama_results['failed'])}")
    print(f"Velo Working: {len(velo_results['working'])}")
    print(f"Velo Failed: {len(velo_results['failed'])}")
    
    # Recommendations
    print(f"\n💡 QUICK RECOMMENDATIONS")
    print("="*30)
    
    if defillama_results["failed"]:
        print("DeFiLlama Issues:")
        for failed_url in defillama_results["failed"]:
            if "pools" in failed_url:
                print("- Use https://yields.llama.fi/pools for yield data")
            elif "stablecoins" in failed_url:
                print("- Use https://stablecoins.llama.fi/stablecoins for stablecoin data")
    
    if len(velo_results["working"]) == 0:
        print("Velo Issues:")
        print("- API key needs higher permissions")
        print("- Consider using official Velo Python SDK")
        print("- Install: pip install velodata")
    
    return {
        "defillama": defillama_results,
        "velo": velo_results,
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    results = main()