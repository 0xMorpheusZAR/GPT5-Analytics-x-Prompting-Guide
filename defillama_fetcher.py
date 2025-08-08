import requests
import time
import pandas as pd

# DefiLlama setup  
DL_KEY = "435722de8920d195d301a595f0c29ed939608c9b1da2d75905e85a68f3ee336d"
DL_BASE = "https://api.llama.fi"
DL_HEADERS = {
    "accept": "application/json"
}

# CoinGecko setup
CG_KEY = "CG-MVg68aVqeVyu8fzagC9E1hPj"
CG_BASE = "https://pro-api.coingecko.com/api/v3"
CG_HEADERS = {
    "accept": "application/json",
    "x-cg-pro-api-key": CG_KEY
}

def fetch_defillama(max_requests=100, delay=1.0):
    url = f"{DL_BASE}/protocols"
    for i in range(max_requests):
        resp = requests.get(url, headers=DL_HEADERS)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 429:
            time.sleep(delay * (2 ** i))
        else:
            resp.raise_for_status()
        time.sleep(delay)
    raise RuntimeError("DefiLlama: Max retries exceeded")

def fetch_coingecko(coin_id="bitcoin", max_requests=100, delay=0.5):
    url = f"{CG_BASE}/coins/{coin_id}"
    for i in range(max_requests):
        resp = requests.get(url, headers=CG_HEADERS)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 429:
            time.sleep(delay * (2 ** i))
        else:
            resp.raise_for_status()
        time.sleep(delay)
    raise RuntimeError("CoinGecko: Max retries exceeded")

def main():
    print("Pulling data from both APIs...")
    dl_data = fetch_defillama()
    cg_data = fetch_coingecko()
    
    df_dl = pd.DataFrame(dl_data)
    df_cg = pd.json_normalize(cg_data)
    
    print("DefiLlama sample:")
    print(df_dl.head())
    
    print("\nCoinGecko sample:")
    print(df_cg.loc[:, ['id', 'symbol', 'market_data.current_price.usd']].head())
    
    df_dl.to_csv("combined_defillama.csv", index=False)
    df_cg.to_csv("combined_coingecko.csv", index=False)
    print("Saved outputs: combined_defillama.csv, combined_coingecko.csv")

if __name__ == "__main__":
    main()