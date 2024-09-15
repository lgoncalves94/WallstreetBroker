from utils import *  # Ensure you only import what's necessary
import logging_config
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import pytz
import ta

broker = WallstreetBroker()

# Sidebar for INPUT
st.sidebar.header('Chart Parameters')
ticker = st.sidebar.selectbox('Ticker Symbol', ['NFLX', 'GOOGL', 'AMZN', 'MSFT','TSLA'])  # Changed 'Time Period' to 'Ticker Symbol'
time_period = st.sidebar.selectbox('Time Period', ['1d', '1w', '1mo', '1y', 'max'])
chart_type = st.sidebar.selectbox('Chart Type', ['Candlestick', 'Line'])
indicators = st.sidebar.multiselect('Technical Indicators', ['SMA 20', 'EMA 20'])

# Mapping time periods to data intervals
interval_mapping = {
    '1d': '1m',
    '1w': '30m',
    '1mo': '1d',
    '1y': '1w',
    'max': '1w'
}

# Update the dashboard based on user input
if st.sidebar.button('Update'):
    # Use 'ticker' instead of 'time_period' for fetching stock data
    data = broker.fetch_stock_data(ticker, time_period, interval_mapping[time_period])
    data = broker.process_data(data)
    data = broker.add_technical_indicators(data)
    last_close, change, pct_change, high, low, volume = broker.calculate_metrics(data)

    st.metric(
        label=f'{ticker} Last Price',
        value=f'{last_close:.2f} USD',
        delta=f'{change:.2f} ({pct_change:.2f}%)'
    )

    col1, col2, col3 = st.columns(3)
    col1.metric('High', f'{high:.2f} USD')
    col2.metric('Low', f'{low:.2f} USD')
    col3.metric('Volume', f'{volume:,}')

    fig = go.Figure()

    match chart_type:
        case 'Candlestick':
            fig.add_trace(go.Candlestick(
                x=data['Datetime'],
                open=data['Open'],
                low=data['Low'],
                close=data['Close']
            ))
        case _:
            fig = px.line(data, x='Datetime', y='Close')

    for indicator in indicators:
        match indicator:
            case 'SMA 20':
                fig.add_trace(go.Scatter(x=data['Datetime'], y=data['SMA_20'], name='SMA 20'))
            case 'EMA 20':
                fig.add_trace(go.Scatter(x=data['Datetime'], y=data['EMA_20'], name='EMA 20'))

    fig.update_layout(
        title=f'{ticker} {time_period.upper()} Chart',
        xaxis_title='Time',
        yaxis_title='Price (USD)',
        height=600  # Adjusted to a reasonable size
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader('Historical Data')
    st.dataframe(data[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']])

    st.subheader('Technical Indicators')
    st.dataframe(data[['Datetime', 'SMA_20', 'EMA_20']])

# Sidebar for Real-Time Stock Prices
st.sidebar.header('Real-Time Stock Prices')
stock_symbols = ['NFLX', 'GOOGL', 'AMZN', 'MSFT','TSLA']

for symbol in stock_symbols:
    real_time_data = broker.fetch_stock_data(symbol, '1d', '1m')
    if not real_time_data.empty:
        real_time_data = broker.process_data(real_time_data)
        last_price = real_time_data['Close'].iloc[-1]
        change = last_price - real_time_data['Open'].iloc[0]
        pct_change = (change / real_time_data['Open'].iloc[0]) * 100
        st.sidebar.metric(
            label=symbol,
            value=f'{last_price:.2f} USD',
            delta=f'{change:.2f} ({pct_change:.2f}%)'
        )
