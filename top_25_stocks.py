import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
import matplotlib.pyplot as plt
from datetime import datetime

def fetch_top_25_stocks():
    s_and_p_500 = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "JPM", "WMT", "PG",
        "BRK-B", "V", "UNH", "MA", "HD", "DIS", "PYPL", "BAC", "CMCSA", "XOM",
        "NFLX", "KO", "PEP", "CSCO", "INTC"
    ]
    top_25 = []
    for ticker in s_and_p_500:
        try:
            df = yf.download(ticker, period="1mo", interval="1d", progress=False, auto_adjust=True)
            if not df.empty:
                volume_avg = df["Volume"].mean()
                bb = BollingerBands(close=df["Close"], window=20, window_dev=2)
                df["ATR"] = bb.bollinger_wband() * df["Close"].std()
                if volume_avg > 1e6 and df["ATR"].mean() > df["Close"].std():
                    top_25.append(ticker)
                if len(top_25) == 25:
                    break
        except Exception:
            continue
    return top_25 if len(top_25) == 25 else s_and_p_500[:25]

def flatten_columns(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def compute_indicators(df):
    df = flatten_columns(df)
    if df.empty or "Close" not in df.columns or "Volume" not in df.columns:
        return None
    close_series = df["Close"].squeeze()
    volume_series = df["Volume"].squeeze()
    try:
        sma_obj = SMAIndicator(close=close_series, window=200)
        ema_obj = EMAIndicator(close=close_series, window=20)
        rsi_obj = RSIIndicator(close=close_series, window=14)
        macd_obj = MACD(close=close_series, window_slow=26, window_fast=12, window_sign=9)
        bb_obj = BollingerBands(close=close_series, window=20, window_dev=2)

        df["SMA200"] = sma_obj.sma_indicator()
        df["EMA20"] = ema_obj.ema_indicator()
        df["RSI14"] = rsi_obj.rsi()
        df["MACD_Line"] = macd_obj.macd()
        df["MACD_Signal"] = macd_obj.macd_signal()
        df["BB_High"] = bb_obj.bollinger_hband()
        df["BB_Low"] = bb_obj.bollinger_lband()
        df["Volume_SMA"] = SMAIndicator(close=volume_series, window=20).sma_indicator()
        df["Trend"] = np.where(df["Close"] > df["SMA200"], "Uptrend", "Downtrend")
        df.dropna(inplace=True)
        return df if not df.empty else None
    except Exception:
        return None

def generate_signal_and_strength(row):
    close = row["Close"]
    ema20 = row["EMA20"]
    rsi = row["RSI14"]
    macd_line = row["MACD_Line"]
    macd_signal = row["MACD_Signal"]
    trend = row["Trend"]
    volume = row["Volume"]
    volume_sma = row["Volume_SMA"]
    bb_high = row["BB_High"]
    bb_low = row["BB_Low"]

    if any(pd.isna(x) for x in [close, ema20, rsi, macd_line, macd_signal, volume, volume_sma]):
        return "N/A", 0

    volume_confirm = volume > volume_sma
    rsi_overbought = 70 if close > bb_high else 65
    rsi_oversold = 30 if close < bb_low else 35

    signal, strength = "⚖️ HOLD", 0
    if trend == "Uptrend" and close > ema20 and macd_line > macd_signal:
        if rsi < rsi_oversold and volume_confirm:
            signal, strength = "🔥 STRONG BUY", 90 if rsi < 25 else 75
        elif rsi < 50 and volume_confirm:
            signal, strength = "💡 BUY", 60 if rsi < 40 else 50
        elif rsi > rsi_overbought:
            signal, strength = "📈 STRONG HOLD", 25
    elif trend == "Downtrend" and close < ema20 and macd_line < macd_signal:
        if rsi > rsi_overbought and volume_confirm:
            signal, strength = "🔴 STRONG SELL", -90 if rsi > 75 else -75
        elif rsi > 50 and volume_confirm:
            signal, strength = "🚫 SELL", -60 if rsi > 60 else -50
    return signal, strength

def fetch_stock_data(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", progress=False, auto_adjust=True)
        df = flatten_columns(df)
        if not df.empty and "Close" in df.columns:
            current_price = float(df["Close"].iloc[-1])
            one_day_change = current_price - df["Close"].iloc[-2] if len(df) > 1 else 0
            fifty_two_week_low = df["Close"].min()
            fifty_two_week_change = current_price - fifty_two_week_low
            info = yf.Ticker(ticker).info
            company = info.get("shortName", ticker)
            currency = info.get("currency", "USD")
            sym = {"USD": "£", "GBP": "£", "EUR": "€"}.get(currency, "£")
            df_full = yf.download(ticker, period="2y", interval="1d", progress=False, auto_adjust=True)
            df_full = compute_indicators(df_full)
            if df_full is not None:
                last_row = df_full.iloc[-1]
                signal, strength = generate_signal_and_strength(last_row)
                return {
                    "Ticker": ticker,
                    "Company": company,
                    "Price": f"{sym}{current_price:.2f}",
                    "1-Day Change": f"{sym}{one_day_change:.2f}",
                    "52-Week Change": f"{sym}{fifty_two_week_change:.2f}",
                    "Signal": signal,
                    "RSI14": last_row["RSI14"],
                    "MACD_Line": last_row["MACD_Line"],
                    "MACD_Signal": last_row["MACD_Signal"],
                    "EMA20": last_row["EMA20"]
                }
    except Exception:
        pass
    return None

def generate_swing_trading_conclusion(signal, df):
    if signal == "N/A" or df is None or df.empty:
        return "Data unavailable for analysis. Unable to provide a trading recommendation."
    
    close = df["Close"].iloc[-1]
    rsi = df["RSI14"].iloc[-1]
    volume = df["Volume"].iloc[-1]
    volume_sma = df["Volume_SMA"].iloc[-1]
    bb_high = df["BB_High"].iloc[-1]
    bb_low = df["BB_Low"].iloc[-1]

    volume_confirm = volume > volume_sma
    rsi_overbought = 70 if close > bb_high else 65
    rsi_oversold = 30 if close < bb_low else 35

    if signal == "🔥 STRONG BUY":
        return "This stock is a strong candidate for swing trading with a bullish trend, low RSI indicating oversold conditions, and high volume confirming momentum. The best decision is to enter a long position for potential upward movement, targeting quick profits within days to weeks."
    elif signal == "💡 BUY":
        return "This stock shows a bullish trend with moderate RSI and high volume, making it a good swing trading opportunity for a potential upward move. The best decision is to consider entering a long position, but monitor for additional confirmation before acting."
    elif signal == "⚖️ HOLD":
        return "This stock is currently neutral for swing trading, showing no strong short-term momentum or trend. The best decision is to hold off on trading until a clearer bullish or bearish signal emerges, or monitor for volatility breakouts using Bollinger Bands."
    elif signal == "📈 STRONG HOLD":
        return "This stock is in an uptrend but overbought (high RSI), suggesting caution for swing trading. The best decision is to hold or wait for a pullback or volume confirmation before entering a position, as it may be nearing a resistance level."
    elif signal == "🚫 SELL":
        return "This stock shows a bearish trend with moderate RSI and high volume, making it a good swing trading opportunity for a potential downward move. The best decision is to consider entering a short position, but monitor for additional confirmation before acting."
    elif signal == "🔴 STRONG SELL":
        return "This stock is a strong candidate for swing trading with a bearish trend, high RSI indicating overbought conditions, and high volume confirming momentum. The best decision is to enter a short position for potential downward movement, targeting quick profits within days to weeks."
    return "Unexpected signal encountered. Please review the data for accuracy."

def plot_full_analysis(ticker, df_full):
    if df_full is None or df_full.empty:
        st.warning("No data available for analysis.")
        return
    
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(12, 16), sharex=True)
    
    # Price Chart with Indicators
    ax1.plot(df_full.index, df_full["Close"], label="Close", color="blue")
    ax1.plot(df_full.index, df_full["EMA20"], label="EMA20", color="#ff8c00")  # Orange
    ax1.plot(df_full.index, df_full["SMA200"], label="SMA200", color="#008000")  # Green
    ax1.fill_between(df_full.index, df_full["BB_Low"], df_full["BB_High"], color="gray", alpha=0.2, label="Bollinger Bands")
    ax1.set_title(f"{ticker} - Price & Indicators (2 Years)")
    ax1.set_ylabel("Price")
    ax1.legend()
    ax1.grid(True, linestyle="--", alpha=0.7)

    # RSI
    ax2.plot(df_full.index, df_full["RSI14"], label="RSI14", color="#800080")  # Purple
    ax2.axhline(70, color="red", linestyle="--", label="Overbought")
    ax2.axhline(30, color="green", linestyle="--", label="Oversold")
    ax2.set_title("Relative Strength Index (RSI)")
    ax2.set_ylabel("RSI")
    ax2.legend()
    ax2.grid(True, linestyle="--", alpha=0.7)

    # MACD
    ax3.plot(df_full.index, df_full["MACD_Line"], label="MACD Line", color="blue")
    ax3.plot(df_full.index, df_full["MACD_Signal"], label="MACD Signal", color="red")
    ax3.set_title("Moving Average Convergence Divergence (MACD)")
    ax3.set_ylabel("MACD")
    ax3.legend()
    ax3.grid(True, linestyle="--", alpha=0.7)

    # Volume
    ax4.bar(df_full.index, df_full["Volume"], color="blue", alpha=0.5, label="Volume")
    ax4.plot(df_full.index, df_full["Volume_SMA"], color="red", label="Volume SMA (20)")
    ax4.set_title("Trading Volume")
    ax4.set_ylabel("Volume")
    ax4.legend()
    ax4.grid(True, linestyle="--", alpha=0.7)

    plt.xlabel("Date")
    st.pyplot(fig)

def run():
    st.title("🏆 Top 25 Stocks for Swing Trading")
    st.write("""
    Discover the top 25 stocks ideal for swing trading, updated daily based on high volume and volatility.
    View buy/sell/hold signals, price changes, and dive into detailed analysis with charts for swing trading opportunities.
    **Guidance:** Swing trading focuses on short-term price movements (days to weeks). Look for:
    - **Strong Buy/Sell Signals**: High potential for quick moves with volume confirmation.
    - **Bollinger Bands**: Price near bands signals volatility for entries/exits.
    - **RSI**: Above 70 (overbought), below 30 (oversold) indicates possible reversals.
    - **MACD**: Crossovers (MACD Line > Signal Line) suggest momentum shifts.
    - **Volume Spikes**: Confirm trends or breakouts.
    - **Tip:** Use signals and conclusions to identify the best entry/exit points for quick profits.
    """)

    top_25 = fetch_top_25_stocks()
    stock_data = [fetch_stock_data(ticker) for ticker in top_25]
    stock_data = [d for d in stock_data if d is not None]
    df = pd.DataFrame(stock_data)
    if not df.empty:
        st.dataframe(df, use_container_width=True, height=400)

        st.subheader("Deep Swing Trading Analysis")
        st.write("""
        Select a ticker to see detailed analysis, including price, RSI, MACD, volume, signals, and a conclusion for swing trading.
        **Tips for Swing Trading:**
        - Use signals to identify entry/exit points (Strong Buy/Sell for high potential, Hold for neutral).
        - Combine signals with Bollinger Bands, RSI, MACD, and volume for confirmation.
        - Check the conclusion for the best decision based on current analysis.
        """)
        selected_ticker = st.selectbox("Select a Ticker for Deep Analysis", options=[""] + df["Ticker"].tolist(), help="Choose a ticker to see in-depth swing trading analysis.")
        if selected_ticker:
            stock = df[df["Ticker"] == selected_ticker].iloc[0]
            st.write(f"**Ticker:** {stock['Ticker']}")
            st.write(f"**Company:** {stock['Company']}")
            st.write(f"**Price:** {stock['Price']}")
            st.write(f"**1-Day Change:** {stock['1-Day Change']}")
            st.write(f"**52-Week Change:** {stock['52-Week Change']}")
            st.write(f"**Signal:** {stock['Signal']}")
            st.write(f"**RSI14:** {stock['RSI14']:.1f}")
            st.write(f"**MACD Line:** {stock['MACD_Line']:.2f}")
            st.write(f"**MACD Signal:** {stock['MACD_Signal']:.2f}")
            st.write(f"**EMA20:** {stock['EMA20']:.2f}")
            conclusion = generate_swing_trading_conclusion(stock['Signal'], yf.download(selected_ticker, period="2y", interval="1d", progress=False, auto_adjust=True).pipe(compute_indicators))
            st.write(f"**Conclusion:** {conclusion}")
            st.write("""
            **Guidance:** Use this signal and conclusion to make informed swing trading decisions. Prioritise Strong Buy/Sell for high-potential trades, but confirm with volume and volatility.
            """)

            # Full Analysis and Graphs
            df_full = yf.download(selected_ticker, period="2y", interval="1d", progress=False, auto_adjust=True)
            df_full = compute_indicators(df_full)
            plot_full_analysis(selected_ticker, df_full)