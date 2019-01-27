from datetime import datetime
import pytest
from pyfinmod.yahoo_finance import YahooFinanceParser, YahooParserError


def test_int_parser():
    assert YahooFinanceParser._int_parse('-48,995,000') == -48995000000


def test_date_parser():
    assert YahooFinanceParser._date_parse('9/29/2018') == datetime(2018, 9, 29, 0, 0)


def test_get():
    with open('./raw_data/aapl_balance_sheet.txt', 'r') as f:
        html = f.read()

    parser = YahooFinanceParser('AAPL', 'balance-sheet')
    df = parser.get_dataframe(html)
    assert not df.empty


def test_wrong_ticker():
    with open('./raw_data/empty_html.txt', 'w+') as f:
        html = f.read()
    parser = YahooFinanceParser('123123123', 'balance-sheet')
    with pytest.raises(YahooParserError):
        df = parser.get_dataframe(html)
        assert not df


