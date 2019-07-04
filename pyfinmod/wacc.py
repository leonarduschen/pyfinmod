from statistics import mean
import pandas as pd


def _company_debt(column):
    """
    Uses balance sheet to get company debt. Works only with YahooFinanceParser
    :param column: Yahoo Finance page parsed to dataframe with pyfinmod.yahoo_finance.YahooFinanceParser
    :return: series of debt values by date
    """
    long_term_debt = column['Long Term Debt']
    short_long_debt = column['Short/Current Long Term Debt']
    cash = column['Cash And Cash Equivalents']

    return long_term_debt + short_long_debt - cash


def _company_net_debt(column):
    """
    Uses balance sheet to get company net debt (How that's different from _company_debt?).
    Works only with YahooFinanceParser
    :param column: Yahoo Finance page parsed to dataframe with pyfinmod.yahoo_finance.YahooFinanceParser
    :return: series of debt values by date
    """
    long_term_debt = column['Long Term Debt']
    short_long_debt = column['Short/Current Long Term Debt']
    cash = column['Cash And Cash Equivalents']
    short_investments = column['Short Term Investments']

    return long_term_debt + short_long_debt - cash - short_investments


def _company_tax_rate(column):
    """
    Uses income statement to get company tax rate. Works only with YahooFinanceParser
    :param column: Yahoo Finance page parsed to dataframe with pyfinmod.yahoo_finance.YahooFinanceParser
    :return: series of tax rate values by date
    """
    income_before_tax = column['Income Before Tax']
    income_tax_expense = column['Income Tax Expense']
    return income_tax_expense / income_before_tax


def get_debt(balance_sheet_dataframe):
    return balance_sheet_dataframe.apply(_company_debt)


def get_tax_rate(income_statement_dataframe):
    return income_statement_dataframe.apply(_company_tax_rate)


def get_cost_of_debt(balance_sheet_dataframe, income_statement_dataframe):
    debt = balance_sheet_dataframe.apply(_company_net_debt)
    averages = [mean(pair) for pair in zip(debt[:-1], debt[1:])]
    average_debt = pd.Series(averages, index=debt.index[:-1])
    average_debt.name = 'average debt'
    interest_paid = -1 * income_statement_dataframe.loc['Interest Expense', :]
    interest_paid.name = 'interest paid'
    debt_and_interest = pd.concat([average_debt, interest_paid], axis=1)
    debt_and_interest.dropna(inplace=True)
    res = debt_and_interest.apply(lambda x: x['interest paid'] / x['average debt'], axis=1)
    return res


def get_cost_of_equity(beta, risk_free_interest_rate, market_return):
    return risk_free_interest_rate + beta * (market_return - risk_free_interest_rate)


def wacc(equity, balance_sheet, income_statement, beta, risk_free_interest_rate, market_return):
    debt = get_debt(balance_sheet)
    tax_rate = get_tax_rate(income_statement)
    rd = get_cost_of_debt(balance_sheet, income_statement)
    re = get_cost_of_equity(beta, risk_free_interest_rate, market_return)
    debt.name = 'd'
    tax_rate.name = 'tc'
    rd.name = 'rd'
    df = pd.concat([debt, tax_rate, rd], axis=1)
    df['e'] = equity
    df['re'] = re
    df.dropna(inplace=True)
    mean_wacc = df.apply(lambda x: (x['re'] * x['e'] + x['rd'] * x['d'] * (1 - x['tc'])) / (x['e'] + x['d']),
                         axis=1).mean()
    return mean_wacc
