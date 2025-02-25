import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

LTI_CSV = "lti_watchlist.csv"

def load_lti_watchlist():
    """Load the LTI watchlist from a local CSV if it exists."""
    if os.path.exists(LTI_CSV):
        df = pd.read_csv(LTI_CSV)
        return df.to_dict("records")
    return []

def save_lti_watchlist(watchlist):
    """Save the LTI watchlist to CSV."""
    df = pd.DataFrame(watchlist)
    df.to_csv(LTI_CSV, index=False)

def run():
    st.title("🏦 Long-Term Investments (Add/Remove Tickers)")

    # A watchlist for your "portfolio" with initial & monthly invests
    if "lti_watchlist" not in st.session_state:
        st.session_state.lti_watchlist = load_lti_watchlist()

    st.subheader("Manage Your Long-Term Portfolio Watchlist")
    col1, col2, col3 = st.columns(3)

    with col1:
        new_ticker = st.text_input("Ticker (e.g. 'AAPL')").upper().strip()
    with col2:
        init_invest = st.number_input("Initial Investment (£)", min_value=0, value=1000, step=500)
    with col3:
        monthly_contrib = st.number_input("Monthly Contrib (£)", min_value=0, value=200, step=50)

    if st.button("Add to Portfolio"):
        if new_ticker:
            existing = [item for item in st.session_state.lti_watchlist if item["ticker"] == new_ticker]
            if existing:
                st.warning(f"{new_ticker} is already in the portfolio.")
            else:
                st.session_state.lti_watchlist.append({
                    "ticker": new_ticker,
                    "init": init_invest,
                    "monthly": monthly_contrib
                })
                save_lti_watchlist(st.session_state.lti_watchlist)
                st.success(f"Added {new_ticker} to portfolio with £{init_invest} initial and £{monthly_contrib}/month")

    # Remove Ticker
    all_tickers = [item["ticker"] for item in st.session_state.lti_watchlist]
    ticker_to_remove = st.selectbox("Remove a Ticker", options=[""] + all_tickers)
    if st.button("Remove Ticker"):
        if ticker_to_remove:
            st.session_state.lti_watchlist = [
                x for x in st.session_state.lti_watchlist if x["ticker"] != ticker_to_remove
            ]
            save_lti_watchlist(st.session_state.lti_watchlist)
            st.warning(f"Removed {ticker_to_remove} from portfolio list.")

    st.write("---")

    # If your portfolio is empty, show a message
    if not st.session_state.lti_watchlist:
        st.info("No tickers in your long-term portfolio yet.")
        return

    st.subheader("Projection Settings")
    years = st.slider("Investment Duration (Years)", 1, 50, 20)
    expected_growth_rate = st.slider("Annual Growth Rate (%)", 0.0, 20.0, 8.0)

    # We'll build a table of final values
    results = []
    for item in st.session_state.lti_watchlist:
        ticker = item["ticker"]
        init = item["init"]
        monthly = item["monthly"]

        balance = init
        for _ in range(years):
            balance = (balance + monthly * 12) * (1 + expected_growth_rate / 100)

        results.append({
            "Ticker": ticker,
            "Initial (£)": init,
            "Monthly (£)": monthly,
            "Final Value After X Years (£)": round(balance, 2)
        })

    df_res = pd.DataFrame(results)
    st.write("### Portfolio Projection Results")
    st.dataframe(df_res)

    # Optionally sum them up
    total_final = df_res["Final Value After X Years (£)"].sum()
    st.write(f"**Total Projected Value** after {years} years: £{total_final:,.2f}")

    # Optional chart of each ticker's final value
    fig, ax = plt.subplots(figsize=(8,5))
    ax.bar(df_res["Ticker"], df_res["Final Value After X Years (£)"], color="green")
    ax.set_title(f"Final Value after {years} years at {expected_growth_rate}% annual growth")
    ax.set_ylabel("Projected Value (£)")
    st.pyplot(fig)

