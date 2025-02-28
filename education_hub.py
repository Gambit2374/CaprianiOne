import streamlit as st
import matplotlib.pyplot as plt
from io import BytesIO

def create_candlestick_illustration():
    fig, ax = plt.subplots(figsize=(10, 6))
    dates = ['2025-02-01', '2025-02-02', '2025-02-03']
    opens = [100, 105, 103]
    highs = [110, 108, 106]
    lows = [98, 102, 100]
    closes = [105, 107, 104]

    # Create candlesticks (green for up, red for down)
    for i in range(len(dates)):
        if closes[i] >= opens[i]:
            ax.vlines(dates[i], lows[i], highs[i], colors='green', linewidth=1)
            ax.vlines(dates[i], opens[i], closes[i], colors='green', linewidth=5)
        else:
            ax.vlines(dates[i], lows[i], highs[i], colors='red', linewidth=1)
            ax.vlines(dates[i], closes[i], opens[i], colors='red', linewidth=5)
    
    ax.set_title("Candlestick Chart Example")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.grid(True, linestyle="--", alpha=0.7)
    ax.legend(["High/Low", "Bullish (Up)", "Bearish (Down)"], loc="upper left")
    
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    return buf.getvalue()

def create_line_chart_illustration():
    fig, ax = plt.subplots(figsize=(10, 6))
    dates = ['2025-02-01', '2025-02-02', '2025-02-03', '2025-02-04', '2025-02-05']
    prices = [100, 102, 98, 105, 103]
    
    ax.plot(dates, prices, color="#00d4ff", marker="o", label="Price Trend")
    ax.set_title("Line Chart Example (Price Trend)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.grid(True, linestyle="--", alpha=0.7)
    ax.legend()
    
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close()
    return buf.getvalue()

def run():
    st.title("📚 Education Hub – Your Comprehensive Trading Guide")
    st.write("""
    Welcome to the Education Hub! This comprehensive resource covers all aspects of trading for beginners and advanced users, with in-depth teachings, illustrations, tips, and FAQs. Use the expanders below to explore topics and apply what you learn in our tools.
    """)

    st.markdown("""
    <style>
    .stExpander {
        background-colour: #2e2e48;
        border-radius: 12px;
        margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .stExpander > div > div {
        padding: 15px;
        colour: #ffffff;
    }
    .main .block-container {
        background-colour: #ffffff;
        border-radius: 15px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
    }
    </style>
    """, unsafe_allow_html=True)

    with st.expander("What is Trading? – Beginner’s Overview", expanded=True):
        st.write("""
        **Trading** is buying and selling financial assets (like shares) to make a profit. It can be short-term (e.g., day or swing trading) or long-term (investing for years).
        - **Shares**: Ownership in companies you can buy or sell on exchanges.
        - **Goals**: Profit from price changes, dividends, or both.
        **Illustration:** See our line chart example below for price trends.
        """)
        st.image(create_line_chart_illustration(), caption="Line Chart Showing Price Trends")

        st.write("""
        **Tip:** Start with small investments, learn from this hub, and use our Stock Analysis and Top 25 Stocks tabs to practise.
        """)

    with st.expander("Trading Strategies – In-Depth Guide"):
        st.write("""
        **1. Day Trading**: Buy and sell within a single day. Requires quick decisions and close attention to charts.
        - **Indicators to Use**: RSI, Bollinger Bands (from Stock Analysis) for momentum and volatility.
        - **Tip:** Focus on high-volume, liquid shares to minimise slippage.

        **2. Swing Trading**: Hold for days to weeks, capturing short-term price swings.
        - **Indicators to Use**: Signals, MACD, and volume (Top 25 Stocks) for entry/exit points.
        - **Tip:** Identify support/resistance levels using Bollinger Bands or moving averages.

        **3. Long-Term Investing**: Hold for years, focusing on growth and dividends.
        - **Indicators to Use**: CAGR, P/E ratios, and historical trends (Long-Term Investments).
        - **Tip:** Prioritise stable, fundamentally strong companies with growth potential.

        **Illustration:** See our candlestick chart for pattern examples.
        """)
        st.image(create_candlestick_illustration(), caption="Candlestick Patterns for Trading")

    with st.expander("How to Get Started – Step-by-Step Guide"):
        st.write("""
        **Step 1: Learn the Basics** – Understand shares, charts, and indicators here.
        **Step 2: Use Our Tools** – Add tickers to Stock Analysis, Top 25 Stocks, or Long-Term Investments tabs to analyse trends.
        **Step 3: Start Small** – Practise with a few shares, perhaps using virtual trading platforms.
        **Step 4: Monitor & Adjust** – Check daily updates, refine strategies, and learn from experience.
        **Illustration:** Use our charts to spot trends and patterns in real time.
        **Tip:** Follow guidance in each tab for specific strategies and decision-making.
        """)

    with st.expander("Candlestick Patterns – Detailed Guide with Illustrations"):
        st.image(create_candlestick_illustration(), caption="Advanced Candlestick Chart")
        st.write("""
        **What are Candlesticks?** Candlesticks visually represent price movements over time, with:
        - **Body**: Shows open and close prices (green = price up, red = price down).
        - **Wicks (Shadows)**: Indicate high and low prices during the period.
        **Common Patterns:**
        - **Doji**: Open = close, signals indecision and potential reversal (e.g., small body, long wicks).
        - **Hammer**: Bullish reversal after a downtrend (small body, long lower wick, little or no upper wick).
        - **Shooting Star**: Bearish reversal after an uptrend (small body, long upper wick, little or no lower wick).
        - **Engulfing Patterns**: Bullish (green body engulfs prior red body) or bearish (red body engulfs prior green body) signals strong reversals.
        **Guidance:** Use Stock Analysis charts to identify patterns; combine with RSI, MACD, or volume for confirmation.
        **Tip:** Practise spotting patterns on historical data in our tabs, focusing on volatility and volume spikes.
        """)

    with st.expander("Technical Indicators – In-Depth Explanations"):
        st.write("""
        **1. Moving Averages (SMA, EMA)**: Smooth price data to identify trends.
        - **SMA200**: Long-term trend (200-day simple moving average).
        - **EMA20**: Short-term trend (20-day exponential moving average, faster response).
        - **Use:** Crossovers signal potential trend changes (e.g., EMA20 crossing SMA200).

        **2. Relative Strength Index (RSI)**: Measures momentum (0–100).
        - **Overbought (>70)**: Possible sell signal.
        - **Oversold (<30)**: Possible buy signal.
        - **Use:** Combine with price action for entry/exit points.

        **3. Moving Average Convergence Divergence (MACD)**: Tracks momentum and trend changes.
        - **MACD Line > Signal Line**: Bullish momentum.
        - **MACD Line < Signal Line**: Bearish momentum.
        - **Use:** Watch for crossovers to confirm trends.

        **4. Bollinger Bands**: Show volatility and potential reversals.
        - **Bands widen**: High volatility (breakout potential).
        - **Bands narrow**: Low volatility (possible breakout brewing).
        - **Use:** Price near lower band = potential buy, near upper band = potential sell.

        **Illustration:** See charts in Stock Analysis and Top 25 Stocks for real examples.
        """)

    with st.expander("Fundamental Analysis – Long-Term Investing"):
        st.write("""
        **Key Metrics:**
        - **CAGR (5-Year Compound Annual Growth Rate)**: Measures long-term growth (higher >10% is strong).
        - **P/E Ratio (Price-to-Earnings)**: Indicates valuation (lower <30 suggests undervaluation).
        - **Market Cap**: Company size (large >£100bn, mid-sized £20–100bn, small <£20bn).
        **Guidance:** Use Long-Term Investments tab to analyse these metrics for stable, growth-oriented stocks.
        **Tip:** Diversify across sectors for reduced risk.
        """)

    with st.expander("Risk Management – Essential Tips"):
        st.write("""
        **1. Start Small**: Invest only what you can afford to lose.
        **2. Diversify**: Spread investments across multiple stocks or sectors.
        **3. Set Stop-Losses**: Limit losses by setting price thresholds to sell.
        **4. Monitor Volatility**: Use Bollinger Bands and RSI to manage risk.
        **5. Educate Continuously**: Revisit this hub and use our tools regularly.
        **Illustration:** See volatility examples in our charts (e.g., Bollinger Bands widening).
        """)

    with st.expander("FAQs – Comprehensive Answers"):
        st.write("""
        **Q: What’s the best strategy for a beginner?**
        - A: Start with swing trading for short-term gains or long-term investing for stability. Use our tabs to test both, beginning with small positions.

        **Q: How do I interpret signals in Stock Analysis or Top 25 Stocks?**
        - A: Strong Buy = enter long, Strong Sell = enter short, Buy/Sell = consider with caution, Hold = wait for clearer signals. Combine with charts and indicators.

        **Q: What does ‘N/A’ mean in data?**
        - A: It means Yahoo Finance couldn’t fetch data. Try another ticker or check later; some stocks may not support all metrics.

        **Q: How do I use RSI, Bollinger Bands, and MACD effectively?**
        - A: RSI >70 or <30 signals overbought/oversold; Bollinger Bands show volatility (wide = high, narrow = low); MACD crossovers indicate momentum shifts. See our tabs’ guidance.

        **Q: Is trading risky, and how can I mitigate it?**
        - A: Yes, trading carries risk, but our tools and risk management tips (e.g., diversification, stop-losses) help. Start small, verify data, and learn continuously.

        **Q: How do I identify candlestick patterns?**
        - A: Look for Doji (indecision), Hammer/Shooting Star (reversals), or Engulfing patterns (strong moves). Use our charts and illustrations, combining with indicators.
        """)

    st.write("""
    **Pro Tip:** Bookmark this hub, revisit regularly, and apply lessons in our tabs. Trading is a journey—start small, stay patient, and enjoy learning!
    """)