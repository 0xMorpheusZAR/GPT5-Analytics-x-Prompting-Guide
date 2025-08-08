#!/usr/bin/env python3
"""
Simple test for Crypto Intelligence Suite endpoints
"""
import requests
import json
import time

def test_endpoints():
    base_url = 'http://localhost:8080/api'
    
    print("Testing Crypto Intelligence Suite...")
    print("=" * 50)
    
    # Test endpoints
    endpoints = [
        ('health', 'Health Check'),
        ('altcoin-outperformers', 'Altcoin Outperformers'),
        ('high-beta-analysis', 'High Beta Analysis'),
        ('defillama-screener', 'DeFiLlama Screener'),
        ('microcap-report', 'Micro-Cap Report'),
        ('deep-dive/BTC', 'Deep Dive Analysis (BTC)')
    ]
    
    results = []
    
    for endpoint, name in endpoints:
        print(f"\nTesting {name}...")
        start_time = time.time()
        
        try:
            response = requests.get(f'{base_url}/{endpoint}', timeout=30)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                print(f"[PASS] {name} - {status} ({elapsed:.2f}s)")
                
                # Show summary data
                if 'outperformers' in data:
                    count = len(data['outperformers'])
                    print(f"       Found {count} outperforming coins")
                elif 'high_beta_coins' in data:
                    count = len(data['high_beta_coins'])
                    print(f"       Found {count} high-beta coins")
                elif 'qualified_protocols' in data:
                    count = data.get('total_found', 0)
                    print(f"       Found {count} qualified protocols")
                elif 'analysis' in data:
                    token = data['analysis'].get('token_info', {})
                    print(f"       Analyzed {token.get('name', 'Unknown')}")
                
                results.append((name, True, elapsed))
            else:
                print(f"[FAIL] {name} - HTTP {response.status_code}")
                results.append((name, False, elapsed))
                
        except requests.exceptions.Timeout:
            print(f"[TIMEOUT] {name} - Request timed out")
            results.append((name, False, 30))
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"[ERROR] {name} - {str(e)}")
            results.append((name, False, elapsed))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    total = len(results)
    passed = sum(1 for _, success, _ in results if success)
    total_time = sum(elapsed for _, _, elapsed in results)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    print(f"Total Time: {total_time:.2f}s")
    print(f"Average Time: {total_time/total:.2f}s")
    
    print("\nDETAILS:")
    for name, success, elapsed in results:
        status = "PASS" if success else "FAIL"
        print(f"  {name:<25} {status:<6} {elapsed:.2f}s")
    
    if passed == total:
        print("\nALL TESTS PASSED! System is fully operational.")
    else:
        print(f"\n{total - passed} test(s) failed. Please review errors above.")
    
    return passed == total

if __name__ == '__main__':
    try:
        success = test_endpoints()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        exit(1)