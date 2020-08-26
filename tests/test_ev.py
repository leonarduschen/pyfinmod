import os
import pandas as pd
from pyfinmod.ev import (
    net_working_capital,
    net_debt,
    enterprise_value,
    enterprise_value_efficient_market,
    fcf,
)

raw_data_dir = os.path.join(os.path.dirname(__file__), 'raw_data')


def test_nwc():
    df_in = pd.read_hdf(os.path.join(raw_data_dir, "aapl_balance_sheet.hdf"), key="aapl_balance_sheet")
    df_res = net_working_capital(df_in)
    df_out = pd.read_hdf(os.path.join(raw_data_dir, "aapl_nwc.hdf"), key="aapl_nwc")
    assert df_res.equals(df_out)


def test_nd():
    df_in = pd.read_hdf(os.path.join(raw_data_dir, "aapl_balance_sheet.hdf"), key="aapl_balance_sheet")
    df_res = net_debt(df_in)
    df_out = pd.read_hdf(os.path.join(raw_data_dir, "aapl_nd.hdf"), key="aapl_nwc")
    assert df_res.equals(df_out)


def test_ev():
    df_in = pd.read_hdf(os.path.join(raw_data_dir, "aapl_balance_sheet.hdf"), key="aapl_balance_sheet")
    df_res = enterprise_value(df_in)
    df_out = pd.read_hdf(os.path.join(raw_data_dir, "aapl_ev.hdf"), key="aapl_ev")
    assert df_res.equals(df_out)


def test_ev_em():
    df_in = pd.read_hdf(os.path.join(raw_data_dir, "aapl_balance_sheet.hdf"), key="aapl_balance_sheet")
    ev_em = enterprise_value_efficient_market(df_in, 1086 * 10 ** 9)
    assert ev_em == 1093490000000.0


def test_get_fcf():
    df_cf = pd.read_hdf(os.path.join(raw_data_dir, "aapl_cash_flow.hdf"), key="aapl_cash_flow")
    df_res = fcf(df_cf)
    df_out = pd.read_hdf(os.path.join(raw_data_dir, "aapl_fcf.hdf"), key="aapl_fcf")
    assert df_res.equals(df_out)
