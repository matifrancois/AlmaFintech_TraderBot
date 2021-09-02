"""*****************************************************************
  @file     RatesCalculator.py
  @brief    This file calculates the implicit rates, the taker rates
            and offered rates
  @author   Matias Francois
#********************************************************************"""

# --------------------------------------------------------------------
#                           Libraries
# --------------------------------------------------------------------

import copy
from config.language import language as LG


# --------------------------------------------------------------------
#                     RatesCalculator class
# --------------------------------------------------------------------

class RatesCalculator:
    """
    This class manages the rate calculations, both for the offered rates and the taker rates

    :param bid_px: Bid Price
    :param offer_px: Offered Price
    :param spot_price: Spot price from yfinance
    :param days_to_end: Days to maturity date
    :param sel_lg: Selected Language
    :param debugging: Selected Mode
    """
    def __init__(self, bid_px, offer_px, spot_price, days_to_end, sel_lg, debugging):
        self.bid_px = bid_px
        self.offer_px = offer_px
        self.spot_price = spot_price
        self.days_to_end = days_to_end
        self._taker_rate = self._calculate_taker_rate()
        self._offered_rate = self._calculate_offered_rate()
        self.sel_lg = sel_lg
        self.debugging = debugging

        # Mode
        if self.debugging == "verbose" or self.debugging == "debugging":
            print(LG[sel_lg]["Bid price: "] + str(bid_px))
            print(LG[sel_lg]["Offer price: "] + str(offer_px))
            print(LG[sel_lg]["Spot price: "] + str(spot_price))

    def _calculate_taker_rate(self):
        """
        Calculates the taker rate
        :return: if there are days left to maturity date, return taker rate else -infinite
        """
        if self.days_to_end > 0:
            return (self.bid_px / self.spot_price - 1) * 365 / self.days_to_end * 100
        else:
            return float("-inf")

    def _calculate_offered_rate(self):
        """
        Calculates the offered rate
        :return: if there are days left to maturity date, return offered rate else infinity
        """
        if self.days_to_end > 0:
            return (self.offer_px / self.spot_price - 1) * 365 / self.days_to_end * 100
        else:
            return float("inf")

    def get_taker_rate(self):
        """
        getter that returns the taker rate
        """
        return copy.deepcopy(self._taker_rate)

    def get_offered_rate(self):
        """
        getter that returns the offered rate
        """
        return copy.deepcopy(self._offered_rate)
