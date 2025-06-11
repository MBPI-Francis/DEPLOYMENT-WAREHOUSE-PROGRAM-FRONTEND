
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .table import AdjustmentEntriesTable


def entries_tab(notebook):
    iaf_entries_tab = ttk.Frame(notebook)
    notebook.add(iaf_entries_tab, text="IAF-Wrong Entries")
    # Populate the Raw Materials Tab
    note_form_label = ttk.Label(
        iaf_entries_tab,
        text="IAF-Wrong Entries",
        font=("Arial", 14, "bold"),
        bootstyle=PRIMARY,
    )
    note_form_label.pack(pady=(20,0), padx=20)

    notes_label = ttk.Label(
        iaf_entries_tab,
        text="The table displays adjustments made to correct inaccurate entries",
        font=("Arial", 11, "bold"),
bootstyle=SECONDARY,
    )
    notes_label.pack(pady=0, padx=20)


    # Call the table function to show the table
    AdjustmentEntriesTable(iaf_entries_tab)
    # table(iaf_entries_tab)



    # Below is the code for Packing the Tableview and show it in the frontend
