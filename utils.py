import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import yfinance as yf
from datetime import datetime,timedelta
import pytz
import ta


class WallstreetBroker:
    def fetch_stock_data(self,ticker,period,interval):
        end_date = datetime.now()
        match period:
            case '1wk':
                start_date = end_date - timedelta(days=7)
                data = yf.download(ticker,start=start_date,end=end_date,interval=interval)
            case _:
                data = yf.download(ticker,period=period,interval=interval)
        return data

    def process_data(self,data):
        if data.index.tzinfo is None:
            data.index = data.index.tz_localize('UTC')
        data.index = data.index.tz_convert('Europe/Berlin')
        data.reset_index(inplace=True)
        data.rename(columns={'Date': 'Datetime'}, inplace= True)
        return data

    def calculate_metrics(self,data):
        last_close = data['Close'].iloc[-1]
        prev_close = data['Close'].iloc[0]
        change = last_close - prev_close
        pct_change = (change / prev_close) *100
        high = data['High'].max()
        low = data['Low'].min()
        volume = data['Volume'].sum()
        return last_close, change, pct_change, high, low, volume

    def add_technical_indicators(self, data):
        data['SMA_20'] = ta.trend.sma_indicator(data['Close'], window=20)
        data['EMA_20'] = ta.trend.ema_indicator(data['Close'],window=20)
        return data

