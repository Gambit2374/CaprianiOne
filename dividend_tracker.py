import os
import streamlit as st
import pandas as pd
import yfinance as yf

DIVIDEND_CSV = "dividend_watchlist.csv"

def load_dividend_watchlist():
    """Load dividend watchlist from a local CSV if it exists, otherwise return an empty list."""
    if os.path.exists(DIVIDEND_CSV):
        df = pd.read_csv(DIVIDEND_CSV)
        return df.to_dict("records")
    return []

def save_dividend_watchlist(watchlist_list):
    """Save watchlist (list of dicts) to a local CSV file."""
    df = pd.DataFrame(watchlist_list)
    df.to_csv(DIVIDEND_CSV, index=False)

def fetch_dividend_info(ticker):
    """
    Tries to fetch upcoming ex-dividend date and pay date from yfinance info.
    The data is often missing or partial in yfinance.

    Returns (company_name, ex_div_date, pay_date)
    If not available, returns placeholders.
    """
    ticker_obj = yf.Ticker(ticker)
    info = ticker_obj.info

    # Attempt to get the short/long name
    company_name = info.get("shortName") or info.get("longName") or ticker

    # yfinance might store these as timestamps or None
    ex_div_ts = info.get("exDividendDate")
    pay_div_ts = info.get("dividendDate")

    # Convert them to strings or placeholders
    ex_div_date = str(ex_div_ts) if ex_div_ts else "No upcoming ex-date"
    pay_date = str(pay_div_ts) if pay_div_ts else "No upcoming pay date"

    return (company_name, ex_div_date, pay_date)

def run():
    st.title("💵 Dividend Tracker (Upcoming Ex-Dates & Pay Dates)")

    # 1) On first run, load from CSV
    if "dividend_watchlist" not in st.session_state:
        st.session_state.dividend_watchlist = load_dividend_watchlist()

    st.subheader("Manage Your Dividend Watchlist")
    # Add Ticker
    new_ticker = st.text_input("Add a Ticker (e.g. 'AAPL')").upper().strip()
    if st.button("Add Ticker"):
        if new_ticker:
            existing = [item for item in st.session_state.dividend_watchlist if item["ticker"] == new_ticker]
            if existing:
                st.warning(f"{new_ticker} is already in the watchlist.")
            else:
                # Attempt to fetch future dividend info
                name, ex_div, pay_div = fetch_dividend_info(new_ticker)
                st.session_state.dividend_watchlist.append({
                    "ticker": new_ticker,
                    "company": name,
                    "ex_div_date": ex_div,
                    "pay_date": pay_div
                })
                save_dividend_watchlist(st.session_state.dividend_watchlist)
                st.success(f"Added {new_ticker} - {name}")

    # Remove Ticker
    all_div_tickers = [item["ticker"] for item in st.session_state.dividend_watchlist]
    ticker_to_remove = st.selectbox("Remove a Ticker", options=[""] + all_div_tickers)
    if st.button("Remove Ticker"):
        if ticker_to_remove:
            st.session_state.dividend_watchlist = [
                x for x in st.session_state.dividend_watchlist if x["ticker"] != ticker_to_remove
            ]
            save_dividend_watchlist(st.session_state.dividend_watchlist)
            st.warning(f"Removed {ticker_to_remove} from watchlist.")

    st.write("---")
    st.subheader("Upcoming Dividend Dates Overview")
    if not st.session_state.dividend_watchlist:
        st.info("No tickers in your dividend watchlist yet.")
        return

    # Possibly refresh ex-date & pay-date info for each ticker
    # (Warning: This can slow down if you have many tickers.)
    # We'll do it once each time the user loads the page.

    updated_data = []
    for item in st.session_state.dividend_watchlist:
        ticker = item["ticker"]
        # Re-fetch to see if there's new info
        name, ex_div, pay_div = fetch_dividend_info(ticker)
        updated_data.append({
            "ticker": ticker,
            "company": name,
            "ex_div_date": ex_div,
            "pay_date": pay_div
        })

    # Save the updated info
    st.session_state.dividend_watchlist = updated_data
    save_dividend_watchlist(updated_data)

    # Display the watchlist table
    df_div = pd.DataFrame(updated_data)
    st.dataframe(df_div)

    st.write("""
    **Note**: Yahoo Finance often does not provide upcoming ex or pay dates 
    for many tickers. This data can be incomplete or missing.
    """)
