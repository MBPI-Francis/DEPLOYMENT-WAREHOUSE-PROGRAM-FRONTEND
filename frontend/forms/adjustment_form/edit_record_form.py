import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import requests
from backend.settings.database import server_ip
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.dialogs.dialogs import Messagebox
from datetime import datetime, timedelta
from .validation import EntryValidation
from ..shared import SharedFunctions
from tkinter import StringVar, messagebox



class EditForm:
    def __init__(self, root):
        self.item = None
        self.old_qty = None
        self.ref_date_value = None
        self.adj_date_value = None
        self.reason_value = None
        self.ref_doc_number_value = None
        self.ref_doc_value = None
        self.warehouse_value = None
        self.status_value = None
        self.qty_value = None
        self.rm_code_value = None
        self.ref_number_value = None
        self.record = None
        self.status_to_id = None
        self.ref_number_entry = None
        self.adj_date_entry = None
        self.ref_date_entry = None
        self.reason_entry = None
        self.ref_doc_number_entry = None
        self.checkbox_warehouse_var = None
        self.warehouse_combobox = None
        self.warehouse_to_id = None
        self.status_combobox = None
        self.qty_entry = None
        self.checkbox_status_var = None
        self.code_to_id = None
        self.rm_codes_combobox = None
        self.checkbox_reference_var = None
        self.ref_doc_combobox = None
        self.root = root
        self.shared_functions = SharedFunctions()
        self.edit_window = None

        self.get_status_api = self.shared_functions.get_status_api()
        self.get_warehouse_api = self.shared_functions.get_warehouse_api()
        self.get_rm_code_api = self.shared_functions.get_rm_code_api(force_refresh=True)




    def get_selected_warehouse_id(self):
        selected_name = self.warehouse_combobox.get()
        selected_id = self.warehouse_to_id.get(selected_name)  # Get the corresponding ID
        if selected_id:
            return selected_id
        else:
            return None

    def get_selected_rm_code_id(self):
        selected_name = self.rm_codes_combobox.get()
        selected_id = self.code_to_id.get(selected_name)  # Get the corresponding ID
        if selected_id:
            return selected_id
        else:
            return None

    def get_selected_status_id(self):
        selected_name = self.status_combobox.get()
        selected_id = self.status_to_id.get(selected_name)  # Get the corresponding ID
        if selected_id:
            return selected_id
        else:
            return None

    def on_edit_window_close(self):
        """Reset the edit_window reference when it is closed."""
        self.edit_window.destroy()
        self.edit_window = None


    def submit_data(self):

        # Collect the form data
        warehouse_id = self.get_selected_warehouse_id()
        rm_code_id = self.get_selected_rm_code_id()
        ref_number = self.ref_number_entry.get()
        referenced_doc = self.ref_doc_combobox.get()
        referenced_doc_no = self.ref_doc_number_entry.get()
        reason = self.reason_entry.get("1.0", "end").strip()

        qty = self.qty_entry.get()

        if qty is None or qty == '':
            qty = '0'

        # This code removes the commas in the qty value
        cleaned_qty = float(qty.replace(",", ""))

        adjustment_date = self.adj_date_entry.entry.get()
        referenced_date = self.ref_date_entry.entry.get()

        status_id = self.get_selected_status_id()

        # Set focus to the Entry field
        self.rm_codes_combobox.focus_set()

        # Convert date to YYYY-MM-DD
        try:
            adjustment_date = datetime.strptime(adjustment_date, "%m/%d/%Y").strftime("%Y-%m-%d")
            referenced_date = datetime.strptime(referenced_date, "%m/%d/%Y").strftime("%Y-%m-%d")
        except ValueError:
            Messagebox.show_error("Invalid date format. Please use MM/DD/YYYY.", "Date Entry Error")
            return

        # Create a dictionary with the data
        data = {
            "rm_code_id": rm_code_id,
            "warehouse_id": warehouse_id,
            "ref_number": ref_number,
            "adjustment_date": adjustment_date,
            "reference_date": referenced_date,
            "ref_form": referenced_doc,
            "ref_form_number": referenced_doc_no,
            "qty_kg": cleaned_qty,
            "status_id": status_id,
            "reason": reason,

        }

        # Validate the data entries in front-end side
        if EntryValidation.entry_validation(data):
            error_text = EntryValidation.entry_validation(data)
            Messagebox.show_error(f"There is no data in these fields {error_text}.", "Data Entry Error", alert=True)
            return

        # Validate if the entry value exceeds the stock

        validation_result = EntryValidation.validate_soh_value_for_update(
            rm_code_id,
            warehouse_id,
            self.old_qty,
            cleaned_qty,
            status_id,
        )

        if validation_result:

            # Send a POST request to the API
            try:
                response = requests.put(f"{server_ip}/api/adjustment_form/v1/update/{self.item}/", json=data)
                if response.status_code == 200:  # Successfully created
                    self.root.refresh_table()
                    messagebox.showinfo("Success", "Record updated successfully")
                    self.edit_window.destroy()

            except requests.exceptions.RequestException as e:
                Messagebox.show_error(e, "Data Entry Error")
                return

        else:
            Messagebox.show_error(
                "The entered quantity in 'Quantity' exceeds the available stock in the database.",
                "Data Entry Error")
            return

        # Function to clear all entry fields
    def clear_fields(self):

        if not self.checkbox_reference_var.get():
            self.ref_number_entry.delete(0, ttk.END)

        if not self.checkbox_warehouse_var.get():
            self.warehouse_combobox.set("")

        if not self.checkbox_status_var.get():
            self.status_combobox.set("")

        self.rm_codes_combobox.set("")
        self.qty_entry.delete(0, ttk.END)


    def edit_records(self,item):
        # If the window already exists, bring it to the front and return
        if self.edit_window and self.edit_window.winfo_exists():
            self.edit_window.lift()
            return

        self.item = item
        self.record = self.root.tree.item(item, 'values')
        self.ref_number_value = self.record[1]
        self.rm_code_value = self.record[2]
        self.qty_value = self.record[3]
        self.status_value = self.record[4]
        self.warehouse_value = self.record[5]
        self.ref_doc_value = self.record[6]
        self.ref_doc_number_value = self.record[7]
        self.reason_value = self.record[8]
        self.adj_date_value = self.record[9]
        self.ref_date_value = self.record[10]
        
        self.edit_window = ttk.Toplevel(self.root)
        self.edit_window.title("Inventory Adjustment Form Edit Modal")

        # **Fixed Size** (Recommended for consistency)
        window_width = 780  # Fixed width
        window_height = 420  # Fixed height

        # **Center the window**
        screen_width = self.edit_window.winfo_screenwidth()
        screen_height = self.edit_window.winfo_screenheight()
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 3  # Slightly higher than center

        self.edit_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.edit_window.resizable(True, True)  # Enable resizing for consistency

        # **Make widgets expand properly**
        self.edit_window.grid_columnconfigure(0, weight=1)
        self.edit_window.grid_rowconfigure(0, weight=1)


        # **Message Label (Warning)**
        message_label = ttk.Label(
            self.edit_window,
            text="Inventory Adjustment Edit Form",
            justify="center",
            font=("Arial", 14, "bold"),
            bootstyle=SECONDARY
        )
        message_label.pack(pady=10)


        # Create a frame for the form inputs
        form_frame = ttk.Frame(self.edit_window)
        form_frame.pack(fill=X, pady=10, padx=20)

        # Configure grid columns to make them behave correctly
        form_frame.grid_columnconfigure(0, weight=1)  # Left (Warehouse) stays at the left
        form_frame.grid_columnconfigure(1, weight=1)  # Right (Ref Number) is pushed to the right




        # ----------------------------------[ADJUSTMENT DATE FIELD]----------------------------------#
        def format_adj_date_while_typing(event):
            """Auto-formats the date entry while typing, ensuring valid MM/DD/YYYY format."""
            text = self.adj_date_entry.entry.get().replace("/", "")  # Remove slashes to get raw number input
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
            self.adj_date_entry.entry.delete(0, "end")
            self.adj_date_entry.entry.insert(0, formatted_date)

        def format_ref_date_while_typing(event):
            """Auto-formats the date entry while typing, ensuring valid MM/DD/YYYY format."""
            text = self.ref_date_entry.entry.get().replace("/", "")  # Remove slashes to get raw number input
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
            self.ref_date_entry.entry.delete(0, "end")
            self.ref_date_entry.entry.insert(0, formatted_date)


        # DATE FRAME (Left-aligned)
        date_frame = ttk.Frame(form_frame)
        date_frame.grid(row=1, column=0, padx=5, pady=(0, 10), sticky="w")

        # Get the Current Date
        current_date = datetime.now()

        date_label = ttk.Label(date_frame, text="Date of Adjustment", style="CustomLabel.TLabel")
        date_label.grid(row=1, column=0, padx=(3,0), pady=0, sticky=W)


        # Create the DateEntry widget with yesterday's date as the default value
        self.adj_date_entry = ttk.DateEntry(
            date_frame,
            bootstyle=PRIMARY,
            dateformat="%m/%d/%Y",
            width=26
        )
        self.adj_date_entry.grid(row=2, column=0, padx=(5,0), pady=0, sticky=W)
        self.adj_date_entry.entry.delete(0, "end")
        self.adj_date_entry.entry.insert(0, self.adj_date_value)
        self.adj_date_entry.entry.config(font=self.shared_functions.custom_font_size)
        self.adj_date_entry.entry.bind("<FocusOut>", format_adj_date_while_typing)
        self.adj_date_entry.entry.bind("<Return>", format_adj_date_while_typing)
        ToolTip(self.adj_date_entry, text="Please enter the date when the adjustment happened")


        # ----------------------------------[REFERENCED DATE FIELD]----------------------------------#
        date_label = ttk.Label(date_frame, text="Referenced Date", style="CustomLabel.TLabel")
        date_label.grid(row=1, column=1, padx=(3, 0), pady=(0, 0), sticky=W)


        # Create the DateEntry widget with yesterday's date as the default value
        self.ref_date_entry = ttk.DateEntry(
            date_frame,
            bootstyle=PRIMARY,
            dateformat="%m/%d/%Y",
            width=26
        )
        self.ref_date_entry.grid(row=2, column=1, padx=(5, 0), pady=(0, 0), sticky=W)
        self.ref_date_entry.entry.delete(0, "end")
        self.ref_date_entry.entry.insert(0, self.ref_date_value)
        self.ref_date_entry.entry.config(font=self.shared_functions.custom_font_size)
        self.ref_date_entry.entry.bind("<FocusOut>", format_ref_date_while_typing)
        self.ref_date_entry.entry.bind("<Return>", format_ref_date_while_typing)
        ToolTip(self.ref_date_entry, text="Please enter the date when the discrepancy happened")



        # ----------------------------------[REFERENCED NUMBER FIELD]----------------------------------#
        # Reference Number FRAME (Right-aligned)
        refno_frame = ttk.Frame(form_frame)
        refno_frame.grid(row=1, column=1, padx=5, pady=(0, 5), sticky="e")

        # REF Number Entry Field
        ref_number_label = ttk.Label(refno_frame, text="Ref#.", style="CustomLabel.TLabel")

        ref_number_label.grid(row=1, column=0, padx=(3,0), pady=(0, 0), sticky=W)
        self.ref_number_entry = ttk.Entry(refno_frame, width=24, font=self.shared_functions.custom_font_size)
        self.ref_number_entry.insert(0, self.ref_number_value)
        self.ref_number_entry.grid(row=2, column=0, padx=(5,0), pady=(0, 0), sticky=W)
        ToolTip(self.ref_number_entry, text="Enter the Reference Number")

        self.checkbox_reference_var = ttk.IntVar()  # Integer variable to store checkbox state (0 or 1)

        # Checkbox beside the combobox
        lock_reference = ttk.Checkbutton(
            refno_frame,
            variable=self.checkbox_reference_var,
            bootstyle="round-toggle"
        )
        lock_reference.grid(row=1, pady=(0, 0), padx=(10, 6), sticky=E)  # Position the checkbox next to the combobox
        ToolTip(lock_reference, text="Lock the reference number by clicking this")



        # ----------------------------------[RAW MATERIAL CODE FIELD]----------------------------------#
        # RM CODE FRAME
        rmcode_frame = ttk.Frame(form_frame)
        rmcode_frame.grid(row=2, column=0, padx=5, pady=(0, 10), sticky="w")

        # RM CODE JSON-format choices (coming from the API)
        rm_codes = self.get_rm_code_api
        self.code_to_id = {item["rm_code"]: item["id"] for item in rm_codes}
        rm_names = list(self.code_to_id.keys())

        # Function to convert typed input to uppercase
        def on_combobox_key_release(event):
            # Get the current text in the combobox
            current_text = self.rm_codes_combobox.get()
            # Convert the text to uppercase and set it back
            self.rm_codes_combobox.set(current_text.upper())

        # Combobox for RM CODE Drop Down
        rm_codes_label = ttk.Label(rmcode_frame, text="Raw Material", style="CustomLabel.TLabel")
        rm_codes_label.grid(row=1, column=0, padx=(3, 0), pady=(0, 0), sticky=W)

        self.rm_codes_combobox = ttk.Combobox(
            rmcode_frame,
            values=rm_names,
            state="normal",
            width=20,
            font=self.shared_functions.custom_font_size
        )

        self.rm_codes_combobox.set(self.rm_code_value)  # Set current value in the combobox
        # Bind the key release event to the combobox to trigger uppercase conversion
        self.rm_codes_combobox.bind("<KeyRelease>", on_combobox_key_release)

        self.rm_codes_combobox.grid(row=2, column=0, pady=(0, 0), padx=(5, 0))
        ToolTip(self.rm_codes_combobox, text="Choose a raw material")


        # ----------------------------------[QUANTITY FIELD]----------------------------------#
        # Function to format numeric input dynamically with cursor preservation
        self.old_qty = self.qty_value

        def format_numeric_input(event):
            entry_widget = event.widget
            input_value = qty_var.get()
            cursor_position = self.qty_entry.index("insert")

            # Strip commas for processing
            raw_value = input_value.replace(",", "")

            # Allow incomplete but valid numeric input
            if raw_value in {"-", ".", "-."} or raw_value.endswith(".") or raw_value == "":
                return

            try:
                # Extract sign
                sign = "-" if raw_value.startswith("-") else ""
                value = raw_value.lstrip("-")

                # If there's a decimal point, format integer part only
                if "." in value:
                    integer_part, decimal_part = value.split(".", 1)
                    formatted_integer = "{:,}".format(int(integer_part)) if integer_part else "0"
                    formatted_value = f"{sign}{formatted_integer}.{decimal_part}"
                else:
                    formatted_value = f"{sign}{int(value):,}"

                # Compute cursor shift from added/removed commas
                num_commas_before = input_value[:cursor_position].count(",")
                num_commas_after = formatted_value[:cursor_position].count(",")
                new_cursor_position = cursor_position + (num_commas_after - num_commas_before)

                # Update entry field
                entry_widget.delete(0, "end")
                entry_widget.insert(0, formatted_value)
                entry_widget.icursor(new_cursor_position)

            except ValueError:
                pass  # Ignore formatting if still invalid input (e.g. just a dash)

        # Tkinter StringVar for real-time updates
        qty_var = StringVar()

        # Validation Command for Entry Widget
        validate_numeric_command = rmcode_frame.register(EntryValidation.validate_numeric_input)

        # Quantity Entry Field
        qty_label = ttk.Label(rmcode_frame, text="Quantity(kg)", style="CustomLabel.TLabel")
        qty_label.grid(row=1, column=2, padx=(3,0), pady=(0, 0), sticky=W)

        self.qty_entry = ttk.Entry(rmcode_frame,
                              width=14,
                              font=self.shared_functions.custom_font_size,
                              textvariable=qty_var,
                              validate="key",
                              validatecommand=(validate_numeric_command, "%P"))  # Pass input for validation
        self.qty_entry.insert(0, self.qty_value)
        self.qty_entry.grid(row=2, column=2, padx=(5,0), pady=(0, 0), sticky=W)

        # Bind the event to format input dynamically while preserving cursor position
        self.qty_entry.bind("<KeyRelease>", format_numeric_input)
        ToolTip(self.qty_entry, text="Enter the Quantity(kg)")



        # ----------------------------------[STATUS FIELD]----------------------------------#
        # Status JSON-format choices (coming from the API)
        status = self.get_status_api
        self.status_to_id = {item["name"]: item["id"] for item in status}
        status_names = list(self.status_to_id.keys())

        status_label = ttk.Label(rmcode_frame, text="Status", style="CustomLabel.TLabel")
        status_label.grid(row=1, column=3, padx=(3, 0), pady=(0, 0), sticky=W)

        self.status_combobox = ttk.Combobox(
            rmcode_frame,
            values=status_names,
            state="readonly",
            width=19,
            font=self.shared_functions.custom_font_size
        )
        self.status_combobox.set(self.status_value)
        self.status_combobox.grid(row=2, column=3, padx=(5, 0), pady=(0, 0), sticky=W)
        # Checkbox for Warehouse lock
        self.checkbox_status_var = ttk.IntVar()
        lock_status = ttk.Checkbutton(
            rmcode_frame,

            variable=self.checkbox_status_var,
            bootstyle="round-toggle"
        )
        lock_status.grid(row=1, column=3, pady=(0, 0), padx=(0, 0), sticky=E)


        ToolTip(lock_status, text="Lock the status by clicking this")
        ToolTip(self.status_combobox, text="Please choose the raw material status")
        self.status_combobox.set(self.status_value)



        # ----------------------------------[WAREHOUSE FIELD]----------------------------------#
        warehouse_frame = ttk.Frame(form_frame)
        warehouse_frame.grid(row=2, column=1, padx=5, pady=(0, 10), sticky="e")

        # Warehouse JSON-format choices (coming from the API)
        warehouses = self.get_warehouse_api
        self.warehouse_to_id = {item["wh_name"]: item["id"] for item in warehouses}
        warehouse_names = list(self.warehouse_to_id.keys())

        # Combobox for Warehouse Drop Down
        warehouse_label = ttk.Label(warehouse_frame, text="Warehouse", style="CustomLabel.TLabel")
        warehouse_label.grid(row=1, column=0, padx=(3, 0), pady=(0, 0), sticky=W)

        # Checkbox for Warehouse lock
        self.checkbox_warehouse_var = ttk.IntVar()
        lock_warehouse = ttk.Checkbutton(
            warehouse_frame,

            variable=self.checkbox_warehouse_var,
            bootstyle="round-toggle"
        )
        lock_warehouse.grid(row=1, column=0, pady=(0, 0), padx=(0, 0), sticky=E)

        # Warehouse Combobox field
        self.warehouse_combobox = ttk.Combobox(warehouse_frame,
                                          values=warehouse_names,
                                          state="readonly",
                                          width=22,
                                          font=self.shared_functions.custom_font_size
                                          )
        self.warehouse_combobox.grid(row=2, column=0, padx=(5, 0), pady=(0, 0), sticky=W)
        self.warehouse_combobox.set(self.warehouse_value)

        ToolTip(self.warehouse_combobox, text="Choose a warehouse")
        ToolTip(lock_warehouse, text="Lock the warehouse by clicking this")


        # ----------------------------------[REFERENCED DOC FIELD]----------------------------------#
        # REFERENCED DOCUMENT FRAME (Left-aligned)
        referenced_doc_frame = ttk.Frame(form_frame)
        referenced_doc_frame.grid(row=3, column=0, padx=5, pady=(0, 10), sticky="w")

        label = ttk.Label(referenced_doc_frame, text="Referenced Doc.", style="CustomLabel.TLabel")
        label.grid(row=1, column=0, padx=(3,0), pady=0, sticky=W)
        self.ref_doc_combobox = ttk.Combobox(referenced_doc_frame,
                                          values=[
                                              "Receiving Form",
                                              "Outgoing Form",
                                              "Preparation Form",
                                              "Change Status Form",
                                              "Transfer Form",
                                              "Adjustment Form",
                                              "Incident Report",
                                              "Data Entry"
                                          ],
                                          state="readonly",
                                          width=29,
                                          font=self.shared_functions.custom_font_size
                                          )
        self.ref_doc_combobox.set(self.ref_doc_value)
        self.ref_doc_combobox.grid(row=2, column=0, padx=(5, 0), pady=0, sticky=W)
        ToolTip(self.ref_doc_combobox, text="Select the form where the adjustment occurred.")




        # ----------------------------------[REFERENCED DOCUMENT NO FIELD]----------------------------------#
        label = ttk.Label(referenced_doc_frame, text="Doc. Reference #", style="CustomLabel.TLabel")
        label.grid(row=1, column=1, padx=5, pady=(3,0), sticky=W)
        self.ref_doc_number_entry = ttk.Entry(referenced_doc_frame, width=29, font=self.shared_functions.custom_font_size)
        self.ref_doc_number_entry.grid(row=2, column=1, padx=(5, 0), pady=0, sticky=W)
        self.ref_doc_number_entry.insert(0, self.ref_doc_number_value)
        ToolTip(self.ref_doc_number_entry, text="Type the reference number associated with the referenced document.")




        # ----------------------------------[REASON FIELD]----------------------------------#
        label = ttk.Label(form_frame, text="Reason/Remarks", style="CustomLabel.TLabel")
        label.grid(row=4, column=0, padx=(8,0), pady=0, sticky=W)
        self.reason_entry = ttk.Text(form_frame, height=4, font=self.shared_functions.custom_font_size)
        self.reason_entry.insert("1.0", self.reason_value)
        self.reason_entry.grid(row=5, column=0,columnspan=2 , padx=(10, 0), pady=0, sticky=NSEW)
        ToolTip(self.reason_entry, text="Enter the reason of the adjustment")



        # Configure columns for even stretch
        form_frame.grid_columnconfigure(1, weight=1)

        # Submit button

        # **Cancel Button**
        cancel_button = ttk.Button(
            form_frame,
            text="Close",
            bootstyle=DANGER,
            command=self.edit_window.destroy
        )
        cancel_button.grid(row=6, column=0, padx=5, sticky="w")

        submit_btn = ttk.Button(form_frame, text="Update", bootstyle=SUCCESS,
                                command=self.submit_data,)
        submit_btn.grid(row=6, column=1, pady=20, sticky="e")






