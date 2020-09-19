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
        """Parse dates and then convert from datetime.datetime to datetime.date

        """
        return datetime.strptime(date_str, "%Y-%m-%d").date()

    @staticmethod
    def _json_to_df(json):
        """Convert JSON to pd.DataFrame

        To be used for balance_sheet_statement, cash_flow_statement, and income_statement only

        """
        _r = defaultdict(list)
        keys = [i for i in json[0].keys() if i != "date"]
        _r["Items"] = keys
        for row in json:
            _r[Financials._date_parse(row["date"])] = [
                float(v) for k, v in row.items() if k in keys
            ]

        df = pd.DataFrame.from_dict(_r)
        df = df.set_index("Items")
        return df

    def _fetch_json(self, datatype):
        """Fetch the requested datatype from the corresponding URL provided in self.datatype class variable

        """
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

    def __getattr__(self, name):
        """Return financial data stored as attribute


        If balance sheet, cash flow statement, or income statement is requested then return a pd.DataFrame.
        If profile is requested then return a dictionary (JSON format).
        Otherwise, attempt to search self.profile for the requested data and return the corresponding value if found.

        """
        if name in ["balance_sheet_statement", "cash_flow_statement", "income_statement"]:
            cached_value = getattr(self, "_" + name, None)
            if cached_value is not None:
                return cached_value
            else:
                json_data = self._fetch_json(name)["financials"]
                df = self._json_to_df(json_data)
                setattr(self, "_" + name, df)
                return df
        elif name in ["profile"]:
            cached_value = getattr(self, "_" + name, None)
            if cached_value is not None:
                return cached_value
            else:
                json_data = self._fetch_json(name)["profile"]
                setattr(self, "_" + name, json_data)
                return json_data
        else:
            json_data = self.profile
            return float(json_data.get(name, 0))
