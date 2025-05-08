import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import requests
import tkinter as tk
from backend.settings.database import server_ip
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.dialogs.dialogs import Messagebox
from datetime import datetime, timedelta
from .table import ChangeStatusFormTable
from .validation import EntryValidation

from tkinter import StringVar

from ..shared import SharedFunctions


def entry_fields(note_form_tab):
    shared_functions = SharedFunctions()

    get_status_api = shared_functions.get_status_api()
    get_rm_code_api = shared_functions.get_rm_code_api(force_refresh=True)
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

        if not checkbox_status_var.get():
            current_status_combobox.set("")
            new_status_combobox.set("")

        rm_codes_combobox.set("")
        qty_entry.delete(0, ttk.END)


    def submit_data():

        # Collect the form data
        warehouse_id = get_selected_warehouse_id()
        rm_code_id = get_selected_rm_code_id()
        ref_number = ref_number_entry.get()

        qty = qty_entry.get()

        if qty is None or qty == '':
            qty = '0'

        cleaned_qty = float(qty.replace(",", ""))

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
            Messagebox.show_error("Invalid date format. Please use MM/DD/YYYY.", "Date Entry Error")
            return

        # Create a dictionary with the data
        data = {
            "rm_code_id": rm_code_id,
            "warehouse_id": warehouse_id,
            "current_status_id": current_status,
            "new_status_id": new_status,
            "ref_number": ref_number,
            "change_status_date": change_status_date,
            "qty_kg": cleaned_qty
        }

        # Validate the data entries in front-end side
        if EntryValidation.entry_validation(data):
            error_text = EntryValidation.entry_validation(data)
            Messagebox.show_error(f"There is no data in these fields {error_text}.", "Data Entry Error", alert=True)
            return

        validatation_result = shared_functions.validate_soh_value(
            rm_code_id,
            warehouse_id,
            cleaned_qty,
            current_status
        )

        if validatation_result:

            # Send a POST request to the API
            try:
                response = requests.post(f"{server_ip}/api/change_status_form/v1/create/", json=data)
                if response.status_code == 200:  # Successfully created
                    clear_fields()
                    change_status_table.refresh_table()

                    # Get the last inserted row ID
                    last_row_id = change_status_table.tree.get_children()[0]  # Get the last row's ID

                    # Highlight the last row
                    change_status_table.tree.selection_set(last_row_id)  # Select the last row
                    change_status_table.tree.focus(last_row_id)  # Focus on the last row
                    change_status_table.tree.see(last_row_id)  # Scroll to make it visible


            except requests.exceptions.RequestException as e:
                Messagebox.show_error(e, "Data Entry Error")

        else:
            Messagebox.show_error(
                "The entered quantity in 'Quantity' exceeds the available stock in the database.",
                "Data Entry Error")
            return



    # Create a frame for the form inputs
    change_status_form_frame = ttk.Frame(note_form_tab)
    change_status_form_frame.pack(fill=X, pady=10, padx=20)

    # Configure grid columns to make them behave correctly
    change_status_form_frame.grid_columnconfigure(0, weight=1)  # Left (Warehouse) stays at the left
    change_status_form_frame.grid_columnconfigure(1, weight=1)  # Right (Ref Number) is pushed to the right

    # Warehouse FRAME (Left-aligned)
    warehouse_frame = ttk.Frame(change_status_form_frame)
    warehouse_frame.grid(row=0, column=0, padx=5, pady=(0, 10), sticky="w")

    # Warehouse JSON-format choices (coming from the API)
    warehouses = get_warehouse_api
    warehouse_to_id = {item["wh_name"]: item["id"] for item in warehouses}
    warehouse_names = list(warehouse_to_id.keys())

    # Combobox for Warehouse Drop Down
    warehouse_label = ttk.Label(warehouse_frame, text="Warehouse", style="CustomLabel.TLabel")
    warehouse_label.grid(row=0, column=0, padx=5, pady=(0, 0), sticky=W)

    # Checkbox for Warehouse lock
    checkbox_warehouse_var = ttk.IntVar()
    lock_warehouse = ttk.Checkbutton(
        warehouse_frame,

        variable=checkbox_warehouse_var,
        bootstyle="round-toggle"
    )
    lock_warehouse.grid(row=0, column=0, pady=(0, 0), padx=10, sticky=E)
    ToolTip(lock_warehouse, text="Lock the warehouse by clicking this")

    # Warehouse Combobox field
    warehouse_combobox = ttk.Combobox(warehouse_frame, values=warehouse_names, state="readonly", width=45,
                                      font=shared_functions.custom_font_size)
    warehouse_combobox.grid(row=1, column=0, padx=10, pady=(0, 0), sticky=W)
    ToolTip(warehouse_combobox, text="Choose a warehouse")



    # Reference Number FRAME (Right-aligned)
    refno_frame = ttk.Frame(change_status_form_frame)
    refno_frame.grid(row=1, column=1, padx=5, pady=(0, 10), sticky="e")


    # REF Number Entry Field
    ref_number_label = ttk.Label(refno_frame, text="CSF No.", style="CustomLabel.TLabel")
    ref_number_label.grid(row=0, column=0, padx=5, pady=(0, 0), sticky=W)
    ref_number_entry = ttk.Entry(refno_frame, width=30, font=shared_functions.custom_font_size)
    ref_number_entry.grid(row=1, column=0, padx=5, pady=(0, 0), sticky=W)
    ToolTip(ref_number_entry, text="Enter the Change Status Form number")

    checkbox_reference_var = ttk.IntVar()  # Integer variable to store checkbox state (0 or 1)

    # Checkbox beside the combobox
    lock_reference = ttk.Checkbutton(
        refno_frame,

        variable=checkbox_reference_var,
        bootstyle="round-toggle"
    )
    lock_reference.grid(row=0, pady=(0, 0), padx=10, sticky=E)  # Position the checkbox next to the combobox
    ToolTip(lock_reference, text="Lock the CSF No. by clicking this")

    # RM CODE FRAME
    rmcode_frame = ttk.Frame(change_status_form_frame)
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
    rm_codes_label = ttk.Label(rmcode_frame, text="Raw Material", style="CustomLabel.TLabel")
    rm_codes_label.grid(row=0, column=0, padx=5, pady=(0, 0), sticky=W)

    rm_codes_combobox = ttk.Combobox(
        rmcode_frame,
        values=rm_names,
        state="normal",
        width=25,
        font=shared_functions.custom_font_size
    )

    # Bind the key release event to the combobox to trigger uppercase conversion
    rm_codes_combobox.bind("<KeyRelease>", on_combobox_key_release)

    rm_codes_combobox.grid(row=1, column=0, pady=(0, 0), padx=(10, 0))
    ToolTip(rm_codes_combobox, text="Choose a raw material")

    # Register the validation command
    # Function to format numeric input dynamically with cursor preservation
    def format_numeric_input(event):
        """
        Formats the input dynamically while preserving the cursor position.
        """
        input_value = qty_var.get()

        # Get current cursor position
        cursor_position = qty_entry.index("insert")

        # Remove commas for processing
        raw_value = input_value.replace(",", "")

        if raw_value == "" or raw_value == ".":
            return  # Prevent formatting when only `.` is typed

        try:
            if "." in raw_value and raw_value[-1] == ".":
                return  # Allow user to manually enter decimal places

            # Convert input to float and format
            float_value = float(raw_value)

            if "." in raw_value:
                integer_part, decimal_part = raw_value.split(".")
                formatted_integer = "{:,}".format(int(integer_part))  # Format integer part with commas
                formatted_value = f"{formatted_integer}.{decimal_part}"  # Preserve user-entered decimal part
            else:
                formatted_value = "{:,}".format(int(float_value))  # Format whole number

            # Adjust cursor position based on new commas added
            num_commas_before = input_value[:cursor_position].count(",")
            num_commas_after = formatted_value[:cursor_position].count(",")

            new_cursor_position = cursor_position + (num_commas_after - num_commas_before)

            # Prevent cursor jumping by resetting the value and restoring cursor position
            qty_entry.delete(0, "end")
            qty_entry.insert(0, formatted_value)
            qty_entry.icursor(new_cursor_position)  # Restore cursor position
        except ValueError:
            pass  # Ignore invalid input

    # Tkinter StringVar for real-time updates
    qty_var = StringVar()

    # Validation Command for Entry Widget
    validate_numeric_command = rmcode_frame.register(EntryValidation.validate_numeric_input)

    # Quantity Entry Field
    qty_label = ttk.Label(rmcode_frame, text="Quantity(kg)", style="CustomLabel.TLabel")
    qty_label.grid(row=0, column=2, padx=2, pady=(0, 0), sticky=W)

    qty_entry = ttk.Entry(rmcode_frame,
                          width=17,
                          font=shared_functions.custom_font_size,
                          textvariable=qty_var,
                          validate="key",
                          validatecommand=(validate_numeric_command, "%P"))  # Pass input for validation
    qty_entry.grid(row=1, column=2, padx=2, pady=(0, 0), sticky=W)
    # Bind the event to format input dynamically while preserving cursor position
    qty_entry.bind("<KeyRelease>", format_numeric_input)
    ToolTip(qty_entry, text="Enter the Quantity(kg)")



    # STATUS FRAME
    status_frame = ttk.Frame(change_status_form_frame)
    status_frame.grid(row=2, column=0, padx=5, pady=(0, 10), sticky="w")

    # Warehouse JSON-format choices (coming from the API)
    status = get_status_api
    status_to_id = {item["name"]: item["id"] for item in status}
    status_names = list(status_to_id.keys())


    # Combobox for Previous Status Drop Down
    current_status_label = ttk.Label(status_frame, text="Previous Status", style="CustomLabel.TLabel")
    current_status_label.grid(row=2, column=0, padx=5, pady=(0,0), sticky=W)
    current_status_combobox = ttk.Combobox(
        status_frame,
        values=status_names,
        state="readonly",
        width=20,
        font=shared_functions.custom_font_size
    )
    current_status_combobox.grid(row=3, column=0, pady=0, padx=(10,2), sticky=W)
    ToolTip(current_status_combobox, text="Choose the previous status")


    # Combobox for Warehouse Drop Down
    new_status_label = ttk.Label(status_frame, text="Present Status", style="CustomLabel.TLabel")
    new_status_label.grid(row=2, column=1, padx=(0,0), pady=(0,0), sticky=W)
    new_status_combobox = ttk.Combobox(
        status_frame,
        values=status_names,
        state="readonly",
        width=20,
        font=shared_functions.custom_font_size
    )
    new_status_combobox.grid(row=3, column=1, pady=0, padx=0, sticky=W)
    ToolTip(new_status_combobox, text="Choose the present status")

    checkbox_status_var = ttk.IntVar()  # Integer variable to store checkbox state (0 or 1)

    # Checkbox beside the combobox
    lock_status = ttk.Checkbutton(
        status_frame,
        variable=checkbox_status_var,
        bootstyle="round-toggle"
    )
    lock_status.grid(row=2, column=1, pady=(0, 0), padx=(0,0), sticky=E)  # Position the checkbox next to the combobox
    ToolTip(lock_status, text="Lock both Previous and Present Status by clicking this")



    def format_date_while_typing(event):
        """Auto-formats the date entry while typing, ensuring valid MM/DD/YYYY format."""
        text = change_status_date_entry.entry.get().replace("/", "")  # Remove slashes to get raw number input
        formatted_date = ""

        if len(text) > 8:  # Prevent overflow of more than 8 characters (MMDDYYYY)
            text = text[:8]

        # Handle the case where the length is 2 (MD)
        if len(text) == 2:
            month = text[:1]
            day = text[1:]
            # Ensure the month is valid (01-12)
            if int(month) < 1 or int(month) > 12:
                month = str(datetime.now().month)  # Default to January if invalid month
            # Ensure the day is valid (01-31)
            if int(day) < 1 or int(day) > 31:
                day = str(datetime.now().day)  # Default to 1st if invalid day
            year = str(datetime.now().year)  # Assume the current year
            formatted_date = f"0{month}/0{day}/{year}"


        # Handle the case where the length is 3 (MDD)
        elif len(text) == 3:
            month = text[:1]
            day = text[1:]
            # Ensure the month is valid (01-12)
            if int(month) < 1 or int(month) > 12:
                month = str(datetime.now().month)  # Default to January if invalid month
            # Ensure the day is valid (01-31)
            if int(day) < 1 or int(day) > 31:
                day = str(datetime.now().day)  # Default to 1st if invalid day
                if len(str(day)) == 1:
                    day = f"0{day}"

            year = str(datetime.now().year)  # Assume the current year
            formatted_date = f"0{month}/{day}/{year}"


        # Handle the case where the length is 4 (MMDD)
        elif len(text) == 4:
            month = text[:2]
            day = text[2:]
            # Ensure the month is valid (01-12)
            if int(month) < 1 or int(month) > 12:
                month = str(datetime.now().month)  # Default to January if invalid month
                if len(str(month)) == 1:
                    month = f"0{month}"

            # Ensure the day is valid (01-31)
            if int(day) < 1 or int(day) > 31:
                day = str(datetime.now().day)  # Default to 1st if invalid day
                if len(str(day)) == 1:
                    day = f"0{day}"

            year = str(datetime.now().year)  # Assume the current year
            formatted_date = f"{month}/{day}/{year}"

            # Handle the case where the length is 5 (MDDYY)
        elif len(text) == 5:
            month = text[:1]
            day = text[1:3]
            year = text[3:]

            # Ensure the month is valid (01-12)
            if int(month) < 1 or int(month) > 12:
                month = str(datetime.now().month)  # Default to January if invalid month
            # Ensure the day is valid (01-31)
            if int(day) < 1 or int(day) > 31:
                day = str(datetime.now().day)  # Default to 1st if invalid day
                if len(str(day)) == 1:
                    day = f"0{day}"
            formatted_date = f"0{month}/{day}/20{year}"

        # Handle the case where the length is 6 (MMDDYY)
        elif len(text) == 6:
            month = text[:2]
            day = text[2:4]
            year = text[4:]
            # Ensure the month is valid (01-12)
            if int(month) < 1 or int(month) > 12:
                month = str(datetime.now().month)  # Default to January if invalid month
                if len(str(month)) == 1:
                    month = f"0{month}"

            # Ensure the day is valid (01-31)
            if int(day) < 1 or int(day) > 31:
                day = str(datetime.now().day)  # Default to 1st if invalid day
                if len(str(day)) == 1:
                    day = f"0{day}"

            formatted_date = f"{month}/{day}/20{year}"  # Assume 20XX for 2-digit year


            # Handle the case where the length is 6 (MMDDYY)
        elif len(text) == 7:
            Messagebox.show_error("Invalid date format. Please use MM/DD/YYYY.", "Date Entry Error")


        # Handle the case where the length is 8 (MMDDYYYY)
        elif len(text) == 8:
            month = text[:2]
            day = text[2:4]
            year = text[4:]
            # Ensure the month is valid (01-12)
            if int(month) < 1 or int(month) > 12:
                month = str(datetime.now().month)  # Default to January if invalid month
                if len(str(month)) == 1:
                    month = f"0{month}"

            # Ensure the day is valid (01-31)
            if int(day) < 1 or int(day) > 31:
                day = str(datetime.now().day)  # Default to 1st if invalid day
                if len(str(day)) == 1:
                    day = f"0{day}"

            formatted_date = f"{month}/{day}/{year}"

        # Update entry field with formatted value
        change_status_date_entry.entry.delete(0, "end")
        change_status_date_entry.entry.insert(0, formatted_date)


    # DATE FRAME
    date_frame = ttk.Frame(change_status_form_frame)
    date_frame.grid(row=0, column=1, padx=5, pady=(0, 10), sticky="e")

    # Date Entry field
    date_label = ttk.Label(date_frame, text="Change Status Date", style="CustomLabel.TLabel")
    date_label.grid(row=0, column=0, padx=5, pady=0, sticky=W)
    # Calculate yesterday's date
    yesterday_date = datetime.now() - timedelta(days=1)

    # Create the DateEntry widget with yesterday's date as the default value
    change_status_date_entry = ttk.DateEntry(
        date_frame,
        bootstyle=PRIMARY,
        dateformat="%m/%d/%Y",
        startdate=yesterday_date,  # Set yesterday's date
        width=26
    )
    change_status_date_entry.grid(row=1, column=0, padx=5, pady=0, sticky=W)
    change_status_date_entry.entry.config(font=shared_functions.custom_font_size)
    ToolTip(change_status_date_entry, text="Please enter the change status date.")
    change_status_date_entry.entry.bind("<FocusOut>", format_date_while_typing)
    change_status_date_entry.entry.bind("<Return>", format_date_while_typing)

    # Add button to submit data
    btn_add_change_status = ttk.Button(
        change_status_form_frame,
        text="+ Add",
        command=submit_data,
    )
    btn_add_change_status.grid(row=3, column=0, columnspan=3, pady=0, padx=400, sticky=NSEW)
    ToolTip(btn_add_change_status, text="Click this add button to add the entry to the list")
    
    
    def bind_shift_enter_to_all_children(parent, callback):
        for child in parent.winfo_children():
            try:
                child.bind("<Shift-Return>", callback)
            except:
                pass
            # Recursively bind if the child is a container
            if isinstance(child, (ttk.Frame, tk.Frame)):
                bind_shift_enter_to_all_children(child, callback)

    # Bind Shift+Enter to all child widgets in this tab
    bind_shift_enter_to_all_children(change_status_form_frame, lambda e: btn_add_change_status.invoke())



    def bind_shift_a_to_toggle_checkbox(parent, toggle_func):
        for child in parent.winfo_children():
            try:
                child.bind("<Control-Shift-A>", toggle_func)
                child.bind("<Control-Shift-a>", toggle_func)
            except:
                pass
            if isinstance(child, (ttk.Frame, tk.Frame)):
                bind_shift_a_to_toggle_checkbox(child, toggle_func)

    def toggle_warehouse_lock(event=None):
        current_state_warehouse = checkbox_warehouse_var.get()
        current_state_reference = checkbox_reference_var.get()
        current_state_status = checkbox_status_var.get()


        # If any checkbox is unchecked, set all to True (1)
        if not all([current_state_warehouse, current_state_reference, current_state_status]):
            checkbox_warehouse_var.set(1)
            checkbox_reference_var.set(1)
            checkbox_status_var.set(1)
        else:
            checkbox_warehouse_var.set(0)
            checkbox_reference_var.set(0)
            checkbox_status_var.set(0)

    bind_shift_a_to_toggle_checkbox(change_status_form_frame, toggle_warehouse_lock)

    # Calling the table
    change_status_table = ChangeStatusFormTable(note_form_tab)

