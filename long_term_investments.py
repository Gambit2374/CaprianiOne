import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def run():
    st.title("🏦 Long-Term Investment Projections")

    st.sidebar.write("## Projection Inputs")
    initial_investment = st.sidebar.number_input(
        "Initial Investment (£)", min_value=0, value=5000, step=500
    )
    monthly_contrib = st.sidebar.number_input(
        "Monthly Contribution (£)", min_value=0, value=300, step=50
    )
    years = st.sidebar.slider(
        "Investment Duration (Years)", min_value=1, max_value=50, value=20
    )
    expected_growth_rate = st.sidebar.slider(
        "Annual Growth Rate (%)", min_value=0.0, max_value=20.0, value=8.0
    )

    st.write("""
        Adjust the **Initial Investment**, **Monthly Contribution**, **Years**, 
        and **Growth Rate** from the sidebar to see how your portfolio might grow.
    """)

    # Projection Calculation
    balance = initial_investment
    year_list = []
    balance_list = []

    for y in range(1, years + 1):
        balance = (balance + monthly_contrib * 12) * (1 + expected_growth_rate / 100)
        year_list.append(y)
        balance_list.append(balance)

    df = pd.DataFrame({
        "Year": year_list,
        "Projected Value (£)": balance_list
    })

    # Plot
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["Year"], df["Projected Value (£)"], marker="o", color="blue")
    ax.set_title("Portfolio Value Over Time")
    ax.set_xlabel("Year")
    ax.set_ylabel("Value (£)")
    st.pyplot(fig)

    # Show Table
    st.write("### Projection Table")
    st.dataframe(df)

