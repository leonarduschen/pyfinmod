from pyfinmod.wacc import get_debt, get_tax_rate
import pandas as pd


def test_get_debt():
    df_in = pd.read_hdf('./raw_data/aapl_balance_sheet.hd5', key='aapl_balance_sheet')
    df_out = pd.read_hdf('./raw_data/aapl_debt.hd5', key='aapl_debt')
    df_res = get_debt(df_in)
    assert df_res.equals(df_out)


def test_get_tax_rate():
    df_in = pd.read_hdf('./raw_data/aapl_income_statement.hd5', key='aapl_income_statement')
    df_out = pd.read_hdf('./raw_data/aapl_tax_rate.hd5', key='aapl_tax_rate')
    df_res = get_tax_rate(df_in)
    assert df_res.equals(df_out)
