
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .entry_fields import entry_fields


def outgoing_form_tab(notebook):
    outgoing_form_tab = ttk.Frame(notebook)
    notebook.add(outgoing_form_tab, text="Outgoing Form")
    # Populate the Raw Materials Tab
    outgoing_form_label = ttk.Label(
        outgoing_form_tab,
        text="Outgoing Form",
        font=("Helvetica", 14, "bold"),
        bootstyle=PRIMARY,
    )
    outgoing_form_label.pack(pady=(10, 0), padx=20)

    entry_fields(outgoing_form_tab)


