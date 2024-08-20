import pandas as pd
from getData import djia_stocks
import matplotlib.pyplot as plt
import numpy as np
import utils

momentum_list = {}


def calculate_momentum(ticker, start_date, end_date):
    df = pd.read_csv(f"./data/{ticker}_historical_data.csv")

    df["Date"] = pd.to_datetime(df["Date"].astype(str).str[:10]).dt.tz_localize(None)

    formatted_start = pd.to_datetime(start_date).tz_localize(None)
    formatted_end = pd.to_datetime(end_date).tz_localize(None)

    if formatted_start in df["Date"].values and formatted_end in df["Date"].values:
        start_row = df[df["Date"] == formatted_start]
        end_row = df[df["Date"] == formatted_end]

        start_price = start_row["Close"].values[0]
        end_price = end_row["Close"].values[0]

        momentum = end_price / start_price - 1
        return momentum

    else:
        print(formatted_start)
        print(formatted_end)
        print("******************************")
        print(f"{ticker}: Not a valid start or end!")
        print("******************************")
        return None


def get_DJIA_momentum(start_date, end_date):
    for ticker in djia_stocks:
        print(start_date)
        print(end_date)
        momentum = calculate_momentum(ticker, start_date, end_date)
        if momentum is not None:
            momentum_list[ticker] = momentum

    print("Momentum List: ", momentum_list)
    return momentum_list


# REQUIRED: tickers_list must be sorted by momentum (highest --> lowest)
def get_returns(tickers_list, start_date, end_date, weights, market_cap_dict):
    portfolio_return = 0
    size = len(tickers_list)

    if weights == "equal":
        weight_coef = 1 / size
        for ticker in tickers_list:
            momentum = calculate_momentum(ticker, start_date, end_date)
            if momentum is not None:
                portfolio_return += weight_coef * momentum
    elif weights == "rank":
        ranks_dict = {
            ticker: rank for rank, ticker in enumerate(reversed(tickers_list), 1)
        }
        total_ranks = sum(range(1, len(tickers_list) + 1))
        for ticker in tickers_list:
            momentum = calculate_momentum(ticker, start_date, end_date)
            weight_coef = ranks_dict[ticker] / total_ranks
            if momentum is not None:
                # print(f"{ticker}:{weight_coef}")
                portfolio_return += weight_coef * momentum
    elif weights == "value":
        if market_cap_dict is None:
            raise ValueError("Market caps are required for value weighting.")
        total_market_cap = sum(market_cap_dict[ticker] for ticker in tickers_list)
        for ticker in tickers_list:
            momentum = calculate_momentum(ticker, start_date, end_date)
            if momentum is not None:
                allocation = market_cap_dict[ticker] / total_market_cap
                portfolio_return += allocation * momentum

    return portfolio_return


def momentum_strategy(start_date, end_date, lookback, portfolio_weight):
    # Convert strings to datetime objects
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    if lookback == "3-month":
        adjusted_start_date = start_date - pd.DateOffset(days=91)
        adjusted_end_date = start_date
    elif lookback == "6-month":
        adjusted_start_date = start_date - pd.DateOffset(days=182)
        adjusted_end_date = start_date
    elif lookback == "9-month":
        adjusted_start_date = start_date - pd.DateOffset(days=273)
        adjusted_end_date = start_date
    elif lookback == "11-month-skip-1-month":
        adjusted_start_date = start_date - pd.DateOffset(days=364)
        adjusted_end_date = start_date - pd.DateOffset(days=28)

    # momentum_list = get_DJIA_momentum(
    #    start_date=adjusted_start_date.strftime("%Y-%m-%d"),
    #    end_date=adjusted_end_date.strftime("%Y-%m-%d"),
    # )

    momentum_list = get_DJIA_momentum(
        start_date=adjusted_start_date, end_date=adjusted_end_date
    )
    top_third, middle_third, bottom_third = utils.split_stock(momentum_list)

    print(f"Top Third:{top_third}")

    top_tickers = [ticker for ticker, _ in top_third]
    middle_tickers = [ticker for ticker, _ in middle_third]
    bottom_tickers = [ticker for ticker, _ in bottom_third]

    months = pd.date_range(start=start_date, end=end_date, freq="28D")

    strategy_returns_top = []
    strategy_returns_middle = []
    strategy_returns_bottom = []

    for i in range(1, len(months)):
        start_month = months[i - 1]
        end_month = months[i]

        print(start_month)
        print(end_month)

        market_cap_top = utils.get_market_cap(top_tickers, start_month)
        market_cap_middle = utils.get_market_cap(middle_tickers, start_month)
        market_cap_bottom = utils.get_market_cap(bottom_tickers, start_month)

        print(f"MarketCapTop:{market_cap_top}")

        monthly_return_top = get_returns(
            top_tickers,
            start_month,
            end_month,
            portfolio_weight,
            market_cap_dict=market_cap_top,
        )
        monthly_return_middle = get_returns(
            middle_tickers,
            start_month,
            end_month,
            portfolio_weight,
            market_cap_dict=market_cap_middle,
        )
        monthly_return_bottom = get_returns(
            bottom_tickers,
            start_month,
            end_month,
            portfolio_weight,
            market_cap_dict=market_cap_bottom,
        )

        strategy_returns_top.append(monthly_return_top)
        strategy_returns_middle.append(monthly_return_middle)
        strategy_returns_bottom.append(monthly_return_bottom)

    return (
        pd.Series(strategy_returns_top, index=months[1:]),
        pd.Series(strategy_returns_middle, index=months[1:]),
        pd.Series(strategy_returns_bottom, index=months[1:]),
    )


def performance_statistics(return_stream, title_name):
    investment = 1000 * (1 + return_stream).cumprod()
    cumulative_returns = (1 + return_stream).cumprod()
    plt.figure(figsize=(10, 6))
    investment.plot(title=f"({title_name}): $1000 Investment Growth")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Returns")
    plt.show()

    # Mean return annualized
    mean_return_annualized = return_stream.mean() * 12

    # Volatility
    volatility = return_stream.std() * np.sqrt(12)

    # Sharpe Ratio (INFO: Look into if the *12 from mean_return_annualized should remain)
    sharpe_ratio = mean_return_annualized / volatility

    hit_rate = (return_stream > 0).sum() / len(return_stream)

    drawdown = cumulative_returns / cumulative_returns.cummax() - 1
    max_drawdown = drawdown.min()

    # Calculate highest monthly gain (annualized)
    highest_monthly_gain = return_stream.max() * 12

    # Calculate worst monthly loss (annualized)
    worst_monthly_loss = return_stream.min() * 12

    # Output the statistics
    stats = {
        "Mean Return (Annualized)": mean_return_annualized,
        "Volatility (Annualized)": volatility,
        "Sharpe Ratio": sharpe_ratio,
        "Hit Rate": hit_rate,
        "Max Drawdown": max_drawdown,
        "Highest Monthly Gain (Annualized)": highest_monthly_gain,
        "Worst Monthly Loss (Annualized)": worst_monthly_loss,
    }

    for key, value in stats.items():
        print(f"{key}: {value:.2f}")

    return stats


# Run the strategy for the period
start_date = "2005-01-04"
end_date = "2006-01-03"
strategy_returns_top, strategy_returns_middle, strategy_returns_bottom = (
    momentum_strategy(start_date, end_date, "11-month-skip-1-month", "equal")
)

# Evaluate the performance for each segment
print("\nPerformance Statistics (Top Third):")
stats_top = performance_statistics(strategy_returns_top, "Top Third")

print("\nPerformance Statistics (Middle Third):")
stats_middle = performance_statistics(strategy_returns_middle, "Middle Third")

print("\nPerformance Statistics (Bottom Third):")
stats_bottom = performance_statistics(strategy_returns_bottom, "Bottom Third")

# Evaluate the performance
cumulative_returns_top = (1 + strategy_returns_top).cumprod()
cumulative_returns_middle = (1 + strategy_returns_middle).cumprod()
cumulative_returns_bottom = (1 + strategy_returns_bottom).cumprod()

# Plot cumulative returns

plt.figure(figsize=(12, 8))
cumulative_returns_top.plot(label="Top Third")
cumulative_returns_middle.plot(label="Middle Third")
cumulative_returns_bottom.plot(label="Bottom Third")
plt.title("Momentum Strategy Cumulative Returns")
plt.xlabel("Date")
plt.ylabel("Cumulative Return")
plt.legend()
plt.show()
