import streamlit as st

st.set_page_config(page_title="Trading Signals for Beginners", layout="wide", page_icon="📊")

# Styling with futuristic design, removing wallpapers
st.markdown("""
    <style>
    .sidebar .sidebar-content {
        background-colour: #1a1a2e;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .stButton>button {
        background-colour: #00d4ff;
        colour: white;
        border-radius: 12px;
        padding: 12px 24px;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-colour: #00aaff;
        transform: scale(1.05);
    }
    .stSelectbox, .stTextInput {
        border-radius: 12px;
        background-colour: #2e2e48;
        border: 1px solid #444;
        colour: white;
    }
    .main .block-container {
        padding: 20px;
        background-colour: #ffffff;
        border-radius: 15px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", [
    "Stock Analysis",
    "Long-Term Investments",
    "Top 25 Stocks",
    "Education Hub",
    "Legal"
])

# Remove the dynamic ID for wallpapers
# st.markdown(f'<div id="{page.replace(" ", "-")}" style="height: 100vh; width: 100%;"></div>', unsafe_allow_html=True)

if page == "Stock Analysis":
    import stock_analysis
    stock_analysis.run()

elif page == "Long-Term Investments":
    import long_term_investments
    long_term_investments.run()

elif page == "Top 25 Stocks":
    import top_25_stocks
    top_25_stocks.run()

elif page == "Education Hub":
    import education_hub
    education_hub.run()

elif page == "Legal":
    import legal_disclaimer
    legal_disclaimer.run()