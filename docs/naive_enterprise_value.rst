============================
Enterprise Value
============================

Value of the enterprise may be used to find out whether the price of company equity - a share - is worth what market offers. It’s also used in acquisitions to get the price of the company as a whole.

I’ll cover 2 methods of Enterprise Value calculations:

- using accounting book
- efficient market approach


Using an accounting book
------------------------

The idea behind this method is to rewrite the balance sheet in a way that all productive items are on the left side and financial items are on the right. Productive items include net working capital, property, intangible assets (copyright, goodwill) and other fixed assets.Net working capital is defined as accounts receivable + inventories - accounts payable - taxes payable. Liquid assets such as cash will go on the right side to net financial debt.

So on the right-hand - financial side - we will have net financial debt (all short and long term debt minus liquid cash), other liabilities such as pensions, equity.

After moving all the items both columns should be in balance - column sums are equal and represent company value.

.. code-block:: python

    from pyfinmod.financials import Financials
    from pyfinmod.ev import enterprise_value
    parser = Financials("AAPL")
    enterprise_value(parser.balance_sheet_statement)




Efficient market approach
-------------------------

If the company is publicly traded we can calculate market cap: number of shares multiplied by the share price. This is equity. It’s different from the equity in the liabilities column from the balance sheet which represents the initial amount of money invested in a business (maybe not initial if the profits were reinvested).

The efficient market approach says that we need to substitute equity from the rewritten balance sheet as in the previous approach with the one defined by the market. Here lies the explanation of the name of the approach - a market with many participants trading company’s shares who have the same information gives the most accurate evaluation of the company.

.. code-block:: python

    from pyfinmod.financials import Financials
    from pyfinmod.ev import enterprise_value_efficient_market
    parser = Financials("AAPL")
    enterprise_value_efficient_market(parser.balance_sheet_statement, parser.mktCap)