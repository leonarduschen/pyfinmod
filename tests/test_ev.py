import pandas as pd
from pyfinmod.ev import get_nwc, get_ev


def test_nwc():
    df_in = pd.read_hdf('./raw_data/aapl_balance_sheet.hd5', key='aapl_balance_sheet')
    df_out = pd.read_hdf('./raw_data/aapl_nwc.hd5', key='aapl_nwc')
    df_res = get_nwc(df_in)
    assert df_res.equals(df_out)


def test_ev():
    df_in = pd.read_hdf('./raw_data/aapl_balance_sheet.hd5', key='aapl_balance_sheet')
    df_out = pd.read_hdf('./raw_data/aapl_ev.hd5', key='aapl_ev')
    df_res = get_ev(df_in)
    assert df_res.equals(df_out)
