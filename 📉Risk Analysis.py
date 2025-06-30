import streamlit as st
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt

# --- Initialize session_state for selected_assets to prevent KeyError ---
if "selected_assets" not in st.session_state:
    st.session_state.selected_assets = []

st.title("📉 Risk Analysis")

if not st.session_state.selected_assets:
    st.warning("⚠️ Please go to the Dashboard and select one or more assets first.")
    st.stop()

@st.cache_data
def load_data(ticker):
    data = yf.Ticker(ticker).history(period="2y")
    data.index = data.index.tz_localize(None)
    return data['Close']

def calculate_volatility(price_series):
    returns = price_series.pct_change().dropna()
    return returns.std() * np.sqrt(252)

def calculate_max_drawdown(price_series):
    cumulative = (1 + price_series.pct_change()).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    return drawdown.min()

for ticker in st.session_state.selected_assets:
    st.subheader(f"Risk Metrics for {ticker}")

    try:
        close_prices = load_data(ticker)
        vol = calculate_volatility(close_prices)
        mdd = calculate_max_drawdown(close_prices)
    except Exception as e:
        st.error(f"Error loading data for {ticker}: {e}")
        continue

    st.write(f"📈 Annualized Volatility: `{vol:.2%}`")
    st.write(f"📉 Max Drawdown: `{mdd:.2%}`")

    # Plotting
    fig, ax = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    ax[0].plot(close_prices.index, close_prices, label='Close Price')
    ax[0].set_title(f"{ticker} Close Price")
    ax[0].grid(True)
    ax[0].legend()

    cumulative = (1 + close_prices.pct_change().fillna(0)).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    ax[1].plot(drawdown.index, drawdown, color='red', label='Drawdown')
    ax[1].set_title(f"{ticker} Drawdown")
    ax[1].grid(True)
    ax[1].legend()

    st.pyplot(fig)
