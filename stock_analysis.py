import os
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
import matplotlib.pyplot as plt

SWING_WATCHLIST_CSV = "swing_watchlist.csv"
CURRENCY_MAP = {"USD": "£", "GBP": "£", "GBp": "£", "EUR": "€"}

def load_watchlist():
    if os.path.exists(SWING_WATCHLIST_CSV):
        return pd.read_csv(SWING_WATCHLIST_CSV).to_dict("records")
    return []

def save_watchlist(watchlist_list):
    pd.DataFrame(watchlist_list).to_csv(SWING_WATCHLIST_CSV, index=False)

def flatten_columns(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def compute_indicators(df, sma_window=200):
    df = flatten_columns(df)
    if df.empty or "Close" not in df.columns or "Volume" not in df.columns:
        return None
    close_series = df["Close"].squeeze()
    volume_series = df["Volume"].squeeze()
    try:
        sma_obj = SMAIndicator(close=close_series, window=sma_window)
        ema_obj = EMAIndicator(close=close_series, window=20)
        rsi_obj = RSIIndicator(close=close_series, window=14)
        macd_obj = MACD(close=close_series, window_slow=26, window_fast=12, window_sign=9)
        bb_obj = BollingerBands(close=close_series, window=20, window_dev=2)

        df[f"SMA{sma_window}"] = sma_obj.sma_indicator()
        df["EMA20"] = ema_obj.ema_indicator()
        df["RSI14"] = rsi_obj.rsi()
        df["MACD_Line"] = macd_obj.macd()
        df["MACD_Signal"] = macd_obj.macd_signal()
        df["BB_High"] = bb_obj.bollinger_hband()
        df["BB_Low"] = bb_obj.bollinger_lband()
        df["Volume_SMA"] = SMAIndicator(close=volume_series, window=20).sma_indicator()
        df["Trend"] = np.where(df["Close"] > df[f"SMA{sma_window}"], "Uptrend", "Downtrend")
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

def get_current_price_and_changes(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", progress=False, auto_adjust=True)
        df = flatten_columns(df)
        if not df.empty and "Close" in df.columns:
            current_price = float(df["Close"].iloc[-1])
            one_day_change = current_price - df["Close"].iloc[-2] if len(df) > 1 else 0
            fifty_two_week_low = df["Close"].min()
            fifty_two_week_change = current_price - fifty_two_week_low
            info = yf.Ticker(ticker).info
            code = info.get("currency", "USD")
            return current_price, CURRENCY_MAP.get(code, "£"), one_day_change, fifty_two_week_change
    except Exception:
        return None, "£", 0, 0

def fetch_technical_summary(ticker, sma_window=200):
    df = yf.download(ticker, period="2y", interval="1d", progress=False, auto_adjust=True)
    df = flatten_columns(df)
    if df.empty:
        return None, None
    df = compute_indicators(df, sma_window)
    if df is None:
        return None, None
    last_row = df.iloc[-1]
    signal, strength = generate_signal_and_strength(last_row)
    return signal, df

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

def fetch_watchlist_data(ticker, sma_window=200):
    tkr = yf.Ticker(ticker)
    info = tkr.info
    company = info.get("shortName", info.get("longName", ticker))
    price, sym, one_day_change, fifty_two_week_change = get_current_price_and_changes(ticker)
    price_str = f"{sym}{price:.2f}" if price else "N/A"
    signal, df = fetch_technical_summary(ticker, sma_window)
    conclusion = generate_swing_trading_conclusion(signal, df)
    if signal:
        return {
            "Ticker": ticker,
            "Company": company,
            "Current Price": price_str,
            "1-Day Change": f"{sym}{one_day_change:.2f}",
            "52-Week Change": f"{sym}{fifty_two_week_change:.2f}",
            "RSI14": f"{df['RSI14'].iloc[-1]:.1f}" if df is not None and not df.empty else "N/A",
            "MACD_Line": f"{df['MACD_Line'].iloc[-1]:.2f}" if df is not None and not df.empty else "N/A",
            "MACD_Signal": f"{df['MACD_Signal'].iloc[-1]:.2f}" if df is not None and not df.empty else "N/A",
            "EMA20": f"{df['EMA20'].iloc[-1]:.2f}" if df is not None and not df.empty else "N/A",
            "Signal": signal
        }
    return {k: "N/A" for k in ["Ticker", "Company", "Current Price", "1-Day Change", "52-Week Change", "RSI14", "MACD_Line", "MACD_Signal", "EMA20", "Signal"]}

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
    st.title("📈 Stock Analysis for Swing Trading")
    st.write("""
    Analyse stocks for swing trading opportunities with technical indicators, signals, and conclusions.
    Add tickers to your swing trading watchlist to track and visualise price movements, RSI, volume, MACD, and more.
    **Guidance:** Swing trading targets short-term price swings (days to weeks). Look for:
    - **Strong Buy/Sell Signals**: High potential for quick moves with volume confirmation.
    - **Bollinger Bands**: Price near bands indicates volatility for entries/exits.
    - **RSI**: Overbought (>70) or oversold (<30) suggests reversals.
    - **MACD**: Crossovers (MACD Line > Signal Line) indicate momentum shifts.
    - **Volume Spikes**: Confirm trends or breakouts.
    - **Tip:** Use signals and conclusions to identify the best entry/exit points for quick profits.
    """)

    if "swing_watchlist" not in st.session_state:
        st.session_state.swing_watchlist = load_watchlist()

    st.subheader("Manage Your Swing Trading Watchlist")
    new_ticker = st.text_input("Add a Ticker (e.g., 'AAPL')", help="Enter a stock symbol like 'AAPL' for Apple.").upper().strip()
    if st.button("Add Ticker") and new_ticker:
        if any(item["ticker"] == new_ticker for item in st.session_state.swing_watchlist):
            st.warning(f"{new_ticker} is already in your swing trading watchlist.")
        else:
            st.session_state.swing_watchlist.append({"ticker": new_ticker})
            save_watchlist(st.session_state.swing_watchlist)
            st.success(f"Added {new_ticker} to your swing trading watchlist.")

    all_tickers = [item["ticker"] for item in st.session_state.swing_watchlist]
    remove_ticker = st.selectbox("Remove a Ticker", options=[""] + all_tickers, help="Select a ticker to remove from your watchlist.")
    if st.button("Remove Ticker") and remove_ticker:
        st.session_state.swing_watchlist = [i for i in st.session_state.swing_watchlist if i["ticker"] != remove_ticker]
        save_watchlist(st.session_state.swing_watchlist)
        st.warning(f"Removed {remove_ticker} from your swing trading watchlist.")

    st.subheader("Swing Trading Watchlist Table")
    if st.session_state.swing_watchlist:
        watchlist_data = [fetch_watchlist_data(ticker) for ticker in all_tickers]
        df = pd.DataFrame(watchlist_data)
        st.dataframe(df, use_container_width=True, height=400)

        st.subheader("Swing Trading Analysis")
        st.write("""
        Select a ticker for detailed swing trading analysis, including charts, signals, and conclusions.
        **Tips for Swing Trading:**
        - Use signals to identify entry/exit points (Strong Buy/Sell for high potential, Hold for neutral).
        - Combine signals with Bollinger Bands, RSI, MACD, and volume for confirmation.
        - Check the conclusion for the best decision based on current analysis.
        """)
        selected_ticker = st.selectbox("Select Ticker for Analysis", options=[""] + all_tickers, help="Choose a ticker to see in-depth swing trading analysis.")
        if selected_ticker:
            data = next(item for item in watchlist_data if item["Ticker"] == selected_ticker)
            st.write(f"**Ticker:** {data['Ticker']}")
            st.write(f"**Company:** {data['Company']}")
            st.write(f"**Price:** {data['Current Price']}")
            st.write(f"**1-Day Change:** {data['1-Day Change']}")
            st.write(f"**52-Week Change:** {data['52-Week Change']}")
            st.write(f"**RSI14:** {data['RSI14']}")
            st.write(f"**MACD Line:** {data['MACD_Line']}")
            st.write(f"**MACD Signal:** {data['MACD_Signal']}")
            st.write(f"**EMA20:** {data['EMA20']}")
            st.write(f"**Signal:** {data['Signal']}")
            conclusion = generate_swing_trading_conclusion(data['Signal'], yf.download(selected_ticker, period="2y", interval="1d", progress=False, auto_adjust=True).pipe(compute_indicators))
            st.write(f"**Conclusion:** {conclusion}")
            st.write("""
            **Guidance:** Use this signal and conclusion to make informed swing trading decisions. Prioritise Strong Buy/Sell for high-potential trades, but confirm with volume and volatility.
            """)

            # Full Analysis and Graphs
            df_full = yf.download(selected_ticker, period="2y", interval="1d", progress=False, auto_adjust=True)
            df_full = compute_indicators(df_full)
            plot_full_analysis(selected_ticker, df_full)