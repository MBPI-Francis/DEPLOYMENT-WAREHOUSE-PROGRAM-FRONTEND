
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .table import DataTable


def data_table_tab(notebook):
    table_tab = ttk.Frame(notebook)
    notebook.add(table_tab, text="RM Transaction Report")
    # Populate the Raw Materials Tab
    note_form_label = ttk.Label(
        table_tab,
        text="RM Transaction Report",
        font=("Arial", 14, "bold"),
        bootstyle=PRIMARY,
    )
    note_form_label.pack(pady=(20,0), padx=20)

    notes_label = ttk.Label(
        table_tab,
        text="The table contains all raw material transactions from form entries.",
        font=("Arial", 11, "bold"),
bootstyle=SECONDARY,
    )
    notes_label.pack(pady=0, padx=20)


    # Call the table function to show the table
    DataTable(table_tab)
    # table(note_form_tab)



    # Below is the code for Packing the Tableview and show it in the frontend
