"""*****************************************************************
  @file     clear.py
  @brief    File used to clear the console if
            the user selects that option
  @author   Matias Francois
#********************************************************************"""

# --------------------------------------------------------------------
#                       Libraries
# --------------------------------------------------------------------

from os import system, name


# --------------------------------------------------------------------
#                      Clear Function
# --------------------------------------------------------------------

def clear():
    """
    This function clears the console when it is called
    """

    # for windows
    if name == 'nt':
        _ = system('cls')

    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')
