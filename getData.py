import yfinance as yf
import pandas as pd
import os

djia_stocks = [
    "AMZN",
    "AXP",
    "AMGN",
    "AAPL",
    "BA",
    "CAT",
    "CSCO",
    "CVX",
    "GS",
    "HD",
    "HON",
    "IBM",
    "INTC",
    "JNJ",
    "KO",
    "JPM",
    "MCD",
    "MMM",
    "MRK",
    "MSFT",
    "NKE",
    "PG",
    "TRV",
    "UNH",
    "CRM",
    "VZ",
    "V",
    "WMT",
    "DIS",
    "DOW",
]


def get_historical_data(ticker, start_date, end_date):
    stock = yf.Ticker(ticker)
    data = stock.history(start=start_date, end=end_date)

    # Getting returns
    data["Daily Return"] = data["Close"].pct_change()
    return data


def get_outstanding_shares(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    return info.get("sharesOutstanding", None)


start_date = "2004-01-01"
end_date = "2024-01-01"
all_data = {}

if False:
    for stock in djia_stocks:
        print(f"Fetching data for {stock}")
        data = get_historical_data(stock, start_date, end_date)
        shares_outstanding = get_outstanding_shares(stock)
        if shares_outstanding:
            data["shares_outstanding"] = shares_outstanding
            data["market_cap"] = data["Close"] * shares_outstanding
        else:
            data["shares_outstanding"] = None
            data["market_cap"] = None
        all_data[stock] = data

    for stock, data in all_data.items():
        data.to_csv(f"{stock}_historical_data.csv")
