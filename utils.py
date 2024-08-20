import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def split_stock(momentum_list):
    sorted_momentum_list = sorted(
        momentum_list.items(), key=lambda x: x[1], reverse=True
    )
    total_num = len(sorted_momentum_list)
    print(total_num)
    third = total_num // 3  # Assume # always divisable by 3

    top_third = sorted_momentum_list[:third]
    middle_third = sorted_momentum_list[third : 2 * third]
    bottom_third = sorted_momentum_list[2 * third :]

    return top_third, middle_third, bottom_third


def get_market_cap(tickers_list, date):
    market_caps = {}
    date = pd.to_datetime(date)
    print(f"MarketCapDate: {date}")

    # Used so we can take earlier Market Cap if not found
    for ticker in tickers_list:
        df = pd.read_csv(f"./data/{ticker}_historical_data.csv")
        df["Date"] = pd.to_datetime(df["Date"].astype(str).str[:10]).dt.tz_localize(
            None
        )
        df_filtered = df[df["Date"] <= date]
        if not df_filtered.empty:
            market_cap = df_filtered.iloc[-1]["market_cap"]
            market_caps[ticker] = market_cap
        else:
            print(f"Market cap data not available for {ticker} on or before {date}")
            market_caps[ticker] = None
    return market_caps
