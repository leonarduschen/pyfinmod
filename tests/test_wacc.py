import os
import pandas as pd
from pyfinmod.wacc import total_debt, tax_rate, cost_of_debt, wacc


raw_data_dir = os.path.join(os.path.dirname(__file__), 'raw_data')


def test_get_debt():
    df_in = pd.read_hdf(os.path.join(raw_data_dir, "aapl_balance_sheet.hdf"), key="aapl_balance_sheet")

    df_res = total_debt(df_in)
    df_out = pd.read_hdf(os.path.join(raw_data_dir, "aapl_debt.hdf"), key="aapl_debt")
    assert df_res.equals(df_out)


def test_get_tax_rate():
    df_in = pd.read_hdf(os.path.join(raw_data_dir, "aapl_income_statement.hdf"), key="aapl_income_statement")
    df_res = tax_rate(df_in)
    df_out = pd.read_hdf(os.path.join(raw_data_dir, "aapl_tax_rate.hdf"), key="aapl_tax_rate")
    assert df_res.equals(df_out)


def test_cost_of_debt():
    balance_sheet = pd.read_hdf(os.path.join(raw_data_dir, "aapl_balance_sheet.hdf"), key="aapl_balance_sheet"
                                )
    income_statement = pd.read_hdf(os.path.join(raw_data_dir, "aapl_income_statement.hdf"), key="aapl_income_statement"
                                   )
    df_res = cost_of_debt(balance_sheet, income_statement)
    df_out = pd.read_hdf(os.path.join(raw_data_dir, "aapl_cost_of_debt.hdf"), key="aapl_cost_of_debt")
    assert df_res.sort_index().equals(df_out.sort_index())


def test_wacc():
    balance_sheet = pd.read_hdf(os.path.join(raw_data_dir, "aapl_balance_sheet.hdf"), key="aapl_balance_sheet")
    income_statement = pd.read_hdf(os.path.join(raw_data_dir, "aapl_income_statement.hdf"), key="aapl_income_statement")
    res_wacc = wacc(1230468047640.00, balance_sheet, income_statement, 1.139593, 0.02, 0.08)
    assert res_wacc == 0.08476104586043534
