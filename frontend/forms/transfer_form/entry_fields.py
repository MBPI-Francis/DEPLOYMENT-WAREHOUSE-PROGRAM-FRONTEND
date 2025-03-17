import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import requests
from backend.settings.database import server_ip
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.dialogs.dialogs import Messagebox
from datetime import datetime, timedelta

from frontend.forms.shared import SharedFunctions
from frontend.forms.transfer_form.table import TransferFormTable
from frontend.forms.transfer_form.validation import EntryValidation as TranferValidation
from tkinter import StringVar
from frontend.forms.preparation_form.validation import EntryValidation as PrepValidation
from uuid import  UUID

def entry_fields(note_form_tab):

    # Instantiate the shared_function class
    shared_functions = SharedFunctions()

    get_warehouse_api = shared_functions.get_warehouse_api()
    get_rm_code_api = shared_functions.get_rm_code_api()
    get_status_api = shared_functions.get_status_api()


    def get_selected_warehouse_from_id():
        selected_name = warehouse_from_combobox.get()
        selected_id = warehouse_to_id.get(selected_name)  # Get the corresponding ID
        if selected_id:
            return selected_id
        else:
            return None

    def get_selected_status_id():
        selected_name = status_combobox.get()
        selected_id = status_to_id.get(selected_name)  # Get the corresponding ID
        if selected_id:
            return selected_id
        else:
            return None

    def get_selected_warehouse_to_id():
        selected_name = warehouse_to_combobox.get()
        selected_id = warehouse_to_id.get(selected_name)  # Get the corresponding ID
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
            warehouse_from_combobox.set("")
            warehouse_to_combobox.set("")

        status_combobox.set("")
        rm_codes_combobox.set("")
        qty_entry.delete(0, ttk.END)

    def check_raw_material(rm_id: UUID, warehouse_id: UUID, status_id: UUID = None):
        url = f"{server_ip}/api/check/raw_material/"  # Replace with the actual URL of your FastAPI server

        # Construct the query parameters
        params = {
            "rm_id": str(rm_id),  # Convert UUID to string for query parameter
            "warehouse_id": str(warehouse_id),
        }

        # Include status_id only if it's not None
        if status_id:
            params["status_id"] = status_id
        # Handle response

        try:
            # Send the GET request
            response = requests.get(url, params=params)

            # Check if the response was successful
            if response.status_code == 200:
                # Parse the response data (True or False)
                return response.json()  # This will return either True or False
            else:
                # Handle errors
                print(f"Error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return False


    def submit_data():

        # Collect the form data
        warehouse_from_id = get_selected_warehouse_from_id()
        warehouse_to_id = get_selected_warehouse_to_id()

        # Validation for the two warehouse choices
        if warehouse_from_id == warehouse_to_id:
            Messagebox.show_error("The Warehouse (FROM) and Warehouse (TO) should be different.", "Data Entry Error")
            return

        rm_code_id = get_selected_rm_code_id()
        status_id = get_selected_status_id()
        ref_number = ref_number_entry.get()
        qty = qty_entry.get()
        transfer_date = transfer_date_entry.entry.get()


        # Set focus to the Entry field
        rm_codes_combobox.focus_set()

        # Convert date to YYYY-MM-DD
        try:
            transfer_date = datetime.strptime(transfer_date, "%m/%d/%Y").strftime("%Y-%m-%d")
        except ValueError:
            Messagebox.show_error("Error", "Invalid date format. Please use MM/DD/YYYY.")
            return

        # Create a dictionary with the data
        data = {
            "rm_code_id": rm_code_id,
            "from_warehouse_id": warehouse_from_id,
            "to_warehouse_id": warehouse_to_id,
            "ref_number": ref_number,
            "status_id": status_id,
            "transfer_date": transfer_date,
            "qty_kg": qty,
        }
        # Validate the data entries in front-end side
        if TranferValidation.entry_validation(data):
            error_text = TranferValidation.entry_validation(data)
            Messagebox.show_error(f"There is no data in these fields {error_text}.", "Data Entry Error", alert=True)
            return

        # Check if the record is existing in the inventory
        # Call the check_raw_material function
        result = check_raw_material(rm_code_id, warehouse_from_id, status_id)
        # Display the result in the GUI
        if result:

            # Validate if the entry value exceeds the stock
            validatation_result = PrepValidation.validate_soh_value(
                rm_code_id,
                warehouse_from_id,
                qty,
                status_id
            )

            if validatation_result:
                    # Send a POST request to the API
                try:
                    response = requests.post(f"{server_ip}/api/transfer_forms/v1/create/", json=data)
                    if response.status_code == 200:  # Successfully created
                        clear_fields()

                        note_table.refresh_table()
                        # refresh_table()  # Refresh the table
                except requests.exceptions.RequestException as e:
                    Messagebox.show_info(e, "Data Entry Error")

            else:
                Messagebox.show_error(
                    "The entered quantity in 'Quantity' exceeds the available stock in the database.",
                    "Data Entry Error")
                return

        else:
            Messagebox.show_error(f"The raw material record is not existing in the database.", "Failed Transfer.", alert=True)
            return


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



    # Warehouse FROM
    warehouse_from_label = ttk.Label(warehouse_frame, text="Warehouse (FROM)", font=("Helvetica", 10, "bold"))
    warehouse_from_label.grid(row=0, column=0, padx=5, pady=(0, 0), sticky=W)

    warehouse_from_combobox = ttk.Combobox(
        warehouse_frame,
        values=warehouse_names,
        state="readonly",
        width=41,
    )
    warehouse_from_combobox.grid(row=1, column=0, padx=10, pady=(0, 0), sticky=W)
    ToolTip(warehouse_from_combobox, text="Choose a warehouse where the raw material is coming from")

    # Warehouse TO
    warehouse_to_label = ttk.Label(warehouse_frame, text="Warehouse (TO)", font=("Helvetica", 10, "bold"))
    warehouse_to_label.grid(row=0, column=1, padx=5, pady=(0, 0), sticky=W)


    warehouse_to_combobox = ttk.Combobox(
        warehouse_frame,
        values=warehouse_names,
        state="readonly",
        width=36,
    )
    warehouse_to_combobox.grid(row=1, column=1, padx=10, pady=(0, 0), sticky=W)
    ToolTip(warehouse_to_combobox, text="Choose a warehouse where the raw material is transferred to")

    # Lock Warehouse Checkbox
    checkbox_warehouse_var = ttk.IntVar()
    lock_warehouse = ttk.Checkbutton(
        warehouse_frame,
        text="Lock",
        variable=checkbox_warehouse_var,
        bootstyle="round-toggle"
    )
    lock_warehouse.grid(row=1, column=2, pady=5, padx=5, sticky=W)
    ToolTip(lock_warehouse, text="Lock the warehouse by clicking this")




    # Reference Number FRAME (Right-aligned)
    refno_frame = ttk.Frame(form_frame)
    refno_frame.grid(row=0, column=2, padx=5, pady=(0, 10), sticky="e")

    # REF Number Entry Field
    ref_number_label = ttk.Label(refno_frame, text="Reference no.", font=("Helvetica", 10, "bold"))
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
        width=23,
    )

    # Bind the key release event to the combobox to trigger uppercase conversion
    rm_codes_combobox.bind("<KeyRelease>", on_combobox_key_release)

    rm_codes_combobox.grid(row=1, column=0, columnspan=2, pady=(0, 0), padx=(10, 0))
    ToolTip(rm_codes_combobox, text="Choose a raw material")

    # Register the validation command
    validate_numeric_command = form_frame.register(TranferValidation.validate_numeric_input)

    # Quantity Entry Field
    qty_label = ttk.Label(rmcode_frame, text="Quantity", font=("Helvetica", 10, "bold"))
    qty_label.grid(row=0, column=2, padx=2, pady=(0, 0), sticky=W)
    qty_entry = ttk.Entry(rmcode_frame,
                          width=15,
                          validate="key",  # Trigger validation on keystrokes
                          validatecommand=(validate_numeric_command, "%P")  # Pass the current widget content ("%P")
                          )
    qty_entry.grid(row=1, column=2, padx=2, pady=(0, 0), sticky=W)
    ToolTip(qty_entry, text="Enter the Quantity(kg)")


     # Status JSON-format choices (coming from the API)
    status = get_status_api
    status_to_id = {item["name"]: item["id"] for item in status}
    status_names = list(status_to_id.keys())

    status_label = ttk.Label(rmcode_frame, text="Status", font=("Helvetica", 10, "bold"))
    status_label.grid(row=0, column=3, padx=(20,0), pady=(0, 0), sticky=W)

    status_combobox = ttk.Combobox(
        rmcode_frame,
        values=status_names,
        state="readonly",
        width=36,
    )
    status_combobox.grid(row=1, column=3, padx=(20,0), pady=(0, 0), sticky=W)
    ToolTip(status_combobox, text="Please choose the raw material status")



    date_frame = ttk.Frame(form_frame)
    date_frame.grid(row=1, column=2, padx=5, pady=(0, 10), sticky="e")

    # Date Entry field
    date_label = ttk.Label(date_frame, text="Transfer Date", font=("Helvetica", 10, "bold"))
    date_label.grid(row=0, column=0, padx=5, pady=0, sticky=W)

    # Calculate yesterday's date
    yesterday_date = datetime.now() - timedelta(days=1)

    # Create the DateEntry widget with yesterday's date as the default value
    transfer_date_entry = ttk.DateEntry(
        date_frame,
        bootstyle=PRIMARY,
        dateformat="%m/%d/%Y",
        startdate=yesterday_date,  # Set yesterday's date
        width=25
    )
    transfer_date_entry.grid(row=1, column=0, padx=5, pady=0, sticky=W)
    ToolTip(transfer_date_entry, text="Please enter the transfer date.")


    # Add button to submit data
    btn_submit = ttk.Button(
        form_frame,
        text="+ Add",
        command=submit_data,
    )
    btn_submit.grid(row=2, column=0, columnspan=3, pady=0, padx=400, sticky=NSEW)
    ToolTip(btn_submit, text="Click this add button to add the entry to the list")

    # Calling the table
    note_table = TransferFormTable(note_form_tab)



