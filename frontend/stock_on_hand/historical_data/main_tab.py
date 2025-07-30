
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from frontend.stock_on_hand.historical_data.table import HistoricalSOHTable


def historical_data_tab(notebook):
    soh_tab = ttk.Frame(notebook)
    notebook.add(soh_tab, text="Historical Raw Material Stock")
    # Populate the Raw Materials Tab
    raw_material_label = ttk.Label(
        soh_tab,
        text="Historical Raw Material Stock",
        font=("Arial", 14, "bold"),
        bootstyle=PRIMARY,
    )
    raw_material_label.pack(pady=(20, 0), padx=20)

    table_label = ttk.Label(
        soh_tab,
        text="The table below shows historical stock data for each raw material by warehouse",
        font=("Arial", 11, "bold"),
        bootstyle=SECONDARY,
    )
    table_label.pack(pady=0, padx=20)



    # Call out the table to show in the panel
    table = HistoricalSOHTable(soh_tab)





