
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from frontend.stock_on_hand.table import BeginningBalanceTable
from frontend.stock_on_hand.import_feature.confirm_messages import ConfirmationMessage
import datetime
from ttkbootstrap.tooltip import ToolTip

def beginning_balance_tab(notebook):
    soh_tab = ttk.Frame(notebook)
    notebook.add(soh_tab, text="Beginning Balance")
    # Populate the Raw Materials Tab


    # Get today's date in a readable format
    today_date = datetime.date.today().strftime("%B %d, %Y")  # Example: March 13, 2025

    # Label for Beginning Balance
    raw_material_label = ttk.Label(
        soh_tab,
        text=f"Beginning Balance as of {today_date}",
        font=("Arial", 14, "bold"),
        bootstyle=PRIMARY,
    )
    raw_material_label.pack(pady=(20, 0), padx=20)

    table_label = ttk.Label(
        soh_tab,
        text="The table below shows the latest stock on hand for each raw material per warehouse",
        font=("Arial", 11, "bold"),
        bootstyle=SECONDARY,
    )
    table_label.pack(pady=0, padx=20)

    # Call out the table to show in the panel
    table = BeginningBalanceTable(soh_tab)





