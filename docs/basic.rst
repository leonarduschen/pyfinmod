============================
Basic Financial Calculations
============================

Net present value
-----------------

Present value allows to answer a simple question “should I put my money in a bank or invest”. Let’s say I have $100 and the bank gives a 12% annual interest rate. Alternatively, I can lend this money to a friend and he promises to pay $10 for 12 months. The moral aspect aside NPV gives an answer which alternative is more profitable.

The second alternative can be described as a series of cash flows:

- -$100 at month=0
- +$10 at month=1
- …
- +$10 at month=12

At each period (t) value (CFt) should be adjusted by the interest rate (t) (also called the discount rate) using formula

.. math::
    \frac{CF_t}{(1 + r)^t}

This basic concept shows that $100 now is not the same as $100 promised in a year. $100 now is $110 in a year.

To calculate the discounted value I’ll convert annual discount (interest) rate to daily and use the number of days elapsed as t. The function accepts a dataframe with a date column and a cash flow column.

.. code-block:: python

    >>> import pandas as pd
    >>> from datetime import date, timedelta
    >>> from dateutil.relativedelta import relativedelta
    >>> from pyfinmod.basic import npv
    >>> dates = [date.today() + relativedelta(months=i) for i in range(13)]
    >>> df = pd.DataFrame(data={'cash flow': [-100] + [10]*12,
                                'date': dates})
    >>> npv(df, 0.1)
    14.011086147172053



The calculated NPV of lending alternative is ~$14 which means that it is profitable. This value represents your wealth increment. Companies use NPVto calculate if it’s, for example, viable to invest in a factory that will generate cash flows in the future or it’s better to put the money elsewhere.

npv function can also operate with time-dated cash flows - that is when the cash flows are not evenly placed.


Internal rate of returns
------------------------

So I decided to lend to a friend. What is the effective interest rate for this alternative? Internal rate of returns (IRR) answers that. The solution of the following equation for r gives IRR:

.. math::
 CF_0 + \sum_{t=1}^{N} \frac{CF_t}{(1 + r)^t} = 0


Effectively we are finding interest rate when NPV is 0.

The function will accept the same dataframe as an input. I’m using scipy numerical solver to find r. The solver accepts the initial guess argument which helps to find the solution.

.. code-block:: python

    >>> from pyfinmod.basic import irr
    >>> irr(df, 0.0)
    [0.41354120272404077]



Sometimes a series of cash flows can have more than one IRR. We can play with guess to find both solutions.

.. code-block:: python

    >>> import pandas as pd
    >>> from datetime import date, timedelta
    >>> from dateutil.relativedelta import relativedelta
    >>> from pyfinmod.basic import irr
    >>> dates = [date.today() + relativedelta(years=i) for i in range(6)]
    >>> df3 = pd.DataFrame(data={'cash flow': [-145, 100, 100, 100, 100, -275],                              'date': dates})
    >>> irr(df3, 0.1), irr(df3, 0.4)
    ([0.08793680470699422], [0.26585705483081506])


Flat payment schedules
----------------------

Let’s look at the lending problems from the friend’s point of view. He knows that with the cash flow he proposed he will be paying 41% annual interest rate. He wants to lower the interest rate to say 30% and calculates a new flat payment scheme. Flat here means that he will pay a constant amount each month for a term amount of months.

First, let’s calculate the monthly payment. Function argument will be

- principal - the lending amount
- annual interest rate - agreed interest rate in a term of a year
- term - how many terms to pay
- period - unit of a term

.. code-block:: python

    >>> from pyfinmod.basic import pmt
    >>> pmt(principal=100, annual_interest_rate=0.3, term=12, period='month')
    9.57859525723352


So he will be paying ~$9.6 each month.


Now he wants to know how fast he’s re-paying the interest and the principal. For that, a loan table is used.

.. code-block:: python

    >>> from pyfinmod.basic import flat_payments
    >>> res_df = flat_payments(principal=100, annual_interest_rate=0.3, term=12, period='month')
    >>> print(tabulate(res_df, tablefmt="pipe", headers="keys"))


====  =======  =====================================  =============================  ==========  =====================
  ..    month    principal at the beginning of month    payment at the end of month    interest    return of principal
====  =======  =====================================  =============================  ==========  =====================
   0        1                              100                               9.5786    2.21045                 7.36815
   1        2                               92.6318                          9.5786    2.04758                 7.53102
   2        3                               85.1008                          9.5786    1.88111                 7.69749
   3        4                               77.4033                          9.5786    1.71096                 7.86764
   4        5                               69.5357                          9.5786    1.53705                 8.04155
   5        6                               61.4942                          9.5786    1.35929                 8.2193
   6        7                               53.2749                          9.5786    1.17761                 8.40098
   7        8                               44.8739                          9.5786    0.991912                8.58668
   8        9                               36.2872                          9.5786    0.802108                8.77649
   9       10                               27.5107                          9.5786    0.608109                8.97049
  10       11                               18.5402                          9.5786    0.409821                9.16877
  11       12                                9.37144                         9.5786    0.207151                9.37144
====  =======  =====================================  =============================  ==========  =====================

The last two columns - interest and return of principal - show how the payment is split between repaying interest and principal. At the end, principal value should be 0 (see assert in function code). It’s interesting to know how much interest is re-payed because that amount sometimes is tax deductible.

Future value
------------

Let’s imagine we put $10000 today for 10 years with an annual interest rate 10%. How much money we will have in 10 years? Using this formula with r=0.1 ant t=10 will give us $2593.74:

.. math::
    deposit * {(1 + r)^t}


A slightly more complex problem is if we want to deposit some money during these 10 years. The future value will tell how much money we’ll have in the end of the period.

.. code-block:: python

    >>> from pyfinmod.basic import fv
    >>> fv([1000 for _ in range(10)], 0.1, period='year')
    17531.16706110001

So depositing $1000 for 10 years will yield $17.5k given the interest rate is 10%.



Retirement problem
------------------

Consider the following exercise. Now I’m 31 and planning to retire at 55 (24 more years working). After retiring I’m planning to live at least 25 more years and will need, say, $50000 a year. To support my retirement I need to deposit money into a bank account with known interest rate (say 5%). What’s the minimum amount do I need to deposit each year?

This problem implies a number of cash flows: 24 terms with CF=x at each time, and 25 terms with CF=-50000. The present value of this cash flows should be 0. Solving this equation for x will give the minimum annual deposit.


.. code-block:: python

    >>> from pyfinmod.basic import retirement_problem
    >>> retirement_problem(terms_of_deposit=24,
                           withdrawal=50000,
                           terms_of_withdrawal=25,
                           annual_discount_rate=0.05)
    [15822.327630785972]



That’s a pretty cool result - I need to deposit only ~$16k yearly for 24 years to be able to withdraw $50k for 25 years later. That’s compound interest working.

Continuous compounding
----------------------

I’m using convert_ir(r, from_period='year', to_period='day') function to convert from annual interest rate to daily interest rate in some examples above.So if I have an annual rate of 20%, a quarterly rate is:

.. code-block:: python

    >>> from pyfinmod.basic import convert_ir
    >>> convert_ir(0.2, from_period='year', to_period='quater')
    0.04663513939210562



So if a bank offers a 20% annual interest rate paid quarterly the effective annual interest rate is 18.6%. So if the number of interest payments increases - for example to every millisecond - this is called continuous compounding. Let’s calculate the annual interest rate continuously compounded given initial and end amounts.

.. code-block:: python

    >>> from pyfinmod.basic import get_annual_rate_cc
    >>> df = pd.DataFrame(data={'amount': [1000, 1500], 'date': [date.today(), date.today() + relativedelta(years=1, months=9)]})
    >>> get_annual_rate_cc(df)
    0.23169434749037965