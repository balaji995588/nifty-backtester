# Algorithmic Trading Backtester — NIFTY50 & BTC/USDT

A Python-based algorithmic trading backtester that implements a Moving Average 
Crossover strategy on real market data. Built from scratch using live data APIs 
— no paid subscriptions required.

## What This Does

- Pulls live NIFTY50 data via yfinance and BTC/USDT data via Binance public API
- Implements a 20/50-day Simple Moving Average Crossover strategy
- Generates buy/sell signals and plots them on price charts
- Calculates real performance metrics: Sharpe Ratio, Max Drawdown, CAGR
- Simulates real brokerage costs including STT, exchange charges, and SEBI fees
- Compares strategy returns against a simple buy and hold benchmark

## Results

### NIFTY50 (2023–2024)
| Metric | Value |
|--------|-------|
| Sharpe Ratio | 1.16 |
| Max Drawdown | -8.34% |
| CAGR | 12.50% |
| Strategy Return | 23.61% |
| Buy & Hold Return | 37.84% |

### BTC/USDT (2023–2024)
| Metric | Value |
|--------|-------|
| Sharpe Ratio | 1.01 |
| Max Drawdown | -26.50% |
| CAGR | 38.11% |
| Strategy Return | 48.90% |
| Buy & Hold Return | 149.99% |

### Key Insight
NIFTY50 delivered better risk-adjusted returns (Sharpe 1.16 vs 1.01) with 
significantly lower drawdown (-8.34% vs -26.50%). BTC offered higher raw 
returns but with 3x the volatility risk. This demonstrates the fundamental 
risk-return tradeoff — higher potential returns always come with higher risk.

Both strategies underperformed buy and hold during the 2023-2024 bull markets, 
which is expected behavior for MA crossover strategies in strong trending 
conditions. The strategy's strength is capital protection during downturns, 
not maximising bull market gains.

## Brokerage Cost Simulation (India-Specific)
The NIFTY backtester includes real Indian market transaction costs:
- STT (Securities Transaction Tax): 0.1% on sell side
- NSE Exchange charges: 0.00325% per trade
- SEBI turnover fee: 0.0001% per trade  
- Brokerage: flat ₹20 per order (discount broker model)
- Total cost drag on 4 trades: 1.57%

## Tech Stack
- Python 3.x
- pandas — data manipulation
- yfinance — NSE/BSE market data
- Binance REST API — crypto market data (no API key required)
- matplotlib — charting and visualisation

## How to Run

### Install dependencies
pip install pandas yfinance matplotlib requests

### Run NIFTY50 backtester
python backtester.py

### Run BTC/USDT backtester
python crypto_backtester.py

## Project Structure
nifty-backtester/
│
├── backtester.py          # NIFTY50 MA crossover strategy + performance metrics
├── crypto_backtester.py   # BTC/USDT strategy via Binance API
└── README.md              # This file

## About
Built as part of a career transition from Java backend engineering 
(fintech/brokerage domain) to quantitative trading systems development.
Domain knowledge from brokerage infrastructure informs the realistic 
cost simulation model.

## What's Next
- RSI indicator as signal filter
- Walk-forward optimisation to avoid overfitting
- Zerodha Kite / Sharekhan API integration for live paper trading
- Machine learning signal generation (Random Forest on OHLCV features)