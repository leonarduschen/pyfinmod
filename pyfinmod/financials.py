from datetime import datetime
from collections import defaultdict
import requests
import pandas as pd


class ParserError(Exception):
    pass


class Financials:
    """Financial data parser

    Parameters:
    ticker : str
        Public company ticker to fetch the financial data of (e.g. 'AAPL')

    """
    base_url = "https://financialmodelingprep.com/api/v3/"
    datatypes = {
        "balance_sheet_statement": base_url + "financials/balance-sheet-statement/{}?apikey=demo",
        "cash_flow_statement": base_url + "financials/cash-flow-statement/{}?apikey=demo",
        "income_statement": base_url + "financials/income-statement/{}?apikey=demo",
        "profile": base_url + "company/profile/{}?apikey=demo"
    }

    def __init__(self, ticker):
        self.ticker = ticker
        self._balance_sheet_statement = None
        self._cash_flow_statement = None
        self._income_statement = None
        self._profile = None

    @staticmethod
    def _date_parse(date_str):
        return datetime.strptime(date_str, "%Y-%m-%d").date()

    def _fetch_json(self, datatype):
        try:
            url = self.datatypes[datatype].format(self.ticker)
            res = requests.get(url, timeout=5)
        except requests.exceptions.RequestException as e:
            raise ParserError("Failed to get data from external API {}".format(e))
        else:
            json = res.json()
            if not json:
                raise ParserError("Empty response from external API")
            return json

    def _json_to_df(self, json):
        _r = defaultdict(list)
        keys = [i for i in json[0].keys() if i != "date"]
        _r["row name"] = keys
        for row in json:
            _r[self._date_parse(row["date"])] = [
                float(v) for k, v in row.items() if k in keys
            ]

        df = pd.DataFrame.from_dict(_r)
        df = df.set_index("row name")
        return df

    def __getattr__(self, item):
        if item in self.datatypes:
            cached_value_key = "_" + item
            cached_value = getattr(self, cached_value_key, None)
            if cached_value:
                return cached_value
            else:
                json_data = self._fetch_json(item)["financials"]
                df = self._json_to_df(json_data)
                setattr(self, cached_value_key, df)
                return df
        else:
            cached_value_key = "_profile"
            cached_value = getattr(self, cached_value_key, None)
            if cached_value:
                return float(cached_value.get(item))
            else:
                json_data = self._fetch_json("profile")["profile"]
                setattr(self, cached_value_key, json_data)
                return float(json_data.get(item, 0))
