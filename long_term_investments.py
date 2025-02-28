import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

LTI_CSV = "lti_watchlist.csv"
CURRENCY_MAP = {"USD": "£", "GBP": "£", "GBp": "£", "EUR": "€"}

def load_watchlist():
    if os.path.exists(LTI_CSV):
        df = pd.read_csv(LTI_CSV)
        df.columns = [col.capitalize() for col in df.columns]
        return df.to_dict("records")
    return []

def save_watchlist(watchlist):
    pd.DataFrame(watchlist).to_csv(LTI_CSV, index=False)

def fetch_fundamental_data(ticker):
    info_dict = {}
    try:
        tkr = yf.Ticker(ticker)
        info = tkr.info
        info_dict["Company"] = info.get("shortName", info.get("longName", ticker) or "N/A")
        info_dict["Forward P/E"] = info.get("forwardPE", "N/A")
        info_dict["Trailing P/E"] = info.get("trailingPE", "N/A")
        info_dict["Market Cap"] = info.get("marketCap", "N/A")
        info_dict["Currency"] = info.get("currency", "USD")
    except Exception as e:
        st.error(f"Failed to fetch fundamentals for {ticker}: {e}")
        info_dict["Company"] = ticker
        info_dict["Forward P/E"] = "N/A"
        info_dict["Trailing P/E"] = "N/A"
        info_dict["Market Cap"] = "N/A"
        info_dict["Currency"] = "USD"
    return info_dict

def compute_historical_cagr(ticker, period="5y"):
    try:
        df = yf.download(ticker, period=period, interval="1d", progress=False)
        if df.empty or "Close" not in df.columns:
            return 0.0
        cagr = float(((df["Close"].iloc[-1] / df["Close"].iloc[0]) ** (1 / (len(df) / 252)) - 1))
        return cagr
    except Exception:
        return 0.0

def get_current_price_and_currency(ticker):
    try:
        tkr = yf.Ticker(ticker)
        info = tkr.info
        price = float(info.get("regularMarketPrice", yf.download(ticker, period="1d", progress=False)["Close"].iloc[-1] if not yf.download(ticker, period="1d", progress=False).empty else None))
        currency = info.get("currency", "USD")
        return price, CURRENCY_MAP.get(currency, "£")
    except Exception:
        return None, "£"

def project_future_price(current_price, years, cagr):
    if current_price is None or not isinstance(current_price, (int, float)):
        return pd.DataFrame([{"Year": 0, "Projected Price": "N/A"}])
    rows = [{"Year": 0, "Projected Price": round(current_price, 2)}]
    price = current_price
    for yr in range(1, years + 1):
        price *= (1 + cagr)
        rows.append({"Year": yr, "Projected Price": round(price, 2)})
    return pd.DataFrame(rows)

def generate_long_term_conclusion(cagr, fundamentals):
    growth_text = "Strong" if cagr > 0.10 else "Moderate" if cagr > 0 else "Negative/No Growth"
    forward_pe = fundamentals.get("Forward P/E", "N/A")
    market_cap = fundamentals.get("Market Cap", "N/A")
    valuation_text = ("Attractive" if forward_pe < 15 else "Fair" if forward_pe < 30 else "High") if isinstance(forward_pe, (float, int)) else "Unknown"
    
    conclusion = f"The best decision for this stock is to "
    if cagr > 0.10 and isinstance(forward_pe, (float, int)) and forward_pe < 30:
        conclusion += f"invest long-term, as it demonstrates strong growth potential (CAGR of {cagr * 100:.2f}%) and an attractive valuation (Forward P/E of {forward_pe:.2f})."
    elif cagr <= 0:
        conclusion += f"avoid long-term investment due to negative or no growth (CAGR of {cagr * 100:.2f}%), indicating high risk."
    else:
        conclusion += f"proceed with caution for long-term investment, as growth is moderate ({cagr * 100:.2f}%) and valuation may not be optimal (Forward P/E {forward_pe if isinstance(forward_pe, (float, int)) else 'unknown'})."

    if isinstance(market_cap, (int, float)):
        conclusion += f" The company’s market cap of {market_cap / 1e9:.2f} billion suggests a {'large' if market_cap > 1e11 else 'mid-sized' if market_cap > 2e10 else 'small'} entity, which may influence your decision."
    return conclusion

def run():
    st.title("🏦 Long-Term Investments – Watchlist & Deep Analysis")
    st.write("""
    Analyse stocks for long-term growth with fundamental data, historical performance, and detailed conclusions.
    Add tickers to your long-term investing watchlist to evaluate long-term potential.
    **Guidance:** Focus on stocks with strong growth (CAGR > 10%), attractive valuations (P/E < 30), and conclusions for long-term holding decisions.
    """)

    if "long_term_watchlist" not in st.session_state:
        st.session_state.long_term_watchlist = load_watchlist()

    st.subheader("Manage Your Long-Term Investing Watchlist")
    new_ticker = st.text_input("Add a Ticker (e.g., 'AAPL')", help="Enter a stock symbol like 'AAPL' for Apple.").upper().strip()
    if st.button("Add Ticker") and new_ticker:
        if any(item.get("ticker", item.get("Ticker", "")) == new_ticker for item in st.session_state.long_term_watchlist):
            st.warning(f"{new_ticker} is already in your long-term investing watchlist.")
        else:
            fundamentals = fetch_fundamental_data(new_ticker)
            price, sym = get_current_price_and_currency(new_ticker)
            cagr_5y = compute_historical_cagr(new_ticker)
            record = {
                "ticker": new_ticker,
                "Company": fundamentals["Company"],
                "Current Price": f"{sym}{price:.2f}" if price else "N/A",
                "5Y CAGR (%)": round(cagr_5y * 100, 2) if cagr_5y else "N/A",
                "Forward P/E": fundamentals["Forward P/E"],
                "Trailing P/E": fundamentals["Trailing P/E"],
                "Market Cap": fundamentals["Market Cap"]
            }
            st.session_state.long_term_watchlist.append(record)
            save_watchlist(st.session_state.long_term_watchlist)
            st.success(f"Added {new_ticker} to your long-term investing watchlist.")

    all_tickers = [item.get("ticker", item.get("Ticker", "")) for item in st.session_state.long_term_watchlist]
    remove_ticker = st.selectbox("Remove a Ticker", options=[""] + all_tickers, help="Select a ticker to remove from your watchlist.")
    if st.button("Remove Ticker") and remove_ticker:
        st.session_state.long_term_watchlist = [item for item in st.session_state.long_term_watchlist if item.get("ticker", item.get("Ticker", "")) != remove_ticker]
        save_watchlist(st.session_state.long_term_watchlist)
        st.warning(f"Removed {remove_ticker} from your long-term investing watchlist.")

    st.subheader("Long-Term Investing Watchlist Table")
    if not st.session_state.long_term_watchlist:
        st.info("No tickers in your long-term investing watchlist yet. Add one above!")
    else:
        watchlist_data = []
        for item in st.session_state.long_term_watchlist:
            ticker = item.get("ticker", item.get("Ticker", ""))
            fundamentals = fetch_fundamental_data(ticker)
            price, sym = get_current_price_and_currency(ticker)
            cagr_5y = compute_historical_cagr(ticker)
            watchlist_data.append({
                "ticker": ticker,
                "Company": fundamentals["Company"],
                "Current Price": f"{sym}{price:.2f}" if price else "N/A",
                "5Y CAGR (%)": round(cagr_5y * 100, 2) if cagr_5y else "N/A",
                "Forward P/E": fundamentals["Forward P/E"],
                "Trailing P/E": fundamentals["Trailing P/E"],
                "Market Cap": fundamentals["Market Cap"]
            })
        st.session_state.long_term_watchlist = watchlist_data
        save_watchlist(watchlist_data)
        df_watchlist = pd.DataFrame(watchlist_data)
        st.dataframe(df_watchlist, use_container_width=True, height=400)

        st.subheader("Deep Analysis")
        st.write("""
        Select a ticker for in-depth long-term analysis, including fundamental data, historical performance, and a conclusion.
        **Tips for Long-Term Investing:**
        - Focus on stocks with strong growth (CAGR > 10%) and attractive valuations (P/E < 30).
        - Use the conclusion to guide your long-term investment decisions.
        - Check historical and projected price charts for trends.
        """)
        chosen_ticker = st.selectbox("Select a Ticker for Deep Analysis", options=[""] + all_tickers, help="Choose a ticker to see in-depth long-term analysis.")
        if chosen_ticker:
            fundamentals = fetch_fundamental_data(chosen_ticker)
            price, sym = get_current_price_and_currency(chosen_ticker)
            cagr_5y = compute_historical_cagr(chosen_ticker)
            conclusion = generate_long_term_conclusion(cagr_5y, fundamentals)

            with st.expander("Fundamental Data", expanded=True):
                st.table(pd.DataFrame(list(fundamentals.items()), columns=["Metric", "Value"]))

            st.write(f"**Current Price:** {sym}{price:.2f}" if price else "**Current Price:** N/A")
            st.write(f"**5-Year Historical CAGR:** {cagr_5y * 100:.2f}%" if cagr_5y else "N/A")
            st.write(f"**Conclusion:** {conclusion}")
            st.write("""
            **Guidance:** Use this conclusion to assess if the stock fits your long-term goals. Prioritise stocks with strong growth, low P/E ratios, and positive assessments for long-term holding.
            """)

            st.write("### Historical Performance (5 Years)")
            df_hist = yf.download(chosen_ticker, period="5y", interval="1d", progress=False)
            if not df_hist.empty:
                fig_hist, ax = plt.subplots(figsize=(12, 6))
                ax.plot(df_hist.index, df_hist["Close"], label="Close Price", color="blue")
                ax.set_title(f"{chosen_ticker} - 5-Year Historical Performance")
                ax.set_xlabel("Date")
                ax.set_ylabel(f"Price ({sym})")
                ax.legend()
                ax.grid(True, linestyle="--", alpha=0.7)
                st.pyplot(fig_hist)
            else:
                st.warning("Historical data not available.")

            st.write("### Future Price Projection")
            years = st.selectbox("Projection Duration (Years)", [1, 5, 10, 15, 25], index=1, help="Select the number of years to project future prices.")
            df_proj = project_future_price(price, years, cagr_5y)
            st.dataframe(df_proj, use_container_width=True)
            fig_proj, ax = plt.subplots(figsize=(10, 5))
            ax.plot(df_proj["Year"], df_proj["Projected Price"], marker="o", color="#008000")  # Green
            ax.set_title(f"Projected Price for {chosen_ticker} (@ {cagr_5y * 100:.2f}% CAGR)")
            ax.set_xlabel("Year")
            ax.set_ylabel(f"Projected Price ({sym})")
            ax.grid(True, linestyle="--", alpha=0.7)
            st.pyplot(fig_proj)