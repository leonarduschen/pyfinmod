from datetime import datetime
from collections import defaultdict
import requests
from bs4 import BeautifulSoup
import pandas as pd


class YahooParserError(Exception):
    pass


class YahooFinanceParser:
    url_template = 'https://finance.yahoo.com/quote/{}/{}'
    available_data_type = ('balance-sheet', 'cash-flow', 'income-statement')

    def __init__(self, ticker, data_type):
        self.ticker = ticker
        if data_type not in YahooFinanceParser.available_data_type:
            raise YahooParserError('Unknown data_type. Allowed values {}'.format(YahooFinanceParser.available_data_type))
        self.data_type = data_type
        self.html = None
        self.parsed_html = None
        self.df = None

    @staticmethod
    def _date_parse(date_str):
        return datetime.strptime(date_str, '%m/%d/%Y')

    @staticmethod
    def _int_parse(int_str):
        if int_str == '-':
            return 0
        return int(int_str.replace(",", ""))*1000

    def _get_html(self, html=None):
        if html:
            self.html = html
        else:
            try:
                data_type = self.data_type if self.data_type != 'income-statement' else 'financials'
                res = requests.get(YahooFinanceParser.url_template.format(self.ticker, data_type),
                                   timeout=5)
            except requests.exceptions.RequestException as e:
                raise YahooParserError('Failed to get data from Yahoo Finance {}'.format(e))
            self.html = res.content

    def _parse_html(self):
        soup = BeautifulSoup(self.html, 'html.parser')
        if not soup:
            raise YahooParserError('No HTML found for {}'.format(self.ticker))
        table = soup.table
        if not table:
            raise YahooParserError('No data found on page for {}'.format(self.ticker))
        results = []
        for row in table('tr'):
            aux = row.findAll('td')
            results.append([cell.string for cell in aux])
        self.parsed_html = results

    def _html_to_df(self):
        _r = defaultdict(list)
        dates = []
        date_row_name = 'Period Ending' if self.data_type != 'income-statement' else 'Revenue'
        for row in self.parsed_html:
            if row[0] == date_row_name:
                dates = [YahooFinanceParser._date_parse(i) for i in row[1:]]
                for i in dates:
                    _r[i] = []
            elif len(row) == len(dates) + 1:
                values = [YahooFinanceParser._int_parse(i) for i in row[1:]]
                _r['row name'].append(row[0])
                for n, i in enumerate(dates):
                    _r[i].append(values[n])

        df = pd.DataFrame.from_dict(_r)
        self.df = df

    def get_dataframe(self, html=None):
        self._get_html(html)
        self._parse_html()
        self._html_to_df()
        self.df = self.df.set_index('row name')
        return self.df
