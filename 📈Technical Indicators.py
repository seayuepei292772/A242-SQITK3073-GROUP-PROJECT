import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="📈 Technical Indicators", layout="wide")
st.title("📈 Technical Indicators")

# Check if assets are selected
# This assumes that the assets are selected on a previous page and stored in session state
if "selected_assets" not in st.session_state or not st.session_state.selected_assets:
    st.warning("⚠️ Please select assets to analyze on the Dashboard page first.")
    st.stop()

# User selects the asset and time period for analysis
ticker = st.selectbox("Select Asset", st.session_state.selected_assets)
period = st.selectbox("Select Period", ['1mo', '3mo', '6mo', '1y', '2y'], index=2)

# Load Data
@st.cache_data
def load_data(ticker, period):
    data = yf.Ticker(ticker).history(period=period)
    data.index = data.index.tz_localize(None)
    return data

# Compute Indicators
def compute_rsi(close, window=14):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def compute_macd(close):
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

def compute_ma(close, short=20, long=50):
    return close.rolling(short).mean(), close.rolling(long).mean()

# Get Data
data = load_data(ticker, period)
if data.empty:
    st.error("❌ Unable to fetch data for the selected asset. Please check the ticker symbol or try a different period.")
    st.stop()

close = data["Close"]
rsi = compute_rsi(close)
macd, signal_line = compute_macd(close)
ma_short, ma_long = compute_ma(close)

# Closing Price
st.subheader("📈 Closing Price")
st.line_chart(close)

# RSI
st.subheader("📊 RSI")
st.line_chart(rsi)

# MACD
st.subheader("📉 MACD")
fig, ax = plt.subplots()
ax.plot(data.index, macd, label='MACD')
ax.plot(data.index, signal_line, label='Signal Line')
ax.legend()
st.pyplot(fig)

# Overall Technical Signal Analysis
st.subheader("📌 Overall Technical Signal Analysis")
try:
    current_rsi = rsi.iloc[-1]
    macd_cross = macd.iloc[-1] > signal_line.iloc[-1]
    ma_cross = ma_short.iloc[-1] > ma_long.iloc[-1]

    if current_rsi < 30 and macd_cross and ma_cross:
        st.success("🟢 Buy Signal")
    elif current_rsi > 70 and not macd_cross and not ma_cross:
        st.error("🔴 Sell Signal")
    else:
        st.info("🟡 No Clear Signal")
except:
    st.warning("⚠️ Insufficient data to determine signal")
