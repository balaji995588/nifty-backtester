import requests
import pandas as pd
import matplotlib.pyplot as plt

# Binance public API endpoint - no account or API key needed
# We are fetching BTC/USDT daily candlestick data
url = "https://api.binance.com/api/v3/klines"

# Parameters: symbol, interval (1 day), start time, limit (500 candles max)
params = {
    "symbol": "BTCUSDT",        # Bitcoin vs US Dollar
    "interval": "1d",           # Daily candles
    "startTime": 1672531200000, # Jan 1 2023 in milliseconds
    "endTime": 1735689600000,   # Jan 1 2025 in milliseconds
    "limit": 500                # Max candles to fetch
}

# Make the API request to Binance
response = requests.get(url, params=params)

# Convert response to a pandas DataFrame
raw = response.json()

# Binance returns: [opentime, open, high, low, close, volume, ...]
df_btc = pd.DataFrame(raw, columns=[
    'OpenTime', 'Open', 'High', 'Low', 'Close', 'Volume',
    'CloseTime', 'QuoteVolume', 'Trades', 'TakerBase', 'TakerQuote', 'Ignore'
])

# Convert timestamp to readable date
df_btc['Date'] = pd.to_datetime(df_btc['OpenTime'], unit='ms')

# Set date as index
df_btc.set_index('Date', inplace=True)

# Convert Close column from string to float
df_btc['Close'] = df_btc['Close'].astype(float)

# Check the data loaded correctly
print(f"BTC data loaded: {len(df_btc)} rows")
print(df_btc['Close'].head())

# Calculate 20-day Simple Moving Average for BTC
df_btc['SMA20'] = df_btc['Close'].rolling(window=20).mean()

# Calculate 50-day Simple Moving Average for BTC
df_btc['SMA50'] = df_btc['Close'].rolling(window=50).mean()

# Generate signal: 1 when SMA20 above SMA50 (bullish), 0 otherwise
df_btc['Signal'] = 0
df_btc.loc[df_btc['SMA20'] > df_btc['SMA50'], 'Signal'] = 1

# Detect crossover points where signal changes
df_btc['Crossover'] = df_btc['Signal'].diff()

# Identify buy and sell signal rows
buy_signals_btc = df_btc[df_btc['Crossover'] == 1]
sell_signals_btc = df_btc[df_btc['Crossover'] == -1]

# --- PLOT ---
plt.figure(figsize=(14, 7))

# Plot BTC closing price
plt.plot(df_btc['Close'], color='#1A1A2E', linewidth=1.2, label='BTC/USDT Close')

# Plot 20-day SMA in amber
plt.plot(df_btc['SMA20'], color='#D97706', linewidth=1.2, label='SMA 20', linestyle='--')

# Plot 50-day SMA in green
plt.plot(df_btc['SMA50'], color='#059669', linewidth=1.2, label='SMA 50', linestyle='--')

# Mark BUY signals with green triangles
plt.scatter(buy_signals_btc.index, buy_signals_btc['Close'],
            marker='^', color='#059669', s=120, zorder=5, label='BUY Signal')

# Mark SELL signals with red triangles
plt.scatter(sell_signals_btc.index, sell_signals_btc['Close'],
            marker='v', color='#DC2626', s=120, zorder=5, label='SELL Signal')

# Chart formatting
plt.title('BTC/USDT — Moving Average Crossover Strategy (2023–2024)')
plt.xlabel('Date')
plt.ylabel('Price (USD)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# Print signal counts
print(f"Total BUY signals:  {len(buy_signals_btc)}")
print(f"Total SELL signals: {len(sell_signals_btc)}")

# Calculate daily returns for BTC
df_btc['Market_Return'] = df_btc['Close'].pct_change()

# Strategy return: only earn returns when signal is 1 (holding)
df_btc['Strategy_Return'] = df_btc['Market_Return'] * df_btc['Signal'].shift(1)

# Drop NaN rows
df_btc.dropna(inplace=True)

# Calculate cumulative returns
df_btc['Cumulative_Market'] = (1 + df_btc['Market_Return']).cumprod()
df_btc['Cumulative_Strategy'] = (1 + df_btc['Strategy_Return']).cumprod()

# Sharpe Ratio annualised (365 days for crypto, trades 24/7)
sharpe_btc = (df_btc['Strategy_Return'].mean() / df_btc['Strategy_Return'].std()) * (365 ** 0.5)

# Maximum Drawdown
rolling_max_btc = df_btc['Cumulative_Strategy'].cummax()
drawdown_btc = (df_btc['Cumulative_Strategy'] - rolling_max_btc) / rolling_max_btc
max_drawdown_btc = drawdown_btc.min()

# CAGR
total_days_btc = (df_btc.index[-1] - df_btc.index[0]).days
cagr_btc = (df_btc['Cumulative_Strategy'].iloc[-1] ** (365 / total_days_btc)) - 1

print("=" * 40)
print("BTC STRATEGY PERFORMANCE SUMMARY")
print("=" * 40)
print(f"Sharpe Ratio      : {sharpe_btc:.2f}")
print(f"Max Drawdown      : {max_drawdown_btc:.2%}")
print(f"CAGR              : {cagr_btc:.2%}")
print(f"Final Return      : {(df_btc['Cumulative_Strategy'].iloc[-1] - 1):.2%}")
print(f"Buy & Hold Return : {(df_btc['Cumulative_Market'].iloc[-1] - 1):.2%}")
print("=" * 40)

# Side by side comparison
print("\n")
print("=" * 50)
print("NIFTY vs BTC — STRATEGY COMPARISON")
print("=" * 50)
print(f"{'Metric':<20} {'NIFTY50':>12} {'BTC/USDT':>12}")
print("-" * 50)
print(f"{'Sharpe Ratio':<20} {'1.16':>12} {sharpe_btc:>11.2f}")
print(f"{'Max Drawdown':<20} {'-8.34%':>12} {max_drawdown_btc:>11.2%}")
print(f"{'CAGR':<20} {'12.50%':>12} {cagr_btc:>11.2%}")
print(f"{'Final Return':<20} {'23.61%':>12} {(df_btc['Cumulative_Strategy'].iloc[-1]-1):>11.2%}")
print("=" * 50)