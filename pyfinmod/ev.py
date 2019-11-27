from math import sqrt
import pandas as pd
from pyfinmod.basic import npv


def enterprise_value(balance_sheet):
    nvc = net_working_capital(balance_sheet)
    nc_assets = balance_sheet.loc["Total non-current assets"]
    other_assets = balance_sheet.loc["Other Assets"]
    return nvc + nc_assets + other_assets


def _net_working_capital(column):
    """
    Uses balance sheet to net working capital
    """
    current_assets = column["Total current assets"]
    current_liabilities = column["Total current liabilities"]
    return current_assets - current_liabilities


def net_working_capital(balance_sheet):
    return balance_sheet.apply(_net_working_capital)


def _net_debt(column):
    """
    Uses balance sheet to get company net debt
    """
    long_term_debt = column["Long-term debt"]
    short_long_debt = column["Short-term debt"]
    cash = column["Cash and cash equivalents"]
    short_investments = column["Short-term investments"]

    return long_term_debt + short_long_debt - cash - short_investments


def net_debt(balance_sheet):
    return balance_sheet.apply(_net_debt)


def enterprise_value_efficient_market(balance_sheet, market_cap):
    nd = net_debt(balance_sheet)
    most_recent_net_debt = nd.loc[max(nd.index)]
    return market_cap + most_recent_net_debt


def fcf(cash_flow):
    return cash_flow.loc["Free Cash Flow"]


def dcf(fcfs, wacc, short_term_growth, long_term_growth):
    latest_fcf_date = fcfs.index.max()
    dates = pd.date_range(latest_fcf_date, periods=6, freq="365D")[1:]
    future_cash_flows = [fcfs[latest_fcf_date]]
    for i in range(5): # 5?
        next_year_fcf = future_cash_flows[-1] * (1 + short_term_growth)
        future_cash_flows.append(next_year_fcf)
    future_cash_flows = future_cash_flows[1:]
    df = pd.DataFrame(data={"fcf": future_cash_flows, "date": dates})
    # df.set_index('date', inplace=True)
    df["terminal value"] = 0
    last_index = df.index[-1]
    last_short_term_fcf = df.at[last_index, "fcf"]
    df.at[last_index, "terminal value"] = (
        last_short_term_fcf * (1 + long_term_growth) / (wacc - long_term_growth)
    )
    df["cash flow"] = df[["fcf", "terminal value"]].apply(sum, axis=1)
    return npv(df, wacc) * sqrt((1 + wacc))
