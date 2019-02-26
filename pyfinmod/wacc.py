def _company_debt(column):
    """
    Uses balance sheet to get company debt. Works only with YahooFinanceParser
    :param column: Yahoo Finance page parsed to dataframe with pyfinmod.yahoo_finance.YahooFinanceParser
    :return: series of debt values by date
    """
    long_term_debt = column['Long Term Debt']
    shor_long_debt = column['Short/Current Long Term Debt']
    cash = column['Cash And Cash Equivalents']
    return long_term_debt + shor_long_debt - cash


def get_debt(dataframe):
    return dataframe.apply(_company_debt)