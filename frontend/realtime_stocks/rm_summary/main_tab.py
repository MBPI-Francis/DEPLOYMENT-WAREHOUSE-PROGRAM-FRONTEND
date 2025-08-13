
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .entry_fields import entry_fields


def rm_summary_tab(notebook):
    stock_per_whse_tab = ttk.Frame(notebook)
    notebook.add(stock_per_whse_tab, text="Stock Summary by Status")

    # Populate the Raw Materials Tab
    submit_entries_label = ttk.Label(
        stock_per_whse_tab,
        text="This table provides real-time updates on the daily stock of raw materials for each warehouse",
        font=("Arial", 14, "bold"),
        bootstyle=PRIMARY,
    )
    submit_entries_label.pack(pady=(10,0), padx=20)


    entry_fields(stock_per_whse_tab)
