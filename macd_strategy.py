import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import pandas_ta as ta

# Download NIFTY50 daily data from Jan 2023 to Dec 2024
df = yf.download("^NSEI", start="2023-01-01", end="2024-12-31")

# Flatten multi-level column headers that yfinance creates
df.columns = df.columns.get_level_values(0)

# Returns a new DataFrame, doesn't touch df
macd= ta.macd(df['Close'], fast=12, slow=26, signal=9, append=True);

# Then manually add to df
df['MACD'] = macd['MACD_12_26_9']
df['MACD_Signal'] = macd['MACDs_12_26_9']
df['MACD_Hist'] = macd['MACDh_12_26_9']

print(df[['Close', 'MACD', 'MACD_Signal', 'MACD_Hist']].tail(5))

df['MACD_Signal_Crossover'] = 0
df.loc[df['MACD'] > df['MACD_Signal'], 'MACD_Signal_Crossover'] = 1
# df.loc[df['MACD'] < df['MACD_Signal'], 'MACD_Signal_Crossover'] = -1

df['MACD_Signal_Crossover'] = df['MACD_Signal_Crossover'].diff();

buy_signals = df[df['MACD_Signal_Crossover'] == 1]
sell_signals = df[df['MACD_Signal_Crossover'] == -1]

# Calculate daily percentage return of NIFTY50
df['Market_Return'] = df['Close'].pct_change()
# Original strategy return
df['Strategy_Return'] = df['Market_Return'] * df['MACD_Signal_Crossover'].shift(1)
# Calculate cumulative returns for both strategies
df['Cumulative_Market'] = (1 + df['Market_Return']).cumprod()
df['Cumulative_Strategy'] = (1 + df['Strategy_Return']).cumprod()

# Total days for CAGR calculation
total_days = (df.index[-1] - df.index[0]).days

# Sharpe Ratio for original strategy
sharpe = (df['Strategy_Return'].mean() / df['Strategy_Return'].std()) * (252 ** 0.5)

# Max Drawdown for original strategy
rolling_max = df['Cumulative_Strategy'].cummax()
max_drawdown = ((df['Cumulative_Strategy'] - rolling_max) / rolling_max).min()

# CAGR for original strategy
cagr = (df['Cumulative_Strategy'].iloc[-1] ** (365 / total_days)) - 1


# ---- CHART 1: MACD CROSSOVER WITH SIGNALS ----

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

# Closing price
ax1.plot(df['Close'], color='#1A1A2E', linewidth=1.2, label='NIFTY50 Close')


# Original buy/sell signals
ax1.scatter(buy_signals.index, buy_signals['Close'],
            marker='^', color='#059669', s=120, zorder=5, label='BUY Signal')
ax1.scatter(sell_signals.index, sell_signals['Close'],
            marker='v', color='#DC2626', s=120, zorder=5, label='SELL Signal')


ax1.set_title('NIFTY50 — MACD Strategy (2023–2024)')
ax1.set_xlabel('Date')
ax1.set_ylabel('Price (INR)')
ax1.legend()
ax1.grid(True, alpha=0.3)

ax2.plot(df['MACD'], color='#D97706', linewidth=1.2, label='MACD Line')
ax2.plot(df['MACD_Signal'], color='#059669', linewidth=1.2, label='Signal Line', linestyle='--')
# Color histogram bars green when positive, red when negative
colors = ['#059669' if v >= 0 else '#DC2626' for v in df['MACD_Hist']]
ax2.bar(df.index, df['MACD_Hist'], color=colors, label='MACD Histogram')
ax2.set_title('MACD Indicator')
ax2.set_xlabel('Date')
ax2.set_ylabel('MACD')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# print("=" * 40)
# print("MACD Strategy Backtest Results")
# print("=" * 40)
# print(macd.head())
# print("=" * 40)

# print("=" * 40)
# print("MACD Strategy Backtest Results") 
# # ---- PRINT RESULTS ----

print("=" * 40)
print("STRATEGY PERFORMANCE SUMMARY")
print("=" * 40)
print(f"Sharpe Ratio      : {sharpe:.2f}")
print(f"Max Drawdown      : {max_drawdown:.2%}")
print(f"CAGR              : {cagr:.2%}")
print(f"Final Return      : {(df['Cumulative_Strategy'].iloc[-1] - 1):.2%}")
print(f"Buy & Hold Return : {(df['Cumulative_Market'].iloc[-1] - 1):.2%}")
print("=" * 40)

