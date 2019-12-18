============================
Enterprise Value with DCF
============================

This approach aims to evaluate a company by its ability to generate money in future.It uses two terms: Future Cash Flows (FCF) and Weighted Average Cost of Capital (WACC)

FCFs are defined as the cash created by the company’s operating activities. WACC is the risk-adjusted discount rate appropriate to the risk of the FCFs. And the value of the company is calculated as net present value of FCFs discounted at WACC.

There is one assumption to this approach is that cash flows occur approximately mid-year. In that case, the formula for the enterprise value (EV) is:


.. math::
    EV = NPV*(FCF_i, WACC)*(1+WACC)^{0.5}

There are two steps in getting FCFs:

- get historical FCFs either from cash flow statements
- project FCFs to the future assuming growth percentages


FCF from cash flow statement
----------------------------
The API provides all the data

.. code-block:: python

    from pyfinmod.financials import Financials
    from pyfinmod.ev import fcf

    parser = Financials("AAPL")
    fcf(parser.cash_flow_statement)


WACC
----

The formula is the following:

.. math::
    WACC = \frac{E}{E+D}r_e +  \frac{D}{E+D}r_d(1-T_c)

where
- E = market value of the firm’s equity
- D = market value of the firm’s debt
- Tc = firm’s corporate tax rate
- rE = firm’s cost of equity
- rD = firm’s cost of debt

There are some difficulties in calculating certain parts:

1. Firm’s cost of equity rE has two approaches to it: Gordon model and capital asset pricing model (CAPM).

- The Gordon model calculates the cost of equity based on the anticipated cash flows paid to the shareholders of the firm
- The capital asset pricing model (CAPM) uses the correlation between firm’s equity return and a broad market portfolio.

2. Cost of debt rD, the anticipated future cost of the firm’s borrowing.

- The cost of debt rD is computed dividing current net interestpayments by average net debt
- Alternatively, it can be obtained from an yield curve

Equity, E
---------

For a public company E equals its market cap:

.. code-block:: python

    from pyfinmod.financials import Financials
    parser = Financials("AAPL")
    parser.mktCap


Debt, D
-------
A sum of Long-term debt and Short-term debt

.. code-block:: python

    from pyfinmod.financials import Financials
    from pyfinmod.wacc import total_debt
    parser = Financials("AAPL")
    total_debt(parser.balance_sheet_statement)


Tax Rate
--------

The Income tax expense and Income before taxes can be found in the income statement. The tax rate is equal to the quotient of the two:

.. code-block:: python

    from pyfinmod.financials import Financials
    from pyfinmod.wacc import tax_rate

    parser = Financials("AAPL")
    tax_rate(parser.income_statement)



Cost of Debt
------------

I’ll cover basic calculation which uses interest paid value from the income statement and debt taken from the balance sheet

.. code-block:: python

    from pyfinmod.financials import Financials
    from pyfinmod.wacc import cost_of_debt
    parser = Financials("AAPL")
    cost_of_debt(parser.balance_sheet_statement, parser.income_statement)



Cost of equity
--------------

The most widely used approach is the CAMP model. The classic CAPM formula uses a security market line (SML) equation that ignores taxes:

.. math::
    r_e = r_f + \beta[E(r_m) - r_f]


rF equal to the risk-free interest rate in the economy (for example, the yield on Treasury bills)
E(rM) equal to the historic average of the market return, defined as the average return of a broad-based market portfolio


The beta value can be easily accessed from the finance summary. So the cost of equity can be calculated as follows



.. code-block:: python

    from pyfinmod.financials import Financials
    from pyfinmod.wacc import cost_of_equity
    parser = Financials("AAPL")
    cost_of_equity(parser.beta, risk_free_interest_rate = 0.02, market_return = 0.08)


Calculate WACC
--------------

.. code-block:: python

    from pyfinmod.financials import Financials
    parser = Financials("AAPL")
    from pyfinmod.wacc import wacc
    aapl_wacc = wacc(parser.mktCap,
                     parser.balance_sheet_statement,
                     parser.income_statement,
                     parser.beta,
                     risk_free_interest_rate=0.02,
                     market_return=0.08)


DCF
---

So now we have historical free cash flows and WACC and we need to project them into the future. But to what extent? Let’s assume 2 growth factors:

- optimistic short term (year 1-5)
- pessimistic long term

Then we take the latest known FCF value and project it by incrementing with short term growth rate until year 5. The rest will be represented by terminal value - FCF at year 5 multiplied by pessimistic growth rate and discounted by WACC.

.. code-block:: python

    from pyfinmod.ev import dcf, fcf
    from pyfinmod.financials import Financials
    parser = Financials("AAPL")
    dcf(fcf(parser.cash_flow_statement), aapl_wacc, short_term_growth=0.08, long_term_growth=0.04)