import os
import datetime
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

def convert_timestamp_to_date(ts_value):
    """
    If ts_value is a valid numeric Unix timestamp,
    convert to 'YYYY-MM-DD'. Otherwise return None.
    """
    if isinstance(ts_value, (int, float)) and ts_value > 0:
        # Convert from Unix timestamp to date string (UTC)
        dt = datetime.datetime.utcfromtimestamp(ts_value)
        return dt.strftime("%Y-%m-%d")
    else:
        return None

def fetch_dividend_info(ticker):
    """
    Fetch upcoming ex-dividend date & pay date from Yahoo Finance.
    Returns (company_name, ex_div_date, pay_date) as strings.
    If ex_div or pay_date are numeric timestamps, we convert them.
    """
    ticker_obj = yf.Ticker(ticker)
    info = ticker_obj.info

    # Company name fallback
    company_name = info.get("shortName") or info.get("longName") or ticker

    # Attempt to read ex_div + pay_date from info
    ex_div_ts = info.get("exDividendDate")
    pay_div_ts = info.get("dividendDate")

    # Convert numeric timestamps to date strings
    ex_div_date = convert_timestamp_to_date(ex_div_ts)
    pay_date = convert_timestamp_to_date(pay_div_ts)

    # Fallback messages if no data
    if ex_div_date is None:
        ex_div_date = "No upcoming ex-date"
    if pay_date is None:
        pay_date = "No upcoming pay date"

    return (company_name, ex_div_date, pay_date)

def run():
    st.title("💵 Dividend Tracker (Upcoming Ex-Dates & Pay Dates)")

    # 1) Load from CSV
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

    # We'll re-fetch ex/pay date each time page loads, so user sees updated info
    updated_data = []
    for item in st.session_state.dividend_watchlist:
        ticker = item["ticker"]
        name, ex_div, pay_div = fetch_dividend_info(ticker)
        updated_data.append({
            "ticker": ticker,
            "company": name,
            "ex_div_date": ex_div,
            "pay_date": pay_div
        })

    st.session_state.dividend_watchlist = updated_data
    save_dividend_watchlist(updated_data)

    df_div = pd.DataFrame(updated_data)
    st.dataframe(df_div)

    st.write("""
    **Note**: Yahoo Finance often does not provide upcoming ex or pay dates 
    for many tickers. This data can be incomplete or missing.
    """)

