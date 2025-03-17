
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .table import NoteTable


def receiving_report_tab(notebook):
    receiving_report_tab = ttk.Frame(notebook)
    notebook.add(receiving_report_tab, text="Receiving Form")
    # Populate the Raw Materials Tab
    receiving_report_label = ttk.Label(
        receiving_report_tab,
        text="Receiving Form",
        font=("Helvetica", 14, "bold"),
        bootstyle=PRIMARY,
    )
    receiving_report_label.pack(pady=(20,0), padx=20)

    receiving_label = ttk.Label(
        receiving_report_tab,
        text="The table contains the user's previous entries, showing historical data and past entries of received raw materials.",
        font=("Helvetica", 10)
    )
    receiving_label.pack(pady=0, padx=20)


    # Calling the table
    note_table = NoteTable(receiving_report_tab)
