import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.constants import *
import requests
from backend.settings.database import server_ip
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.dialogs.dialogs import Messagebox
from datetime import datetime, timedelta
from .validation import EntryValidation
from ..shared import SharedFunctions
from tkinter import StringVar
import re



class Forms:
    def __init__(self, root):
        self.status_to_id = None
        self.spillage_no_entry = None
        self.incident_date_entry = None
        self.ref_number_entry = None
        self.adj_date_entry = None
        self.ref_date_entry = None
        self.person_responsible_entry = None
        self.checkbox_warehouse_var = None
        self.warehouse_combobox = None
        self.warehouse_to_id = None
        self.status_combobox = None
        self.qty_entry = None
        self.checkbox_status_var = None
        self.code_to_id = None
        self.rm_codes_combobox = None
        self.checkbox_reference_var = None
        self.root = root
        self.shared_functions = SharedFunctions()
        self.add_record_window = None

        self.get_status_api = self.shared_functions.get_status_api()
        self.get_warehouse_api = self.shared_functions.get_warehouse_api()
        self.get_rm_code_api = self.shared_functions.get_rm_code_api(force_refresh=True)

        self.discrepancy_reason = tk.StringVar(value="None Selected")  # Default value for the Radio Buttons
        

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


    def on_add_window_close(self):
        """Reset the edit_window reference when it is closed."""
        self.add_record_window.destroy()
        self.add_record_window = None


    def submit_data(self):

        # Collect the form data
        warehouse_id = self.get_selected_warehouse_id()
        rm_code_id = self.get_selected_rm_code_id()
        ref_number = self.ref_number_entry.get()
        person_responsible = self.person_responsible_entry.get()
        spillage_no = self.spillage_no_entry.get()



        qty = self.qty_entry.get()

        if qty is None or qty == '':
            qty = '0'

        # This code removes the commas in the qty value
        cleaned_qty = float(qty.replace(",", ""))

        adjustment_date = self.adj_date_entry.entry.get()
        referenced_date = self.ref_date_entry.entry.get()
        incident_date = self.incident_date_entry.entry.get()

        status_id = self.get_selected_status_id()

        # Set focus to the Entry field
        self.adj_date_entry.entry.focus_set()

        # Convert date to YYYY-MM-DD
        try:
            adjustment_date = datetime.strptime(adjustment_date, "%m/%d/%Y").strftime("%Y-%m-%d")
            referenced_date = datetime.strptime(referenced_date, "%m/%d/%Y").strftime("%Y-%m-%d")
            incident_date = datetime.strptime(incident_date, "%m/%d/%Y").strftime("%Y-%m-%d")
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
            "qty_kg": cleaned_qty,
            "status_id": status_id,
            "spillage_form_number": spillage_no,
            "incident_date": incident_date,
            "responsible_person": person_responsible,
        }


        # Validate the data entries in front-end side
        if EntryValidation.entry_validation(data):
            error_text = EntryValidation.entry_validation(data)
            Messagebox.show_error(f"There is no data in these fields {error_text}.", "Data Entry Error", alert=True)
            return



        # Validate if the entry value exceeds the stock
        validatation_result = EntryValidation.validate_soh_value(
            rm_code_id,
            warehouse_id,
            cleaned_qty,
            status_id
        )

        if validatation_result:

            # Send a POST request to the API
            try:
                response = requests.post(f"{server_ip}/api/adjustment_form/spillage/v1/create/", json=data)
                if response.status_code == 200:  # Successfully created
                    self.clear_fields()

                    self.root.refresh_table()

                    # Get the last inserted row ID
                    last_row_id = self.root.tree.get_children()[0]  # Get the last row's ID

                    # Highlight the last row
                    self.root.tree.selection_set(last_row_id)  # Select the last row
                    self.root.tree.focus(last_row_id)  # Focus on the last row
                    self.root.tree.see(last_row_id)  # Scroll to make it visible


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


    def add_records(self):
        # If the window already exists, bring it to the front and return
        if self.add_record_window and self.add_record_window.winfo_exists():
            self.add_record_window.lift()
            return


        self.add_record_window = ttk.Toplevel(self.root)
        self.add_record_window.title("Spillage Inventory Adjustment Form")

        # **Fixed Size** (Recommended for consistency)
        window_width = 490  # Fixed width
        window_height = 550  # Fixed height

        # **Center the window**
        screen_width = self.add_record_window.winfo_screenwidth()
        screen_height = self.add_record_window.winfo_screenheight()
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 3  # Slightly higher than center

        self.add_record_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.add_record_window.resizable(False, False)  # Enable resizing for consistency

        # **Make widgets expand properly**
        self.add_record_window.grid_columnconfigure(0, weight=1)
        self.add_record_window.grid_rowconfigure(0, weight=1)


        # **Message Label (Warning)**
        message_label = ttk.Label(
            self.add_record_window,
            text="Inventory Adjustment Form",
            justify="center",
            font=("Arial", 14, "bold"),
            bootstyle=SECONDARY
        )
        message_label.pack(pady=10)


        # Create a frame for the form inputs
        form_frame = ttk.Frame(self.add_record_window)
        form_frame.pack(fill=X, pady=10, padx=20)

        # Configure grid columns to make them behave correctly
        form_frame.grid_columnconfigure(0, weight=1)  # Left (Warehouse) stays at the left
        form_frame.grid_columnconfigure(1, weight=1)  # Right (Ref Number) is pushed to the right




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

        def format_incident_date_while_typing(event):
            """Auto-formats the date entry while typing, ensuring valid MM/DD/YYYY format."""
            text = self.incident_date_entry.entry.get().replace("/", "")  # Remove slashes to get raw number input
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
            self.incident_date_entry.entry.delete(0, "end")
            self.incident_date_entry.entry.insert(0, formatted_date)

        # ----------------------------------[ADJUSTMENT DATE FIELD]----------------------------------#
        date_label = ttk.Label(form_frame, text="Date of Adjustment", style="CustomLabel.TLabel")
        date_label.grid(row=0, column=0, padx=(3,0), pady=0, sticky=W)


        # Create the DateEntry widget with yesterday's date as the default value
        self.adj_date_entry = ttk.DateEntry(
            form_frame,
            bootstyle=PRIMARY,
            dateformat="%m/%d/%Y",
            width=25
        )
        self.adj_date_entry.grid(row=1, column=0, padx=(5,0), pady=0, sticky=W)
        self.adj_date_entry.entry.delete(0, "end")
        self.adj_date_entry.entry.config(font=self.shared_functions.custom_font_size)
        self.adj_date_entry.entry.bind("<FocusOut>", format_adj_date_while_typing)
        self.adj_date_entry.entry.bind("<Return>", format_adj_date_while_typing)
        ToolTip(self.adj_date_entry, text="Please enter the date when the adjustment happened")

        # Set focus to the Entry field
        self.adj_date_entry.entry.focus_set()

        # ----------------------------------[REFERENCED NUMBER FIELD]----------------------------------#



        # REF Number Entry Field
        ref_number_label = ttk.Label(form_frame, text="Ref#.", style="CustomLabel.TLabel")
        ref_number_label.grid(row=0, column=1, padx=(8, 0), pady=(0, 0), sticky=W)
        self.ref_number_entry = ttk.Entry(form_frame, width=29, font=self.shared_functions.custom_font_size)
        self.ref_number_entry.grid(row=1, column=1, padx=(10, 0), pady=(0, 0), sticky=W)
        ToolTip(self.ref_number_entry, text="Enter the Reference Number")

        self.checkbox_reference_var = ttk.IntVar()  # Integer variable to store checkbox state (0 or 1)

        # Checkbox beside the combobox
        lock_reference = ttk.Checkbutton(
            form_frame,
            variable=self.checkbox_reference_var,
            bootstyle="round-toggle"
        )
        lock_reference.grid(row=0, column=1, pady=(0, 0), padx=(10, 0), sticky=E)  # Position the checkbox next to the combobox
        ToolTip(lock_reference, text="Lock the reference number by clicking this")


        # ----------------------------------[REFERENCED DATE FIELD]----------------------------------#
        date_label = ttk.Label(form_frame, text="Referenced Date Affected", style="CustomLabel.TLabel")
        date_label.grid(row=2, column=0, padx=(3, 0), pady=(10, 0), sticky=W)

        # Create the DateEntry widget with yesterday's date as the default value
        self.ref_date_entry = ttk.DateEntry(
            form_frame,
            bootstyle=PRIMARY,
            dateformat="%m/%d/%Y",
            width=57
        )
        self.ref_date_entry.grid(row=3, column=0, columnspan=2, padx=(5, 0), pady=(0, 0), sticky=W)
        self.ref_date_entry.entry.delete(0, "end")
        self.ref_date_entry.entry.config(font=self.shared_functions.custom_font_size)
        self.ref_date_entry.entry.bind("<FocusOut>", format_ref_date_while_typing)
        self.ref_date_entry.entry.bind("<Return>", format_ref_date_while_typing)
        ToolTip(self.ref_date_entry, text="Please enter the date when the discrepancy happened")




        # ----------------------------------[SPILLAGE REPORT # FIELD]----------------------------------#
        label = ttk.Label(form_frame, text="Spillage Report #", style="CustomLabel.TLabel")
        label.grid(row=4, column=0, padx=5,  pady=(10, 0), sticky=W)

        self.spillage_no_entry = ttk.Entry(form_frame, width=29, font=self.shared_functions.custom_font_size)
        self.spillage_no_entry.grid(row=5, column=0, padx=(5, 0), pady=0, sticky=W)
        ToolTip(self.spillage_no_entry, text="Type the Spillage Report Reference Number.")




        # ----------------------------------[INCIDENT REPORT DATE FIELD]----------------------------------#
        date_label = ttk.Label(form_frame, text="Date of Incident", style="CustomLabel.TLabel")
        date_label.grid(row=4, column=1, padx=(3, 0),  pady=(10, 0), sticky=W)


        # Create the DateEntry widget with yesterday's date as the default value
        self.incident_date_entry = ttk.DateEntry(
            form_frame,
            bootstyle=PRIMARY,
            dateformat="%m/%d/%Y",
            width=25
        )
        self.incident_date_entry.grid(row=5, column=1, padx=(5, 0), pady=(0, 0), sticky=W)
        self.incident_date_entry.entry.delete(0, "end")
        self.incident_date_entry.entry.config(font=self.shared_functions.custom_font_size)
        self.incident_date_entry.entry.bind("<FocusOut>", format_incident_date_while_typing)
        self.incident_date_entry.entry.bind("<Return>", format_incident_date_while_typing)
        ToolTip(self.incident_date_entry, text="Please enter the date when the discrepancy happened")


        # ----------------------------------[WAREHOUSE FIELD]----------------------------------#

        # Warehouse JSON-format choices (coming from the API)
        warehouses = self.get_warehouse_api
        self.warehouse_to_id = {item["wh_name"]: item["id"] for item in warehouses}
        warehouse_names = list(self.warehouse_to_id.keys())

        # Combobox for Warehouse Drop Down
        warehouse_label = ttk.Label(form_frame, text="Location", style="CustomLabel.TLabel")
        warehouse_label.grid(row=6, column=0, padx=(3, 0),  pady=(10, 0), sticky=W)

        # Checkbox for Warehouse lock
        self.checkbox_warehouse_var = ttk.IntVar()
        lock_warehouse = ttk.Checkbutton(
            form_frame,

            variable=self.checkbox_warehouse_var,
            bootstyle="round-toggle"
        )
        lock_warehouse.grid(row=6, column=0, pady=(10, 0), padx=(0, 0), sticky=E)

        # Warehouse Combobox field
        self.warehouse_combobox = ttk.Combobox(form_frame,
                                          values=warehouse_names,
                                          state="readonly",
                                          width=27,
                                          font=self.shared_functions.custom_font_size
                                          )
        self.warehouse_combobox.grid(row=7, column=0, padx=(5, 0), pady=(0, 0), sticky=W)


        ToolTip(self.warehouse_combobox, text="Choose a warehouse")
        ToolTip(lock_warehouse, text="Lock the warehouse by clicking this")
        self.warehouse_combobox.set("Warehouse #1")



        # ----------------------------------[STATUS FIELD]----------------------------------#

        # Status JSON-format choices (coming from the API)
        status = self.get_status_api
        self.status_to_id = {item["name"]: item["id"] for item in status}
        status_names = list(self.status_to_id.keys())

        status_label = ttk.Label(form_frame, text="Status", style="CustomLabel.TLabel")
        status_label.grid(row=6, column=1, padx=(3, 0), pady=(10, 0), sticky=W)

        self.status_combobox = ttk.Combobox(
            form_frame,
            values=status_names,
            state="readonly",
            width=27,
            font=self.shared_functions.custom_font_size
        )
        self.status_combobox.grid(row=7, column=1, padx=(5, 0), pady=(0, 0), sticky=W)
        # Checkbox for Warehouse lock
        self.checkbox_status_var = ttk.IntVar()
        lock_status = ttk.Checkbutton(
            form_frame,

            variable=self.checkbox_status_var,
            bootstyle="round-toggle"
        )
        lock_status.grid(row=6, column=1, pady=(10, 0), padx=(0, 0), sticky=E)


        ToolTip(lock_status, text="Lock the status by clicking this")
        ToolTip(self.status_combobox, text="Please choose the raw material status")
        self.status_combobox.set("good")




        # ----------------------------------[RM CODE FIELD]----------------------------------#

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
        rm_codes_label = ttk.Label(form_frame, text="Raw Material", style="CustomLabel.TLabel")
        rm_codes_label.grid(row=8, column=0, padx=(3, 0),  pady=(10, 0), sticky=W)

        self.rm_codes_combobox = ttk.Combobox(
            form_frame,
            values=rm_names,
            state="normal",
            width=27,
            font=self.shared_functions.custom_font_size
        )

        # Bind the key release event to the combobox to trigger uppercase conversion
        self.rm_codes_combobox.bind("<KeyRelease>", on_combobox_key_release)

        self.rm_codes_combobox.grid(row=9, column=0, pady=(0, 0), padx=(5, 0), sticky=W)
        ToolTip(self.rm_codes_combobox, text="Choose a raw material")

        # ----------------------------------[QUANTITY FIELD]----------------------------------#

        # New validation function to restrict input characters
        def validate_qty_input(P):
            """
            Validates the input for the quantity field.
            Allows:
            - Optional leading '+' or '-'
            - Digits (0-9)
            - A single optional decimal point '.'
            - No other special characters or letters
            """
            # This regex allows:
            # ^[+-]?  : optional leading '+' or '-'
            # \d* : zero or more digits
            # \.?     : optional single decimal point
            # \d* : zero or more digits after the decimal
            # $       : end of the string
            # It also handles empty string, just a sign, or just a sign and a dot.
            if re.fullmatch(r"^[+-]?\d*\.?\d*$", P):
                return True
            else:
                return False

        def format_numeric_input(event):
            entry_widget = event.widget
            input_value = entry_widget.get()
            cursor_position = entry_widget.index("insert")

            # Strip commas for processing
            raw_value = input_value.replace(",", "")

            # Determine the sign and the numeric part
            current_sign = ""
            numeric_part = raw_value

            if raw_value.startswith("-"):
                current_sign = "-"
                numeric_part = raw_value.lstrip("-")
            elif raw_value.startswith("+"):
                # For formatting, we don't re-add the '+' sign, it's treated as positive.
                current_sign = "+"
                numeric_part = raw_value.lstrip("+")

            # Allow incomplete but valid numeric input (e.g., just a sign, or a sign followed by a dot)
            # This check is crucial for allowing users to type '-' or '+', or '-.' or '+.'
            if numeric_value := re.fullmatch(r"^\d*\.?\d*$", numeric_part):  # Check if numeric_part is valid
                if numeric_part == "" or numeric_part == ".":
                    # If it's just a sign, or a sign with a dot, or empty, allow as is.
                    # The validation command already ensures it's a valid pattern.
                    return
            else:
                # If numeric_part itself is not valid (e.g., empty after stripping sign but not just a sign),
                # this means the input is in an un-formattable state.
                # This case should ideally be caught by validate_qty_input before reaching here.
                return

            try:
                formatted_value = ""
                # If there's a decimal point, format integer part only
                if "." in numeric_part:
                    integer_part, decimal_part = numeric_part.split(".", 1)
                    # Format integer part, handle empty integer part before decimal
                    formatted_integer = "{:,}".format(int(integer_part)) if integer_part else "0"
                    formatted_value = f"{current_sign if current_sign == '-' else ''}{formatted_integer}.{decimal_part}"
                else:
                    # Format as integer with commas
                    formatted_value = f"{current_sign if current_sign == '-' else ''}{int(numeric_part):,}"

                # Compute cursor shift from added/removed commas
                # A more robust way to handle cursor position with dynamic formatting:
                original_digits_before_cursor = 0
                for char in numeric_part[:cursor_position - (1 if current_sign else 0)]:  # Adjust for sign
                    if char.isdigit():
                        original_digits_before_cursor += 1

                new_cursor_position = 0
                digits_counted = 0
                # Iterate through formatted_value to find the new cursor position
                # accounting for the sign and commas.
                if current_sign == '-':
                    new_cursor_position += 1  # Account for the '-' sign

                for i, char in enumerate(formatted_value[len(current_sign if current_sign == '-' else ''):]):
                    if char.isdigit():
                        digits_counted += 1
                    if digits_counted == original_digits_before_cursor:
                        new_cursor_position += i + 1
                        break
                else:  # If loop completes, means original_digits_before_cursor was too large or no digits
                    new_cursor_position = len(formatted_value)  # Place at end

                # Update entry field
                entry_widget.delete(0, "end")
                entry_widget.insert(0, formatted_value)
                entry_widget.icursor(new_cursor_position)

            except ValueError:
                # This should ideally not be hit often if validate_qty_input is working
                pass

        # Tkinter StringVar for real-time updates
        qty_var = StringVar()

        # Register the validation command with the form_frame
        validate_numeric_command = form_frame.register(validate_qty_input)

        # Quantity Entry Field
        qty_label = ttk.Label(form_frame, text="Variance (Gain/Loss)", style="CustomLabel.TLabel")
        qty_label.grid(row=8, column=1, padx=(3, 0), pady=(10, 0), sticky=W)

        self.qty_entry = ttk.Entry(form_frame,
                                   width=29,
                                   font=self.shared_functions.custom_font_size,
                                   textvariable=qty_var,
                                   validate="key",  # Validate on each key press
                                   validatecommand=(validate_numeric_command,
                                                    "%P"))  # %P is the value of the entry if the edit is allowed
        self.qty_entry.grid(row=9, column=1, padx=(5, 0), pady=(0, 0), sticky=W)

        # Bind the event to format input dynamically while preserving cursor position
        self.qty_entry.bind("<KeyRelease>", format_numeric_input)
        ToolTip(self.qty_entry, text="Enter the Variance if it is Gain or Loss")



        # -------------------------------[REASON FOR DISCREPANCY FIELD]----------------------------------#
        label = ttk.Label(form_frame, text="Reason for Discrepancy", style="CustomLabel.TLabel")
        label.grid(row=10, column=0, padx=5,  pady=(12, 0), sticky=W)

        spillage_radio = ttk.Radiobutton(
            form_frame,
            text="Spillage",
            variable=self.discrepancy_reason,
            value="Spillage",
            style="Custom.TRadiobutton",
            bootstyle="primary",

        )
        spillage_radio.grid(row=11, column=0, padx=5,  pady=(12, 0), sticky=W)

        inventory_radio = ttk.Radiobutton(
            form_frame,
            text="Inventory Discrepancy",
            variable=self.discrepancy_reason,
            value="Inventory Discrepancy",
            style="Custom.TRadiobutton",
            bootstyle="primary",

        )
        inventory_radio.grid(row=11, column=1, padx=5,  pady=(12, 0), sticky=W)


        # ----------------------------------[PERSON RESPONSIBLE FIELD]----------------------------------#
        label = ttk.Label(form_frame, text="Responsible Person", style="CustomLabel.TLabel")
        label.grid(row=12, column=0, padx=5,  pady=(12, 0), sticky=W)

        self.person_responsible_entry = ttk.Entry(form_frame, width=61, font=self.shared_functions.custom_font_size)
        self.person_responsible_entry.grid(row=13, column=0, columnspan=2, padx=(5, 0), pady=0, sticky=W)
        ToolTip(self.person_responsible_entry, text="Type the Spillage Report Reference Number.")



        # Submit button

        # **Cancel Button**
        cancel_button = ttk.Button(
            form_frame,
            text="Close",
            bootstyle=DANGER,
            command=self.add_record_window.destroy
        )
        cancel_button.grid(row=14, column=0, padx=5, sticky="w")

        submit_btn = ttk.Button(form_frame, text="+ Add", bootstyle=SUCCESS,
                                command=self.submit_data,)
        submit_btn.grid(row=14, column=1, pady=20, sticky="e")




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
        bind_shift_enter_to_all_children(form_frame, lambda e: submit_btn.invoke())

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
            current_state_warehouse = self.checkbox_warehouse_var.get()
            current_state_reference = self.checkbox_reference_var.get()
            current_state_status = self.checkbox_status_var.get()

            # If any checkbox is unchecked, set all to True (1)
            if not all([current_state_warehouse, current_state_reference, current_state_status]):
                self.checkbox_warehouse_var.set(1)
                self.checkbox_reference_var.set(1)
                self.checkbox_status_var.set(1)
            else:
                self.checkbox_warehouse_var.set(0)
                self.checkbox_reference_var.set(0)
                self.checkbox_status_var.set(0)

        bind_shift_a_to_toggle_checkbox(form_frame, toggle_warehouse_lock)

        # This is for the tab button for the tab sequence when the user hits tab to move to the next field
        self.adj_date_entry.entry.bind("<Tab>", lambda e: self.shared_functions.focus_next_widget(e, self.ref_number_entry))
        self.ref_number_entry.bind("<Tab>", lambda e: self.shared_functions.focus_next_widget(e, self.ref_date_entry.entry))
        self.ref_date_entry.entry.bind("<Tab>",
                                       lambda e: self.shared_functions.focus_next_widget(e, self.spillage_no_entry))
        self.spillage_no_entry.bind("<Tab>", lambda e: self.shared_functions.focus_next_widget(e, self.incident_date_entry.entry))
        self.incident_date_entry.entry.bind("<Tab>",
                                    lambda e: self.shared_functions.focus_next_widget(e, self.warehouse_combobox))
        self.warehouse_combobox.bind("<Tab>", lambda e: self.shared_functions.focus_next_widget(e, self.status_combobox))
        self.status_combobox.bind("<Tab>", lambda e: self.shared_functions.focus_next_widget(e, self.rm_codes_combobox))
        self.rm_codes_combobox.bind("<Tab>", lambda e: self.shared_functions.focus_next_widget(e, self.qty_entry))
        self.qty_entry.bind("<Tab>", lambda e: self.shared_functions.focus_next_widget(e, self.person_responsible_entry))
        self.person_responsible_entry.bind("<Tab>", lambda e: self.shared_functions.focus_next_widget(e, submit_btn))

