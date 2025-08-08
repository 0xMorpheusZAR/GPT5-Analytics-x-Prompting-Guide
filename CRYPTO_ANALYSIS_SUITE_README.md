# 🚀 SuperClaude Crypto Analysis Suite

## Professional-Grade Multi-Role Crypto Analysis Platform

A comprehensive crypto analysis framework integrating **SuperClaude Framework v3.0** with multi-API data sources for professional trading and risk management.

---

## 🎭 Six Specialized Analysis Roles

### 1. 🛡️ **Risk Manager & Macro PM**
**Daily risk regime scoring (0-100) + tactical allocation recommendations**

**Role Prompt:**
```
Role: Crypto risk manager + macro PM.

Task: Build a daily "risk regime score" (0–100) and a simple allocation plan (BTC % / ETH % / Top-N Alts % / Cash %) for {date_range}, with a 1–3 day trading plan.
```

**Data Sources:**
- CoinGecko Pro: Global metrics, dominance, volume, market breadth
- DefiLlama: TVL momentum, stablecoins, yields  
- Velo Data: Futures/spot flow, funding rates, OI analysis

**Output:** Risk score, allocation percentages, trading plan with entry/exit levels

---

### 2. 🔍 **Quant Sector Scout** 
**Sector rotation opportunity identification**

**Role Prompt:**
```
Role: Quant sector scout.

Task: Identify 3–5 sectors primed for outperformance in the next {7–21} days and the top {5–15} tickers per sector with entry zones & invalidations.
```

**Data Sources:**
- CoinGecko Pro: Categories ROI, volume, trending pools
- DefiLlama: TVL velocity by sector/protocol
- Velo Data: OI validation, funding neutrality, taker flow

**Output:** Top 5 sectors, 8-15 tickers per sector, entry zones, invalidation levels

---

### 3. 📉 **Tactical Dip-Buyer**
**Leverage reset detection and scaling plans**

**Role Prompt:**
```
Role: Tactical dip-buyer.

Task: Detect pairs where leverage has *meaningfully reset* while spot demand is stabilizing, then produce laddered bids & time-based scaling plan for {N} assets.
```

**Data Sources:**
- CoinGecko Pro: OHLC, volume charts, derivatives data
- DefiLlama: Protocol TVL drawdown vs price analysis
- Velo Data: OI reset magnitude, funding percentile flips, taker imbalance

**Output:** Laddered entry plans, reset scores, invalidation levels, position sizing

---

### 4. 💰 **Yield PM**
**DeFi opportunity ranking with risk adjustment**

**Role Prompt:**
```
Role: Yield PM.

Task: Rank the top {K} DeFi opportunities where net APY is attractive *after* protocol liquidity, token concentration, and market beta risk.
```

**Data Sources:**
- DefiLlama: Yields universe, TVL trends, APY variance
- CoinGecko Pro: Token liquidity, category beta, drawdown risk
- Velo Data: Flow analysis for exit risk assessment

**Output:** Risk-adjusted yield scores, stress test scenarios, sizing guidance

---

### 5. ⚡ **Five-Minute Altcoin Strength**
**Quick ETH outperformance check**

**Role Prompt:**
```
Task: List five altcoins that beat ETH's weekly return today. Give each coin's one-sentence catalyst and a link to price data.
```

**Data Sources:**
- CoinGecko Pro: Weekly returns, market performance
- Real-time price comparison vs ETH

**Output:** 5 ETH outperformers, catalysts, price chart links

---

### 6. 💎 **Gem Deep Dive**
**Micro-cap fundamental analysis**

**Role Prompt:**
```
Task: Select one micro-cap below USD 30 million with rising on-chain volume this week. Write a concise fundamental report: team, product, tokenomics, runway, and three red flags.
```

**Data Sources:**
- CoinGecko Pro: Market cap, volume, on-chain metrics
- DefiLlama: Protocol analysis, TVL trends
- Fundamental research: Team, tokenomics, roadmap

**Output:** Complete fundamental report, red flag analysis, investment thesis

---

## 🖥️ Beautiful Web Dashboard

### Interactive Features:
- **Real-time API status monitoring**
- **One-click analysis execution**
- **Professional data visualization** 
- **Mobile-responsive design**
- **Executive dashboard summary**
- **Embedded role prompts**

### Dashboard Components:
```html
• 6 Role Cards with embedded prompts
• Live API status indicators
• Real-time results display
• Professional metrics grids
• Executive summary panel
• Mobile-optimized interface
```

---

## 🔧 Technical Implementation

### Core Architecture:
```python
class CryptoAnalysisSuite:
    - Multi-API data fetching with retry logic
    - Rate limiting and error handling
    - Composite scoring algorithms
    - Risk-adjusted allocation models
    - Professional report generation
```

### API Integration:
- **CoinGecko Pro API**: `CG-MVg68aVqeVyu8fzagC9E1hPj`
- **DefiLlama API**: Public endpoint access
- **Velo Data API**: `25965dc53c424038964e2f720270bece`

### Key Features:
✅ **Professional error handling**  
✅ **Rate limiting & retry logic**  
✅ **Multi-timeframe analysis**  
✅ **Risk-adjusted scoring**  
✅ **Real-time data integration**  
✅ **JSON report export**  
✅ **Executive dashboard**  

---

## 🚀 Usage Examples

### Command Line:
```bash
python crypto_analysis_suite.py
```

### Web Interface:
```bash
# Open crypto_dashboard.html in browser
start crypto_dashboard.html
```

### Programmatic:
```python
from crypto_analysis_suite import CryptoAnalysisSuite

suite = CryptoAnalysisSuite()
results = suite.run_full_analysis_suite()
```

---

## 📊 Sample Outputs

### Risk Manager Output:
```json
{
  "composite_risk_score": 67.3,
  "allocation": {
    "BTC": 42.5,
    "ETH": 27.0, 
    "Top_Alts": 18.5,
    "Cash": 12.0
  },
  "regime": "NEUTRAL"
}
```

### Sector Scout Output:
```json
{
  "sector": "AI & Big Data",
  "momentum": "+24.7% (7d)",
  "top_picks": [
    {
      "symbol": "FET",
      "entry": 0.82,
      "invalidation": 0.65
    }
  ]
}
```

---

## 🎯 SuperClaude Framework Integration

### Commands Available:
- `/sc:analyze crypto_analysis_suite.py`
- `/sc:implement new-analysis-module` 
- `/sc:design risk-scoring-algorithm`
- `/sc:troubleshoot api-connection-issues`

### Framework Benefits:
🔹 **16 specialized commands** for development  
🔹 **Smart personas** for domain expertise  
🔹 **MCP server integration**  
🔹 **Task management** with progress tracking  
🔹 **Token optimization** for efficient conversations  

---

## 📈 Professional Results

### Executive Dashboard:
- **Market Regime Classification**
- **Risk Level Assessment** 
- **Opportunity Pipeline Counts**
- **Key Recommendations**
- **Quick Highlights**

### Detailed Analysis:
- **Multi-timeframe momentum scoring**
- **Risk-adjusted allocation recommendations**
- **Sector rotation opportunities**  
- **Leverage reset detection**
- **DeFi yield optimization**
- **Micro-cap fundamental research**

---

## 🔗 Integration & Deployment

### Files Structure:
```
├── crypto_analysis_suite.py     # Main analysis engine
├── crypto_dashboard.html        # Web interface  
├── crypto_risk_manager.py       # Risk scoring system
├── enhanced_crypto_data_fetcher.py  # Data pipeline
├── CLAUDE.md                    # Framework configuration
└── analysis_results/            # JSON exports
```

### GitHub Repository:
**https://github.com/0xMorpheusZAR/GPT5-Analytics-x-Prompting-Guide**

---

## 🏆 Professional Features

✅ **Six specialized analysis roles**  
✅ **Beautiful web dashboard interface**  
✅ **Real-time multi-API integration**  
✅ **Professional risk management**  
✅ **Sector rotation detection**  
✅ **Leverage reset analysis**  
✅ **DeFi yield optimization**  
✅ **Micro-cap research capabilities**  
✅ **Executive summary reporting**  
✅ **SuperClaude Framework integration**  

---

*Built with SuperClaude Framework v3.0.0 • Professional-grade crypto analysis • Multi-API integration*