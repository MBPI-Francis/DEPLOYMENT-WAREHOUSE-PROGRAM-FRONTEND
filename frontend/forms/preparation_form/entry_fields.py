from tkinter import StringVar

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import requests
from backend.settings.database import server_ip
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.dialogs.dialogs import Messagebox
from datetime import datetime, timedelta
from .table import PreparationFormTable
from .validation import EntryValidation
from frontend.forms.shared import SharedFunctions


def entry_fields(note_form_tab):

    preparation_validation = EntryValidation()
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
            status_combobox.set("")

        rm_codes_combobox.set("")
        qty_prepared_entry.delete(0, ttk.END)
        qty_return_entry.delete(0, ttk.END)

    def get_selected_status_id():
        selected_name = status_combobox.get()
        selected_id = status_to_id.get(selected_name)  # Get the corresponding ID
        if selected_id:
            return selected_id
        else:
            return None


    def submit_data():

        # Collect the form data
        warehouse_id = get_selected_warehouse_id()
        rm_code_id = get_selected_rm_code_id()
        ref_number = ref_number_entry.get()
        qty_prepared = qty_prepared_entry.get()
        qty_return = qty_return_entry.get()


        # If the user didn't enter a value in the qty return field, then it will store 0.00 value in the variable
        if qty_return == None or qty_return == '':
            qty_return = '0'


        if qty_prepared is None or qty_prepared == '':
            qty_prepared = '0'


        # This code removes the commas in the qty value
        cleaned_qty_prepared = float(qty_prepared.replace(",", ""))
        cleaned_qty_return = float(qty_return.replace(",", ""))


        preparation_date = preparation_date_entry.entry.get()
        status_id = get_selected_status_id()

        # Set focus to the Entry field
        rm_codes_combobox.focus_set()

        # Convert date to YYYY-MM-DD
        try:
            preparation_date = datetime.strptime(preparation_date, "%m/%d/%Y").strftime("%Y-%m-%d")
        except ValueError:
            Messagebox.show_error("Invalid date format. Please use MM/DD/YYYY.", "Date Entry Error")
            return

        # Create a dictionary with the data
        data = {
            "rm_code_id": rm_code_id,
            "warehouse_id": warehouse_id,
            "ref_number": ref_number,
            "status_id": status_id,
            "preparation_date": preparation_date,
            "qty_prepared": cleaned_qty_prepared,
            "qty_return": cleaned_qty_return,
        }


        if cleaned_qty_return > cleaned_qty_prepared:
            Messagebox.show_error(
                "Cannot add the record because the QTY (Return) exceeds the QTY (Prepared). "
                "Make sure the value of QTY (Prepared) is higher than the QTY (Return)",
                "Data Entry Error",
                alert=True
            )
            return


        # Validate the data entries in front-end side
        if EntryValidation.entry_validation(data):
            error_text = EntryValidation.entry_validation(data)
            Messagebox.show_error(f"There is no data in these fields {error_text}.", "Data Entry Error", alert=True)
            return

        validatation_result = preparation_validation.validate(
            rm_code_id,
            warehouse_id,
            cleaned_qty_prepared,
            cleaned_qty_return,
            status_id
        )
        if validatation_result:
            # Send a POST request to the API
            try:
                response = requests.post(f"{server_ip}/api/preparation_forms/v1/create/", json=data)
                if response.status_code == 200:  # Successfully created
                    clear_fields()
                    prepration_form_table.refresh_table()
                    # refresh_table()  # Refresh the table

                    # Get the last inserted row ID
                    last_row_id = prepration_form_table.tree.get_children()[0]  # Get the last row's ID

                    # Highlight the last row
                    prepration_form_table.tree.selection_set(last_row_id)  # Select the last row
                    prepration_form_table.tree.focus(last_row_id)  # Focus on the last row
                    prepration_form_table.tree.see(last_row_id)  # Scroll to make it visible

            except requests.exceptions.RequestException as e:
                Messagebox.show_error(e, "Data Entry Error")

        else:
            Messagebox.show_error(
                "The consumption of the raw material exceeds the available stock in the database.",
                "Data Entry Error")
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
    lock_warehouse.grid(row=0, column=0, pady=(0, 0), padx=0, sticky=E)
    ToolTip(lock_warehouse, text="Lock the warehouse by clicking this")

    # Warehouse Combobox field
    warehouse_combobox = ttk.Combobox(warehouse_frame,
                                      values=warehouse_names,
                                      state="readonly",
                                      width=30,
                                      font=shared_functions.custom_font_size)
    warehouse_combobox.grid(row=1, column=0, padx=(10,0), pady=(0, 0), sticky=W)
    ToolTip(warehouse_combobox, text="Choose a warehouse")

    # Status JSON-format choices (coming from the API)
    status = get_status_api
    status_to_id = {item["name"]: item["id"] for item in status}
    status_names = list(status_to_id.keys())

    status_label = ttk.Label(warehouse_frame, text="Status", style="CustomLabel.TLabel")
    status_label.grid(row=0, column=3, padx=(10, 0), pady=(0, 0), sticky=W)

    status_combobox = ttk.Combobox(
        warehouse_frame,
        values=status_names,
        state="readonly",
        width=40,
        font=shared_functions.custom_font_size
    )
    status_combobox.grid(row=1, column=3, padx=(10, 0), pady=(0, 0), sticky=W)
    ToolTip(status_combobox, text="Please choose the raw material status")


    checkbox_status_var = ttk.IntVar()  # Integer variable to store checkbox state (0 or 1)

    # Checkbox beside the combobox
    lock_status = ttk.Checkbutton(
        warehouse_frame,

        variable=checkbox_status_var,
        bootstyle="round-toggle"
    )
    lock_status.grid(row=0,  column=3, pady=(0, 0), padx=(0,0), sticky=E)  # Position the checkbox next to the combobox
    ToolTip(lock_status, text="Lock the status by clicking this")



    # Reference Number FRAME (Right-aligned)
    refno_frame = ttk.Frame(form_frame)
    refno_frame.grid(row=0, column=1, padx=5, pady=(0, 10), sticky="e")

    # REF Number Entry Field
    ref_number_label = ttk.Label(refno_frame, text="PF ID No.", style="CustomLabel.TLabel")
    ref_number_label.grid(row=0, column=0, padx=5, pady=(0, 0), sticky=W)
    ref_number_entry = ttk.Entry(refno_frame, width=30, font=shared_functions.custom_font_size)
    ref_number_entry.grid(row=1, column=0, padx=5, pady=(0, 0), sticky=W)
    ToolTip(ref_number_entry, text="Enter the Reference Number")

    checkbox_reference_var = ttk.IntVar()  # Integer variable to store checkbox state (0 or 1)

    # Checkbox beside the combobox
    lock_reference = ttk.Checkbutton(
        refno_frame,

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
    rm_codes_label = ttk.Label(rmcode_frame, text="Raw Material", style="CustomLabel.TLabel")
    rm_codes_label.grid(row=0, column=0, padx=5, pady=(0, 0), sticky=W)

    rm_codes_combobox = ttk.Combobox(
        rmcode_frame,
        values=rm_names,
        state="normal",
        width=30,
        font=shared_functions.custom_font_size
    )

    # Bind the key release event to the combobox to trigger uppercase conversion
    rm_codes_combobox.bind("<KeyRelease>", on_combobox_key_release)

    rm_codes_combobox.grid(row=1, column=0, pady=(0, 0), padx=(10, 0), sticky=W)
    ToolTip(rm_codes_combobox, text="Choose a raw material")


    # Function to format numeric input dynamically with cursor preservation
    def format_numeric_input_prepared(event):
        """
        Formats the input dynamically while preserving the cursor position.
        """
        input_value = qty_prepared_var.get()

        # Get current cursor position
        cursor_position = qty_prepared_entry.index("insert")

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
            qty_prepared_entry.delete(0, "end")
            qty_prepared_entry.insert(0, formatted_value)
            qty_prepared_entry.icursor(new_cursor_position)  # Restore cursor position
        except ValueError:
            pass  # Ignore invalid input


    # Function to format numeric input dynamically with cursor preservation
    def format_numeric_input_return(event):
        """
        Formats the input dynamically while preserving the cursor position.
        """
        input_value = qty_return_var.get()

        # Get current cursor position
        cursor_position = qty_return_entry.index("insert")

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
            qty_return_entry.delete(0, "end")
            qty_return_entry.insert(0, formatted_value)
            qty_return_entry.icursor(new_cursor_position)  # Restore cursor position
        except ValueError:
            pass  # Ignore invalid input

    # Tkinter StringVar for real-time updates
    qty_prepared_var = StringVar()
    qty_return_var = StringVar()

    # Register the validation command
    validate_numeric_command = rmcode_frame.register(EntryValidation.validate_numeric_input)

    # Quantity (Prepared) Entry Field
    qty_prepared_label = ttk.Label(rmcode_frame, text="QTY (Prepared)", style="CustomLabel.TLabel")
    qty_prepared_label.grid(row=0, column=1, padx=(10, 0), pady=0, sticky=W)
    qty_prepared_entry = ttk.Entry(rmcode_frame,
                                   width=20,
                                   font=shared_functions.custom_font_size,
                                   textvariable=qty_prepared_var,
                                   validate="key",  # Trigger validation on keystrokes
                                   validatecommand=(validate_numeric_command, "%P")  # Pass the current widget content ("%P")
                            )
    qty_prepared_entry.grid(row=1, column=1, padx=(10, 0), pady=0, sticky=W)
    qty_prepared_entry.bind("<KeyRelease>", format_numeric_input_prepared)
    ToolTip(qty_prepared_entry, text="Enter the value for the Quantity (Prepared) in KG")


    # Quantity (Return) Entry Field
    qty_return_label = ttk.Label(rmcode_frame, text="QTY (Return)", style="CustomLabel.TLabel")
    qty_return_label.grid(row=0, column=2, padx=(5,0), pady=0, sticky=W)
    qty_return_entry = ttk.Entry(rmcode_frame,
                          width=20,
                            font=shared_functions.custom_font_size,
                        textvariable=qty_return_var,
                          validate="key",  # Trigger validation on keystrokes
                          validatecommand=(validate_numeric_command, "%P")  # Pass the current widget content ("%P")
                          )
    qty_return_entry.grid(row=1, column=2, padx=(2,0), pady=0, sticky=W)
    qty_return_entry.bind("<KeyRelease>", format_numeric_input_return)
    ToolTip(qty_return_entry, text="Enter the value for the Quantity (Return) in KG")




    def format_date_while_typing(event):
        """Auto-formats the date entry while typing, ensuring valid MM/DD/YYYY format."""
        text = preparation_date_entry.entry.get().replace("/", "")  # Remove slashes to get raw number input
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
        preparation_date_entry.entry.delete(0, "end")
        preparation_date_entry.entry.insert(0, formatted_date)





    date_frame = ttk.Frame(form_frame)
    date_frame.grid(row=1, column=1, padx=5, pady=(0, 10), sticky="e")

    # Date Entry field
    date_label = ttk.Label(date_frame, text="Report Date", style="CustomLabel.TLabel")
    date_label.grid(row=0, column=0, padx=5, pady=0, sticky=W)

    # Calculate yesterday's date
    yesterday_date = datetime.now() - timedelta(days=1)

    # Create the DateEntry widget with yesterday's date as the default value
    preparation_date_entry = ttk.DateEntry(
        date_frame,
        bootstyle=PRIMARY,
        dateformat="%m/%d/%Y",
        startdate=yesterday_date,  # Set yesterday's date
        width=26
    )
    preparation_date_entry.grid(row=1, column=0, padx=5, pady=0, sticky=W)
    preparation_date_entry.entry.config(font=shared_functions.custom_font_size)
    ToolTip(preparation_date_entry, text="Please enter the preparation date.")
    preparation_date_entry.entry.bind("<Return>", format_date_while_typing)
    preparation_date_entry.entry.bind("<FocusOut>", format_date_while_typing)


    # Add button to submit data
    btn_add = ttk.Button(
        form_frame,
        text="+ Add",
        command=submit_data,
    )
    btn_add.grid(row=2, column=0, columnspan=3, pady=0, padx=400, sticky=NSEW)
    ToolTip(btn_add, text="Click this add button to add the entry to the list")

    prepration_form_table = PreparationFormTable(note_form_tab)

