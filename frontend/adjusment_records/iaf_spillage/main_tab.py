
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .table import AdjustmentSpillageTable


def spillage_tab(notebook):
    iaf_spillage_tab = ttk.Frame(notebook)
    notebook.add(iaf_spillage_tab, text="IAF-Spillage")
    # Populate the Raw Materials Tab
    note_form_label = ttk.Label(
        iaf_spillage_tab,
        text="IAF-Spillage",
        font=("Arial", 14, "bold"),
        bootstyle=PRIMARY,
    )
    note_form_label.pack(pady=(20,0), padx=20)

    notes_label = ttk.Label(
        iaf_spillage_tab,
        text="The table displays adjustments made to account for raw material spillage",
        font=("Arial", 11, "bold"),
bootstyle=SECONDARY,
    )
    notes_label.pack(pady=0, padx=20)


    # Call the table function to show the table
    AdjustmentSpillageTable(iaf_spillage_tab)
    # table(iaf_spillage_tab)



    # Below is the code for Packing the Tableview and show it in the frontend
