
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .entry_fields import entry_fields


def submit_entries_tab(notebook):
    submit_entries_tab = ttk.Frame(notebook)
    notebook.add(submit_entries_tab, text="Real-Time Tracking of Raw Material Inventory")

    # Populate the Raw Materials Tab
    submit_entries_label = ttk.Label(
        submit_entries_tab,
        text="This table provides real-time updates on the daily stock of raw materials for each warehouse",
        font=("Arial", 14, "bold"),
        bootstyle=PRIMARY,
    )
    submit_entries_label.pack(pady=(10,0), padx=20)

    submit_entries_label = ttk.Label(
        submit_entries_tab,
        text="Click the 'Export' button to export the New Beginning Balance into EXCEL",
        font=("Arial", 11, "bold"),
        bootstyle=SECONDARY,
    )
    submit_entries_label.pack(pady=0, padx=20)

    entry_fields(submit_entries_tab)
