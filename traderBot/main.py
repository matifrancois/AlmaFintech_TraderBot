"""****************************************************************
  @file     main.py
  @brief    This file has the code for the menu
            and it is the first file used to run the program
  @author   Matias Francois
#*******************************************************************"""

# --------------------------------------------------------------------
#                       Libraries
# --------------------------------------------------------------------

from __future__ import print_function, unicode_literals
import src.TraderBot as TraderBot
from PyInquirer import prompt
from examples import custom_style_2

# --------------------------------------------------------------------
#                        Constants
# --------------------------------------------------------------------

symbols = ['GGAL', 'YPFD', 'PAMP', 'DLR']

# --------------------------------------------------------------------
#                           Menu
# --------------------------------------------------------------------

questions = [
    {
        'type': 'list',
        'name': 'debugging',
        'message': 'Mode?',
        'choices': ['No Extra Info', 'Verbose', 'Debugging'],
        'filter': lambda val: val.lower()
    },
    {
        'type': 'list',
        'name': 'dlr',
        'message': 'How many future dollars do you want?',
        'choices': [
            'One',
            'Five',
            'All Available (takes longer)',
        ]
    },
{
        'type': 'list',
        'name': 'clear',
        'message': 'Do you want to clear the console with every price change?',
        'choices': [
            'No',
            'Yes'
        ]
    },
    {
        'type': 'list',
        'name': 'language',
        'message': 'What language do you prefer?',
        'choices': [
            'English',
            'Spanish'
        ]
    }
]

answers = prompt(questions, style=custom_style_2)

language = answers["language"]
debugging = answers["debugging"]
num_of_dollars = answers["dlr"]
clear_bool = answers["clear"]

# --------------------------------------------------------------------
#                           Start
# --------------------------------------------------------------------

if __name__ == "__main__":
    TraderBot.TraderBot(symbols, 0, language, debugging, num_of_dollars, clear_bool)
