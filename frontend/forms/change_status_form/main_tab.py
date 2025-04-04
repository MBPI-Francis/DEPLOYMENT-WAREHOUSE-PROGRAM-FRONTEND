
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .entry_fields import entry_fields


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
    held_form_label.pack(pady=(10,0), padx=20)

    entry_fields(held_form_tab)



