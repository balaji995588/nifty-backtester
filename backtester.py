import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import pandas_ta as ta

# Download NIFTY50 daily data from Jan 2023 to Dec 2024
df = yf.download("^NSEI", start="2023-01-01", end="2024-12-31")

# Flatten multi-level column headers that yfinance creates
df.columns = df.columns.get_level_values(0)

# Calculate 20-day Simple Moving Average (short term trend)
df['SMA20'] = df['Close'].rolling(window=20).mean()

# Calculate 50-day Simple Moving Average (long term trend)
df['SMA50'] = df['Close'].rolling(window=50).mean()

# Calculate RSI with 14-day window (industry standard period)
# RSI above 70 = overbought (avoid buying), below 30 = oversold (good to buy)
df['RSI'] = ta.rsi(df['Close'], length=14)

# Calculate daily percentage return of NIFTY50
df['Market_Return'] = df['Close'].pct_change()

# Create original MA signal: 1 when SMA20 above SMA50 (bullish), 0 otherwise
df['Signal'] = 0
df.loc[df['SMA20'] > df['SMA50'], 'Signal'] = 1

# Detect original crossover points
df['Crossover'] = df['Signal'].diff()

# Create RSI filtered signal: only buy when MA crossover AND RSI below 70
df['Signal_RSI'] = 0
df.loc[(df['SMA20'] > df['SMA50']) & (df['RSI'] < 70), 'Signal_RSI'] = 1

# Detect crossovers on RSI filtered signal
df['Crossover_RSI'] = df['Signal_RSI'].diff()

# Original strategy return
df['Strategy_Return'] = df['Market_Return'] * df['Signal'].shift(1)

# RSI filtered strategy return
df['Strategy_Return_RSI'] = df['Market_Return'] * df['Signal_RSI'].shift(1)

# Remove NaN rows
df.dropna(inplace=True)

# Keep only signals where original MA crossover also fires
# This prevents RSI from generating extra signals mid-trend
df.loc[df['Crossover'] == 0, 'Crossover_RSI'] = 0

# Identify buy and sell signals for original strategy
buy_signals = df[df['Crossover'] == 1]
sell_signals = df[df['Crossover'] == -1]

# Identify buy and sell signals for RSI filtered strategy
buy_signals_rsi = df[df['Crossover_RSI'] == 1]
sell_signals_rsi = df[df['Crossover_RSI'] == -1]

# Calculate cumulative returns for both strategies
df['Cumulative_Market'] = (1 + df['Market_Return']).cumprod()
df['Cumulative_Strategy'] = (1 + df['Strategy_Return']).cumprod()
df['Cumulative_RSI'] = (1 + df['Strategy_Return_RSI']).cumprod()

# Total days for CAGR calculation
total_days = (df.index[-1] - df.index[0]).days

# Sharpe Ratio for original strategy
sharpe = (df['Strategy_Return'].mean() / df['Strategy_Return'].std()) * (252 ** 0.5)

# Sharpe Ratio for RSI filtered strategy
sharpe_rsi = (df['Strategy_Return_RSI'].mean() / df['Strategy_Return_RSI'].std()) * (252 ** 0.5)

# Max Drawdown for original strategy
rolling_max = df['Cumulative_Strategy'].cummax()
max_drawdown = ((df['Cumulative_Strategy'] - rolling_max) / rolling_max).min()

# Max Drawdown for RSI strategy
rolling_max_rsi = df['Cumulative_RSI'].cummax()
max_drawdown_rsi = ((df['Cumulative_RSI'] - rolling_max_rsi) / rolling_max_rsi).min()

# CAGR for original strategy
cagr = (df['Cumulative_Strategy'].iloc[-1] ** (365 / total_days)) - 1

# CAGR for RSI filtered strategy
cagr_rsi = (df['Cumulative_RSI'].iloc[-1] ** (365 / total_days)) - 1

# ---- PRINT RESULTS ----

print("=" * 40)
print("STRATEGY PERFORMANCE SUMMARY")
print("=" * 40)
print(f"Sharpe Ratio      : {sharpe:.2f}")
print(f"Max Drawdown      : {max_drawdown:.2%}")
print(f"CAGR              : {cagr:.2%}")
print(f"Final Return      : {(df['Cumulative_Strategy'].iloc[-1] - 1):.2%}")
print(f"Buy & Hold Return : {(df['Cumulative_Market'].iloc[-1] - 1):.2%}")
print("=" * 40)

print("\n")
print("=" * 50)
print("ORIGINAL vs RSI FILTERED STRATEGY")
print("=" * 50)
print(f"{'Metric':<20} {'Original':>12} {'RSI Filtered':>12}")
print("-" * 50)
print(f"{'Sharpe Ratio':<20} {sharpe:>12.2f} {sharpe_rsi:>11.2f}")
print(f"{'Max Drawdown':<20} {max_drawdown:>12.2%} {max_drawdown_rsi:>11.2%}")
print(f"{'CAGR':<20} {cagr:>12.2%} {cagr_rsi:>11.2%}")
print(f"{'Buy Signals':<20} {len(buy_signals):>12} {len(buy_signals_rsi):>12}")
print("=" * 50)

# ---- BROKERAGE COST SIMULATION ----

# STT on sell side: 0.1%
STT_RATE = 0.001

# NSE exchange charges per trade
EXCHANGE_CHARGE = 0.0000325

# SEBI turnover fee per trade
SEBI_FEE = 0.000001

# Flat brokerage Rs 20 per order converted to percentage
avg_price = df['Close'].mean()
BROKERAGE = 20 / avg_price

# Total cost per round trip (buy + sell)
TOTAL_COST_PER_TRADE = (STT_RATE + EXCHANGE_CHARGE + SEBI_FEE + BROKERAGE) * 2

# Total cost drag across all trades
total_cost_drag = TOTAL_COST_PER_TRADE * len(buy_signals)

# Adjusted return after costs
adjusted_return = (df['Cumulative_Strategy'].iloc[-1] - 1) - total_cost_drag

print("\n")
print("=" * 40)
print("AFTER BROKERAGE COSTS (Sharekhan Model)")
print("=" * 40)
print(f"Cost per trade     : {TOTAL_COST_PER_TRADE:.4%}")
print(f"Total trades       : {len(buy_signals)}")
print(f"Total cost drag    : {total_cost_drag:.4%}")
print(f"Return before costs: {(df['Cumulative_Strategy'].iloc[-1] - 1):.2%}")
print(f"Return after costs : {adjusted_return:.2%}")
print("=" * 40)

# ---- CHART 1: MA CROSSOVER WITH SIGNALS ----

plt.figure(figsize=(14, 7))

# Closing price
plt.plot(df['Close'], color='#1A1A2E', linewidth=1.2, label='NIFTY50 Close')

# SMA lines
plt.plot(df['SMA20'], color='#D97706', linewidth=1.2, label='SMA 20', linestyle='--')
plt.plot(df['SMA50'], color='#059669', linewidth=1.2, label='SMA 50', linestyle='--')

# Original buy/sell signals
plt.scatter(buy_signals.index, buy_signals['Close'],
            marker='^', color='#059669', s=120, zorder=5, label='BUY Signal')
plt.scatter(sell_signals.index, sell_signals['Close'],
            marker='v', color='#DC2626', s=120, zorder=5, label='SELL Signal')

plt.title('NIFTY50 — Moving Average Crossover Strategy (2023–2024)')
plt.xlabel('Date')
plt.ylabel('Price (INR)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# ---- CHART 2: CUMULATIVE RETURNS COMPARISON ----

plt.figure(figsize=(14, 6))

# All three lines: buy and hold, original strategy, RSI filtered strategy
plt.plot(df['Cumulative_Market'],
         color='#1A1A2E', linewidth=1.5, label='Buy & Hold NIFTY50')
plt.plot(df['Cumulative_Strategy'],
         color='#D97706', linewidth=1.5, label='MA Crossover Strategy')
plt.plot(df['Cumulative_RSI'],
         color='#4F46E5', linewidth=1.5, label='RSI Filtered Strategy', linestyle='--')

# Starting capital line
plt.axhline(y=1.0, color='#6B7280', linewidth=0.8, linestyle='--', label='Starting Capital')

plt.title('Strategy vs RSI Filtered vs Buy & Hold — Cumulative Returns')
plt.xlabel('Date')
plt.ylabel('Growth of ₹1 Invested')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# ---- CHART 3: RSI VALUES ----

plt.figure(figsize=(14, 6))

# All three lines: buy and hold, original strategy, RSI filtered strategy
plt.plot(df['RSI'],
         color='#1A1A2E', linewidth=1.5, label='RSI (14-day)')

# Starting capital line
plt.axhline(y=70, color="#F00E1A", linewidth=0.8, linestyle='-', label='OverBought Level')
plt.axhline(y=30, color="#15F00E", linewidth=0.8, linestyle='-', label='OverSold Level')

plt.title('NIFTY50 RSI (14-day)')
plt.xlabel('Date')
plt.ylabel('RSI Value')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()