
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .table import ReceivingFormTable
from .entry_fields import entry_fields


def receiving_report_tab(notebook):
    receiving_report_tab = ttk.Frame(notebook)
    notebook.add(receiving_report_tab, text="Receiving Form")
    # Populate the Raw Materials Tab
    receiving_report_label = ttk.Label(
        receiving_report_tab,
        text="Receiving Form",
        font=("Helvetica", 14, "bold"),
        bootstyle=PRIMARY,
    )
    receiving_report_label.pack(pady=(10,0), padx=20)

    # Call the entry fields function to show the table
    entry_fields(receiving_report_tab)
