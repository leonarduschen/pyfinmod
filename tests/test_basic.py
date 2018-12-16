import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
from pyfinmod.basic import convert_ir, npv, irr, pmt, flat_payments


def test_convert_ir():
    assert round(convert_ir(0.1), 6) == 0.000261
    assert round(convert_ir(0.1, 'year', 'quarter'), 6) == 0.024114


def test_npv():
    df = pd.DataFrame(data={'cash flow': [-100] + [10] * 12,
                            'date': [date.today() + relativedelta(months=i) for i in range(13)]})
    assert round(npv(df, 0.1), 6) == 14.011086


def test_irr():
    df3 = pd.DataFrame(data={'cash flow': [-145, 100, 100, 100, 100, -275],
                             'date': [date.today() + relativedelta(years=i) for i in range(6)]})
    assert round(irr(df3, 0.1)[0], 6) == 0.087937
    assert round(irr(df3, 0.4)[0], 6) == 0.265857


def test_pmt():
    assert round(pmt(10000, 0.07, 6, period='year'), 6) == 2097.957998


def test_flat_payments():
    df = flat_payments(10000, 0.1, 2, period='year')
    df_test = pd.DataFrame.from_dict({'year': [1, 2],
                                      'principal at the beginning of year': [10000, 5238.095238095237],
                                      'payment at the end of year': 5761.904761904764,
                                      'interest': [1000.0000000000009, 523.8095238095241],
                                      'return of principal': [4761.904761904763, 5238.09523809524]})
    assert df.equals(df_test)

