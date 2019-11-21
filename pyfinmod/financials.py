from datetime import datetime
from collections import defaultdict
import requests
import pandas as pd


class ParserError(Exception):
    pass


class Financials:
    url_financials = "https://financialmodelingprep.com/api/v3/financials/{}/{}"
    url_profile = "https://financialmodelingprep.com/api/v3/company/profile/{}"
    available_data_type = (
        "balance_sheet_statement",
        "cash_flow_statement",
        "income_statement",
    )

    def __init__(self, ticker):
        self.ticker = ticker
        self._balance_sheet_statement = None
        self._cash_flow_statement = None
        self._income_statement = None
        self._profile = None

    @staticmethod
    def _date_parse(date_str):
        return datetime.strptime(date_str, "%Y-%m-%d")

    def _fetch_json(self, data_type):
        try:
            if data_type != "profile":
                url = self.url_financials.format(
                    data_type.replace("_", "-"), self.ticker
                )
            else:
                url = self.url_profile.format(self.ticker)
            res = requests.get(url, timeout=5)
        except requests.exceptions.RequestException as e:
            raise ParserError("Failed to get data from external api {}".format(e))
        json = res.json()
        print(json)
        if not json:
            raise ParserError("empty response from api")
        return json

    def __getattr__(self, item):
        if item in self.available_data_type:
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
                return cached_value.get(item)
            else:
                json_data = self._fetch_json("profile")["profile"]
                setattr(self, cached_value_key, json_data)
                return float(json_data.get(item, 0))

    def _json_to_df(self, json):
        _r = defaultdict(list)
        keys = [i for i in json[0].keys() if i != "date"]
        _r["row name"] = keys
        for row in json:
            _r[self._date_parse(row["date"])] = [
                float(v) for k, v in row.items() if k in keys
            ]

        df = pd.DataFrame.from_dict(_r)
        return df


# if __name__ == "__main__":
# parser = Financials("AAPL")
# print(parser.balance_sheet_statement)
# print(parser.cash_flow_statement)
# print(parser.income_statement)
# print(parser.mktCap)
