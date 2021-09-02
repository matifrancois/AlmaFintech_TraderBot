"""*****************************************************************
  @file     Strategy.py
  @brief    This file manages the strategy to determine if there is
            an opportunity for arbitrage
  @author   Matias Francois
#********************************************************************"""

# --------------------------------------------------------------------
#                           Libraries
# --------------------------------------------------------------------

from config.language import language as LG

# --------------------------------------------------------------------
#                        Strategy class
# --------------------------------------------------------------------

class Strategy:
    """
    This class manages the arbitrage possibilities

    :param dict_ordered_by_taker: Dictionary with the maturityDate as key and array with
                                  dictionaries ordered by the taker rate inside.
    :param dict_ordered_by_offered: Dictionary with the maturityDate as key and array with
                                    dictionaries ordered by the offered rate inside.
    :param commission: Commission rate per transaction
    """

    def __init__(self, dict_ordered_by_taker, dict_ordered_by_offered, commission):
        self.dict_ordered_by_taker = dict_ordered_by_taker
        self.dict_ordered_by_offered = dict_ordered_by_offered
        self.dict_with_arbitrage_possibilities = {}
        self.is_arbitrage_possible = False
        self.commission = commission

    def arbitrage_options(self, sel_lg):
        """
        This function returns a dictionary with the arbitrage possibilities found
        """
        self.is_arbitrage_possible = False
        for key in self.dict_ordered_by_taker:
            if self.dict_ordered_by_taker[key][0]["name"] != self.dict_ordered_by_offered[key][0]["name"]:
                if self.dict_ordered_by_taker[key][0]["taker_rate"] - self.dict_ordered_by_offered[key][0]["offered_rate"] - self.commission > 0:
                    self.dict_with_arbitrage_possibilities[key] = {
                        "taker_symbol": self.dict_ordered_by_taker[key][0]["name"],
                        "taker_rate": self.dict_ordered_by_taker[key][0]["taker_rate"],
                        "offer_symbol": self.dict_ordered_by_offered[key][0]["name"],
                        "offered_rate": self.dict_ordered_by_offered[key][0]["offered_rate"]}
                    self.is_arbitrage_possible = True
            else:
                if (len(self.dict_ordered_by_offered[key]) > 1 and self.dict_ordered_by_taker[key][0]["taker_rate"] -
                        self.dict_ordered_by_offered[key][1][
                            "offered_rate"] - self.commission > 0):
                    self.dict_with_arbitrage_possibilities[key] = {
                        "taker_symbol": self.dict_ordered_by_taker[key][0]["name"],
                        "taker_rate": self.dict_ordered_by_taker[key][0]["taker_rate"],
                        "offer_symbol": self.dict_ordered_by_offered[key][1]["name"],
                        "offered_rate": self.dict_ordered_by_offered[key][1]["offered_rate"]}
                    self.is_arbitrage_possible = True
                else:
                    if (len(self.dict_ordered_by_taker[key]) > 1 and self.dict_ordered_by_taker[key][1]["taker_rate"] -
                            self.dict_ordered_by_offered[key][0][
                                "offered_rate"] - self.commission > 0):
                        self.dict_with_arbitrage_possibilities[key] = {
                            "taker_symbol": self.dict_ordered_by_taker[key][1]["name"],
                            "taker_rate": self.dict_ordered_by_taker[key][1]["taker_rate"],
                            "offer_symbol": self.dict_ordered_by_offered[key][1]["name"],
                            "offered_rate": self.dict_ordered_by_offered[key][1]["offered_rate"]}
                        self.is_arbitrage_possible = True
        if not self.is_arbitrage_possible:
            print(LG[sel_lg]["There is no arbitrage possibility"])
        return self.dict_with_arbitrage_possibilities
