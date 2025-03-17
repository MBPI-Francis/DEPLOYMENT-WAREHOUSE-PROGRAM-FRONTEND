import ttkbootstrap as ttk

from ttkbootstrap.constants import *
import requests
from backend.settings.database import server_ip
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.dialogs.dialogs import Messagebox
from .table import RawMaterialTable
from .validation import EntryValidation
import re

def entry_fields(note_form_tab):

        # Function to clear all entry fields
    def clear_fields():
        rm_code_entry.delete(0, ttk.END)


    def submit_data():
        # Collect the form data
        rm_code = rm_code_entry.get()


        # Create a dictionary with the data
        data = {
            "rm_code": rm_code,
        }


        # Validate the data entries in front-end side
        if EntryValidation.entry_validation(data):
            error_text = EntryValidation.entry_validation(data)
            Messagebox.show_error(f"There is no data in these fields {error_text}.", "Data Entry Error", alert=True)
            return

            # Send a POST request to the API
        try:
            response = requests.post(f"{server_ip}/api/raw_materials/v1/create/", json=data)
            if response.status_code == 200:  # Successfully created
                clear_fields()

                note_table.refresh_table()
                # refresh_table()  # Refresh the table
            else:
                Messagebox.show_error("The raw material might already exist in the database.", "Validation Error")
        except requests.exceptions.RequestException as e:
            Messagebox.show_info(e, "Data Entry Error")



    # Create a frame for the form inputs
    form_frame = ttk.Frame(note_form_tab)
    form_frame.pack(fill=X, pady=10, padx=20)

    # Function to convert typed input to uppercase
    def on_combobox_key_release(event):
        # Get the current text in the entry field
        rm_code_current_text = rm_code_var.get()

        # Convert the text to uppercase and set it back
        rm_code_var.set(rm_code_current_text.upper())

    def validate_rm_code(value):
        """
        Validation Rules:
        - Allows letters (A-Z, a-z), numbers (0-9), and spaces.
        - Maximum of 5 spaces allowed.
        - Rejects special characters.
        """
        # Count spaces
        space_count = value.count(" ")

        # Check if input contains only allowed characters (letters, numbers, and spaces)
        if re.fullmatch(r'^[A-Za-z0-9 ]*$', value) and space_count <= 5:
            return True
        else:
            Messagebox.show_error("❌ Only letters, numbers, and up to 5 spaces are allowed.", "Invalid Input")
            return False
    # Create a Tkinter validation command
    validate_command = form_frame.register(validate_rm_code)

    # Raw Material Code Entry Field
    rm_code_var = ttk.StringVar(value="")
    rm_code_label = ttk.Label(form_frame, text="Raw Material Code:", font=("Helvetica", 10, "bold"))
    rm_code_label.grid(row=0, column=0, padx=5, pady=5, sticky=W)
    rm_code_entry = ttk.Entry(form_frame, width=30,
                              validate="key",
                                validatecommand=(validate_command, "%P"),  # %P = new text in the entry field
                              textvariable=rm_code_var
        )

    rm_code_entry.bind("<KeyRelease>", on_combobox_key_release)
    rm_code_entry.grid(row=1, column=0, padx=5, pady=5)
    ToolTip(rm_code_entry, text="Add New Raw Material Code")


    # Add button to submit data
    btn_submit = ttk.Button(
        form_frame,
        text="+ Add",
        command=submit_data,
    )
    btn_submit.grid(row=1, column=2, columnspan=2, pady=10)

    # Calling the table
    note_table = RawMaterialTable(note_form_tab)








