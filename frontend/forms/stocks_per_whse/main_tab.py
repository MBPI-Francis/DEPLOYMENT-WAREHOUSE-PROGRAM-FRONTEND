# stocks_per_whse/main_tab.py

# Make sure you are importing the updated class
from .table import StocksPerWHSE

def stock_per_whse_tab(parent_notebook):
    """
    Initializes the warehouse tabs and adds them directly to the parent notebook.
    """
    # No longer creates an intermediate frame.
    # Just create an instance of the class, which will handle adding its own tabs.
    StocksPerWHSE(parent_notebook)