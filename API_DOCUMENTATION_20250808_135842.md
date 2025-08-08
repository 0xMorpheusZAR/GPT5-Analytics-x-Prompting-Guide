# SuperClaude API Documentation & Testing Report

Comprehensive documentation and stress testing results for all integrated APIs in the SuperClaude GPT-5 Analytics framework.

**Generated:** 2025-08-08T13:58:42.430953

## Test Summary

- **Total Endpoints Tested:** 15
- **Successful Tests:** 8
- **Failed Tests:** 7
- **Success Rate:** 53.3%

## Performance Overview

- **Average Response Time:** 733.8ms
- **Fastest Endpoint:** coingecko (fastest endpoint) (328.5ms)
- **Slowest Endpoint:** defillama (slowest endpoint) (1660.8ms)

## Coingecko API

**Base URL:** https://pro-api.coingecko.com/api/v3
**Rate Limit:** 500 requests/minute
**Authentication:** API Key Required

### Endpoints

#### [PASS] Market Data

- **Status:** PASS
- **Response Time:** [MEDIUM] 393.2ms
- **Data Size:** 84620 bytes
- **HTTP Status:** 200
- **Fields Found:** id, symbol, name, current_price, market_cap...

#### [PASS] Price History

- **Status:** PASS
- **Response Time:** [MEDIUM] 401.0ms
- **Data Size:** 3261 bytes
- **HTTP Status:** 200
- **Fields Found:** prices, market_caps, total_volumes

#### [PASS] Global Data

- **Status:** PASS
- **Response Time:** [MEDIUM] 328.5ms
- **Data Size:** 3626 bytes
- **HTTP Status:** 200
- **Fields Found:** active_cryptocurrencies, total_market_cap, total_volume

#### [PASS] Trending Coins

- **Status:** PASS
- **Response Time:** [MEDIUM] 330.0ms
- **Data Size:** 54233 bytes
- **HTTP Status:** 200
- **Fields Found:** coins, nfts

#### [PASS] Coin Details

- **Status:** PASS
- **Response Time:** [MEDIUM] 411.1ms
- **Data Size:** 95834 bytes
- **HTTP Status:** 200
- **Fields Found:** id, symbol, name, id, id...

## Defillama API

**Base URL:** https://api.llama.fi
**Rate Limit:** 300 requests/minute
**Authentication:** Public API

### Endpoints

#### [PASS] Protocols List

- **Status:** PASS
- **Response Time:** [SLOW] 1441.0ms
- **Data Size:** 6097757 bytes
- **HTTP Status:** 200
- **Fields Found:** name, symbol, chain, category, tvl

#### [PASS] Protocol Tvl

- **Status:** PASS
- **Response Time:** [SLOW] 1660.8ms
- **Data Size:** 7405496 bytes
- **HTTP Status:** 200
- **Fields Found:** tvl, tokensInUsd, tokens, tvl, tokensInUsd...

#### [PASS] Chains Tvl

- **Status:** PASS
- **Response Time:** [SLOW] 904.6ms
- **Data Size:** 45932 bytes
- **HTTP Status:** 200
- **Fields Found:** tvl, tokenSymbol, name

#### [FAIL] Yields Pools

- **Status:** FAIL
- **Response Time:** [SLOW] 967.5ms
- **Data Size:** 0 bytes
- **HTTP Status:** 404
- **Missing Fields:** pool, chain, project, apy, tvlUsd
- **Error:** HTTP 404: 

#### [FAIL] Stablecoins

- **Status:** FAIL
- **Response Time:** [SLOW] 817.0ms
- **Data Size:** 0 bytes
- **HTTP Status:** 404
- **Missing Fields:** name, symbol, circulating, price
- **Error:** HTTP 404: 

## Velo API

**Base URL:** https://api.velo.xyz
**Rate Limit:** 100 requests/minute
**Authentication:** API Key Required

### Endpoints

#### [FAIL] Market Overview

- **Status:** FAIL
- **Response Time:** [FAST] 60.0ms
- **Data Size:** 0 bytes
- **HTTP Status:** 403
- **Missing Fields:** market_cap, volume, dominance, sentiment
- **Error:** HTTP 403: api key not authorized

#### [FAIL] Institutional Flows

- **Status:** FAIL
- **Response Time:** [FAST] 22.0ms
- **Data Size:** 0 bytes
- **HTTP Status:** 403
- **Missing Fields:** inflows, outflows, net_flow, volume
- **Error:** HTTP 403: api key not authorized

#### [FAIL] Options Flow

- **Status:** FAIL
- **Response Time:** [SLOW] 677.2ms
- **Data Size:** 88 bytes
- **HTTP Status:** 200
- **Missing Fields:** calls, puts, volume, open_interest
- **Error:** Invalid JSON response: Expecting value: line 1 column 1 (char 0)

#### [FAIL] Sentiment Analysis

- **Status:** FAIL
- **Response Time:** [FAST] 32.8ms
- **Data Size:** 0 bytes
- **HTTP Status:** 403
- **Missing Fields:** sentiment_score, social_volume, mentions
- **Error:** HTTP 403: api key not authorized

#### [FAIL] Whale Activity

- **Status:** FAIL
- **Response Time:** [FAST] 14.8ms
- **Data Size:** 0 bytes
- **HTTP Status:** 403
- **Missing Fields:** transactions, total_value, addresses
- **Error:** HTTP 403: api key not authorized
