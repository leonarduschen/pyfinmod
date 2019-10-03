from collections import defaultdict
from datetime import datetime
from typing import Sequence, Dict

import pandas as pd
import requests
from bs4 import BeautifulSoup
from decorator import decorator
from envparse import env
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

CHROMEDRIVER_PATH = env('CHROMEDRIVER_PATH', cast=str, default=None)
HEADLESS = env('HEADLESS', cast=bool, default=True)


class YahooParserError(Exception):
    pass


@decorator
def with_driver(func, *args, **kwargs):
    self = args[0]
    options = Options()
    options.headless = HEADLESS
    driver = webdriver.Chrome(
        executable_path=self._chromedriver_path, options=options)
    self.driver = driver
    res = func(*args, **kwargs)
    self.driver.close()
    self.driver = None
    return res


class YahooFinanceParser:
    url_template = 'https://finance.yahoo.com/quote/{}/{}'
    available_data_type = ('balance-sheet', 'cash-flow', 'income-statement', 'summary')
    driver = None

    def __init__(self, ticker, data_type='summary', chromedriver_path: str = None, headless: bool = True):
        if not chromedriver_path and not CHROMEDRIVER_PATH:
            raise YahooParserError(
                f'Please set CHROMEDRIVER_PATH env variable or pass a chromedrive_path keyword argument.')
        self._chromedriver_path = chromedriver_path if chromedriver_path else CHROMEDRIVER_PATH
        self.ticker = ticker
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
        return int(int_str.replace(",", "")) * 1000

    @staticmethod
    def _billion_value_parse(value_str):
        return int(value_str.replace(".", "")[:-1]) * 10 ** 9

    @staticmethod
    def _float_value_parse(value_str):
        return float(value_str)

    @with_driver
    def _get_income_statement(self):
        def append_row(row):
            nonlocal df
            if isinstance(row, Dict):
                df = df.append(pd.Series(row), ignore_index=True)
            else:
                for i in row:
                    append_row(i)

        if hasattr(self, '_income_statement_df'):
            return self._income_statement_df.copy()

        self.driver.get(f'https://finance.yahoo.com/quote/{self.ticker}/financials?p={self.ticker}')
        table_header = self.driver.find_element_by_xpath(
            '//*[@id="Col1-1-Financials-Proxy"]/section/div[4]/div[1]/div[1]/div[1]/div')
        header_children = table_header.find_elements_by_css_selector("*")
        headers = self._parse_headers([i.text for i in header_children if hasattr(i, 'text') and i.text != ''][::2])

        table_rows = self.driver.find_elements_by_class_name('rw-expnded')
        df_list = [self._split_row(row.text, headers) for row in table_rows]
        df = pd.DataFrame(columns=headers)
        for i in df_list:
            append_row(i)
        df = df.replace('-', 0)
        df = df.fillna(0)
        df[df.columns[1:]] = df[df.columns[1:]].astype(str).applymap(
            lambda x: int(x.replace(',', '')) if '.' not in x else float(x))
        first_column = df.columns[0]
        df.index = df[first_column]
        df = df.drop(axis='columns', labels=[first_column, 'TTM'])
        self._income_statement_df = df
        return self._income_statement_df.copy()

    @classmethod
    def _parse_headers(cls, headers: Sequence):
        res = []
        for i in headers:
            try:
                res.append(datetime.strptime(i, '%m/%d/%Y'))
            except ValueError:
                res.append(i)
        return res

    @classmethod
    def _split_row(cls, row: str, labels: Sequence):
        split_row = row.split('\n')
        if len(split_row) == 1:
            return {labels[0]: split_row[0]}
        if len(split_row) == 2:
            res = [row.split('\n')[0]] + row.split('\n')[1].split(' ')
            return {i[0]: i[1] for i in zip(labels, res)}
        else:
            header = split_row[0]
            data_rows = [split_row[1:][i:i + 2] for i in range(0, len(split_row[1:]), 2)]
            return [cls._split_row(header, labels)] + [cls._split_row('\n'.join(i), labels) for i in data_rows]

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
        tables = soup.findAll("table")
        if not tables:
            raise YahooParserError('No data found on page for {}'.format(self.ticker))
        results = []
        for table in tables:
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

    def _extract_value(self, value_name):
        for v, d in self.parsed_html:
            if v == value_name:
                if d.endswith('B'):
                    return YahooFinanceParser._billion_value_parse(d)
                if '.' in d:
                    return YahooFinanceParser._float_value_parse(d)

    def get_dataframe(self, data_type, html=None):
        if data_type not in YahooFinanceParser.available_data_type:
            raise YahooParserError(
                'Unknown data_type. Allowed values {}'.format(YahooFinanceParser.available_data_type))
        self.data_type = data_type
        # self._get_html(html)
        # self._parse_html()
        # self._html_to_df()
        self.df = self.df.set_index('row name')
        return self.df

    def get_value(self, value_name, html=None):
        self._get_html(html)
        self._parse_html()
        value_data = self._extract_value(value_name)
        if not value_data:
            raise YahooParserError('No data found on page for {}'.format(self.ticker))
        return value_data
