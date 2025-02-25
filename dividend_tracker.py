import streamlit as st
import yfinance as yf
import pandas as pd

def run():
    st.title("💵 Dividend Tracker")
    st.write("Track dividends for your selected stocks. (Data from Yahoo Finance)")

    # Tickers Input
    tickers_input = st.sidebar.text_input("Enter Ticker(s), comma-separated", "AAPL, O, T").upper()
    tickers = [t.strip() for t in tickers_input.split(",") if t.strip()]

    if not tickers:
        st.warning("No tickers entered.")
        return

    all_divs = pd.DataFrame()
    for ticker in tickers:
        df = yf.download(ticker, period="2y", interval="1d", actions=True, progress=False)
        if df.empty:
            st.warning(f"No data found for {ticker}.")
            continue

        # Filter rows where 'Dividends' > 0
        df_div = df[df["Dividends"] > 0].copy()
        df_div["Ticker"] = ticker
        all_divs = pd.concat([all_divs, df_div])

    if all_divs.empty:
        st.warning("No dividends found for the given tickers.")
        return

    st.write("### Dividend History (Last 2 Years)")
    st.dataframe(all_divs[["Ticker", "Dividends"]].sort_index(ascending=False))

    # Placeholder for ex-date calendar approach
    st.write("### Upcoming Dividend Calendar")
    st.write("Note: Yahoo doesn't always provide ex-dates. For full ex-date data, a specialized API may be needed.")
