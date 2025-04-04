
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .entry_fields import entry_fields


def transfer_form_tab(notebook):
    transfer_form_tab = ttk.Frame(notebook)
    notebook.add(transfer_form_tab, text="Transfer Form")
    # Populate the Raw Materials Tab
    transfer_form_label = ttk.Label(
        transfer_form_tab,
        text="Transfer Form",
        font=("Arial", 14, "bold"),
        bootstyle=PRIMARY,
    )
    transfer_form_label.pack(pady=(10, 0), padx=20)

    entry_fields(transfer_form_tab)


