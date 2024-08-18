import pandas as pd
from getData import djia_stocks
import matplotlib.pyplot as plt

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


def get_returns(tickers_list, start_date, end_date):
    portfolio_return = 0
    weights = 1 / len(tickers_list)
    for ticker in tickers_list:
        momentum = calculate_momentum(ticker, start_date, end_date)
        if momentum is not None:
            portfolio_return += weights * momentum
    return portfolio_return


def momentum_strategy(start_date, end_date):
    # Convert strings to datetime objects
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Adjust the dates
    adjusted_start_date = start_date - pd.DateOffset(months=12)
    adjusted_end_date = start_date - pd.DateOffset(months=1)

    # momentum_list = get_DJIA_momentum(
    #    start_date=adjusted_start_date.strftime("%Y-%m-%d"),
    #    end_date=adjusted_end_date.strftime("%Y-%m-%d"),
    # )

    momentum_list = get_DJIA_momentum(start_date="2004-01-02", end_date="2004-12-02")
    top_third, middle_third, bottom_third = split_stock(momentum_list)

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

        monthly_return_top = get_returns(top_tickers, start_month, end_month)
        monthly_return_middle = get_returns(middle_tickers, start_month, end_month)
        monthly_return_bottom = get_returns(bottom_tickers, start_month, end_month)

        strategy_returns_top.append(monthly_return_top)
        strategy_returns_middle.append(monthly_return_middle)
        strategy_returns_bottom.append(monthly_return_bottom)

    return (
        pd.Series(strategy_returns_top, index=months[1:]),
        pd.Series(strategy_returns_middle, index=months[1:]),
        pd.Series(strategy_returns_bottom, index=months[1:]),
    )


# Run the strategy for the period
start_date = "2005-01-04"
end_date = "2006-01-03"
strategy_returns_top, strategy_returns_middle, strategy_returns_bottom = (
    momentum_strategy(start_date, end_date)
)

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

# Calculate performance metrics
sharpe_ratio_top = strategy_returns_top.mean() / strategy_returns_top.std() * (12**0.5)
sharpe_ratio_middle = (
    strategy_returns_middle.mean() / strategy_returns_middle.std() * (12**0.5)
)
sharpe_ratio_bottom = (
    strategy_returns_bottom.mean() / strategy_returns_bottom.std() * (12**0.5)
)

print(f"Sharpe Ratio (Top Third): {sharpe_ratio_top:.2f}")
print(f"Sharpe Ratio (Middle Third): {sharpe_ratio_middle:.2f}")
print(f"Sharpe Ratio (Bottom Third): {sharpe_ratio_bottom:.2f}")
