from pyfinmod.wacc import get_debt
import pandas as pd


def test_get_debt():
    df_in = pd.read_hdf('./raw_data/aapl_balance_sheet.hd5', key='aapl_balance_sheet')
    df_out = pd.read_hdf('./raw_data/aapl_debt.hd5', key='aapl_debt')
    df_res = get_debt(df_in)
    assert df_res.equals(df_out)
