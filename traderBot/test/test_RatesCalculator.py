"""****************************************************************
  @file     test_RatesCalculator.py
  @brief    This file is a test for the RatesCalculator function
  @author   Matias Francois
#*******************************************************************"""

# --------------------------------------------------------------------
#                           Libraries
# --------------------------------------------------------------------

from src.RatesCalculator import RatesCalculator
import pytest

# --------------------------------------------------------------------
#                       test_get_taker_rate
# --------------------------------------------------------------------

"""
How to initialize parameter values: to add a new value remember the parameters in the RatesCalculator class:

:param bid_px: Bid Price
:param offer_px: Offered Price
:param spot_price: Spot price from yfinance
:param days_to_end: Days to maturity date
:param sel_lg: Selected Language
:param debugging: Selected Mode

You must add the minimum acceptable value and the maximum acceptable result value.
"""


@pytest.mark.parametrize('RC, min_rate, max_rate',
                         [
                             (RatesCalculator(130, 120, 120, 240, "English", "verbose"), 12.5, 12.7),
                             (RatesCalculator(89.5, 90.5, 90, 30, "English", "debugging"), -6.8, -6.6),
                             (RatesCalculator(178.25, 179.95, 180.4499969482422, 60, "Spanish", "verbose"), -7.42, -7.41)
                         ])
def test_get_taker_rate(RC, min_rate, max_rate):
    assert (min_rate < RC.get_taker_rate() < max_rate)


# --------------------------------------------------------------------
#                       test_get_offered_rate
# --------------------------------------------------------------------

@pytest.mark.parametrize('RC, min_rate, max_rate',
                         [
                             (RatesCalculator(130, 120, 120, 240, "English", "verbose"), -0.1, 0.1),
                             (RatesCalculator(89.5, 90.5, 90, 30, "English", "debugging"), 6.6, 6.8),
                             (RatesCalculator(178.25, 179.95, 180.4499969482422, 60, "Spanish", "verbose"), -1.7, -1.6)
                         ])
def test_get_offered_rate(RC, min_rate, max_rate):
    assert (min_rate < RC.get_offered_rate() < max_rate)
