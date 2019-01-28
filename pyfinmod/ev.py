left_rows = [('Total Assets', 1),
             ('Cash And Cash Equivalents', -1),
             ('Total Current Liabilities', -1),
             ('Short/Current Long Term Debt', 1),
             ('Other Current Liabilities', 1)]

right_rows = [('Total Liabilities', 1),
              ('Total Stockholder Equity', +1),
              ('Cash And Cash Equivalents', -1),
              ('Total Current Liabilities', -1),
              ('Short/Current Long Term Debt', 1),
              ('Other Current Liabilities', 1)]


def _ev(column):
    """
    Uses balance sheet to calculate enterprise value. Works only with YahooFinanceParser
    :param column: Yahoo Finance page parsed to dataframe with pyfinmod.yahoo_finance.YahooFinanceParser
    :return: series of enterprise values by date
    """
    left_sum = sum([column[i]*sign for i, sign in left_rows])
    right_sum = sum([column[i]*sign for i, sign in right_rows])
    assert left_sum == right_sum
    return left_sum


def get_ev(dataframe):
    return dataframe.apply(_ev)


def _net_working_capital(column):
    """
    Uses balance sheet to net working capital. Works only with YahooFinanceParser
    :param column: Yahoo Finance page parsed to dataframe with pyfinmod.yahoo_finance.YahooFinanceParser
    :return: series of enterprise values by date
    """
    net_receivables = column['Net Receivables']
    inventory = column['Inventory']
    acc_payable = column['Accounts Payable']
    other_curr_liabilities = column['Other Current Liabilities']
    return net_receivables + inventory - acc_payable - other_curr_liabilities


def get_nwc(dataframe):
    return dataframe.apply(_net_working_capital)