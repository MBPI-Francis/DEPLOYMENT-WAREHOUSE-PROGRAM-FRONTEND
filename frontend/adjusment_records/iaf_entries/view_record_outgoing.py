import ttkbootstrap as ttk
import tkinter as tk

from ttkbootstrap.constants import *
import requests
from backend.settings.database import server_ip
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.dialogs.dialogs import Messagebox
from datetime import datetime, timedelta
from .validation import EntryValidation
from ...forms.shared import SharedFunctions
from tkinter import StringVar, messagebox


class OutgoingRecord:
    def __init__(self, root):
        self.is_adjusted = None
        self.item_id = None
        self.ref_form_number_entry = None
        self.referenced_form_combobox = None
        self.adjustment_type_combobox = None
        self.status_to_id = None
        self.ref_number_entry = None
        self.adj_date_entry = None
        self.ref_date_entry = None
        self.person_responsible_entry = None
        self.warehouse_combobox = None
        self.warehouse_to_id = None
        self.status_combobox = None
        self.qty_entry = None
        self.code_to_id = None
        self.rm_codes_combobox = None
        self.root = root
        self.shared_functions = SharedFunctions()
        self.add_record_window = None

        self.item = None
        self.record = None
        self.ref_number_value = None
        self.rm_code_value = None
        self.qty_value = None
        self.status_value = None
        self.warehouse_value = None
        self.spillage_form_no_value = None
        self.responsible_person_value = None
        self.incident_date_value = None
        self.adj_date_value = None
        self.ref_date_value = None

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

    def on_add_window_close(self):
        """Reset the edit_window reference when it is closed."""
        self.add_record_window.destroy()
        self.add_record_window = None

    def delete_entry(self, entry_id):
        """Delete selected entry via API with confirmation and error handling."""
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this entry?")
        if not confirm:
            return

        try:
            url = f"{server_ip}/api/adjustment_form/form_entries/v1/delete/{entry_id}/"
            response = requests.delete(url, timeout=10)

            if response.status_code == 200:
                self.root.tree.delete(entry_id)
                messagebox.showinfo("Success", "Adjustment record deleted successfully.")
            elif response.status_code == 404:
                messagebox.showerror("Not Found", "The record was not found on the server.")
            else:
                messagebox.showerror("Error", f"Failed to delete the record. Status Code: {response.status_code}")

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Network Error", f"Could not connect to the server:\n{str(e)}")

    def get_outgoing_record(self, record_id):
        # Include status_id only if it's not None

        params = {}
        if record_id:
            params["record_id"] = record_id
        # Handle response
        try:
            # Make the GET request
            response = requests.get(f"{server_ip}/api/outgoing_reports/v1/list/historical/", params=params)

            if response.status_code == 200:

                outgoing_record = response.json()
                if outgoing_record:
                    filtered_record = outgoing_record[0]
                    return filtered_record

                else:
                    return None

            else:
                return None
        except requests.exceptions.RequestException as e:
            return None

    def submit_data(self):

        # Collect the form data
        warehouse_id = self.get_selected_warehouse_id()
        rm_code_id = self.get_selected_rm_code_id()
        ref_number = self.ref_number_entry.get()
        person_responsible = self.person_responsible_entry.get()
        adjustment_type = self.adjustment_type_combobox.get()

        qty = self.qty_entry.get()

        if qty is None or qty == '':
            qty = '0'

        # This code removes the commas in the qty value
        cleaned_qty = float(qty.replace(",", ""))

        adjustment_date = self.adj_date_entry.entry.get()
        referenced_date = self.ref_date_entry.entry.get()

        status_id = self.get_selected_status_id()

        # Set focus to the Entry field
        self.adj_date_entry.entry.focus_set()

        # Convert date to YYYY-MM-DD
        try:
            adjustment_date = datetime.strptime(adjustment_date, "%m/%d/%Y").strftime("%Y-%m-%d")
            referenced_date = datetime.strptime(referenced_date, "%m/%d/%Y").strftime("%Y-%m-%d")

        except ValueError:
            Messagebox.show_error("Invalid date format. Please use MM/DD/YYYY.", "Date Entry Error")
            return

        # Create a dictionary with the data
        data = {
            "ref_number": ref_number,
            "adjustment_date": adjustment_date,
            "referenced_date": referenced_date,
            "rm_code_id": rm_code_id,
            "warehouse_id": warehouse_id,
            "qty_kg": cleaned_qty,
            "status_id": status_id,
            "responsible_person": person_responsible,
            "adjustment_type": adjustment_type,
            "incorrect_receiving_id": self.item_id,
        }

        # Validate the data entries in front-end side
        if EntryValidation.entry_validation(data):
            error_text = EntryValidation.entry_validation(data)
            Messagebox.show_error(f"There is no data in these fields {error_text}.", "Data Entry Error", alert=True)
            return

        # Send a POST request to the API
        try:
            response = requests.post(f"{server_ip}/api/adjustment_form/form_entries/v1/create/receiving_form/",
                                     json=data)
            if response.status_code == 200:  # Successfully created

                self.root.refresh_table()
                self.add_record_window.destroy()
                messagebox.showinfo("Success",
                                    "The record successfully adjusted. Please see the New Adjusted Ending Balance to confirm the adjustment.")


        except requests.exceptions.RequestException as e:
            Messagebox.show_error(e, "Data Entry Error")
            return

    def edit_record(self, item):
        # If the window already exists, bring it to the front and return
        if self.add_record_window and self.add_record_window.winfo_exists():
            self.add_record_window.lift()
            return

        # Get the data from the record and assign each data to its corresponding variable
        self.item_id = item
        self.record = self.root.tree.item(item, 'values')
        self.ref_number_value = self.record[1]
        self.rm_code_value = self.record[2]
        self.qty_value = self.record[3]
        self.status_value = self.record[4]
        self.warehouse_value = self.record[5]
        self.is_adjusted = self.record[8]

        self.add_record_window = ttk.Toplevel(self.root)
        self.add_record_window.title("Receiving Form Adjustment - Type 1")

        # **Fixed Size** (Recommended for consistency)
        window_width = 1020  # Fixed width
        window_height = 580  # Fixed height

        # **Center the window**
        screen_width = self.add_record_window.winfo_screenwidth()
        screen_height = self.add_record_window.winfo_screenheight()
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 3  # Slightly higher than center

        self.add_record_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.add_record_window.resizable(True, True)  # Enable resizing for consistency

        # **Make widgets expand properly**
        self.add_record_window.grid_columnconfigure(0, weight=1)
        self.add_record_window.grid_rowconfigure(0, weight=1)

        # **Message Label (Warning)**
        message_label = ttk.Label(
            self.add_record_window,
            text="Inventory Adjustment Form - Type 1",
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

        # Create a frame for the form inputs
        first_child_frame = ttk.Frame(form_frame)
        first_child_frame.pack(fill=X, pady=10, padx=20)

        # Create a frame for the form inputs
        second_child_frame = ttk.Frame(form_frame)
        second_child_frame.pack(fill=X, pady=10, padx=20)

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

        # ----------------------------------[ADJUSTMENT DATE FIELD]----------------------------------#
        date_label = ttk.Label(first_child_frame, text="Date of Adjustment", style="CustomLabel.TLabel")
        date_label.grid(row=0, column=0, padx=(3, 0), pady=0, sticky=W)

        # Create the DateEntry widget with yesterday's date as the default value
        self.adj_date_entry = ttk.DateEntry(
            first_child_frame,
            bootstyle=PRIMARY,
            dateformat="%m/%d/%Y",
            width=25
        )
        self.adj_date_entry.grid(row=1, column=0, padx=(5, 0), pady=0, sticky=W)
        self.adj_date_entry.entry.delete(0, "end")
        self.adj_date_entry.entry.config(font=self.shared_functions.custom_font_size)
        self.adj_date_entry.entry.bind("<FocusOut>", format_adj_date_while_typing)
        self.adj_date_entry.entry.bind("<Return>", format_adj_date_while_typing)
        ToolTip(self.adj_date_entry, text="Please enter the date when the adjustment happened")

        # Set focus to the Entry field
        self.adj_date_entry.entry.focus_set()

        # ----------------------------------[REFERENCED NUMBER FIELD]----------------------------------#
        # REF Number Entry Field
        ref_number_label = ttk.Label(first_child_frame, text="Ref#.", style="CustomLabel.TLabel")
        ref_number_label.grid(row=0, column=1, padx=(8, 0), pady=(0, 0), sticky=W)

        self.ref_number_entry = ttk.Entry(first_child_frame, width=29, font=self.shared_functions.custom_font_size)
        self.ref_number_entry.grid(row=1, column=1, padx=(10, 0), pady=(0, 0), sticky=W)
        ToolTip(self.ref_number_entry, text="Enter the Reference Number")

        # ----------------------------------[REFERENCED DATE FIELD]----------------------------------#
        date_label = ttk.Label(first_child_frame, text="Referenced Date Affected", style="CustomLabel.TLabel")
        date_label.grid(row=2, column=0, padx=(3, 0), pady=(10, 0), sticky=W)

        # Create the DateEntry widget with yesterday's date as the default value
        self.ref_date_entry = ttk.DateEntry(
            first_child_frame,
            bootstyle=PRIMARY,
            dateformat="%m/%d/%Y",
            width=25
        )
        self.ref_date_entry.grid(row=3, column=0, columnspan=2, padx=(5, 0), pady=(0, 0), sticky=W)
        self.ref_date_entry.entry.delete(0, "end")
        self.ref_date_entry.entry.config(font=self.shared_functions.custom_font_size)
        self.ref_date_entry.entry.bind("<FocusOut>", format_ref_date_while_typing)
        self.ref_date_entry.entry.bind("<Return>", format_ref_date_while_typing)
        ToolTip(self.ref_date_entry, text="Please enter the date when the discrepancy happened")

        # ----------------------------------[Adjustment Type FIELD]----------------------------------#

        adjustment_types_choices = ('Paper Form Error', 'System Entry Error')

        adjustment_type_label = ttk.Label(first_child_frame, text="Adjustment Type", style="CustomLabel.TLabel")
        adjustment_type_label.grid(row=2, column=1, padx=(8, 0), pady=(10, 0), sticky=W)

        self.adjustment_type_combobox = ttk.Combobox(
            first_child_frame,
            values=adjustment_types_choices,
            state="readonly",
            width=27,
            font=self.shared_functions.custom_font_size
        )
        self.adjustment_type_combobox.grid(row=3, column=1, padx=(10, 0), pady=(0, 0), sticky=W)

        # ----------------------------------[REFERENCED FORMS]----------------------------------#
        referenced_form_label = ttk.Label(first_child_frame, text="Referenced Forms", style="CustomLabel.TLabel")
        referenced_form_label.grid(row=4, column=0, padx=(3, 0), pady=(10, 0), sticky=W)

        self.referenced_form_combobox = ttk.Combobox(
            first_child_frame,
            state="disabled",
            width=27,
            font=self.shared_functions.custom_font_size
        )
        self.referenced_form_combobox.grid(row=5, column=0, padx=(5, 0), pady=(0, 0), sticky=W)

        ToolTip(self.referenced_form_combobox, text="You are adjusting a receiving form record")
        self.referenced_form_combobox.set("Receiving Form")

        # ----------------------------------[Referenced Form Number]----------------------------------

        # REF Number Entry Field
        ref_form_number_label = ttk.Label(first_child_frame, text="Referenced Form No.", style="CustomLabel.TLabel")
        ref_form_number_label.grid(row=4, column=1, padx=(8, 0), pady=(0, 0), sticky=W)

        self.ref_form_number_entry = ttk.Entry(first_child_frame, width=29, font=self.shared_functions.custom_font_size)
        self.ref_form_number_entry.grid(row=5, column=1, padx=(10, 0), pady=(0, 0), sticky=W)
        ToolTip(self.ref_form_number_entry,
                text="This is the reference number of the receiving form you will be adjusting")
        self.ref_form_number_entry.insert(0, self.ref_number_value)
        # Configure the entry as read-only
        self.ref_form_number_entry.state(['disabled'])

        # --------------------------------------------------[INCORRECT DETAILS]---------------------------------------------------

        incorrect_label = ttk.Label(second_child_frame, text="Incorrect Details", font=('Arial', 14, 'bold'))
        incorrect_label.grid(row=0, column=0, padx=(3, 0), pady=(10, 0), sticky=W)

        correct_label = ttk.Label(second_child_frame, text="Correct Details", font=('Arial', 14, 'bold'))
        correct_label.grid(row=0, column=3, padx=(50, 0), pady=(10, 0), sticky=W)

        # ----------------------------------[WAREHOUSE FIELD]----------------------------------#

        # Combobox for Warehouse Drop Down
        incorrect_warehouse_label = ttk.Label(second_child_frame, text="Warehouse", style="CustomLabel.TLabel")
        incorrect_warehouse_label.grid(row=1, column=0, padx=(3, 0), pady=(10, 0), sticky=W)

        # Warehouse Combobox field
        incorrect_warehouse_combobox = ttk.Combobox(second_child_frame,
                                                    state="disabled",
                                                    width=27,
                                                    font=self.shared_functions.custom_font_size
                                                    )
        incorrect_warehouse_combobox.grid(row=2, column=0, padx=(5, 0), pady=(0, 0), sticky=W)

        incorrect_warehouse_combobox.set(self.warehouse_value)

        # ----------------------------------[STATUS FIELD]----------------------------------#

        incorrect_status_label = ttk.Label(second_child_frame, text="Status", style="CustomLabel.TLabel")
        incorrect_status_label.grid(row=1, column=1, padx=(3, 0), pady=(10, 0), sticky=W)

        incorrect_status_combobox = ttk.Combobox(
            second_child_frame,
            state="disabled",
            width=27,
            font=self.shared_functions.custom_font_size
        )
        incorrect_status_combobox.grid(row=2, column=1, padx=(5, 0), pady=(0, 0), sticky=W)
        incorrect_status_combobox.set(self.status_value)

        # ----------------------------------[RM CODE FIELD]----------------------------------#

        # Combobox for RM CODE Drop Down
        incorrect_rm_codes_label = ttk.Label(second_child_frame, text="Raw Material", style="CustomLabel.TLabel")
        incorrect_rm_codes_label.grid(row=3, column=0, padx=(3, 0), pady=(10, 0), sticky=W)

        incorrect_rm_codes_combobox = ttk.Combobox(
            second_child_frame,
            state="disabled",
            width=27,
            font=self.shared_functions.custom_font_size
        )

        incorrect_rm_codes_combobox.grid(row=4, column=0, pady=(0, 0), padx=(5, 0), sticky=W)
        incorrect_rm_codes_combobox.set(self.rm_code_value)

        # ----------------------------------[QUANTITY FIELD]----------------------------------#
        # Quantity Entry Field
        incorrect_qty_label = ttk.Label(second_child_frame, text="Quantity", style="CustomLabel.TLabel")
        incorrect_qty_label.grid(row=3, column=1, padx=(3, 0), pady=(10, 0), sticky=W)

        incorrect_qty_entry = ttk.Entry(second_child_frame,
                                        width=29,
                                        font=self.shared_functions.custom_font_size,
                                        )  # Pass input for validation
        incorrect_qty_entry.grid(row=4, column=1, padx=(5, 0), pady=(0, 0), sticky=W)
        incorrect_qty_entry.insert(0, self.qty_value)
        # Configure the entry as read-only
        incorrect_qty_entry.state(['disabled'])

        # --------------------------------------------------[CORRECT DETAILS]---------------------------------------------------
        # Warehouse JSON-format choices (coming from the API)
        warehouses = self.get_warehouse_api
        self.warehouse_to_id = {item["wh_name"]: item["id"] for item in warehouses}
        warehouse_names = list(self.warehouse_to_id.keys())

        # Combobox for Warehouse Drop Down
        warehouse_label = ttk.Label(second_child_frame, text="Warehouse", style="CustomLabel.TLabel")
        warehouse_label.grid(row=1, column=3, pady=(10, 0), padx=(50, 0), sticky=W)

        # Warehouse Combobox field
        self.warehouse_combobox = ttk.Combobox(second_child_frame,
                                               values=warehouse_names,
                                               state="readonly",
                                               width=27,
                                               font=self.shared_functions.custom_font_size
                                               )
        self.warehouse_combobox.grid(row=2, column=3, padx=(50, 0), pady=(0, 0), sticky=W)

        ToolTip(self.warehouse_combobox, text="Choose a warehouse")

        self.warehouse_combobox.set(self.warehouse_value)

        # ----------------------------------[STATUS FIELD]----------------------------------#

        # Status JSON-format choices (coming from the API)
        status = self.get_status_api
        self.status_to_id = {item["name"]: item["id"] for item in status}
        status_names = list(self.status_to_id.keys())

        status_label = ttk.Label(second_child_frame, text="Status", style="CustomLabel.TLabel")
        status_label.grid(row=1, column=4, padx=(3, 0), pady=(10, 0), sticky=W)

        self.status_combobox = ttk.Combobox(
            second_child_frame,
            values=status_names,
            state="readonly",
            width=27,
            font=self.shared_functions.custom_font_size
        )
        self.status_combobox.grid(row=2, column=4, padx=(5, 0), pady=(0, 0), sticky=W)
        ToolTip(self.status_combobox, text="Please choose the raw material status")
        self.status_combobox.set(self.status_value)

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
        rm_codes_label = ttk.Label(second_child_frame, text="Raw Material", style="CustomLabel.TLabel")
        rm_codes_label.grid(row=3, column=3, padx=(50, 0), pady=(10, 0), sticky=W)

        self.rm_codes_combobox = ttk.Combobox(
            second_child_frame,
            values=rm_names,
            state="normal",
            width=27,
            font=self.shared_functions.custom_font_size
        )

        # Bind the key release event to the combobox to trigger uppercase conversion
        self.rm_codes_combobox.bind("<KeyRelease>", on_combobox_key_release)

        self.rm_codes_combobox.grid(row=4, column=3, pady=(0, 0), padx=(50, 0), sticky=W)
        ToolTip(self.rm_codes_combobox, text="Choose a raw material")
        self.rm_codes_combobox.set(self.rm_code_value)

        # ----------------------------------[QUANTITY FIELD]----------------------------------#

        def format_numeric_input(event):
            input_value = qty_var.get()

            # Get current cursor position
            cursor_position = self.qty_entry.index("insert")

            # Remove commas for processing
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
                self.qty_entry.delete(0, "end")
                self.qty_entry.insert(0, formatted_value)
                self.qty_entry.icursor(new_cursor_position)

            except ValueError:
                pass  # Ignore formatting if still invalid input (e.g. just a dash)

        # Tkinter StringVar for real-time updates
        qty_var = StringVar()

        # Validation Command for Entry Widget
        validate_numeric_command = second_child_frame.register(EntryValidation.validate_numeric_input)

        # Quantity Entry Field
        qty_label = ttk.Label(second_child_frame, text="Quantity", style="CustomLabel.TLabel")
        qty_label.grid(row=3, column=4, padx=(3, 0), pady=(10, 0), sticky=W)

        self.qty_entry = ttk.Entry(second_child_frame,
                                   width=29,
                                   font=self.shared_functions.custom_font_size,
                                   textvariable=qty_var,
                                   validate="key",
                                   validatecommand=(validate_numeric_command, "%P"))  # Pass input for validation
        self.qty_entry.grid(row=4, column=4, padx=(3, 0), pady=(0, 0), sticky=W)

        # Bind the event to format input dynamically while preserving cursor position
        self.qty_entry.bind("<KeyRelease>", format_numeric_input)
        ToolTip(self.qty_entry, text="Enter the Quantity(kg)")
        self.qty_entry.insert(0, self.qty_value)

        # ----------------------------------[PERSON RESPONSIBLE FIELD]----------------------------------#
        label = ttk.Label(second_child_frame, text="Responsible Person", style="CustomLabel.TLabel")
        label.grid(row=5, column=0, padx=5, pady=(10, 0), sticky=W)

        self.person_responsible_entry = ttk.Entry(second_child_frame, width=61,
                                                  font=self.shared_functions.custom_font_size)
        self.person_responsible_entry.grid(row=6, column=0, columnspan=2, padx=(5, 0), pady=0, sticky=W)
        ToolTip(self.person_responsible_entry, text="Type the Spillage Report Reference Number.")

        # **Button Frame (Properly Aligned)**
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill="x", padx=10, pady=10)

        # **Button Grid Configuration**
        button_frame.columnconfigure(0, weight=1)  # Cancel (Left)
        button_frame.columnconfigure(1, weight=1)  # Submit (Right)

        # **Cancel Button**
        cancel_button = ttk.Button(
            button_frame,
            text="Close",
            bootstyle=DANGER,
            command=self.add_record_window.destroy
        )
        cancel_button.grid(row=7, column=0, padx=10, sticky="w")

        submit_btn = ttk.Button(button_frame, text="Save the Adjustment", bootstyle=SUCCESS,
                                command=self.submit_data, )
        submit_btn.grid(row=7, column=1, pady=20, padx=10, sticky="e")

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

        # This is for the tab button for the tab sequence when the user hits tab to move to the next field
        self.adj_date_entry.entry.bind("<Tab>",
                                       lambda e: self.shared_functions.focus_next_widget(e, self.ref_number_entry))
        self.ref_number_entry.bind("<Tab>",
                                   lambda e: self.shared_functions.focus_next_widget(e, self.ref_date_entry.entry))
        self.ref_date_entry.entry.bind("<Tab>",
                                       lambda e: self.shared_functions.focus_next_widget(e,
                                                                                         self.adjustment_type_combobox))
        self.adjustment_type_combobox.bind("<Tab>",
                                           lambda e: self.shared_functions.focus_next_widget(e,
                                                                                             self.warehouse_combobox))
        self.warehouse_combobox.bind("<Tab>",
                                     lambda e: self.shared_functions.focus_next_widget(e, self.status_combobox))
        self.status_combobox.bind("<Tab>", lambda e: self.shared_functions.focus_next_widget(e, self.rm_codes_combobox))
        self.rm_codes_combobox.bind("<Tab>", lambda e: self.shared_functions.focus_next_widget(e, self.qty_entry))
        self.qty_entry.bind("<Tab>",
                            lambda e: self.shared_functions.focus_next_widget(e, self.person_responsible_entry))
        self.person_responsible_entry.bind("<Tab>", lambda e: self.shared_functions.focus_next_widget(e, submit_btn))

    def view_record(self, item):
        # If the window already exists, bring it to the front and return
        if self.add_record_window and self.add_record_window.winfo_exists():
            self.add_record_window.lift()
            return

        # Get the data from the record and assign each data to its corresponding variable

        self.item_id = item
        self.record = self.root.tree.item(item, 'values')
        self.ref_number_value = self.record[1]
        self.rm_code_value = self.record[2]
        self.adjustment_date_value = self.record[3]
        self.referenced_date_value = self.record[4]
        self.adjustment_type_value = self.record[5]
        self.responsible_person_value = self.record[6]
        self.qty_value = self.record[8]
        self.qty_prepared_value = self.record[9]
        self.qty_return_value = self.record[10]
        self.warehouse_value = self.record[11]
        self.warehouse_from_value = self.record[12]
        self.warehouse_to_value = self.record[13]
        self.status_value = self.record[14]
        self.status_old_value = self.record[15]
        self.status_new_value = self.record[16]

        self.preparation_record_id = self.record[17]
        self.receiving_record_id = self.record[18]
        self.outgoing_record_id = self.record[19]
        self.transfer_record_id = self.record[20]
        self.change_status_record_id = self.record[21]

        self.outgoing_record = self.get_outgoing_record(self.outgoing_record_id)

        self.add_record_window = ttk.Toplevel(self.root)
        self.add_record_window.title("Outgoing Form Adjustment - Type 1")

        # **Fixed Size** (Recommended for consistency)
        window_width = 1020  # Fixed width
        window_height = 580  # Fixed height

        # **Center the window**
        screen_width = self.add_record_window.winfo_screenwidth()
        screen_height = self.add_record_window.winfo_screenheight()
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 3  # Slightly higher than center

        self.add_record_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.add_record_window.resizable(True, True)  # Enable resizing for consistency

        # **Make widgets expand properly**
        self.add_record_window.grid_columnconfigure(0, weight=1)
        self.add_record_window.grid_rowconfigure(0, weight=1)

        # **Message Label (Warning)**
        message_label = ttk.Label(
            self.add_record_window,
            text="Outgoing Inventory Adjustment Form - Type 1",
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

        # Create a frame for the form inputs
        first_child_frame = ttk.Frame(form_frame)
        first_child_frame.pack(fill=X, pady=10, padx=20)

        # Create a frame for the form inputs
        second_child_frame = ttk.Frame(form_frame)
        second_child_frame.pack(fill=X, pady=10, padx=20)

        # ----------------------------------[ADJUSTMENT DATE FIELD]----------------------------------#
        date_label = ttk.Label(first_child_frame, text="Date of Adjustment", style="CustomLabel.TLabel")
        date_label.grid(row=0, column=0, padx=(3, 0), pady=0, sticky=W)

        # Create the DateEntry widget with yesterday's date as the default value
        self.adj_date_entry = ttk.Entry(
            first_child_frame,
            bootstyle=SECONDARY,
            width=25,
            font=self.shared_functions.custom_font_size
        )
        self.adj_date_entry.grid(row=1, column=0, padx=(5, 0), pady=0, sticky=W)
        self.adj_date_entry.insert(0, self.adjustment_date_value)
        self.adj_date_entry.state(["disabled"])

        # Set focus to the Entry field

        # ----------------------------------[REFERENCED NUMBER FIELD]----------------------------------#
        # REF Number Entry Field
        ref_number_label = ttk.Label(first_child_frame, text="Ref#.", style="CustomLabel.TLabel")
        ref_number_label.grid(row=0, column=1, padx=(8, 0), pady=(0, 0), sticky=W)

        self.ref_number_entry = ttk.Entry(first_child_frame, width=29, font=self.shared_functions.custom_font_size)
        self.ref_number_entry.grid(row=1, column=1, padx=(10, 0), pady=(0, 0), sticky=W)
        self.ref_number_entry.insert(0, self.ref_number_value)
        self.ref_number_entry.state(["disabled"])

        # ----------------------------------[REFERENCED DATE FIELD]----------------------------------#
        date_label = ttk.Label(first_child_frame, text="Referenced Date Affected", style="CustomLabel.TLabel")
        date_label.grid(row=2, column=0, padx=(3, 0), pady=(10, 0), sticky=W)

        # Create the DateEntry widget with yesterday's date as the default value
        self.ref_date_entry = ttk.Entry(
            first_child_frame,
            bootstyle=SECONDARY,
            width=25,
        )

        self.ref_date_entry.grid(row=3, column=0, columnspan=2, padx=(5, 0), pady=(0, 0), sticky=W)
        self.ref_date_entry.delete(0, "end")
        self.ref_date_entry.insert(0, self.referenced_date_value)
        self.ref_date_entry.state(["disabled"])
        self.ref_date_entry.config(font=self.shared_functions.custom_font_size)

        # ----------------------------------[Adjustment Type FIELD]----------------------------------#
        self.adjustment_type_combobox = ttk.Combobox(
            first_child_frame,
            state="disabled",
            width=27,
            font=self.shared_functions.custom_font_size
        )
        self.adjustment_type_combobox.grid(row=3, column=1, padx=(10, 0), pady=(0, 0), sticky=W)
        self.adjustment_type_combobox.set(self.adjustment_type_value)

        # ----------------------------------[REFERENCED FORMS]----------------------------------#
        referenced_form_label = ttk.Label(first_child_frame, text="Referenced Forms", style="CustomLabel.TLabel")
        referenced_form_label.grid(row=4, column=0, padx=(3, 0), pady=(10, 0), sticky=W)
        self.referenced_form_combobox = ttk.Combobox(
            first_child_frame,
            state="disabled",
            width=27,
            font=self.shared_functions.custom_font_size
        )
        self.referenced_form_combobox.grid(row=5, column=0, padx=(5, 0), pady=(0, 0), sticky=W)
        ToolTip(self.referenced_form_combobox, text="You are adjusting a receiving form record")
        self.referenced_form_combobox.set("Outgoing Form")

        # ----------------------------------[Referenced Form Number]----------------------------------
        # REF Number Entry Field
        ref_form_number_label = ttk.Label(first_child_frame, text="Referenced Form No.", style="CustomLabel.TLabel")
        ref_form_number_label.grid(row=4, column=1, padx=(8, 0), pady=(0, 0), sticky=W)

        self.ref_form_number_entry = ttk.Entry(first_child_frame, width=29, font=self.shared_functions.custom_font_size)
        self.ref_form_number_entry.grid(row=5, column=1, padx=(10, 0), pady=(0, 0), sticky=W)
        ToolTip(self.ref_form_number_entry,
                text="This is the reference number of the receiving form you will be adjusting")
        self.ref_form_number_entry.insert(0, self.outgoing_record['ref_number'])
        # Configure the entry as read-only
        self.ref_form_number_entry.state(['disabled'])

        # --------------------------------------------------[INCORRECT DETAILS]---------------------------------------------------
        incorrect_label = ttk.Label(second_child_frame, text="Incorrect Details", font=('Arial', 14, 'bold'))
        incorrect_label.grid(row=0, column=0, padx=(3, 0), pady=(10, 0), sticky=W)

        correct_label = ttk.Label(second_child_frame, text="Correct Details", font=('Arial', 14, 'bold'))
        correct_label.grid(row=0, column=3, padx=(50, 0), pady=(10, 0), sticky=W)

        # ----------------------------------[WAREHOUSE FIELD]----------------------------------#
        # Combobox for Warehouse Drop Down
        incorrect_warehouse_label = ttk.Label(second_child_frame, text="Warehouse", style="CustomLabel.TLabel")
        incorrect_warehouse_label.grid(row=1, column=0, padx=(3, 0), pady=(10, 0), sticky=W)

        # Warehouse Combobox field
        incorrect_warehouse_combobox = ttk.Combobox(second_child_frame,
                                                    state="disabled",
                                                    width=27,
                                                    font=self.shared_functions.custom_font_size
                                                    )
        incorrect_warehouse_combobox.grid(row=2, column=0, padx=(5, 0), pady=(0, 0), sticky=W)
        incorrect_warehouse_combobox.set(self.outgoing_record['wh_name'])

        # ----------------------------------[STATUS FIELD]----------------------------------#
        incorrect_status_label = ttk.Label(second_child_frame, text="Status", style="CustomLabel.TLabel")
        incorrect_status_label.grid(row=1, column=1, padx=(3, 0), pady=(10, 0), sticky=W)

        incorrect_status_combobox = ttk.Combobox(
            second_child_frame,
            state="disabled",
            width=27,
            font=self.shared_functions.custom_font_size
        )
        incorrect_status_combobox.grid(row=2, column=1, padx=(5, 0), pady=(0, 0), sticky=W)
        incorrect_status_combobox.set(self.outgoing_record['status'])

        # ----------------------------------[RM CODE FIELD]----------------------------------#
        # Combobox for RM CODE Drop Down
        incorrect_rm_codes_label = ttk.Label(second_child_frame, text="Raw Material", style="CustomLabel.TLabel")
        incorrect_rm_codes_label.grid(row=3, column=0, padx=(3, 0), pady=(10, 0), sticky=W)

        incorrect_rm_codes_combobox = ttk.Combobox(
            second_child_frame,
            state="disabled",
            width=27,
            font=self.shared_functions.custom_font_size
        )
        incorrect_rm_codes_combobox.grid(row=4, column=0, pady=(0, 0), padx=(5, 0), sticky=W)
        incorrect_rm_codes_combobox.set(self.outgoing_record['raw_material'])

        # ----------------------------------[QUANTITY FIELD]----------------------------------#
        # Quantity Entry Field
        incorrect_qty_label = ttk.Label(second_child_frame, text="Quantity", style="CustomLabel.TLabel")
        incorrect_qty_label.grid(row=3, column=1, padx=(3, 0), pady=(10, 0), sticky=W)

        incorrect_qty_entry = ttk.Entry(second_child_frame,
                                        width=29,
                                        font=self.shared_functions.custom_font_size,
                                        )  # Pass input for validation
        incorrect_qty_entry.grid(row=4, column=1, padx=(5, 0), pady=(0, 0), sticky=W)
        incorrect_qty_entry.insert(0, self.outgoing_record['qty_kg'])

        # Configure the entry as read-only
        incorrect_qty_entry.state(['disabled'])

        # --------------------------------------------------[CORRECT DETAILS]---------------------------------------------------
        # Warehouse JSON-format choices (coming from the API)

        # Combobox for Warehouse Drop Down
        warehouse_label = ttk.Label(second_child_frame, text="Warehouse", style="CustomLabel.TLabel")
        warehouse_label.grid(row=1, column=3, pady=(10, 0), padx=(50, 0), sticky=W)

        # Warehouse Combobox field
        self.warehouse_combobox = ttk.Combobox(second_child_frame,
                                               state="disabled",
                                               width=27,
                                               font=self.shared_functions.custom_font_size
                                               )
        self.warehouse_combobox.grid(row=2, column=3, padx=(50, 0), pady=(0, 0), sticky=W)
        ToolTip(self.warehouse_combobox, text="Choose a warehouse")
        self.warehouse_combobox.set(self.warehouse_value)

        # ----------------------------------[STATUS FIELD]----------------------------------#
        # Status JSON-format choices (coming from the API)

        status_label = ttk.Label(second_child_frame, text="Status", style="CustomLabel.TLabel")
        status_label.grid(row=1, column=4, padx=(3, 0), pady=(10, 0), sticky=W)

        self.status_combobox = ttk.Combobox(
            second_child_frame,
            state="disabled",
            width=27,
            font=self.shared_functions.custom_font_size
        )
        self.status_combobox.grid(row=2, column=4, padx=(5, 0), pady=(0, 0), sticky=W)
        ToolTip(self.status_combobox, text="Please choose the raw material status")
        self.status_combobox.set(self.status_value)

        # ----------------------------------[RM CODE FIELD]----------------------------------#
        # Combobox for RM CODE Drop Down
        rm_codes_label = ttk.Label(second_child_frame, text="Raw Material", style="CustomLabel.TLabel")
        rm_codes_label.grid(row=3, column=3, padx=(50, 0), pady=(10, 0), sticky=W)

        self.rm_codes_combobox = ttk.Combobox(
            second_child_frame,
            state="disabled",
            width=27,
            font=self.shared_functions.custom_font_size

        )
        self.rm_codes_combobox.grid(row=4, column=3, pady=(0, 0), padx=(50, 0), sticky=W)
        self.rm_codes_combobox.set(self.rm_code_value)

        # ----------------------------------[QUANTITY FIELD]----------------------------------#
        # Quantity Entry Field
        qty_label = ttk.Label(second_child_frame, text="Quantity", style="CustomLabel.TLabel")
        qty_label.grid(row=3, column=4, padx=(3, 0), pady=(10, 0), sticky=W)

        self.qty_entry = ttk.Entry(second_child_frame,
                                   width=29,
                                   font=self.shared_functions.custom_font_size,
                                   validate="key")
        self.qty_entry.grid(row=4, column=4, padx=(3, 0), pady=(0, 0), sticky=W)
        # Bind the event to format input dynamically while preserving cursor position
        self.qty_entry.insert(0, self.qty_value)

        # Configure the entry as read-only
        self.qty_entry.state(['disabled'])

        # ----------------------------------[PERSON RESPONSIBLE FIELD]----------------------------------#
        label = ttk.Label(second_child_frame, text="Responsible Person", style="CustomLabel.TLabel")
        label.grid(row=5, column=0, padx=5, pady=(10, 0), sticky=W)

        self.person_responsible_entry = ttk.Entry(second_child_frame,
                                                  width=61,
                                                  font=self.shared_functions.custom_font_size,
                                                  )
        self.person_responsible_entry.grid(row=6, column=0, columnspan=2, padx=(5, 0), pady=0, sticky=W)
        self.person_responsible_entry.insert(0, self.responsible_person_value)
        self.person_responsible_entry.state(['disabled'])

        # **Button Frame (Properly Aligned)**
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill="x", padx=10, pady=10)

        # **Button Grid Configuration**
        button_frame.columnconfigure(0, weight=1)  # Cancel (Left)
        button_frame.columnconfigure(1, weight=1)  # Submit (Right)

        # **Cancel Button**
        cancel_button = ttk.Button(
            button_frame,
            text="Close",
            bootstyle=DANGER,
            command=self.add_record_window.destroy
        )
        cancel_button.grid(row=7, column=0, padx=10, sticky="w")
