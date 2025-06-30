import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.stats import norm

st.set_page_config(page_title="📊 Potential Price Range", layout="wide")
st.title("📊 Potential Price Range Estimator")

# User input
period = st.selectbox("📆 Historical Data Period", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)
days_forward = st.slider("🔮 Forecast Horizon (days)", 5, 90, 30)
confidence = st.slider("📊 Confidence Level", 0.80, 0.99, 0.95, step=0.01)

# Load close price data
@st.cache_data
def load_data(ticker, period):
    data = yf.Ticker(ticker).history(period=period)
    data.index = data.index.tz_localize(None)
    return data['Close']

# Calculate future price range using log returns
def get_potential_range(price_series, days_forward, confidence):
    last_price = price_series.dropna().iloc[-1]
    log_returns = np.log(price_series / price_series.shift(1)).dropna()
    vol = log_returns.std() * np.sqrt(days_forward)
    z = norm.ppf(1 - (1 - confidence) / 2)
    lower = last_price * np.exp(-z * vol)
    upper = last_price * np.exp(z * vol)
    return lower, upper, vol

# Ensure assets selected
if "selected_assets" not in st.session_state or not st.session_state.selected_assets:
    st.warning("⚠️ Please go to the Dashboard to select assets.")
else:
    for ticker in st.session_state.selected_assets:
        st.subheader(f"📌 {ticker} — {days_forward}-Day Projection ({int(confidence * 100)}% CI)")

        close = load_data(ticker, period)
        if close.empty:
            st.warning(f"⚠ No data for {ticker}")
            continue

        lower, upper, vol = get_potential_range(close, days_forward, confidence)

        # Plot with Plotly
        fig = go.Figure()

        # Historical price
        fig.add_trace(go.Scatter(
            x=close.index, y=close, name="Historical Price", mode='lines'
        ))

        # Projected interval band
        projection_date = pd.date_range(close.index[-1] + pd.Timedelta(days=1), periods=1)
        fig.add_trace(go.Scatter(
            x=[projection_date[0], projection_date[0]],
            y=[lower, upper],
            name=f"{int(confidence * 100)}% Confidence Interval",
            mode='lines',
            line=dict(width=0),
            showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=[projection_date[0], projection_date[0]],
            y=[lower, upper],
            fill='tonexty',
            fillcolor='rgba(0,100,200,0.2)',
            mode='none',
            name='Projected Range'
        ))

        fig.update_layout(
            title=f"{ticker} Potential Price Range",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_white",
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)

        # Metrics summary
        col1, col2, col3 = st.columns(3)
        col1.metric("📉 Lower Bound", f"${lower:.2f}")
        col2.metric("📈 Upper Bound", f"${upper:.2f}")
        col3.metric("📊 Volatility (σ)", f"{vol*100:.2f}%")

        with st.expander("ℹ️ Range Calculation Formula"):
            st.markdown(f"""
                - Last Price = **${close.iloc[-1]:.2f}**
                - Confidence Level = **{confidence:.2f}**
                - Forecast Days = **{days_forward}**
                - Using: `Log-Normal Model`
                - Range = `price × exp(±z × σ × √days)`
            """)
