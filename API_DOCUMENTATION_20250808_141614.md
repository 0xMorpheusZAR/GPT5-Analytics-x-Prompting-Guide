# SuperClaude API Documentation & Testing Report

Comprehensive documentation and stress testing results for all integrated APIs in the SuperClaude GPT-5 Analytics framework.

**Generated:** 2025-08-08T14:16:14.001532

## Test Summary

- **Total Endpoints Tested:** 15
- **Successful Tests:** 10
- **Failed Tests:** 5
- **Success Rate:** 66.7%

## Performance Overview

- **Average Response Time:** 303.1ms
- **Fastest Endpoint:** defillama (fastest endpoint) (39.0ms)
- **Slowest Endpoint:** coingecko (slowest endpoint) (516.5ms)

## Coingecko API

**Base URL:** https://pro-api.coingecko.com/api/v3
**Rate Limit:** 500 requests/minute
**Authentication:** API Key Required

### Endpoints

#### [PASS] Market Data

- **Status:** PASS
- **Response Time:** [SLOW] 516.5ms
- **Data Size:** 84519 bytes
- **HTTP Status:** 200
- **Fields Found:** id, symbol, name, current_price, market_cap...

#### [PASS] Price History

- **Status:** PASS
- **Response Time:** [MEDIUM] 342.6ms
- **Data Size:** 3258 bytes
- **HTTP Status:** 200
- **Fields Found:** prices, market_caps, total_volumes

#### [PASS] Global Data

- **Status:** PASS
- **Response Time:** [MEDIUM] 358.9ms
- **Data Size:** 3617 bytes
- **HTTP Status:** 200
- **Fields Found:** active_cryptocurrencies, total_market_cap, total_volume

#### [PASS] Trending Coins

- **Status:** PASS
- **Response Time:** [MEDIUM] 367.0ms
- **Data Size:** 54040 bytes
- **HTTP Status:** 200
- **Fields Found:** coins, nfts

#### [PASS] Coin Details

- **Status:** PASS
- **Response Time:** [MEDIUM] 436.9ms
- **Data Size:** 96021 bytes
- **HTTP Status:** 200
- **Fields Found:** id, symbol, name, id, id...

## Defillama API

**Base URL:** https://api.llama.fi
**Rate Limit:** 300 requests/minute
**Authentication:** Public API

### Endpoints

#### [PASS] Protocols List

- **Status:** PASS
- **Response Time:** [FAST] 114.7ms
- **Data Size:** 6097757 bytes
- **HTTP Status:** 200
- **Fields Found:** name, symbol, chain, category, tvl

#### [PASS] Protocol Tvl

- **Status:** PASS
- **Response Time:** [MEDIUM] 495.4ms
- **Data Size:** 7405496 bytes
- **HTTP Status:** 200
- **Fields Found:** tvl, tokensInUsd, tokens, tvl, tokensInUsd...

#### [PASS] Chains Tvl

- **Status:** PASS
- **Response Time:** [FAST] 39.0ms
- **Data Size:** 45932 bytes
- **HTTP Status:** 200
- **Fields Found:** tvl, tokenSymbol, name

#### [PASS] Yields Pools

- **Status:** PASS
- **Response Time:** [MEDIUM] 303.3ms
- **Data Size:** 12878750 bytes
- **HTTP Status:** 200
- **Fields Found:** chain, project, tvlUsd, apy, pool

#### [PASS] Stablecoins

- **Status:** PASS
- **Response Time:** [FAST] 57.2ms
- **Data Size:** 377717 bytes
- **HTTP Status:** 200
- **Fields Found:** name, symbol, circulating, price, name

## Velo API

**Base URL:** https://api.velo.xyz
**Rate Limit:** 100 requests/minute
**Authentication:** API Key Required

### Endpoints

#### [FAIL] Market Overview

- **Status:** FAIL
- **Response Time:** [FAST] 38.1ms
- **Data Size:** 0 bytes
- **HTTP Status:** 403
- **Missing Fields:** market_cap, volume, dominance, sentiment
- **Error:** HTTP 403: api key not authorized

#### [FAIL] Institutional Flows

- **Status:** FAIL
- **Response Time:** [FAST] 18.9ms
- **Data Size:** 0 bytes
- **HTTP Status:** 403
- **Missing Fields:** inflows, outflows, net_flow, volume
- **Error:** HTTP 403: api key not authorized

#### [FAIL] Options Flow

- **Status:** FAIL
- **Response Time:** [SLOW] 681.0ms
- **Data Size:** 88 bytes
- **HTTP Status:** 200
- **Missing Fields:** calls, puts, volume, open_interest
- **Error:** Invalid JSON response: Expecting value: line 1 column 1 (char 0)

#### [FAIL] Sentiment Analysis

- **Status:** FAIL
- **Response Time:** [FAST] 12.3ms
- **Data Size:** 0 bytes
- **HTTP Status:** 403
- **Missing Fields:** sentiment_score, social_volume, mentions
- **Error:** HTTP 403: api key not authorized

#### [FAIL] Whale Activity

- **Status:** FAIL
- **Response Time:** [FAST] 14.1ms
- **Data Size:** 0 bytes
- **HTTP Status:** 403
- **Missing Fields:** transactions, total_value, addresses
- **Error:** HTTP 403: api key not authorized
