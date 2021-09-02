"""*****************************************************************
  @file     test_RatesCalculator.py
  @brief    This is the core file, here we control the communication
            with websocket and with yfinance, and we also call the
            functions in other files such as RatesCalculator.py,
            consolePrinter.py and Strategy.py
  @author   Matias Francois
#********************************************************************"""

# --------------------------------------------------------------------
#                       Libraries
# --------------------------------------------------------------------

import pyRofex
from config import Secrets
from src.RatesCalculator import RatesCalculator
import yfinance
from src.Strategy import Strategy
from datetime import datetime
from dateutil.parser import parse
from src.consolePrinter import Printer, Printer_arbitrage_oportunities
from config.language import language as LG
from rich.progress import track
from operator import itemgetter
from src.clear import clear


# --------------------------------------------------------------------
#                        TraderBot class
# --------------------------------------------------------------------

class TraderBot:
    """
        This class controls the communication with the other classes such as
        RatesCalculator, Strategy etc. and the communication with the backend
        (yfinance and Remarkets) It also prints the content in the console with
        help from the functions inside consolePrinter.py

        :param instrument: List of instruments to consider
        :param commission: the commission for the transaction
        :param language: console display language
        :param debugging: information display mode
        :param num_of_dollars: Number of dollar futures that we want to look at
        :param clear_bool: boolean value to know if we want to clear the console with every price change or not
        """

    def __init__(self, instrument, commission, language, debugging, num_of_dollars, clear_bool):
        self.instrument = instrument
        self.commission = commission
        self.lg = language
        self.debugging = debugging
        self.clear_bool = True if clear_bool == "Yes" else False
        if num_of_dollars == 'One':
            self.num_dlr = 1
        elif num_of_dollars == 'Five':
            self.num_dlr = 5
        elif num_of_dollars == 'All Available (takes longer)':
            self.num_dlr = float('inf')
        self.spot = None
        self.my_order = dict()

        # This dictionary will contain the futures for every instrument
        self.futures = dict.fromkeys(self.instrument)

        # Initializes the environment
        pyRofex.initialize(user=Secrets.USER,
                           password=Secrets.PASSWORD,
                           account=Secrets.ACCOUNT,
                           environment=pyRofex.Environment.REMARKET)

        # Initializes Websocket Connection with the handler
        pyRofex.init_websocket_connection(
            market_data_handler=self.market_data_handler
        )

        # Subscribes to receive order report for the default account
        pyRofex.order_report_subscription()

        print(LG[self.lg]["This may take a while"])

        # Gets all the instruments to get the futures' names
        self.allInstruments = pyRofex.get_all_instruments()

        if self.debugging == "debugging":
            print("all instruments are:")
            print(self.allInstruments)

        # Retrieves the futures' names for all the instruments that we want
        for key_word in self.instrument:
            num_dol = 0
            aux_var = []
            for instrument in self.allInstruments["instruments"]:
                instrument_helper = instrument["instrumentId"]["symbol"]
                if instrument_helper[0:len(key_word)] == key_word:
                    if key_word == "DLR":
                        if num_dol < self.num_dlr:
                            # to avoid things like GGAL/AGO21/SEP21
                            if len(instrument_helper.split("/")) <= 2:
                                num_dol = num_dol + 1
                                aux_var.append(instrument_helper)
                    else:
                        # to avoid things like GGAL/AGO21/SEP21
                        if len(instrument_helper.split("/")) <= 2:
                            aux_var.append(instrument_helper)
            self.futures[key_word] = aux_var

        # Creates a list of lists with the futures' values.
        self.list_of_list_of_futures = list(self.futures.values())

        # Flattens the "list of lists" into one with every future
        self.list_of_futures = [item for sublist in self.list_of_list_of_futures for item in sublist]

        self.dict_with_dates_of_futures = {}

        # Downloads the information about the maturityDate of the futures that we want
        for future in track(self.list_of_futures, description=LG[self.lg]["Checking for available futures"]):
            self.dict_with_dates_of_futures[future] = pyRofex.get_instrument_details(future)['instrument'][
                'maturityDate']
        if self.debugging == "verbose" or self.debugging == "debugging":
            print(LG[self.lg]["The dictionary with the futures' maturity date is:"])
            print(self.dict_with_dates_of_futures)
        self.dict_tiempos_val = {k: [] for k in list(set(self.dict_with_dates_of_futures.values()))}

        # Updates the market data BI and OF for every future that we want to track
        for key in track(self.dict_with_dates_of_futures, description=LG[self.lg]["Updating Market Data          "]):
            market_data = pyRofex.get_market_data(ticker=key)["marketData"]
            bid = market_data["BI"]
            offer = market_data["OF"]
            # Checks that bid and offered are not null
            if bid and offer:
                # Because we care about the bid and offered price
                bid_px = bid[0]["price"]
                offer_px = offer[0]["price"]
                self.spot = None
                # Spot price update
                self.update_prices(key)
                if self.spot is not None:
                    # Calculates the dates to maturity date
                    dates_to_end = self.DC(key)
                    # Obtains the take and offered rates
                    RC = RatesCalculator(bid_px, offer_px, self.spot, dates_to_end, self.lg, self.debugging)
                    taker_rate = RC.get_taker_rate()
                    offered_rate = RC.get_offered_rate()
                    # The values in the dictionary with every future with their own taker and offered rate are appended
                    self.dict_tiempos_val[self.dict_with_dates_of_futures[key]].append(
                        {"name": key, "taker_rate": taker_rate, "offered_rate": offered_rate})
                else:
                    # if we can not calculate taker/offered rate => we use -inf for taker rate and inf for offered rate
                    self.dict_tiempos_val[self.dict_with_dates_of_futures[key]].append(
                        {"name": key, "taker_rate": float("-inf"), "offered_rate": float("inf")})
            else:
                self.dict_tiempos_val[self.dict_with_dates_of_futures[key]].append(
                    {"name": key, "taker_rate": float("-inf"), "offered_rate": float("inf")})

        if self.debugging == "verbose" or self.debugging == "debugging":
            print(LG[self.lg]["Dictionary with the maturity dates and the implicit rates:"])
            print(self.dict_tiempos_val)

        self.dict_time_val_ordered_by_taker = self.dict_tiempos_val.copy()
        self.dict_time_val_ordered_by_offered = self.dict_tiempos_val.copy()

        # Arrays sorted within every key in the dictionary
        for maturityDate in self.dict_time_val_ordered_by_taker:
            self.dict_time_val_ordered_by_taker[maturityDate] = sorted(self.dict_tiempos_val[maturityDate],
                                                                       key=itemgetter('taker_rate'), reverse=True)
        # Arrays sorted within every key in the dictionary
        for maturityDate in self.dict_time_val_ordered_by_offered:
            self.dict_time_val_ordered_by_offered[maturityDate] = sorted(self.dict_tiempos_val[maturityDate],
                                                                         key=itemgetter('taker_rate'),
                                                                         reverse=True)
        # print("dict_tiempos_val:")
        # print(self.dict_tiempos_val)

        if self.debugging == "debugging":
            print(LG[self.lg]["dict_tiempos_val before filling:"])
            print(self.dict_tiempos_val)

            print(LG[self.lg]["dict_tiempos_val after filling:"])
            print(self.dict_tiempos_val)

            print("\n\n" + LG[self.lg]["The futures dictionary is:"] + "\n" + str(self.futures))
            print(
                LG[self.lg]["The dictionary with the futures' dates is:"] + "\n" + str(self.dict_with_dates_of_futures))
            print(LG[self.lg]["The list with futures is:"] + "\n" + str(self.list_of_futures) + "\n")

        # Subscribes for Market Data
        pyRofex.market_data_subscription(
            tickers=
            self.list_of_futures
            ,
            entries=[
                pyRofex.MarketDataEntry.BIDS,
                pyRofex.MarketDataEntry.OFFERS
            ]
        )

    # --------------------------------------------------------------------
    #                        market_data_handler
    # --------------------------------------------------------------------

    def market_data_handler(self, message):
        """
        This function is used as a callback in pyRofex.init_websocket_connection function,
        we get into this function every time that the market data changes, so we store
        the new data and sort it, then send it to Strategy.py and get the possible strategy
        options to then pass to the consolePrinter.py file
        :param message: information related with the new change
        """
        # print("entre a market_data_handler")
        if self.debugging == "debugging":
            print("\n" + LG[self.lg]["Market Data Message Received:"] + "\n{0}".format(message) + "\n")
        bid = message["marketData"]["BI"]
        offer = message["marketData"]["OF"]
        maturityDate = pyRofex.get_instrument_details(message["instrumentId"]["symbol"])['instrument']['maturityDate']
        # Checks that bid and offered are not null
        if bid and offer:
            # Because we care about the bid and offered price
            bid_px = bid[0]["price"]
            offer_px = offer[0]["price"]
            # Resets the spot price to ensure that we won't be using an old spot price
            self.spot = None
            self.update_prices(message["instrumentId"]["symbol"])
            if self.spot is not None:
                if self.clear_bool:
                    clear()
                symbol = message["instrumentId"]["symbol"]
                # Calculates the dates to maturity date
                dates_to_end = self.DC(symbol)
                # Obtains the take and offered rates
                RC = RatesCalculator(bid_px, offer_px, self.spot, dates_to_end, self.lg, self.debugging)
                taker_rate = RC.get_taker_rate()
                offered_rate = RC.get_offered_rate()
                # Dictionary values are updated
                for i in range(len(self.dict_tiempos_val[maturityDate])):
                    if self.dict_tiempos_val[maturityDate][i]["name"] == symbol:
                        self.dict_tiempos_val[maturityDate][i]["taker_rate"] = taker_rate
                        self.dict_tiempos_val[maturityDate][i]["offered_rate"] = offered_rate

                print("\n")

                # Dictionaries are sorted by taker and offered rates
                self.dict_time_val_ordered_by_taker[maturityDate] = sorted(self.dict_tiempos_val[maturityDate],
                                                                           key=itemgetter('taker_rate'),
                                                                           reverse=True)

                self.dict_time_val_ordered_by_offered[maturityDate] = sorted(self.dict_tiempos_val[maturityDate],
                                                                             key=itemgetter('offered_rate'))

                if self.debugging == "debugging":
                    print(LG[self.lg]["List ordered by taker rate"])
                    print(self.dict_time_val_ordered_by_taker)
                    print(LG[self.lg]["List ordered by offered rate"])
                    print(self.dict_time_val_ordered_by_offered)

                # Checking strategy possibilities

                strat = Strategy(self.dict_time_val_ordered_by_taker, self.dict_time_val_ordered_by_offered,
                                 self.commission)
                possible_arbitrage_dict = strat.arbitrage_options(self.lg)
                if self.debugging == "debugging":
                    print(LG[self.lg]["Dict with arbitrage possibilities"])
                    print(possible_arbitrage_dict)

                # Prints the results in the console
                Printer(symbol, taker_rate, offered_rate, self.lg)
                Printer_arbitrage_oportunities(possible_arbitrage_dict, self.lg)
            else:
                if self.debugging == "debugging":
                    print(LG[self.lg]["I can not calculate the taker and offered rates because I have no spot price"])
        else:
            if self.debugging == "debugging":
                print(LG[self.lg]["There is no bid and/or offer"])

    # --------------------------------------------------------------------
    #                     Update Prices (yfinance)
    # --------------------------------------------------------------------

    def update_prices(self, future_word):
        """
        This function allows us to retrieve
        the information of the tickers in yfinance
        :param future_word: the name of the future, for example GGAL/AGO21
        """
        try:
            # convert the future_word to the name of the corresponding spot
            if future_word.split('/')[0] == "DLR":
                ticker = "ARS=X"
            else:
                ticker = future_word.split('/')[0] + '.BA'
            data = yfinance.download(
                tickers=ticker,
                period='1d',
                interval='1d',
                progress=False)
            if self.debugging == "debugging":
                print(LG[self.lg]["The data from yfinance is:"])
                print(data)
            self.spot = data['Close'].to_numpy()[0]
        except Exception as e:
            self.spot = None
            print(LG[self.lg]['Exception occurred updating yfinance prices.'])

    # --------------------------------------------------------------------
    #                         Days Calculator
    # --------------------------------------------------------------------

    def DC(self, symbol):
        """
        This function returns the days left to the maturity date of the future passed
        :param symbol: the name of the future, for example GGAL/AGO21
        :return: days left to maturity date
        """
        maturity_date = parse(self.dict_with_dates_of_futures[symbol])
        if self.debugging == "verbose" or self.debugging == "debugging":
            print(LG[self.lg]["The data of the updated future is:"])
            print(LG[self.lg]["maturity date is: "] + str(maturity_date.strftime("%Y-%m-%d")))
            print(LG[self.lg]["Today is: "] + str(datetime.now().strftime("%Y-%m-%d")))
            print(LG[self.lg]["The difference in days is: "] + str((maturity_date - datetime.now()).days + 1))
        return (maturity_date - datetime.now()).days + 1
