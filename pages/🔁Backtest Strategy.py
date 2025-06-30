import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="🔁 Backtest: MA Crossover", layout="wide")
st.title("🔁 Backtest: MA Crossover Strategy")

# Backtesting logic
def backtest_ma_strategy(data, short_window, long_window):
    data = data.copy()
    data['Short_MA'] = data['Close'].rolling(window=short_window).mean()
    data['Long_MA'] = data['Close'].rolling(window=long_window).mean()
    data['Signal'] = 0
    data.loc[data['Short_MA'] > data['Long_MA'], 'Signal'] = 1
    data['Position'] = data['Signal'].diff()
    data['Strategy_Returns'] = data['Close'].pct_change() * data['Signal'].shift(1)
    data['Strategy'] = (1 + data['Strategy_Returns']).cumprod()
    data['BuyHold'] = (1 + data['Close'].pct_change()).cumprod()

    buy_signals = data[data['Position'] == 1]
    sell_signals = data[data['Position'] == -1]
    return data, buy_signals, sell_signals

# Check if assets are selected
if "selected_assets" not in st.session_state or not st.session_state.selected_assets:
    st.warning("⚠️ Please select assets from the Dashboard first.")
    st.stop()

# User selection
ticker = st.selectbox("Select Asset for Backtest", st.session_state.selected_assets)
period = st.selectbox("Select Time Period", ['6mo', '1y', '2y'], index=2)
short_ma = st.slider("Short MA Window", 5, 50, 20)
long_ma = st.slider("Long MA Window", 30, 200, 100)

# Load data
data = yf.Ticker(ticker).history(period=period)
if data.empty:
    st.error("❌ No data available for this asset.")
    st.stop()

# Run backtest
result, buys, sells = backtest_ma_strategy(data, short_ma, long_ma)

# Plotting with Plotly
fig = go.Figure()

fig.add_trace(go.Scatter(x=result.index, y=result["Strategy"], mode='lines', name='MA Strategy'))
fig.add_trace(go.Scatter(x=result.index, y=result["BuyHold"], mode='lines', name='Buy & Hold', line=dict(dash='dot')))

# Buy signals
fig.add_trace(go.Scatter(
    x=buys.index,
    y=result.loc[buys.index, "Strategy"],
    mode='markers',
    marker=dict(color='green', size=10, symbol='triangle-up'),
    name='Buy Signal'
))

# Sell signals
fig.add_trace(go.Scatter(
    x=sells.index,
    y=result.loc[sells.index, "Strategy"],
    mode='markers',
    marker=dict(color='red', size=10, symbol='triangle-down'),
    name='Sell Signal'
))

fig.update_layout(
    title=f"{ticker} Strategy Backtest ({period})",
    xaxis_title="Date",
    yaxis_title="Cumulative Return",
    template="plotly_white",
    legend=dict(x=0, y=1)
)

st.plotly_chart(fig, use_container_width=True)

# Explanation
st.markdown("🟢 **Green markers** indicate Buy signals. 🔴 **Red markers** indicate Sell signals.")
