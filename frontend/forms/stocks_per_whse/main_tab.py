
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .entry_fields import entry_fields


def stock_per_whse_tab(notebook):
    stock_per_whse_tab = ttk.Frame(notebook)
    notebook.add(stock_per_whse_tab, text="Warehouse Stocks")

    # Populate the Raw Materials Tab
    submit_entries_label = ttk.Label(
        stock_per_whse_tab,
        text="This table provides real-time updates on the daily stock of raw materials that are grouped by status",
        font=("Arial", 14, "bold"),
        bootstyle=PRIMARY,
    )
    submit_entries_label.pack(pady=(10,0), padx=20)


    entry_fields(stock_per_whse_tab)
