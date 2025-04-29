
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .entry_fields import entry_fields


def adjustment_form_tab(notebook):
    adjustment_form_tab = ttk.Frame(notebook)
    notebook.add(adjustment_form_tab, text="Adjustment Form")
    # Populate the Raw Materials Tab
    adjustment_form_label = ttk.Label(
        adjustment_form_tab,
        text="Adjustment Form",
        font=("Arial", 14, "bold"),
        bootstyle=PRIMARY,
    )
    adjustment_form_label.pack(pady=(10, 0), padx=20)

    entry_fields(adjustment_form_tab)


