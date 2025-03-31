import ttkbootstrap as ttk
from click.termui import raw_terminal
from ttkbootstrap.constants import *
import requests
from backend.settings.database import server_ip
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.dialogs.dialogs import Messagebox
from datetime import datetime, timedelta
from .table import NoteTable
from .validation import EntryValidation
from tkinter import StringVar


def entry_fields(note_form_tab):

        # Function to clear all entry fields
    def clear_fields():
        warehouse_name_entry.delete(0, ttk.END)
        warehouse_number_entry.delete(0, ttk.END)


    def submit_data():
        # Collect the form data
        wh_number = warehouse_number_entry.get()
        wh_name =warehouse_name_entry.get()

        # Create a dictionary with the data
        data = {
            "wh_number": wh_number,
            "wh_name": wh_name
        }


        # Validate the data entries in front-end side
        if EntryValidation.entry_validation(data):
            error_text = EntryValidation.entry_validation(data)
            Messagebox.show_error(f"There is no data in these fields {error_text}.", "Data Entry Error", alert=True)
            return

            # Send a POST request to the API
        try:
            response = requests.post(f"{server_ip}/api/warehouses/v1/create/", json=data)
            if response.status_code == 200:  # Successfully created
                clear_fields()
                note_table.refresh_table()
        except requests.exceptions.RequestException as e:
            Messagebox.show_info(e, "Data Entry Error")



    # Create a frame for the form inputs
    form_frame = ttk.Frame(note_form_tab)
    form_frame.pack(fill=X, pady=10, padx=20)

    validate_numeric_command = form_frame.register(EntryValidation.validate_numeric_input)

    # Warehouse Number Entry Field
    warehouse_number_label = ttk.Label(form_frame, text="Warehouse Number:", style="CustomLabel.TLabel")
    warehouse_number_label.grid(row=0, column=0, padx=5, pady=5, sticky=W)
    warehouse_number_entry = ttk.Entry(form_frame, width=30,
                                        validate="key",  # Trigger validation on keystrokes
                                        validatecommand=(validate_numeric_command, "%P"))
    warehouse_number_entry.grid(row=1, column=0, padx=5, pady=5)
    ToolTip(warehouse_number_entry, text="Enter new warehouse number")

    # Warehouse Name Entry Field
    warehouse_name_label = ttk.Label(form_frame, text="Warehouse Name:", style="CustomLabel.TLabel")
    warehouse_name_label.grid(row=0, column=3, padx=5, pady=5, sticky=W)
    warehouse_name_entry = ttk.Entry(form_frame, width=30)
    warehouse_name_entry.grid(row=1, column=3, padx=5, pady=5)
    ToolTip(warehouse_name_entry, text="Enter new warehouse name")


    # Add button to submit data
    btn_submit = ttk.Button(
        form_frame,
        text="+ Add",
        command=submit_data,
    )
    btn_submit.grid(row=1, column=6, columnspan=2, pady=10)

    # Calling the table
    note_table = NoteTable(note_form_tab)








