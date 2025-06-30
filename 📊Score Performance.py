import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# -- Technical Indicator Functions --
def compute_rsi(series, window=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def compute_macd(series, fast=12, slow=26, signal=9):
    exp1 = series.ewm(span=fast, adjust=False).mean()
    exp2 = series.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line

def compute_ma(series, short_window=20, long_window=100):
    ma_short = series.rolling(window=short_window).mean()
    ma_long = series.rolling(window=long_window).mean()
    return ma_short, ma_long

# -- Simulated Forecast Logic (You can connect your model here) --
def get_forecast(ticker):
    import random
    return random.choice(['up', 'down', 'neutral'])

# -- Total Score --
def score_asset(data, ticker):
    close = data['Close']
    rsi = compute_rsi(close).iloc[-1]
    macd, signal_line = compute_macd(close)
    macd_val, signal_val = macd.iloc[-1], signal_line.iloc[-1]
    ma_short, ma_long = compute_ma(close)
    ma_s, ma_l = ma_short.iloc[-1], ma_long.iloc[-1]

    forecast = get_forecast(ticker)

    score = 0
    if rsi < 30: score += 1
    elif rsi > 70: score -= 1
    if macd_val > signal_val: score += 1
    else: score -= 1
    if ma_s > ma_l: score += 1
    else: score -= 1
    if forecast == 'up': score += 1
    elif forecast == 'down': score -= 1

    if score >= 3:
        recommendation = "🟢 Strong Buy"
    elif score <= -3:
        recommendation = "🔴 Strong Sell"
    else:
        recommendation = "🟡 Hold/Wait"

    return score, rsi, macd_val - signal_val, ma_s - ma_l, forecast, recommendation

# -- Main Process --
def main():
    st.title("📊 Overall Scoring + Price Forecast Analysis")

    # Check if assets are selected
    if "selected_assets" not in st.session_state or not st.session_state.selected_assets:
        st.warning("⚠️ Please go to the Dashboard to select assets.")
        st.stop()

    assets_to_score = st.session_state.selected_assets
    period = st.selectbox("Select Analysis Period", ['1mo', '3mo', '6mo', '1y', '2y'], index=2)
    days_forward = st.slider("Forecast Days Ahead", 1, 30, 7)
    confidence = st.slider("Forecast Confidence Interval", 0.5, 0.99, 0.95)

    rows = []

    for ticker in assets_to_score:
        st.subheader(f"📌 {ticker} - {days_forward} Days Forecast (Confidence Interval: {int(confidence*100)}%)")

        data = yf.Ticker(ticker).history(period=period)
        if data.empty:
            st.warning(f"⚠ No data for {ticker}")
            continue

        score, rsi, macd_diff, ma_diff, forecast, recommendation = score_asset(data, ticker)
        rows.append({
            "Ticker": ticker,
            "Score": score,
            "RSI": round(rsi, 2),
            "MACD Signal": round(macd_diff, 4),
            "MA Diff": round(ma_diff, 4),
            "Forecast": forecast,
            "Recommendation": recommendation
        })

        # 📌 TODO: you can connect your forecasting model here
        st.info(f"Forecast Trend: **{forecast}** — (You can implement your own forecasting model here)")

    df = pd.DataFrame(rows)

    def color_recommendation(val):
        if "Buy" in val:
            return 'background-color: #b6fcb6'
        elif "Sell" in val:
            return 'background-color: #fcb6b6'
        else:
            return 'background-color: #fcfcb6'

    if not df.empty:
        st.markdown("### 📋 Overall Scoring Summary")
        st.dataframe(df.style.applymap(color_recommendation, subset=['Recommendation']))

        selected = st.selectbox("Select Asset for Detailed Signals", df['Ticker'])
        detail = df[df['Ticker'] == selected].iloc[0]

        st.markdown(f"### {selected} Technical Signal Analysis")
        st.write(f"- RSI: {detail['RSI']} (below 30 = Buy, above 70 = Sell)")
        st.write(f"- MACD Diff: {detail['MACD Signal']} (Positive = Buy)")
        st.write(f"- MA Diff: {detail['MA Diff']} (Positive = Short-term > Long-term = Bullish)")
        st.write(f"- Simulated Forecast: {detail['Forecast']}")
        st.markdown(f"## Recommended Action: {detail['Recommendation']}")

if __name__ == "__main__":
    main()
