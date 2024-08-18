import yfinance as yf
import pandas as pd

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
    data["ticker"] = ticker  # Add ticker column
    return data


def get_outstanding_shares(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    return info.get("sharesOutstanding", None)


start_date = "2004-01-01"
end_date = "2024-01-01"
all_data = []

for stock in djia_stocks:
    print(f"Fetching data for {stock}")
    data = get_historical_data(stock, start_date, end_date)
    shares_outstanding = get_outstanding_shares(stock)
    if shares_outstanding:
        data["market_cap"] = data["Close"] * shares_outstanding
    else:
        data["market_cap"] = None  # Handle missing shares outstanding data
    all_data.append(data)

# Combine all data into a single DataFrame
combined_data = pd.concat(all_data)

# Save combined data to a CSV file
combined_data.to_csv("djia_historical_data_with_market_cap.csv", index=False)

# Save individual stock data to CSV files
for stock, data in zip(djia_stocks, all_data):
    data.to_csv(f"{stock}_historical_data.csv")
