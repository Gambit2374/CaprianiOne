import streamlit as st

def run():
    st.title("⚖️ Legal Disclaimer")
    st.markdown("""
    <style>
    .main .block-container {
        padding: 20px;
        background-colour: #ffffff;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }
    .stText {
        colour: #333;
        font-size: 16px;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

    st.write("""
    ### Important Legal Information

    **Disclaimer of Liability:**  
    The information provided in this application (Trading Signals for Beginners) is for educational and informational purposes only. It is not intended as financial advice, investment advice, or a recommendation to buy, sell, or hold any securities or financial instruments. All data and analysis are provided "as is" without warranty of any kind, either express or implied.

    **No Professional Advice:**  
    The content within this app does not constitute professional financial or investment advice. You should consult a qualified financial adviser or conduct your own thorough research before making any investment or trading decisions.

    **Risk Acknowledgement:**  
    Trading and investing in financial markets carry a high level of risk, and you may lose all or part of your investment. Past performance is not indicative of future results. The use of this app does not guarantee profits or protect against losses.

    **Data Accuracy:**  
    All data is sourced from third-party providers (e.g., Yahoo Finance) and may contain inaccuracies or delays. The developers of this application are not responsible for any errors, omissions, or losses resulting from the use of this data.

    **User Responsibility:**  
    You are solely responsible for your own investment decisions and for verifying the accuracy and suitability of any information or tools provided. The developers and distributors of this app shall not be liable for any direct, indirect, incidental, special, or consequential damages arising from the use of this application.

    **Governing Law:**  
    This disclaimer is governed by the laws of the United Kingdom. Any disputes arising from the use of this app will be subject to the exclusive jurisdiction of the courts of England and Wales.

    **Contact:**  
    For questions or concerns, please contact the developer at [your-email@example.com]. This app is provided by [Your Name/Company Name], registered in the UK.

    **Last Updated:** 26 February 2025
    """)

    # Disclaimer at the bottom (kept only in Legal tab)
    st.markdown("""
    <div style="position: fixed; bottom: 10px; left: 10px; colour: #ffffff; font-size: 12px; background-colour: rgba(0, 0, 0, 0.7); padding: 5px 10px; border-radius: 5px;">
    All data provided is for reference only. You should always conduct your own analysis and verify information before making any trading or investment decisions.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    run()