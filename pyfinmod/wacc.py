from statistics import mean
import pandas as pd


def _company_tax_rate(column):
    """ Uses income statement to get company tax rate """
    income_before_tax = column["Earnings before Tax"]
    income_tax_expense = column["Income Tax Expense"]
    return income_tax_expense / income_before_tax


def _company_total_debt(column):
    """ Uses balance sheet to get company total debt rate """
    long_term_debt = column["Long-term debt"]
    short_long_debt = column["Short-term debt"]
    return long_term_debt + short_long_debt


def tax_rate(income_statement):
    return income_statement.apply(_company_tax_rate)


def total_debt(balance_sheet):
    return balance_sheet.apply(_company_total_debt)


def cost_of_debt(balance_sheet, income_statement):
    debt = total_debt(balance_sheet)
    averages = [mean(pair) for pair in zip(debt[:-1], debt[1:])]
    average_debt = pd.Series(averages, index=debt.index[:-1])
    average_debt.name = "average debt"
    interest_paid = -1 * income_statement.loc["Interest Expense", :]
    interest_paid.name = "interest paid"
    debt_and_interest = pd.concat([average_debt, interest_paid], axis=1)

    debt_and_interest.dropna(inplace=True)
    res = debt_and_interest.apply(
        lambda x: float(x["interest paid"]) / float(x["average debt"])
        if x["average debt"]
        else 0,
        axis=1,
    )
    return res


def cost_of_equity(beta, risk_free_interest_rate, market_return):
    return risk_free_interest_rate + beta * (market_return - risk_free_interest_rate)


def wacc(
    equity,
    balance_sheet,
    income_statement,
    beta,
    risk_free_interest_rate,
    market_return,
):
    debt = total_debt(balance_sheet)
    tax_rate_for_wacc = tax_rate(income_statement)
    rd = cost_of_debt(balance_sheet, income_statement)
    re = cost_of_equity(beta, risk_free_interest_rate, market_return)
    debt.name = "d"
    tax_rate_for_wacc.name = "tc"
    rd.name = "rd"
    df = pd.concat([debt, tax_rate_for_wacc, rd], axis=1)
    df["e"] = equity
    df["re"] = re
    df.dropna(inplace=True)
    mean_wacc = df.apply(
        lambda x: (x["re"] * x["e"] + x["rd"] * x["d"] * (1 - x["tc"]))
        / (x["e"] + x["d"]),
        axis=1,
    ).mean()
    return mean_wacc
