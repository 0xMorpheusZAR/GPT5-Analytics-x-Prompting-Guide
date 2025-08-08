#!/usr/bin/env python3
"""
Test script for GPT-5 Crypto Intelligence Suite
Tests all 5 analysis modules and generates validation report
"""
import os
import sys
import time
import json
import subprocess
import threading
from datetime import datetime
import requests

def start_server():
    """Start the crypto intelligence backend server"""
    os.environ['COINGECKO_API_KEY'] = 'CG-MVg68aVqeVyu8fzagC9E1hPj'
    os.environ['VELO_API_KEY'] = '25965dc53c424038964e2f720270bece'
    
    # Start the server in a separate process
    return subprocess.Popen([
        sys.executable, 'crypto_intel_backend.py'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def wait_for_server(max_attempts=30):
    """Wait for server to be ready"""
    for attempt in range(max_attempts):
        try:
            response = requests.get('http://localhost:8080/api/health', timeout=2)
            if response.status_code == 200:
                print(f"✅ Server ready after {attempt + 1} attempts")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(1)
    
    print("❌ Server failed to start within timeout")
    return False

def test_endpoint(endpoint, name, timeout=30):
    """Test a specific API endpoint"""
    print(f"\n🧪 Testing {name}...")
    start_time = time.time()
    
    try:
        response = requests.get(f'http://localhost:8080/api/{endpoint}', timeout=timeout)
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'unknown')
            
            print(f"✅ {name} - Status: {status} ({elapsed_time:.2f}s)")
            
            # Show key metrics from response
            if endpoint == 'altcoin-outperformers':
                outperformers = data.get('outperformers', [])
                print(f"   📊 Found {len(outperformers)} outperforming altcoins")
                if outperformers:
                    top = outperformers[0]
                    print(f"   🏆 Top: {top['symbol']} (+{top['return_30d']}%)")
            
            elif endpoint == 'high-beta-analysis':
                coins = data.get('high_beta_coins', [])
                print(f"   📊 Found {len(coins)} high-beta coins")
                if coins:
                    top = coins[0]
                    print(f"   🏆 Top: {top['symbol']} (Beta: {top['beta']})")
            
            elif endpoint == 'defillama-screener':
                protocols = data.get('qualified_protocols', [])
                total = data.get('total_found', 0)
                print(f"   📊 Found {total} qualified protocols")
                if protocols:
                    top = protocols[0]
                    print(f"   🏆 Top: {top['name']} (+{top['tvl_growth_30d']}% TVL growth)")
            
            elif endpoint == 'microcap-report':
                report = data.get('report', {})
                coin_info = report.get('coin_info', {})
                if coin_info:
                    print(f"   📊 Analyzed: {coin_info.get('name')} ({coin_info.get('symbol')})")
                    print(f"   💰 Market Cap: ${coin_info.get('market_cap', 0):,.0f}")
            
            return True, elapsed_time, data
        else:
            print(f"❌ {name} - HTTP {response.status_code}: {response.text[:100]}")
            return False, elapsed_time, None
            
    except requests.exceptions.Timeout:
        print(f"⏱️ {name} - Request timed out after {timeout}s")
        return False, timeout, None
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"❌ {name} - Error: {str(e)}")
        return False, elapsed_time, None

def test_deep_dive():
    """Test deep dive analysis with a specific ticker"""
    print(f"\n🧪 Testing Deep Dive Analysis (BTC)...")
    start_time = time.time()
    
    try:
        response = requests.get('http://localhost:8080/api/deep-dive/BTC', timeout=30)
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            analysis = data.get('analysis', {})
            token_info = analysis.get('token_info', {})
            
            print(f"✅ Deep Dive Analysis - Success ({elapsed_time:.2f}s)")
            print(f"   📊 Token: {token_info.get('name')} ({token_info.get('symbol')})")
            print(f"   💰 Price: ${token_info.get('current_price', 0):,.2f}")
            print(f"   📈 30d Change: {token_info.get('price_change_30d', 0):.2f}%")
            
            return True, elapsed_time, data
        else:
            print(f"❌ Deep Dive Analysis - HTTP {response.status_code}")
            return False, elapsed_time, None
            
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"❌ Deep Dive Analysis - Error: {str(e)}")
        return False, elapsed_time, None

def generate_report(results):
    """Generate validation report"""
    print("\n" + "="*80)
    print("🎯 GPT-5 CRYPTO INTELLIGENCE SUITE - VALIDATION REPORT")
    print("="*80)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Server: http://localhost:8080")
    print()
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['success'])
    total_time = sum(r['time'] for r in results)
    
    print("📊 SUMMARY:")
    print(f"   • Total Tests: {total_tests}")
    print(f"   • Passed: {passed_tests}")
    print(f"   • Failed: {total_tests - passed_tests}")
    print(f"   • Success Rate: {passed_tests/total_tests*100:.1f}%")
    print(f"   • Total Time: {total_time:.2f}s")
    print(f"   • Average Time: {total_time/total_tests:.2f}s")
    print()
    
    print("🔍 DETAILED RESULTS:")
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"   • {result['name']:<25} {status:<8} {result['time']:.2f}s")
    
    print("\n🎉 CONCLUSION:")
    if passed_tests == total_tests:
        print("   ALL TESTS PASSED! 🚀")
        print("   The crypto intelligence suite is fully operational.")
    else:
        print(f"   {total_tests - passed_tests} test(s) failed. Please review the errors above.")
    
    print("="*80)

def main():
    print("GPT-5 Crypto Intelligence Suite - End-to-End Testing")
    print("="*60)
    
    # Start server
    print("🔧 Starting backend server...")
    server_process = start_server()
    
    try:
        # Wait for server to be ready
        if not wait_for_server():
            return 1
        
        # Test all endpoints
        test_results = []
        
        # Core analysis modules
        modules = [
            ('health', 'Health Check'),
            ('altcoin-outperformers', 'Altcoin Outperformers'),
            ('high-beta-analysis', 'High Beta Analysis'), 
            ('defillama-screener', 'DeFiLlama Screener'),
            ('microcap-report', 'Micro-Cap Report')
        ]
        
        for endpoint, name in modules:
            success, time_taken, data = test_endpoint(endpoint, name)
            test_results.append({
                'name': name,
                'endpoint': endpoint,
                'success': success,
                'time': time_taken,
                'data': data
            })
        
        # Test deep dive separately
        success, time_taken, data = test_deep_dive()
        test_results.append({
            'name': 'Deep Dive Analysis',
            'endpoint': 'deep-dive/BTC',
            'success': success,
            'time': time_taken,
            'data': data
        })
        
        # Generate report
        generate_report(test_results)
        
        # Save detailed results
        with open('test_results.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'results': test_results
            }, f, indent=2, default=str)
        print(f"\n💾 Detailed results saved to test_results.json")
        
        return 0 if all(r['success'] for r in test_results) else 1
        
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        server_process.terminate()
        server_process.wait()

if __name__ == '__main__':
    sys.exit(main())