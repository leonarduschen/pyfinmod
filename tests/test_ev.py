import pandas as pd
from pyfinmod.ev import (get_net_working_capital,
                         get_enterprise_value,
                         get_enterprise_value_efficient_market,
                         get_fcf_from_cscf)


def test_nwc():
    df_in = pd.read_hdf('./raw_data/aapl_balance_sheet.hd5', key='aapl_balance_sheet')
    df_out = pd.read_hdf('./raw_data/aapl_nwc.hd5', key='aapl_nwc')
    df_res = get_net_working_capital(df_in)
    assert df_res.equals(df_out)


def test_ev():
    df_in = pd.read_hdf('./raw_data/aapl_balance_sheet.hd5', key='aapl_balance_sheet')
    df_out = pd.read_hdf('./raw_data/aapl_ev.hd5', key='aapl_ev')
    df_res = get_enterprise_value(df_in)
    assert df_res.equals(df_out)


def test_ev_em():
    df_in = pd.read_hdf('./raw_data/aapl_balance_sheet.hd5', key='aapl_balance_sheet')
    df_out = pd.read_hdf('./raw_data/aapl_ev.hd5', key='aapl_ev')
    df_res = get_enterprise_value_efficient_market(df_in, 1086*10**9)
    assert not df_res.empty
    # assert df_res.equals(df_out)


def test_get_fcf():
    df_is = pd.read_hdf('./raw_data/aapl_income_statement.hd5', key='aapl_income_statement')
    df_cf = pd.read_hdf('./raw_data/aapl_cash_flow.hd5', key='aapl_cash_flow')
    res = get_fcf_from_cscf(df_is, df_cf)
    res.to_hdf('./raw_data/aapl_fcf_cscf.hd5', key='aapl_fcf_cscf')

