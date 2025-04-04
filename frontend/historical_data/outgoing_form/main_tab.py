
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .table import OutgoingFormTable


def outgoing_form_tab(notebook):
    outgoing_form_tab = ttk.Frame(notebook)
    notebook.add(outgoing_form_tab, text="Outgoing Form")
    # Populate the Raw Materials Tab
    outgoing_form_label = ttk.Label(
        outgoing_form_tab,
        text="Outgoing Form",
        font=("Arial", 14, "bold"),
        bootstyle=PRIMARY,
    )
    outgoing_form_label.pack(pady=(20,0), padx=20)

    outgoing_label = ttk.Label(
        outgoing_form_tab,
        text="The table contains the user's previous entries, showing historical data and past records of dispatched raw materials.",
        font=("Arial", 11)
    )
    outgoing_label.pack(pady=0, padx=20)

    table = OutgoingFormTable(outgoing_form_tab)
