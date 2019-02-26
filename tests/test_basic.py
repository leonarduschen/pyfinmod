from datetime import date
from pytest import approx
import pandas as pd
from dateutil.relativedelta import relativedelta
from pyfinmod.basic import convert_ir, npv, irr, pmt, flat_payments, fv, retirement_problem, get_annual_rate_cc

FLOAT_ABS = 1e-6


def test_convert_ir():
    assert convert_ir(0.1) == approx(0.000261, abs=FLOAT_ABS)
    assert convert_ir(0.1, 'year', 'quarter') == approx(0.024114, abs=FLOAT_ABS)


def test_npv():
    df = pd.DataFrame(data={'cash flow': [-100] + [10] * 12,
                            'date': [date.today() + relativedelta(months=i) for i in range(13)]})
    assert npv(df, 0.1) == approx(14.04634, abs=FLOAT_ABS)


def test_irr():
    df3 = pd.DataFrame(data={'cash flow': [-145, 100, 100, 100, 100, -275],
                             'date': [date.today() + relativedelta(years=i) for i in range(6)]})
    assert irr(df3, 0.1) == approx([0.087937], abs=FLOAT_ABS)
    assert irr(df3, 0.4) == approx([0.265857], abs=FLOAT_ABS)


def test_pmt():
    assert pmt(10000, 0.07, 6, period='year') == approx(2097.957998, abs=FLOAT_ABS)


def test_flat_payments():
    df = flat_payments(10000, 0.1, 2, period='year')
    df_test = pd.DataFrame.from_dict({'year': [1, 2],
                                      'principal at the beginning of year': [10000, 5238.095238],
                                      'payment at the end of year': 5761.904761,
                                      'interest': [1000, 523.809523],
                                      'return of principal': [4761.904761, 5238.095238]})
    assert df.values == approx(df_test.values, abs=FLOAT_ABS)


def test_fv():
    assert fv([1000 for _ in range(10)], 0.1, period='year') == approx(17531.167061, abs=FLOAT_ABS)


def test_retirement_problem():
    assert retirement_problem(24, 50000, 25, 0.05) == approx([15822.327630], abs=FLOAT_ABS)


def test_get_annual_rate_cc():
    df = pd.DataFrame(data={'amount': [1000, 1500],
                            'date': [date.today(), date.today() + relativedelta(years=1, months=9)]})
    assert get_annual_rate_cc(df) == approx(0.231694, abs=FLOAT_ABS)
