
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .table import PreparationFormTable



def preparation_form_tab(notebook):
    preparation_form_tab = ttk.Frame(notebook)
    notebook.add(preparation_form_tab, text="Preparation Form")
    # Populate the Raw Materials Tab
    preparation_form_label = ttk.Label(
        preparation_form_tab,
        text="Preparation Form",
        font=("Helvetica", 14, "bold"),
        bootstyle=PRIMARY,
    )
    preparation_form_label.pack(pady=(20,0), padx=20)

    preparation_label = ttk.Label(
        preparation_form_tab,
        text="The table contains the user's previous entries, showing historical data and past usage of raw materials.",
        font=("Helvetica", 10)
    )
    preparation_label.pack(pady=0, padx=20)

    table = PreparationFormTable(preparation_form_tab)



