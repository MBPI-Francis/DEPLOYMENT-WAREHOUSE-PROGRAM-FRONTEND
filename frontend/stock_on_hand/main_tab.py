
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from frontend.stock_on_hand.table import BeginningBalanceTable
from frontend.stock_on_hand.import_feature.confirm_messages import ConfirmationMessage
import datetime
from ttkbootstrap.tooltip import ToolTip

def beginning_balance_tab(notebook):
    soh_tab = ttk.Frame(notebook)
    notebook.add(soh_tab, text="Finalized Stocks")
    # Populate the Raw Materials Tab


    # Get today's date in a readable format
    today_date = datetime.date.today().strftime("%B %d, %Y")  # Example: March 13, 2025

    # Label for Beginning Balance
    raw_material_label = ttk.Label(
        soh_tab,
        text=f"Finalized Stocks as of {today_date}",
        font=("Arial", 14, "bold"),
        bootstyle=PRIMARY,
    )
    raw_material_label.pack(pady=(20, 0), padx=20)

    table_label = ttk.Label(
        soh_tab,
        text="""This table shows the finalized stock levels from today, which will be used as the starting balance for the next day.""",
        font=("Arial", 11, "bold"),
        bootstyle=SECONDARY,
    )
    table_label.pack(pady=0, padx=20)

    # Call out the table to show in the panel
    table = BeginningBalanceTable(soh_tab)





