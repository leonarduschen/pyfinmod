from datetime import datetime
import pandas as pd
from pyfinmod.financials import Financials
import json


def test_date_parser():
    assert Financials._date_parse("2018-9-29") == datetime(2018, 9, 29, 0, 0)


def test_get_balance_sheet():
    parser = Financials("AAPL")
    with open("./raw_data/aapl_balance_sheet.json", "r") as f:
        json_data = json.load(f)

    parser._fetch_json = lambda x: {"financials": json_data}

    df = parser.balance_sheet_statement
    assert not df.empty

    df_test = pd.read_hdf("./raw_data/aapl_balance_sheet.hdf", key="aapl_balance_sheet")
    assert df.equals(df_test)


def test_get_income_statement():
    parser = Financials("AAPL")
    with open("./raw_data/aapl_income_statement.json", "r") as f:
        json_data = json.load(f)
    parser._fetch_json = lambda x: json_data

    df = parser.income_statement
    assert not df.empty

    df_test = pd.read_hdf(
        "./raw_data/aapl_income_statement.hdf", key="aapl_income_statement"
    )
    assert df.equals(df_test)


def test_get_cash_flow():
    parser = Financials("AAPL")
    with open("./raw_data/aapl_cash_flow.json", "r") as f:
        json_data = json.load(f)
    parser._fetch_json = lambda x: json_data

    df = parser.cash_flow_statement
    assert not df.empty

    df_test = pd.read_hdf("./raw_data/aapl_cash_flow.hdf", key="aapl_cash_flow")
    assert df.equals(df_test)


def test_get_market_cap():
    parser = Financials("AAPL")
    with open("./raw_data/aapl_summary.txt", "r") as f:
        json_data = json.load(f)
    parser._fetch_json = lambda x: json_data

    mktCap = parser.mktCap
    assert mktCap == float(1213843845240.0)

