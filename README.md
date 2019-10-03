# Financial modeling with Python and Pandas

1. [Introduction](#introduction)
2. [Basic calculations](#basic)
    1. [Net present Value](#npv)
    1. [Internal rate of returns](#irr)
    1. [Flat loan payments](#pmt)
    1. [Future value](#fv)
    1. [Continuously compounded interest rate](#icc)
3. [Yahoo Finance parser](#yahoo)
3. [Enterprise value](#ev)
    1. [Free Cash Flows](#fcf)
    1. [Weighted average cost of capital and DCF](#wacc)
3. [Blog posts](#blog)
3. [Library and references](#ref)

## Introduction <a name="introduction"></a>
**PyFinMod** is a framework implementing financial calculations in
Python using pandas library.

*Installation*:
```
pip install -e git+https://github.com/smirnov-am/pyfinmod.git#egg=pyfinmod
```

Since recent changes in Yahoo Finance website it is not possible any more to get data directly from the html source. Instead
we need to use Selenium Webdriver to render the scripted table.

You need to specify `CHROMEDRIVER_PATH` environment variable or initialize `YahooFinanceParser` with the path to ChromeDriver 
executable.

## Basic calculations <a name="basic"></a>
### Net present Value <a name="npv"></a>
```
import pandas as pd
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
dates = [date.today() + relativedelta(months=i) for i in range(13)]
df = pd.DataFrame(data={'cash flow': [-100] + [10]*12,
                        'date': dates})
annual_discount_rate = 0.1

from pyfinmod.basic import npv
npv(df, annual_discount_rate)
```

### Internal rate of returns <a name="irr"></a>
```
from pyfinmod.basic import irr
dates = [date.today() + relativedelta(years=i) for i in range(6)]
df3 = pd.DataFrame(data={'cash flow': [-145, 100, 100, 100, 100, -275],                              'date': dates})
irr(df3, guess=0.1)
```

### Payment for a loan based on constant payments and a constant interest rate <a name="pmt"></a>
```python
from pyfinmod.basic import pmt
pmt(principal=100, annual_interest_rate=0.3, term=12, period='month')
9.57859525723352
```

### Future value <a name="fv"></a>
```python
from pyfinmod.basic import fv
fv(deposits=[1000 for _ in range(10)], annual_interest_rate=0.1, period='year')
```

## Continuously compounded interest rate <a name="icc"></a>
```
df = pd.DataFrame(data={'amount': [1000, 1500], 'date': [date.today(), date.today() + relativedelta(years=1, months=9)]})
from pyfinmod.basic import get_annual_rate_cc
get_annual_rate_cc(df)
0.23169434749037965
```

## Yahoo Finance parser <a name="yahoo"></a>
Parses Yahoo finance page for the ticker and returns a dataframe for
`balance-sheet`, `cash-flow` and `income-statement`:

```python
from pyfinmod.yahoo_finance import YahooFinanceParser

parser = YahooFinanceParser('AAPL')
parser.get_dataframe('balance-sheet')
```

Individual values from summary page:
```
parser = YahooFinanceParser('AAPL')
parser.get_value('Market Cap')
```

## Enterprise value <a name="ev"></a>
### Free Cash Flows <a name="fcf"></a>
Get free cash flows using accounting book:
```
from pyfinmod.yahoo_finance import YahooFinanceParser
from pyfinmod.ev import get_enterprise_value

parser = YahooFinanceParser('AAPL')
df = parser.get_dataframe('balance-sheet')
get_enterprise_value(df)
```

Сash flows from cash flow statement:
```
from pyfinmod.ev import get_fcf_from_cscf
aapl_parser = YahooFinanceParser('AAPL')
balance_sheet = aapl_parser.get_dataframe('balance-sheet')
cash_flow = aapl_parser.get_dataframe('cash-flow')
get_fcf_from_cscf(income_statement, cash_flow)
```

### Weighted average cost of capital and DCF<a name="wacc"></a>
```python
from pyfinmod.yahoo_finance import YahooFinanceParser
from pyfinmod.wacc import wacc
from pyfinmod.ev import dcf

parser = YahooFinanceParser('AAPL')
e = parser.get_value('Market Cap')
beta = parser.get_value('Beta (3Y Monthly)')
income_statement = parser.get_dataframe('income-statement')
balance_sheet = parser.get_dataframe('balance-sheet')

aapl_wacc = wacc(e, balance_sheet, income_statement, beta,
                 risk_free_interest_rate=0.02,
                 market_return=0.08)
dcf(fcf, aapl_wacc, short_term_growth=0.08, long_term_growth=0.04)
```

## Blog posts  <a name="blog"></a>
1. [Basic financial calculations](https://smirnov-am.github.io/2018/12/24/basic-financial-calculations.html)
2. [Enterprise value. Free Cash Flows](https://smirnov-am.github.io/2019/02/07/company-evaluation-pt1.html)
3. [Enterprise value. WACC and DCF](https://smirnov-am.github.io/calculating-enterprise-value-with-python-and-pandas-part-1-wacc-and-dcf/)

## Library and references  <a name="ref"></a>:
[Financial Modeling by Simon Benninga](https://www.amazon.com/Financial-Modeling-Simon-Benninga/dp/0262026287)

[Python for Finance by Yves Hilpisch](https://www.amazon.com/Python-Finance-Analyze-Financial-Data/dp/1491945281)
