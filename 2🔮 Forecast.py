import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="🔮 Price Forecast", layout="wide")
st.title("🔮 Price Forecast (SMA-based)")

# Select time range and forecast horizon
period = st.selectbox("📆 Historical Data Period", ["1mo", "3mo", "6mo", "1y", "2y"], index=3)
forecast_days = st.slider("🔮 Forecast Horizon (days)", 5, 60, 14)

# Load historical close price
@st.cache_data
def load_data(ticker, period):
    df = yf.Ticker(ticker).history(period=period)
    df.index = df.index.tz_localize(None)
    return df["Close"]

# Simple forecast using last SMA value
def simple_moving_average_forecast(close, forecast_days=14, window=5):
    last_date = close.index[-1]
    sma = close.rolling(window=window).mean().dropna()
    last_sma = sma.iloc[-1]
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=forecast_days)
    forecast = pd.Series(last_sma, index=future_dates)
    return forecast

# Asset selection
if "selected_assets" not in st.session_state or not st.session_state.selected_assets:
    st.warning("⚠ Please select assets from the Dashboard first.")
    st.stop()

ticker = st.selectbox("Select Asset to Forecast", st.session_state.selected_assets)

close = load_data(ticker, period)
if close.empty:
    st.warning(f"No data found for {ticker}")
    st.stop()

# Forecast
forecast = simple_moving_average_forecast(close, forecast_days=forecast_days)

# Plot with Plotly
fig = go.Figure()

# Historical prices
fig.add_trace(go.Scatter(x=close.index, y=close, mode='lines', name='Historical Price'))

# Forecasted prices
fig.add_trace(go.Scatter(x=forecast.index, y=forecast, mode='lines+markers', name='Forecast (SMA)',
                         line=dict(dash='dot', color='orange')))

fig.update_layout(
    title=f"{ticker} Price Forecast ({forecast_days} Days)",
    xaxis_title="Date",
    yaxis_title="Price",
    template="plotly_white",
    legend=dict(x=0, y=1)
)

st.plotly_chart(fig, use_container_width=True)

# Forecast Summary
st.markdown(f"### Forecast Summary for {forecast_days} Days")
st.success(f"📅 Projected Price: **${forecast.iloc[-1]:.2f}** (based on last SMA value)")
