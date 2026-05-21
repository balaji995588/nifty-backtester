import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Download NIFTY50 daily data from Jan 2023 to Dec 2024
df = yf.download("^NSEI", start="2023-01-01", end="2024-12-31")

# Flatten multi-level column headers that yfinance creates
df.columns = df.columns.get_level_values(0)

# Calculate 20-day Simple Moving Average (short term trend)
df['SMA20'] = df['Close'].rolling(window=20).mean()

# Calculate 50-day Simple Moving Average (long term trend)
df['SMA50'] = df['Close'].rolling(window=50).mean()

# Create signal column: 1 when SMA20 is above SMA50 (bullish), 0 otherwise
df['Signal'] = 0
df.loc[df['SMA20'] > df['SMA50'], 'Signal'] = 1

# Detect crossover points: where signal changes from 0 to 1 (buy) or 1 to 0 (sell)
df['Crossover'] = df['Signal'].diff()

# --- PLOT ---
plt.figure(figsize=(14, 7))

# Plot the closing price in dark blue
plt.plot(df['Close'], color='#1A1A2E', linewidth=1.2, label='NIFTY50 Close')

# Plot 20-day SMA in amber
plt.plot(df['SMA20'], color='#D97706', linewidth=1.2, label='SMA 20', linestyle='--')

# Plot 50-day SMA in green
plt.plot(df['SMA50'], color='#059669', linewidth=1.2, label='SMA 50', linestyle='--')

# Mark BUY signals (where SMA20 crosses above SMA50) with green triangles
buy_signals = df[df['Crossover'] == 1]
plt.scatter(buy_signals.index, buy_signals['Close'], 
            marker='^', color='#059669', s=120, zorder=5, label='BUY Signal')

# Mark SELL signals (where SMA20 crosses below SMA50) with red triangles
sell_signals = df[df['Crossover'] == -1]
plt.scatter(sell_signals.index, sell_signals['Close'], 
            marker='v', color='#DC2626', s=120, zorder=5, label='SELL Signal')

# Add chart labels and formatting
plt.title('NIFTY50 — Moving Average Crossover Strategy (2023–2024)')
plt.xlabel('Date')
plt.ylabel('Price (INR)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# Print how many buy and sell signals were generated
print(f"Total BUY signals: {len(buy_signals)}")
print(f"Total SELL signals: {len(sell_signals)}")

# ---- PERFORMANCE METRICS ----

# Calculate daily percentage return of NIFTY50
df['Market_Return'] = df['Close'].pct_change()

# Strategy return: only earn market return on days when Signal is 1 (we are holding)
# Shift signal by 1 day because we act on next day's open after signal fires
df['Strategy_Return'] = df['Market_Return'] * df['Signal'].shift(1)

# Remove NaN rows created by rolling windows and pct_change
df.dropna(inplace=True)

# Calculate cumulative returns to see total growth over period
df['Cumulative_Market'] = (1 + df['Market_Return']).cumprod()
df['Cumulative_Strategy'] = (1 + df['Strategy_Return']).cumprod()

# Sharpe Ratio: measures return per unit of risk (higher is better, above 1.0 is good)
# Multiply by sqrt(252) to annualise (252 trading days in a year)
sharpe = (df['Strategy_Return'].mean() / df['Strategy_Return'].std()) * (252 ** 0.5)

# Maximum Drawdown: biggest peak-to-trough drop the strategy experienced
rolling_max = df['Cumulative_Strategy'].cummax()
drawdown = (df['Cumulative_Strategy'] - rolling_max) / rolling_max
max_drawdown = drawdown.min()

# CAGR: Compound Annual Growth Rate over the full period
total_days = (df.index[-1] - df.index[0]).days
cagr = (df['Cumulative_Strategy'].iloc[-1] ** (365 / total_days)) - 1

# Print the results
print("=" * 40)
print("STRATEGY PERFORMANCE SUMMARY")
print("=" * 40)
print(f"Sharpe Ratio      : {sharpe:.2f}")
print(f"Max Drawdown      : {max_drawdown:.2%}")
print(f"CAGR              : {cagr:.2%}")
print(f"Final Return      : {(df['Cumulative_Strategy'].iloc[-1] - 1):.2%}")
print(f"Buy & Hold Return : {(df['Cumulative_Market'].iloc[-1] - 1):.2%}")
print("=" * 40)

# ---- BROKERAGE COST SIMULATION ----

# STT (Securities Transaction Tax) charged by SEBI on sell side only for equity delivery
# Current rate: 0.1% of transaction value on sell
STT_RATE = 0.001

# Exchange transaction charges (NSE charges approx 0.00325% per trade)
EXCHANGE_CHARGE = 0.0000325

# SEBI turnover fee (0.0001% per trade)
SEBI_FEE = 0.000001

# Brokerage: assume flat Rs 20 per order (Zerodha/discount broker model)
# We divide by average NIFTY price to convert to percentage
avg_price = df['Close'].mean()
BROKERAGE = 20 / avg_price

# Total cost per trade (buy + sell combined)
TOTAL_COST_PER_TRADE = (STT_RATE + EXCHANGE_CHARGE + SEBI_FEE + BROKERAGE) * 2

# Count total number of trades (each buy signal = 1 trade)
num_trades = len(buy_signals)

# Calculate total cost drag on returns
total_cost_drag = TOTAL_COST_PER_TRADE * num_trades

# Adjust final strategy return after brokerage costs
adjusted_return = (df['Cumulative_Strategy'].iloc[-1] - 1) - total_cost_drag

print("=" * 40)
print("AFTER BROKERAGE COSTS (Sharekhan Model)")
print("=" * 40)
print(f"Cost per trade     : {TOTAL_COST_PER_TRADE:.4%}")
print(f"Total trades       : {num_trades}")
print(f"Total cost drag    : {total_cost_drag:.4%}")
print(f"Return before costs: {(df['Cumulative_Strategy'].iloc[-1] - 1):.2%}")
print(f"Return after costs : {adjusted_return:.2%}")
print("=" * 40)

# ---- CUMULATIVE RETURNS CHART ----

# Plot strategy returns vs simply buying and holding NIFTY50
plt.figure(figsize=(14, 6))

# Plot buy and hold cumulative return in dark blue
plt.plot(df['Cumulative_Market'], 
         color='#1A1A2E', linewidth=1.5, label='Buy & Hold NIFTY50')

# Plot strategy cumulative return in amber
plt.plot(df['Cumulative_Strategy'], 
         color='#D97706', linewidth=1.5, label='MA Crossover Strategy')

# Add a horizontal line at 1.0 representing starting capital (no gain no loss)
plt.axhline(y=1.0, color='#6B7280', linewidth=0.8, linestyle='--', label='Starting Capital')

# Shade the area under strategy curve to make it visually clear
plt.fill_between(df.index, df['Cumulative_Strategy'], 1, 
                 alpha=0.1, color='#D97706')

# Add annotations showing final returns
plt.annotate(f"Strategy: {(df['Cumulative_Strategy'].iloc[-1]-1):.1%}", 
             xy=(df.index[-1], df['Cumulative_Strategy'].iloc[-1]),
             xytext=(-120, 10), textcoords='offset points',
             color='#D97706', fontsize=10, fontweight='bold')

plt.annotate(f"Buy & Hold: {(df['Cumulative_Market'].iloc[-1]-1):.1%}", 
             xy=(df.index[-1], df['Cumulative_Market'].iloc[-1]),
             xytext=(-120, 10), textcoords='offset points',
             color='#1A1A2E', fontsize=10, fontweight='bold')

# Labels and formatting
plt.title('Strategy vs Buy & Hold — Cumulative Returns (2023–2024)')
plt.xlabel('Date')
plt.ylabel('Growth of ₹1 Invested')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
