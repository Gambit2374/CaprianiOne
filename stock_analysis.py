import os
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator

WATCHLIST_CSV = "watchlist.csv"

def load_watchlist():
    """Load watchlist from a local CSV if it exists, otherwise return an empty list."""
    if os.path.exists(WATCHLIST_CSV):
        df = pd.read_csv(WATCHLIST_CSV)
        return df.to_dict("records")  # convert DataFrame rows into a list of dicts
    return []

def save_watchlist(watchlist_list):
    """Save watchlist (list of dicts) to a local CSV file."""
    df = pd.DataFrame(watchlist_list)
    df.to_csv(WATCHLIST_CSV, index=False)

###########################################
# Existing indicator + signal code
###########################################
def compute_indicators(df, sma_window=200):
    df[f"SMA{sma_window}"] = SMAIndicator(close=df["Close"], window=sma_window).sma_indicator()
    df["EMA20"] = EMAIndicator(close=df["Close"], window=20).ema_indicator()
    df["RSI14"] = RSIIndicator(close=df["Close"], window=14).rsi()

    macd = MACD(close=df["Close"], window_slow=26, window_fast=12, window_sign=9)
    df["MACD_Line"] = macd.macd()
    df["MACD_Signal"] = macd.macd_signal()

    df["Trend"] = np.where(df["Close"] > df[f"SMA{sma_window}"], "Uptrend", "Downtrend")
    df.dropna(inplace=True)
    return df

def generate_signal(row, sma_window=200):
    close_price = row["Close"]
    ema20 = row["EMA20"]
    rsi = row["RSI14"]
    macd_line = row["MACD_Line"]
    macd_signal = row["MACD_Signal"]
    trend = row["Trend"]

    # -- STRONG BUY --
    if (
        trend == "Uptrend"
        and close_price > ema20
        and (rsi < 30 or rsi > 50)
        and macd_line > macd_signal
    ):
        return "🔥 STRONG BUY"

    # -- BUY --
    if trend == "Uptrend" and (
        close_price > ema20
        or macd_line > macd_signal
        or rsi > 50
    ):
        return "BUY"

    # -- STRONG HOLD --
    if (
        trend == "Uptrend"
        and 50 <= rsi <= 70
        and macd_line > macd_signal
        and close_price > ema20
    ):
        return "STRONG HOLD"

    # -- HOLD --
    if trend == "Uptrend":
        return "HOLD"

    # -- STRONG SELL --
    if (
        trend == "Downtrend"
        and close_price < ema20
        and (rsi > 70 or rsi < 50)
        and macd_line < macd_signal
    ):
        return "🚨 STRONG SELL"

    # -- SELL --
    if trend == "Downtrend" and (
        close_price < ema20
        or macd_line < macd_signal
        or rsi < 50
    ):
        return "SELL"

    return "HOLD"

def get_latest_signal(ticker, sma_window=200):
    df_raw = yf.download(ticker, period="2y", interval="1d", progress=False)
    if df_raw.empty:
        return ("Unknown Company", "NO DATA")

    df_close = df_raw["Close"]
    if isinstance(df_close, pd.DataFrame):
        df_close = df_close.iloc[:, 0]
    df_close = df_close.squeeze()
    df_close.name = "Close"

    df = df_close.to_frame()
    df = compute_indicators(df, sma_window=sma_window)

    if df.empty:
        return ("Unknown Company", "NO SIGNAL")

    last_row = df.iloc[-1]
    sig = generate_signal(last_row, sma_window=sma_window)
    info = yf.Ticker(ticker).info
    company_name = info.get("shortName") or info.get("longName") or ticker

    return (company_name, sig)

def analyze_in_depth(ticker, sma_window=200):
    df_raw = yf.download(ticker, period="2y", interval="1d", progress=False)
    if df_raw.empty:
        return None, None

    df_close = df_raw["Close"]
    if isinstance(df_close, pd.DataFrame):
        df_close = df_close.iloc[:, 0]
    df_close = df_close.squeeze()
    df_close.name = "Close"

    df = df_close.to_frame()
    df = compute_indicators(df, sma_window=sma_window)
    df["Signal"] = df.apply(lambda row: generate_signal(row, sma_window=sma_window), axis=1)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df.index, df["Close"], label="Close", color="blue")

    strong_buy = df[df["Signal"] == "🔥 STRONG BUY"]
    buy = df[df["Signal"] == "BUY"]
    strong_sell = df[df["Signal"] == "🚨 STRONG SELL"]
    sell = df[df["Signal"] == "SELL"]

    ax.scatter(strong_buy.index, strong_buy["Close"], marker="^", color="green", s=100, label="🔥 STRONG BUY")
    ax.scatter(buy.index, buy["Close"], marker="^", color="lime", s=80, label="BUY")
    ax.scatter(strong_sell.index, strong_sell["Close"], marker="v", color="red", s=100, label="🚨 STRONG SELL")
    ax.scatter(sell.index, sell["Close"], marker="v", color="orange", s=80, label="SELL")

    ax.set_title(f"{ticker} - In-Depth Analysis")
    ax.legend()
    ax.set_ylabel("Price")
    return df, fig

############################################
# MAIN "run()" FUNCTION
############################################
def run():
    st.title("📈 Stock Analysis with Watchlist (Persistent)")

    # 1) On first run, load from CSV
    if "watchlist" not in st.session_state:
        st.session_state.watchlist = load_watchlist()

    st.subheader("Manage Your Ticker Watchlist")

    new_ticker = st.text_input("Add a Ticker (e.g. 'AAPL')").upper().strip()
    if st.button("Add Ticker"):
        if new_ticker:
            existing = [item for item in st.session_state.watchlist if item["ticker"] == new_ticker]
            if existing:
                st.warning(f"{new_ticker} is already in the watchlist.")
            else:
                name, sig = get_latest_signal(new_ticker, sma_window=200)
                if sig == "NO DATA":
                    st.error(f"No price data found for {new_ticker}.")
                else:
                    st.session_state.watchlist.append({
                        "ticker": new_ticker,
                        "name": name,
                        "signal": sig
                    })
                    # Save to CSV whenever we update
                    save_watchlist(st.session_state.watchlist)
                    st.success(f"Added {new_ticker} - {name} with signal: {sig}")

    all_tickers = [item["ticker"] for item in st.session_state.watchlist]
    ticker_to_remove = st.selectbox("Remove a Ticker", options=[""] + all_tickers)
    if st.button("Remove Ticker"):
        if ticker_to_remove:
            st.session_state.watchlist = [i for i in st.session_state.watchlist if i["ticker"] != ticker_to_remove]
            save_watchlist(st.session_state.watchlist)
            st.warning(f"Removed {ticker_to_remove} from watchlist.")

    st.write("---")
    st.subheader("Your Current Watchlist")
    if st.session_state.watchlist:
        df_watch = pd.DataFrame(st.session_state.watchlist)

        col_width_css = """
        <style>
        .dataframe td:nth-child(3) {
            min-width: 120px;
        }
        </style>
        """
        st.markdown(col_width_css, unsafe_allow_html=True)
        st.dataframe(df_watch)
    else:
        st.info("No tickers in your watchlist yet.")

    st.write("---")
    st.subheader("In-Depth Analysis")

    if st.session_state.watchlist:
        choice = st.selectbox("Select Ticker for Detailed Analysis", options=[""] + all_tickers)
        if choice:
            df_detail, fig_detail = analyze_in_depth(choice, sma_window=200)
            if df_detail is None:
                st.error("No data returned for that ticker.")
            else:
                st.pyplot(fig_detail)
                st.write("### Last 30 Rows of Data & Signals")
                st.dataframe(df_detail.tail(30))
    else:
        st.write("Add some tickers above to enable in-depth analysis.")






