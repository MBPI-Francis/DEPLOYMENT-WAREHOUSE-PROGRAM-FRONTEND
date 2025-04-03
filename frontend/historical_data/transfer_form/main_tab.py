
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .table import TransferFormTable


def transfer_form_tab(notebook):
    transfer_form_tab = ttk.Frame(notebook)
    notebook.add(transfer_form_tab, text="Transfer Form")
    # Populate the Raw Materials Tab
    transfer_form_label = ttk.Label(
        transfer_form_tab,
        text="Transfer Form",
        font=("Helvetica", 14, "bold"),
        bootstyle=PRIMARY,
    )
    transfer_form_label.pack(pady=(20,0), padx=20)

    transfer_label = ttk.Label(
        transfer_form_tab,
        text="The table contains the user's previous entries, showing historical data and past transfers of raw materials between warehouses.",
        font=("Helvetica", 11)
    )
    transfer_label.pack(pady=0, padx=20)


    table = TransferFormTable(transfer_form_tab)




