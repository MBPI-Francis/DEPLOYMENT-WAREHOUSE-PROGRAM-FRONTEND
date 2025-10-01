
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .entry_fields import entry_fields


def supplies_outgoing_form_tab(notebook):
    outgoing_form_tab = ttk.Frame(notebook)
    notebook.add(outgoing_form_tab, text="Supplies Outgoing")
    # Populate the Raw Materials Tab
    outgoing_form_label = ttk.Label(
        outgoing_form_tab,
        text="Supply Outgoing Form",
        font=("Arial", 14, "bold"),
        bootstyle=PRIMARY,
    )
    outgoing_form_label.pack(pady=(10, 0), padx=20)

    entry_fields(outgoing_form_tab)


