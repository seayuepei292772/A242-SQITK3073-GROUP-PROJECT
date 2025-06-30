import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Multi-Asset Dashboard", layout="wide")
st.title("📈 Multi-Asset Price Tracker")

# Initialize Session State
if "selected_assets" not in st.session_state:
    st.session_state.selected_assets = []

# Available ticker list
tickers = {
    "Bitcoin (BTC-USD)": "BTC-USD",
    "Ethereum (ETH-USD)": "ETH-USD",
    "Ethereum Classic (ETC-USD)": "ETC-USD",
    "Apple (AAPL)": "AAPL",
    "Tesla (TSLA)": "TSLA",
    "Microsoft (MSFT)": "MSFT"
}

# === Select Asset ===
selected_name = st.selectbox("🔍 Select an asset to add", list(tickers.keys()))
selected_ticker = tickers[selected_name]

# Click button to add to selected assets list
if st.button("➕ Add Asset"):
    if selected_ticker not in st.session_state.selected_assets:
        st.session_state.selected_assets.append(selected_ticker)

# Show currently selected assets
st.sidebar.header("🗂️ Selected Assets")
for ticker in st.session_state.selected_assets:
    st.sidebar.write(ticker)

# Function: Get Historical Data
@st.cache_data
def load_data(ticker):
    data = yf.Ticker(ticker)
    hist = data.history(period="5y")
    hist.index = pd.to_datetime(hist.index)
    return hist

# === Display Charts for Selected Assets ===
for ticker in st.session_state.selected_assets:
    hist = load_data(ticker)
    if hist.empty:
        st.error(f"❌ Data not available for {ticker}")
        continue

    # Compute Moving Averages
    ma50 = hist['Close'].rolling(window=50).mean()
    ma200 = hist['Close'].rolling(window=200).mean()

    st.subheader(f"📉 {ticker} Price Chart")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(hist.index, hist['Close'], label='Close Price')
    ax.plot(hist.index, ma50, label='50-Day MA', color='orange')
    ax.plot(hist.index, ma200, label='200-Day MA', color='red')
    ax.set_title(f'{ticker} Price Chart')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.legend()
    ax.grid()
    st.pyplot(fig)

    # Price Summary
    st.markdown(f"**Min:** ${hist['Close'].min():.2f} | **Max:** ${hist['Close'].max():.2f}")
    trend = "Bullish" if ma50.iloc[-1] > ma200.iloc[-1] else "Bearish"
    st.markdown(f"**Trend:** `{trend}`") 