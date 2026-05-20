import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from ta.trend import SMAIndicator
from ta.momentum import RSIIndicator
from streamlit_option_menu import option_menu

# PAGE CONFIG
st.set_page_config(
    page_title="Crypto Forecasting Dashboard",
    layout="wide"
)

# -----------------------------
# LOGIN AUTHENTICATION
# -----------------------------

USERNAME = "admin"
PASSWORD = "1234"

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login():

    st.title("Login Page")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
            st.success("Login Successful")
            st.rerun()

        else:
            st.error("Invalid Username or Password")

# STOP APP IF NOT LOGGED IN
if not st.session_state.logged_in:
    login()
    st.stop()

# -----------------------------
# SIDEBAR
# -----------------------------

with st.sidebar:

    st.success("Logged In")

    selected = option_menu(
        menu_title="Crypto Dashboard",
        options=[
            "Home",
            "Prediction",
            "Technical Indicators"
        ],
        icons=["house", "graph-up", "bar-chart"],
        default_index=0
    )

    # LOGOUT BUTTON
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

# -----------------------------
# TITLE
# -----------------------------

st.title("Cryptocurrency Forecasting Dashboard")

# -----------------------------
# CRYPTO SELECTION
# -----------------------------

crypto = st.selectbox(
    "Select Cryptocurrency",
    ["BTC-USD", "ETH-USD", "SOL-USD", "DOGE-USD"]
)

# -----------------------------
# DOWNLOAD DATA
# -----------------------------

df = yf.download(
    crypto,
    start="2020-01-01",
    auto_adjust=True
)

# FIX MULTIINDEX
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

# -----------------------------
# HOME PAGE
# -----------------------------

if selected == "Home":

    st.subheader(f"{crypto} Historical Data")

    st.write(df.tail())

    # CANDLESTICK CHART
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']
    )])

    fig.update_layout(
        title=f"{crypto} Candlestick Chart",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_dark"
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# PREDICTION PAGE
# -----------------------------

elif selected == "Prediction":

    st.subheader("Crypto Price Prediction")

    # LAST 30 DAYS DATA
    recent_data = df['Close'].tail(30)

    # SIMPLE MOVING AVERAGE PREDICTION
    predicted_price = recent_data.mean()

    # ACTUAL PRICES
    actual_prices = recent_data.values

    # PREDICTED LINE
    predicted_prices = np.full(
        shape=len(actual_prices),
        fill_value=predicted_price
    )

    # GRAPH
    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(
        y=actual_prices,
        mode='lines',
        name='Actual Price'
    ))

    fig2.add_trace(go.Scatter(
        y=predicted_prices,
        mode='lines',
        name='Predicted Price'
    ))

    fig2.update_layout(
        title="Actual vs Predicted Prices",
        xaxis_title="Time",
        yaxis_title="Price",
        template="plotly_dark"
    )

    st.plotly_chart(fig2, use_container_width=True)

    # NEXT DAY PREDICTION
    st.subheader("Next Day Prediction")

    latest_price = df['Close'].iloc[-1]

    # SIMPLE TREND CALCULATION
    trend = recent_data.pct_change().mean()

    next_day_prediction = latest_price * (1 + trend)

    st.success(
        f"Predicted Next Day Price: ${next_day_prediction:.2f}"
    )

# -----------------------------
# TECHNICAL INDICATORS
# -----------------------------

elif selected == "Technical Indicators":

    st.subheader("Technical Indicators")

    # SMA
    sma = SMAIndicator(
        close=df['Close'].squeeze(),
        window=20
    )

    df['SMA20'] = sma.sma_indicator()

    # RSI
    rsi = RSIIndicator(
        close=df['Close'].squeeze(),
        window=14
    )

    df['RSI'] = rsi.rsi()

    # PRICE + SMA CHART
    fig3 = go.Figure()

    fig3.add_trace(go.Scatter(
        x=df.index,
        y=df['Close'],
        mode='lines',
        name='Close Price'
    ))

    fig3.add_trace(go.Scatter(
        x=df.index,
        y=df['SMA20'],
        mode='lines',
        name='20 Day SMA'
    ))

    fig3.update_layout(
        title="Close Price vs SMA20",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_dark"
    )

    st.plotly_chart(fig3, use_container_width=True)

    # RSI GRAPH
    fig4 = go.Figure()

    fig4.add_trace(go.Scatter(
        x=df.index,
        y=df['RSI'],
        mode='lines',
        name='RSI'
    ))

    fig4.add_hline(y=70)
    fig4.add_hline(y=30)

    fig4.update_layout(
        title="RSI Indicator",
        xaxis_title="Date",
        yaxis_title="RSI Value",
        template="plotly_dark"
    )

    st.plotly_chart(fig4, use_container_width=True)

    # BUY/SELL SIGNAL
    latest_rsi = df['RSI'].iloc[-1]

    st.subheader("Trading Signal")

    if latest_rsi < 30:
        st.success("BUY SIGNAL")

    elif latest_rsi > 70:
        st.error("SELL SIGNAL")

    else:
        st.warning("HOLD")
