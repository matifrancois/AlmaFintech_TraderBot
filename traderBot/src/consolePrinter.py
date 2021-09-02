"""*****************************************************************
  @file     consolePrinter.py
  @brief    This file manages the console; it prints the price changes and
            the arbitrage table.
  @author   Matias Francois
#********************************************************************"""

# --------------------------------------------------------------------
#                           Libraries
# --------------------------------------------------------------------

from rich.console import Console
from rich.table import Table
from datetime import datetime
from config.language import language as LG

# --------------------------------------------------------------------
#                           Printer
# --------------------------------------------------------------------

def Printer(symbol, taker_rate, offered_rate, sel_lg):
    """
    This function prints price changes in a table.

    :param symbol: Future name
    :param taker_rate: Calculated taker_rate for the future.
    :param offered_rate: Calculated offered_rate for the future.
    :param sel_lg: Selected Language
    """

    table = Table(title=LG[sel_lg]["There was a change in:"])

    table.add_column(LG[sel_lg]["Futuro"])
    table.add_column(LG[sel_lg]["Date"])
    table.add_column(LG[sel_lg]["Taker Rate"], style="magenta")
    table.add_column(LG[sel_lg]["Offered Rate"], style="cyan")

    table.add_row(str(symbol), str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), str(round(taker_rate, 3)) + "%",
                  str(round(offered_rate, 3)) + "%")

    console = Console()
    console.print(table)

# --------------------------------------------------------------------
#                      Printer Arbitrage
# --------------------------------------------------------------------

def Printer_arbitrage_oportunities(possible_arbitrage_dict, sel_lg):
    """
    This function prints Arbitrage Opportunities in a table.

    :param possible_arbitrage_dict: Dictionary with the possible arbitrage opportunities
    """

    table_arb = Table(title=LG[sel_lg]["Arbitrage Opportunities:"])

    # Harcodeado falta el control de idiomas aca
    table_arb.add_column(LG[sel_lg]["Maturity Date"])
    table_arb.add_column(LG[sel_lg]["Short sell"])
    table_arb.add_column(LG[sel_lg]["Taker Rate"], style="magenta")
    table_arb.add_column(LG[sel_lg]["Long buy"])
    table_arb.add_column(LG[sel_lg]["Offered Rate"], style="cyan")

    for key in possible_arbitrage_dict:
        date_parsed = str(key)[:4] + "/" + str(key)[4:6] + "/" + str(key)[6:]
        table_arb.add_row(date_parsed, str(possible_arbitrage_dict[key]["taker_symbol"]),
                          str(possible_arbitrage_dict[key]["taker_rate"]) + "%",
                          str(possible_arbitrage_dict[key]["offer_symbol"]),
                          str(possible_arbitrage_dict[key]["offered_rate"]) + "%")

    console = Console()
    console.print(table_arb)
