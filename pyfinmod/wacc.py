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
    Uses balance sheet to get company net debt. Works only with YahooFinanceParser
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
    return balance_sheet_dataframe.apply(_company_net_debt)
