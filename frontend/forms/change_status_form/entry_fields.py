import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import requests
from backend.settings.database import server_ip
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.dialogs.dialogs import Messagebox
from datetime import datetime, timedelta
from .table import NoteTable
from .validation import EntryValidation
from ..preparation_form.validation import EntryValidation as PrepValidation
from tkinter import StringVar

from ..shared import SharedFunctions


def entry_fields(note_form_tab):
    shared_functions = SharedFunctions()

    get_status_api = shared_functions.get_status_api()
    get_rm_code_api = shared_functions.get_rm_code_api()
    get_warehouse_api = shared_functions.get_warehouse_api()

    def get_selected_warehouse_id():
        selected_name = warehouse_combobox.get()
        selected_id = warehouse_to_id.get(selected_name)  # Get the corresponding ID
        if selected_id:
            return selected_id
        else:
            return None

    def get_selected_current_status_id():
        selected_name = current_status_combobox.get()
        selected_id = status_to_id.get(selected_name)  # Get the corresponding ID
        if selected_id:
            return selected_id
        else:
            return None

    def get_selected_new_status_id():
        selected_name = new_status_combobox.get()
        selected_id = status_to_id.get(selected_name)  # Get the corresponding ID
        if selected_id:
            return selected_id
        else:
            return None

    def get_selected_rm_code_id():
        selected_name = rm_codes_combobox.get()
        selected_id = code_to_id.get(selected_name)  # Get the corresponding ID
        if selected_id:
            return selected_id
        else:
            return None

        # Function to clear all entry fields
    def clear_fields():

        if not checkbox_reference_var.get():
            ref_number_entry.delete(0, ttk.END)

        if not checkbox_warehouse_var.get():
            warehouse_combobox.set("")
        rm_codes_combobox.set("")
        current_status_combobox.set("")
        new_status_combobox.set("")
        qty_entry.delete(0, ttk.END)


    def submit_data():

        # Collect the form data
        warehouse_id = get_selected_warehouse_id()
        rm_code_id = get_selected_rm_code_id()
        ref_number = ref_number_entry.get()
        qty = qty_entry.get()
        current_status = get_selected_current_status_id()
        current_status_name = current_status_combobox.get()
        new_status = get_selected_new_status_id()
        change_status_date = change_status_date_entry.entry.get()

        # Set focus to the Entry field
        rm_codes_combobox.focus_set()


        # Convert date to YYYY-MM-DD
        try:
            change_status_date = datetime.strptime(change_status_date, "%m/%d/%Y").strftime("%Y-%m-%d")
        except ValueError:
            Messagebox.show_error("Error", "Invalid date format. Please use MM/DD/YYYY.")
            return

        # Create a dictionary with the data
        data = {
            "rm_code_id": rm_code_id,
            "warehouse_id": warehouse_id,
            "current_status_id": current_status,
            "new_status_id": new_status,
            "ref_number": ref_number,
            "change_status_date": change_status_date,
            "qty_kg": qty
        }

        # Validate the data entries in front-end side
        if EntryValidation.entry_validation(data):
            error_text = EntryValidation.entry_validation(data)
            Messagebox.show_error(f"There is no data in these fields {error_text}.", "Data Entry Error", alert=True)
            return

        validatation_result = PrepValidation.validate_soh_value(
            rm_code_id,
            warehouse_id,
            qty,
            current_status
        )

        if validatation_result:

            # Send a POST request to the API
            try:
                response = requests.post(f"{server_ip}/api/change_status_form/v1/create/", json=data)
                if response.status_code == 200:  # Successfully created
                    clear_fields()
                    note_table.refresh_table()
            except requests.exceptions.RequestException as e:
                Messagebox.show_error(e, "Data Entry Error")

        else:
            Messagebox.show_error(
                "The entered quantity in 'Quantity' exceeds the available stock in the database.",
                "Data Entry Error")
            return

    # # Create a frame for the form inputs
    # form_frame = ttk.Frame(note_form_tab)
    # form_frame.pack(fill=X, pady=10, padx=20)
    #
    #
    # # Warehouse JSON-format choices (coming from the API)
    # warehouses = get_warehouse_api
    # warehouse_to_id = {item["wh_name"]: item["id"] for item in warehouses}
    # warehouse_names = list(warehouse_to_id.keys())
    #
    # # Combobox for Warehouse Drop Down
    # warehouse_label = ttk.Label(form_frame, text="Warehouse:", font=("Helvetica", 10, "bold"))
    # warehouse_label.grid(row=0, column=0, padx=5, pady=5, sticky=W)
    # warehouse_combobox = ttk.Combobox(
    #     form_frame,
    #     values=warehouse_names,
    #     state="readonly",
    #     width=30,
    # )
    # warehouse_combobox.grid(row=1, column=0, columnspan=2, pady=10, padx=10)
    # ToolTip(warehouse_combobox, text="Choose a warehouse")
    #
    # # Checkbox for Warehouse lock
    # checkbox_warehouse_var = ttk.IntVar()  # Integer variable to store checkbox state (0 or 1)
    # lock_warehouse = ttk.Checkbutton(
    #     form_frame,
    #     text="Lock Warehouse",
    #     variable=checkbox_warehouse_var,
    #     bootstyle="round-toggle"
    # )
    # lock_warehouse.grid(row=1, column=3, pady=10, padx=10, sticky=W)  # Position the checkbox next to the combobox
    # ToolTip(lock_warehouse, text="Lock the warehouse by clicking this")
    #
    # # REF Number Entry Field
    # ref_number_label = ttk.Label(form_frame, text="Reference Number:", font=("Helvetica", 10, "bold"))
    # ref_number_label.grid(row=2, column=0, padx=5, pady=5, sticky=W)
    # ref_number_entry = ttk.Entry(form_frame, width=30)
    # ref_number_entry.grid(row=3, column=0, padx=5, pady=5)
    # ToolTip(ref_number_entry, text="Enter the Reference Number")
    #
    # checkbox_reference_var = ttk.IntVar()  # Integer variable to store checkbox state (0 or 1)
    # # Checkbox beside the combobox
    # lock_reference = ttk.Checkbutton(
    #     form_frame,
    #     text="Lock Reference Number",
    #     variable=checkbox_reference_var,
    #     bootstyle="round-toggle"
    # )
    # lock_reference.grid(row=3, column=3, pady=10, padx=10, sticky=W)  # Position the checkbox next to the combobox
    # ToolTip(lock_reference, text="Lock the reference number by clicking this")
    #
    # #RM CODE JSON-format choices (coming from the API)
    # rm_codes = get_rm_code_api
    # code_to_id = {item["rm_code"]: item["id"] for item in rm_codes}
    # rm_names = list(code_to_id.keys())
    #
    #
    # # Function to convert typed input to uppercase
    # def on_combobox_key_release(event):
    #     # Get the current text in the combobox
    #     current_text = rm_codes_combobox.get()
    #     # Convert the text to uppercase and set it back
    #     rm_codes_combobox.set(current_text.upper())
    #
    # # Combobox for RM CODE Drop Down
    # rm_codes_label = ttk.Label(form_frame, text="Raw Material:", font=("Helvetica", 10, "bold"))
    # rm_codes_label.grid(row=4, column=0, padx=5, pady=5, sticky=W)
    #
    # rm_codes_combobox = ttk.Combobox(
    #     form_frame,
    #     values=rm_names,
    #     state="normal",
    #     width=30,
    # )
    #
    # # Bind the key release event to the combobox to trigger uppercase conversion
    # rm_codes_combobox.bind("<KeyRelease>", on_combobox_key_release)
    #
    # rm_codes_combobox.grid(row=5, column=0, columnspan=2, pady=10, padx=10)
    # ToolTip(rm_codes_combobox, text="Choose a raw material")
    #
    #
    # # Quantity Entry Field
    # # Register the validation command
    # validate_numeric_command = form_frame.register(EntryValidation.validate_numeric_input)
    #
    # qty_label = ttk.Label(form_frame, text="Quantity:", font=("Helvetica", 10, "bold"))
    # qty_label.grid(row=4, column=3, padx=5, pady=5, sticky=W)
    # qty_entry = ttk.Entry(form_frame,
    #                       width=30,
    #                       validate="key",  # Trigger validation on keystrokes
    #                       validatecommand=(validate_numeric_command, "%P")  # Pass the current widget content ("%P")
    # )
    # qty_entry.grid(row=5, column=3, padx=5, pady=5)
    # ToolTip(qty_entry, text="Enter the Quantity(kg)")
    #
    # # Date Entry field
    # date_label = ttk.Label(form_frame, text="Change Status Date:", font=("Helvetica", 10, "bold"))
    # date_label.grid(row=4, column=5, padx=5, pady=5, sticky=W)
    #
    # # Calculate yesterday's date
    # yesterday_date = datetime.now() - timedelta(days=1)
    #
    # # Create the DateEntry widget with yesterday's date as the default value
    # change_status_date_entry = ttk.DateEntry(
    #     form_frame,
    #     bootstyle=PRIMARY,
    #     dateformat="%m/%d/%Y",
    #     startdate=yesterday_date,  # Set yesterday's date
    #     width=30
    # )
    # change_status_date_entry.grid(row=5, column=5, padx=5, pady=5, sticky=W)
    # ToolTip(change_status_date_entry, text="Choose a change status date.")
    #
    #
    # # Warehouse JSON-format choices (coming from the API)
    # status = get_status_api
    # status_to_id = {item["name"]: item["id"] for item in status}
    # status_names = list(status_to_id.keys())
    #
    #
    # # Combobox for Current Status Drop Down
    # current_status_label = ttk.Label(form_frame, text="Current Status", font=("Helvetica", 10, "bold"))
    # current_status_label.grid(row=6, column=0, padx=5, pady=5, sticky=W)
    # current_status_combobox = ttk.Combobox(
    #     form_frame,
    #     values=status_names,
    #     state="readonly",
    #     width=30,
    # )
    # current_status_combobox.grid(row=7, column=0, columnspan=2, pady=10, padx=10)
    # ToolTip(current_status_combobox, text="Choose the current status")
    #
    #
    # # Combobox for Warehouse Drop Down
    # new_status_label = ttk.Label(form_frame, text="New Status", font=("Helvetica", 10, "bold"))
    # new_status_label.grid(row=6, column=3, padx=5, pady=5, sticky=W)
    # new_status_combobox = ttk.Combobox(
    #     form_frame,
    #     values=status_names,
    #     state="readonly",
    #     width=30,
    # )
    # new_status_combobox.grid(row=7, column=3, columnspan=2, pady=10, padx=10)
    # ToolTip(new_status_combobox, text="Choose a new status")
    #
    #
    # # Add button to submit data
    # btn_submit = ttk.Button(
    #     form_frame,
    #     text="+ Add",
    #     command=submit_data,
    #     width = 10
    # )
    # btn_submit.grid(row=7, column=5, padx=5, pady=5, sticky=W)
    # ToolTip(btn_submit, text="Click to add new record")

    # Create a frame for the form inputs
    form_frame = ttk.Frame(note_form_tab)
    form_frame.pack(fill=X, pady=10, padx=20)

    # Configure grid columns to make them behave correctly
    form_frame.grid_columnconfigure(0, weight=1)  # Left (Warehouse) stays at the left
    form_frame.grid_columnconfigure(1, weight=1)  # Right (Ref Number) is pushed to the right

    # Warehouse FRAME (Left-aligned)
    warehouse_frame = ttk.Frame(form_frame)
    warehouse_frame.grid(row=0, column=0, padx=5, pady=(0, 10), sticky="w")

    # Warehouse JSON-format choices (coming from the API)
    warehouses = get_warehouse_api
    warehouse_to_id = {item["wh_name"]: item["id"] for item in warehouses}
    warehouse_names = list(warehouse_to_id.keys())

    # Combobox for Warehouse Drop Down
    warehouse_label = ttk.Label(warehouse_frame, text="Warehouse", font=("Helvetica", 10, "bold"))
    warehouse_label.grid(row=0, column=0, padx=5, pady=(0, 0), sticky=W)

    # Checkbox for Warehouse lock
    checkbox_warehouse_var = ttk.IntVar()
    lock_warehouse = ttk.Checkbutton(
        warehouse_frame,
        text="Lock",
        variable=checkbox_warehouse_var,
        bootstyle="round-toggle"
    )
    lock_warehouse.grid(row=0, column=0, pady=(0, 0), padx=10, sticky=E)
    ToolTip(lock_warehouse, text="Lock the warehouse by clicking this")

    # Warehouse Combobox field
    warehouse_combobox = ttk.Combobox(warehouse_frame, values=warehouse_names, state="readonly", width=45)
    warehouse_combobox.grid(row=1, column=0, padx=10, pady=(0, 0), sticky=W)
    ToolTip(warehouse_combobox, text="Choose a warehouse")



    # Reference Number FRAME (Right-aligned)
    refno_frame = ttk.Frame(form_frame)
    refno_frame.grid(row=0, column=1, padx=5, pady=(0, 10), sticky="e")

    # REF Number Entry Field
    ref_number_label = ttk.Label(refno_frame, text="PF ID no.", font=("Helvetica", 10, "bold"))
    ref_number_label.grid(row=0, column=0, padx=5, pady=(0, 0), sticky=W)
    ref_number_entry = ttk.Entry(refno_frame, width=30)
    ref_number_entry.grid(row=1, column=0, padx=5, pady=(0, 0), sticky=W)
    ToolTip(ref_number_entry, text="Enter the Reference Number")

    checkbox_reference_var = ttk.IntVar()  # Integer variable to store checkbox state (0 or 1)

    # Checkbox beside the combobox
    lock_reference = ttk.Checkbutton(
        refno_frame,
        text="Lock",
        variable=checkbox_reference_var,
        bootstyle="round-toggle"
    )
    lock_reference.grid(row=0, pady=(0, 0), padx=10, sticky=E)  # Position the checkbox next to the combobox
    ToolTip(lock_reference, text="Lock the reference number by clicking this")

    # RM CODE FRAME
    rmcode_frame = ttk.Frame(form_frame)
    rmcode_frame.grid(row=1, column=0, padx=5, pady=(0, 10), sticky="w")

    # RM CODE JSON-format choices (coming from the API)
    rm_codes = get_rm_code_api
    code_to_id = {item["rm_code"]: item["id"] for item in rm_codes}
    rm_names = list(code_to_id.keys())

    # Function to convert typed input to uppercase
    def on_combobox_key_release(event):
        # Get the current text in the combobox
        current_text = rm_codes_combobox.get()
        # Convert the text to uppercase and set it back
        rm_codes_combobox.set(current_text.upper())

    # Combobox for RM CODE Drop Down
    rm_codes_label = ttk.Label(rmcode_frame, text="Raw Material", font=("Helvetica", 10, "bold"))
    rm_codes_label.grid(row=0, column=0, padx=5, pady=(0, 0), sticky=W)

    rm_codes_combobox = ttk.Combobox(
        rmcode_frame,
        values=rm_names,
        state="normal",
        width=25,
    )

    # Bind the key release event to the combobox to trigger uppercase conversion
    rm_codes_combobox.bind("<KeyRelease>", on_combobox_key_release)

    rm_codes_combobox.grid(row=1, column=0, pady=(0, 0), padx=(10, 0))
    ToolTip(rm_codes_combobox, text="Choose a raw material")

    # Register the validation command

    validate_numeric_command = rmcode_frame.register(EntryValidation.validate_numeric_input)

    # Quantity Entry Field
    qty_label = ttk.Label(rmcode_frame, text="Quantity", font=("Helvetica", 10, "bold"))
    qty_label.grid(row=0, column=1, padx=2, pady=(0, 0), sticky=W)
    qty_entry = ttk.Entry(rmcode_frame,
                          width=17,
                          validate="key",  # Trigger validation on keystrokes
                          validatecommand=(validate_numeric_command, "%P")  # Pass the current widget content ("%P")
                          )
    qty_entry.grid(row=1, column=1, padx=2, pady=(0, 0), sticky=W)
    ToolTip(qty_entry, text="Enter the Quantity(kg)")




    # STATUS FRAME
    status_frame = ttk.Frame(form_frame)
    status_frame.grid(row=2, column=0, padx=5, pady=(0, 10), sticky="w")

    # Warehouse JSON-format choices (coming from the API)
    status = get_status_api
    status_to_id = {item["name"]: item["id"] for item in status}
    status_names = list(status_to_id.keys())


    # Combobox for Current Status Drop Down
    current_status_label = ttk.Label(status_frame, text="Current Status", font=("Helvetica", 10, "bold"))
    current_status_label.grid(row=2, column=0, padx=5, pady=(0,0), sticky=W)
    current_status_combobox = ttk.Combobox(
        status_frame,
        values=status_names,
        state="readonly",
        width=20,
    )
    current_status_combobox.grid(row=3, column=0, pady=0, padx=(10,2), sticky=W)
    ToolTip(current_status_combobox, text="Choose the current status")


    # Combobox for Warehouse Drop Down
    new_status_label = ttk.Label(status_frame, text="New Status", font=("Helvetica", 10, "bold"))
    new_status_label.grid(row=2, column=1, padx=(0,0), pady=(0,0), sticky=W)
    new_status_combobox = ttk.Combobox(
        status_frame,
        values=status_names,
        state="readonly",
        width=20,
    )
    new_status_combobox.grid(row=3, column=1, pady=0, padx=0, sticky=W)
    ToolTip(new_status_combobox, text="Choose a new status")


    # DATE FRAME
    date_frame = ttk.Frame(form_frame)
    date_frame.grid(row=1, column=1, padx=5, pady=(0, 10), sticky="e")

    # Date Entry field
    date_label = ttk.Label(date_frame, text="Change Status Date", font=("Helvetica", 10, "bold"))
    date_label.grid(row=0, column=0, padx=5, pady=0, sticky=W)
    # Calculate yesterday's date
    yesterday_date = datetime.now() - timedelta(days=1)

    # Create the DateEntry widget with yesterday's date as the default value
    change_status_date_entry = ttk.DateEntry(
        date_frame,
        bootstyle=PRIMARY,
        dateformat="%m/%d/%Y",
        startdate=yesterday_date,  # Set yesterday's date
        width=25
    )
    change_status_date_entry.grid(row=1, column=0, padx=5, pady=0, sticky=W)

    ToolTip(change_status_date_entry, text="Please enter the change status date.")

    # Add button to submit data
    btn_submit = ttk.Button(
        form_frame,
        text="+ Add",
        command=submit_data,
    )
    btn_submit.grid(row=3, column=0, columnspan=3, pady=0, padx=400, sticky=NSEW)
    ToolTip(btn_submit, text="Click this add button to add the entry to the list")




    # Calling the table
    note_table = NoteTable(note_form_tab)

