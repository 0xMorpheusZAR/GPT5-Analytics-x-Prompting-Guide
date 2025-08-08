import time
import pandas as pd
import requests

# External libraries
try:
    from velodata import lib as velo
    VELO_AVAILABLE = True
except ImportError:
    print("Warning: velodata library not available. Velo integration disabled.")
    VELO_AVAILABLE = False

# === API KEYS ===
DEFILLAMA_KEY = "435722de8920d195d301a595f0c29ed939608c9b1da2d75905e85a68f3ee336d"
COINGECKO_KEY = "CG-MVg68aVqeVyu8fzagC9E1hPj"
VELO_KEY = "25965dc53c424038964e2f720270bece"

# === Base URLs ===
DL_BASE = "https://api.llama.fi"
CG_BASE = "https://pro-api.coingecko.com/api/v3"

# === Headers ===
DL_HEADERS = {"accept": "application/json"}
CG_HEADERS = {"accept": "application/json", "x-cg-pro-api-key": COINGECKO_KEY}

# === Rate-safe HTTP fetchers with retries ===
def fetch_with_retries(url, headers, max_retries=5, delay=0.5):
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 429:
                print(f"[{url}] Rate limited. Backing off (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay * (2 ** attempt))
                continue
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"[{url}] Request failed: {e} (attempt {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(delay * (2 ** attempt))
                continue
            raise
    raise RuntimeError(f"Failed to fetch {url} after {max_retries} retries.")

# === DeFiLlama Data Fetcher ===
def fetch_defillama_protocols():
    print("Fetching DeFiLlama protocols...")
    data = fetch_with_retries(f"{DL_BASE}/protocols", DL_HEADERS)
    df = pd.DataFrame(data)
    print(f"[OK] Fetched {len(df)} DeFiLlama protocols")
    return df

# === CoinGecko Data Fetcher ===
def fetch_coingecko_bitcoin():
    print("Fetching Bitcoin market data from CoinGecko...")
    data = fetch_with_retries(f"{CG_BASE}/coins/bitcoin", CG_HEADERS)
    df = pd.json_normalize(data)
    current_price = df.iloc[0]['market_data.current_price.usd']
    print(f"[OK] Bitcoin price: ${current_price:,.2f}")
    return df

# === Velo Data Fetcher ===
def fetch_velo_spot_data():
    if not VELO_AVAILABLE:
        print("[WARN] Velo data unavailable (library not installed)")
        return pd.DataFrame()
    
    try:
        print("Fetching Velo spot data...")
        client = velo.client(VELO_KEY)
        
        # Pull ETHUSDT spot data over past 10 minutes at 1-minute interval
        ten_min = 1000 * 60 * 10
        params = {
            'type': 'spot',
            'columns': ['buy_dollar_volume', 'sell_dollar_volume'],
            'exchanges': ['binance-spot'],
            'products': ['ETHUSDT'],
            'begin': client.timestamp() - ten_min,
            'end': client.timestamp(),
            'resolution': '1m'
        }
        df = client.get_rows(params)
        print(f"[OK] Fetched {len(df)} Velo data points")
        return df
    except Exception as e:
        print(f"[WARN] Velo data fetch failed: {e}")
        return pd.DataFrame()

# === Enhanced Analytics Functions ===
def analyze_defillama_data(df):
    if df.empty:
        return {}
    
    analysis = {
        'total_protocols': len(df),
        'total_tvl': df['tvl'].sum() if 'tvl' in df.columns else 0,
        'top_5_protocols': df.nlargest(5, 'tvl')[['name', 'tvl']].to_dict('records') if 'tvl' in df.columns else [],
        'chain_distribution': df['chain'].value_counts().head(10).to_dict() if 'chain' in df.columns else {}
    }
    return analysis

def analyze_market_data(df):
    if df.empty:
        return {}
    
    market_data = df.iloc[0]['market_data'] if 'market_data' in df.columns else {}
    analysis = {
        'current_price_usd': market_data.get('current_price', {}).get('usd', 0),
        'market_cap_usd': market_data.get('market_cap', {}).get('usd', 0),
        'total_volume_usd': market_data.get('total_volume', {}).get('usd', 0),
        'price_change_24h': market_data.get('price_change_percentage_24h', 0)
    }
    return analysis

# === Main Function ===
def main():
    print("=" * 60)
    print("    Enhanced Crypto Data Fetcher - SuperClaude Framework")
    print("=" * 60)
    
    # Fetch all data sources
    df_defillama = fetch_defillama_protocols()
    df_coingecko = fetch_coingecko_bitcoin()
    df_velo = fetch_velo_spot_data()
    
    print("\n" + "=" * 60)
    print("                    DATA ANALYSIS")
    print("=" * 60)
    
    # Analyze DeFiLlama data
    dl_analysis = analyze_defillama_data(df_defillama)
    print(f"\nDeFiLlama Analysis:")
    print(f"  - Total Protocols: {dl_analysis.get('total_protocols', 0)}")
    print(f"  - Total TVL: ${dl_analysis.get('total_tvl', 0):,.2f}")
    
    # Analyze Bitcoin data
    btc_analysis = analyze_market_data(df_coingecko)
    print(f"\nBitcoin Analysis:")
    print(f"  - Current Price: ${btc_analysis.get('current_price_usd', 0):,.2f}")
    print(f"  - Market Cap: ${btc_analysis.get('market_cap_usd', 0):,.2f}")
    print(f"  - 24h Change: {btc_analysis.get('price_change_24h', 0):+.2f}%")
    
    # Velo data summary
    if not df_velo.empty:
        print(f"\nVelo Data:")
        print(f"  - Data Points: {len(df_velo)}")
        print(f"  - Columns: {list(df_velo.columns)}")
    
    # Save data
    print("\n" + "=" * 60)
    print("                   SAVING DATA")
    print("=" * 60)
    
    df_defillama.head(20).to_csv("defillama_protocols.csv", index=False)
    df_coingecko.to_csv("coingecko_bitcoin.csv", index=False)
    
    if not df_velo.empty:
        df_velo.to_csv("velo_spot_data.csv", index=False)
        print("[OK] Saved: defillama_protocols.csv, coingecko_bitcoin.csv, velo_spot_data.csv")
    else:
        print("[OK] Saved: defillama_protocols.csv, coingecko_bitcoin.csv")
    
    print("\n" + "=" * 60)
    print("              DATA FETCHING COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()