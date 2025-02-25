import streamlit as st

st.set_page_config(page_title="Investing Dashboard", layout="wide")

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    [
        "Stock Analysis",
        "Long-Term Investments",
        "Dividend Tracker"
    ]
)

if page == "Stock Analysis":
    import stock_analysis
    stock_analysis.run()

elif page == "Long-Term Investments":
    import long_term_investments
    long_term_investments.run()

elif page == "Dividend Tracker":
    import dividend_tracker
    dividend_tracker.run()
