import re
from datetime import datetime
from typing import Sequence, Dict

import pandas as pd
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
    data_type = None

    def __init__(self, ticker, data_type='summary', *, chromedriver_path: str = None, **kwargs):
        if data_type not in YahooFinanceParser.available_data_type:
            raise YahooParserError(
                'Unknown data_type. Allowed values {}'.format(YahooFinanceParser.available_data_type))

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
    def get_table(self, url: str, *, table_xpath: str, table_header_xpath: str) -> pd.DataFrame:
        def append_row(row):
            nonlocal df
            if isinstance(row, Dict):
                df = df.append(pd.Series(row), ignore_index=True)
            else:
                for i in row:
                    append_row(i)

        self.driver.get(url)
        table = self.driver.find_element_by_xpath(table_xpath)
        table_header = table.find_element_by_xpath(table_header_xpath)
        header_children = table_header.find_elements_by_css_selector("*")
        headers = self._parse_headers([i.text for i in header_children if hasattr(i, 'text') and i.text != ''][::2])
        table_rows = table.find_elements_by_class_name('rw-expnded')
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
        df = df.drop(axis='columns', labels=[first_column])
        return df

    def _get_balance_sheet(self):
        url = f'https://finance.yahoo.com/quote/{self.ticker}/balance-sheet?p={self.ticker}'
        table_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[4]/div[1]/div[1]'
        table_header_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[4]/div[1]/div[1]/div[1]/div'
        self.df = self.get_table(url, table_xpath=table_xpath, table_header_xpath=table_header_xpath)
        return self.df.copy()

    def _get_income_statement(self):
        url = f'https://finance.yahoo.com/quote/{self.ticker}/financials?p={self.ticker}'
        table_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[4]'
        table_header_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[4]/div[1]/div[1]/div[1]/div'
        self.df = self.get_table(url, table_xpath=table_xpath, table_header_xpath=table_header_xpath)
        return self.df.copy()

    def _get_cash_flow(self):
        url = 'https://finance.yahoo.com/quote/AAPL/cash-flow?p=AAPL'
        table_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[4]/div[1]/div[1]'
        table_header_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[4]/div[1]/div[1]/div[1]/div'
        self.df = self.get_table(url, table_xpath=table_xpath, table_header_xpath=table_header_xpath)
        return self.df.copy()

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
        pattern = re.compile(r'.+\n[\d\-]+.+')
        meaningful_rows = pattern.findall(row)
        if len(meaningful_rows) == 1:
            r = meaningful_rows[0]
            res = [r.split('\n')[0]] + r.split('\n')[1].split(' ')
            return {i[0]: i[1] for i in zip(labels, res)}
        return [cls._split_row(r, labels) for r in meaningful_rows]

    def get_dataframe(self, **kwargs):
        implemented = {
            'income-statement': self._get_income_statement,
            'balance-sheet': self._get_balance_sheet,
            'cash-flow': self._get_cash_flow
        }
        if self.data_type not in implemented:
            raise NotImplementedError(f'{self.data_type} not implemented using Selenium yet')

        return implemented[self.data_type]()
