import os
import datetime
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

LTI_CSV = "lti_watchlist.csv"

########################################
# 1) LOADING & SAVING THE WATCHLIST
########################################
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

########################################
# 2) COMPUTING HISTORICAL CAGR
########################################
def compute_historical_cagr(ticker, period="5y"):
    """
    Fetches 'period' (e.g. 5y) of daily data from yfinance,
    then computes the compound annual growth rate (CAGR) based
    on first vs. last close. If insufficient data, returns 0.0.
    """
    try:
        df = yf.download(ticker, period=period, interval="1d", progress=False)
        if df.empty:
            return 0.0
        first_price = df["Close"].iloc[0]
        last_price = df["Close"].iloc[-1]
        total_years = (df.index[-1] - df.index[0]).days / 365.0
        if total_years < 0.5:  # less than half a year of data
            return 0.0

        cagr = (last_price / first_price) ** (1 / total_years) - 1
        return cagr
    except:
        return 0.0

########################################
# 3) FUTURE PROJECTION
########################################
def project_future(
    cost_per_share,
    shares_owned,
    monthly_contribution,
    years,
    cagr
):
    """
    Projects year-by-year value, assuming:
      - We start with `shares_owned` at a share price of `cost_per_share`.
      - Each year, the share price grows by `cagr`.
      - Each year, we invest monthly_contribution * 12,
        buying new shares at that year's share price.
    Returns a DataFrame with columns: Year, Share_Price, Shares_Owned, Portfolio_Value
    """
    rows = []
    share_price = cost_per_share
    total_shares = shares_owned

    for yr in range(1, years + 1):
        # End-of-year share price grows by (1 + cagr)
        share_price = share_price * (1 + cagr)
        # We buy new shares with monthly_contribution * 12
        # at this year-end share price
        new_shares = 0.0
        if share_price > 0:
            new_shares = (monthly_contribution * 12) / share_price
        total_shares += new_shares
        portfolio_value = total_shares * share_price

        rows.append({
            "Year": yr,
            "Share_Price": round(share_price, 2),
            "Shares_Owned": round(total_shares, 4),
            "Portfolio_Value": round(portfolio_value, 2),
        })

    return pd.DataFrame(rows)

########################################
# 4) MAIN STREAMLIT PAGE
########################################
def run():
    st.title("🏦 Long-Term Investments (Enhanced)")

    # 1) Load from CSV once
    if "lti_watchlist" not in st.session_state:
        st.session_state.lti_watchlist = load_lti_watchlist()

    st.subheader("Add/Remove Tickers in Your Portfolio")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        new_ticker = st.text_input("Ticker (e.g. 'AAPL')").upper().strip()
    with col2:
        cost_per_share = st.number_input("Cost/Share (£)", min_value=0.0, value=100.0, step=5.0)
    with col3:
        shares_owned = st.number_input("Shares Owned", min_value=0.0, value=10.0, step=1.0)
    with col4:
        monthly_contrib = st.number_input("Monthly Contrib (£)", min_value=0.0, value=200.0, step=50.0)

    if st.button("Add to Portfolio"):
        if new_ticker:
            existing = [item for item in st.session_state.lti_watchlist if item["ticker"] == new_ticker]
            if existing:
                st.warning(f"{new_ticker} is already in the portfolio.")
            else:
                st.session_state.lti_watchlist.append({
                    "ticker": new_ticker,
                    "cost_per_share": cost_per_share,
                    "shares_owned": shares_owned,
                    "monthly_contribution": monthly_contrib
                })
                save_lti_watchlist(st.session_state.lti_watchlist)
                st.success(f"Added {new_ticker} to portfolio")

    # Remove Ticker
    all_tickers = [item["ticker"] for item in st.session_state.lti_watchlist]
    remove_col1, remove_col2 = st.columns(2)
    with remove_col1:
        ticker_to_remove = st.selectbox("Remove a Ticker", options=[""] + all_tickers)
    with remove_col2:
        if st.button("Remove"):
            if ticker_to_remove:
                st.session_state.lti_watchlist = [
                    x for x in st.session_state.lti_watchlist if x["ticker"] != ticker_to_remove
                ]
                save_lti_watchlist(st.session_state.lti_watchlist)
                st.warning(f"Removed {ticker_to_remove} from portfolio.")

    st.write("---")

    # 2) Show current portfolio
    if not st.session_state.lti_watchlist:
        st.info("No tickers in your portfolio yet.")
        return

    df_watch = pd.DataFrame(st.session_state.lti_watchlist)
    st.write("### Your Portfolio")
    st.dataframe(df_watch)

    st.write("---")
    st.subheader("In-Depth Projection for a Single Ticker")

    # 3) Select ticker for deeper analysis
    chosen_ticker = st.selectbox("Select Ticker:", options=[""] + all_tickers)
    if not chosen_ticker:
        st.info("Select a ticker to see long-term projections.")
        return

    # Find the portfolio item for that ticker
    portfolio_item = next((x for x in st.session_state.lti_watchlist if x["ticker"] == chosen_ticker), None)
    if not portfolio_item:
        st.error("Ticker not found in portfolio list.")
        return

    # 4) Compute historical CAGR (5y)
    cagr = compute_historical_cagr(chosen_ticker, period="5y")

    # 5) Choose # of years to project
    years = st.slider("Projection Years", min_value=1, max_value=25, value=10)

    st.write(f"**Estimated CAGR from last 5 years** for {chosen_ticker}: {cagr*100:.2f}%")

    # 6) Run the projection
    df_proj = project_future(
        cost_per_share=portfolio_item["cost_per_share"],
        shares_owned=portfolio_item["shares_owned"],
        monthly_contribution=portfolio_item["monthly_contribution"],
        years=years,
        cagr=cagr
    )

    st.write("### Projection Table")
    st.dataframe(df_proj)

    # 7) Plot the result
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(df_proj["Year"], df_proj["Portfolio_Value"], marker="o", color="blue")
    ax.set_title(f"{chosen_ticker} - Projected Value Over {years} Years (CAGR ~ {cagr*100:.2f}%)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Portfolio Value (£)")
    st.pyplot(fig)

    st.write("""
    **Note**: This is a simplified model. We:
    1. Use your 'cost per share' and 'shares owned' as the starting point.
    2. Estimate future share price growth via the historical 5-year CAGR from Yahoo Finance.
    3. Each year, the share price grows by that CAGR; you invest your monthly total * 12 once at year-end.
    4. Actual market conditions may differ significantly!
    """)



