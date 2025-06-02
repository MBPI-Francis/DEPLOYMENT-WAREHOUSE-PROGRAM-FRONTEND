
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .table import ChangeStatusFormTable


def held_form_tab(notebook):
    held_form_tab = ttk.Frame(notebook)
    notebook.add(held_form_tab, text="Change Status Form")
    # Populate the Raw Materials Tab
    held_form_label = ttk.Label(
        held_form_tab,
        text="Change Status Form",
        font=("Arial", 14, "bold"),
        bootstyle=PRIMARY,
    )
    held_form_label.pack(pady=(20,0), padx=20)

    change_status_label = ttk.Label(
        held_form_tab,
        text="The table contains the user's previous entries, showing historical data and past status changes of raw materials.",
        font=("Arial", 11, "bold"),
bootstyle=SECONDARY,
    )
    change_status_label.pack(pady=0, padx=20)

    table = ChangeStatusFormTable(held_form_tab)



