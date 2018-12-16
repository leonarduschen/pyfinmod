from functools import partial
from datetime import date
from collections import defaultdict
from math import log

from dateutil.relativedelta import relativedelta
import pandas as pd
from scipy.optimize import fsolve

from pyfinmod.constants import (DAYS_IN_YEAR,
                                MONTH_IN_YEAR, 
                                QUATERS_IN_YEAR,
                                MONTH_IN_QUATER,
                                DAYS_IN_WEEK)


def convert_ir(r, from_period='year', to_period='day'):
    powers = {'year': {'day': 1/DAYS_IN_YEAR,
                       'week': DAYS_IN_WEEK/DAYS_IN_YEAR,
                       'month': 1/MONTH_IN_YEAR,
                       'quarter': 1/QUATERS_IN_YEAR,
                       'year': 1},
              'quarter': {'day': 1/(DAYS_IN_YEAR/QUATERS_IN_YEAR),
                          'week': 1/(DAYS_IN_YEAR/QUATERS_IN_YEAR/DAYS_IN_WEEK),
                          'month': 1/MONTH_IN_QUATER,
                          'quarter': 1,
                          'year': QUATERS_IN_YEAR},
              'month': {'day': 1/(DAYS_IN_YEAR/MONTH_IN_YEAR),
                        'week': 1/(DAYS_IN_YEAR/MONTH_IN_YEAR/DAYS_IN_WEEK),
                        'month': 1,
                        'quarter': MONTH_IN_QUATER,
                        'year': MONTH_IN_YEAR},
              'week': {'day': 1/DAYS_IN_WEEK,
                       'week': 1,
                       'month': DAYS_IN_YEAR/MONTH_IN_YEAR/DAYS_IN_WEEK,
                       'quarter': DAYS_IN_YEAR/QUATERS_IN_YEAR/DAYS_IN_WEEK,
                       'year': DAYS_IN_YEAR/DAYS_IN_WEEK},
              'day': {'day': 1,
                      'week': DAYS_IN_WEEK,
                      'month': DAYS_IN_YEAR/MONTH_IN_YEAR,
                      'quarter': DAYS_IN_YEAR/QUATERS_IN_YEAR,
                      'year': DAYS_IN_YEAR}}
    return (1 + r)**(powers[from_period][to_period]) - 1


def _calculate_discounted(cf, annual_interest_rate, days_passed):
    daily_interest_rate = convert_ir(annual_interest_rate, from_period='year', to_period='day')
    return cf / (1 + daily_interest_rate)**days_passed


def npv(dataframe, annual_discount_rate, cash_flow_column_name='cash flow', date_column_name='date'):
    date_start = dataframe[date_column_name].min()
    mapper = lambda x: _calculate_discounted(x[cash_flow_column_name],
                                             annual_discount_rate,
                                             (x[date_column_name] - date_start).days)
    return dataframe[[cash_flow_column_name, date_column_name]].apply(mapper, axis=1).sum()


def irr(dataframe, guess=0, cash_flow_column_name='cash flow', date_column_name='date'):
    f = partial(npv, dataframe,
                cash_flow_column_name=cash_flow_column_name,
                date_column_name=date_column_name)
    result = fsolve(f, guess)
    return list(result)


def pmt(principal, annual_interest_rate, term, period='year'):
    periodic_interest = convert_ir(annual_interest_rate, from_period='year', to_period=period)
    payment = (principal*periodic_interest)/(1 - (1 + periodic_interest)**(-term))
    return payment


def flat_payments(principal, annual_interest_rate, term, period='year'):
    _pmt = pmt(principal, annual_interest_rate, term, period=period)
    data = defaultdict(list)
    current_principal = principal
    principal_col_name = 'principal at the beginning of {}'.format(period)
    payment_col_name = 'payment at the end of {}'.format(period)
    interest_col_name = 'interest'
    return_principal_col_name = 'return of principal'
    periodic_interest = convert_ir(annual_interest_rate, from_period='year', to_period=period)
    for _t in range(1, term + 1):
        data[period].append(_t)
        data[principal_col_name].append(current_principal)
        data[payment_col_name] = _pmt
        current_interest = current_principal * periodic_interest
        data[interest_col_name].append(current_interest)
        current_return_of_principal = _pmt - current_interest
        data[return_principal_col_name].append(current_return_of_principal)
        current_principal -= current_return_of_principal
    assert round(current_principal) == 0
    return pd.DataFrame.from_dict(data)


def fv(deposits, annual_interest_rate, period='year'):
    periodic_interest = convert_ir(annual_interest_rate, from_period='year', to_period=period)
    future_value = 0
    number_of_deposits = len(deposits)
    for n, deposit in enumerate(deposits):
        future_value += deposit * (1 + periodic_interest)**(number_of_deposits - n)
    return future_value


def get_retirement_cf_dataframe(deposit, terms_of_deposit, withdrawal, terms_of_withdrawal, period='year'):
    cash_flows = [deposit]*terms_of_deposit + [-withdrawal]*terms_of_withdrawal
    terms = terms_of_deposit + terms_of_withdrawal
    dates = [date.today() + relativedelta(**{period + 's': i}) for i in range(terms)]
    df = pd.DataFrame(data={'cash flow': cash_flows, 'date': dates})
    return df


def retirement_problem(terms_of_deposit, withdrawal, terms_of_withdrawal, annual_discount_rate, period='year'):
    retirement_dataframe_by_deposit = partial(get_retirement_cf_dataframe,
                                              terms_of_deposit=terms_of_deposit,
                                              withdrawal=withdrawal,
                                              terms_of_withdrawal=terms_of_withdrawal,
                                              period=period)
    f = lambda deposit: npv(retirement_dataframe_by_deposit(deposit), annual_discount_rate)
    result = fsolve(f, withdrawal)
    return list(result)


def get_annual_rate_cc(dataframe, amount_column_name='amount', date_column_name='date'):
    amount_first = dataframe[amount_column_name].iloc[0]
    amount_last = dataframe[amount_column_name].iloc[-1]
    date_first = dataframe[date_column_name].iloc[0]
    date_last = dataframe[date_column_name].iloc[-1]
    delta = relativedelta(date_last, date_first)
    t = delta.years + delta.months/12 + delta.days/365
    r = log(amount_last/amount_first)/t
    return r
