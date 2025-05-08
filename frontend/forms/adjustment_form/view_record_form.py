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



class ViewRecordForm:
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
        self.view_record_window = None

        self.get_status_api = self.shared_functions.get_status_api()
        self.get_warehouse_api = self.shared_functions.get_warehouse_api()
        self.get_rm_code_api = self.shared_functions.get_rm_code_api(force_refresh=True)









    def on_edit_window_close(self):
        """Reset the edit_window reference when it is closed."""
        self.view_record_window.destroy()
        self.view_record_window = None


    def view_records(self,item):
        # If the window already exists, bring it to the front and return
        if self.view_record_window and self.view_record_window.winfo_exists():
            self.view_record_window.lift()
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
        
        self.view_record_window = ttk.Toplevel(self.root)
        self.view_record_window.title("Inventory Adjustment Form View Modal")

        # **Fixed Size** (Recommended for consistency)
        window_width = 780  # Fixed width
        window_height = 330  # Fixed height

        # **Center the window**
        screen_width = self.view_record_window.winfo_screenwidth()
        screen_height = self.view_record_window.winfo_screenheight()
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 3  # Slightly higher than center

        self.view_record_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.view_record_window.resizable(True, True)  # Enable resizing for consistency

        # **Make widgets expand properly**
        self.view_record_window.grid_columnconfigure(0, weight=1)
        self.view_record_window.grid_rowconfigure(0, weight=1)


        # **Message Label (Warning)**
        message_label = ttk.Label(
            self.view_record_window,
            text="Inventory Adjustment View Form",
            justify="center",
            font=("Arial", 14, "bold"),
            bootstyle=SECONDARY
        )
        message_label.pack(pady=10)


        # Create a frame for the form inputs
        form_frame = ttk.Frame(self.view_record_window)
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

        date_label = ttk.Label(date_frame, text="Date of Adjustment",  bootstyle=SECONDARY, font=("Arial", 11, "bold"))
        date_label.grid(row=1, column=0, padx=(3,10), pady=0, sticky=W)

        adj_date_label = ttk.Label(date_frame, text=self.adj_date_value, style="CustomLabel.TLabel")
        adj_date_label.grid(row=2, column=0, padx=(5,10), pady=0, sticky=W)




        # ----------------------------------[REFERENCED DATE FIELD]----------------------------------#
        date_label = ttk.Label(date_frame, text="Referenced Date", bootstyle=SECONDARY, font=("Arial", 11, "bold"))
        date_label.grid(row=1, column=1, padx=(3, 0), pady=(0, 0), sticky=W)


        ref_date_label = ttk.Label(date_frame, text=self.ref_date_value,style="CustomLabel.TLabel")
        ref_date_label.grid(row=2, column=1, padx=(5, 0), pady=(0, 0), sticky=W)



        # ----------------------------------[REFERENCED NUMBER FIELD]----------------------------------#
        # Reference Number FRAME (Right-aligned)
        refno_frame = ttk.Frame(form_frame)
        refno_frame.grid(row=1, column=1, padx=5, pady=(0, 5), sticky="w")

        # REF Number Entry Field
        ref_number_label = ttk.Label(refno_frame, text="Ref#.", bootstyle=SECONDARY, font=("Arial", 11, "bold"))
        ref_number_label.grid(row=1, column=0, padx=(3,0), pady=(0, 0), sticky=W)

        ref_number_label_value = ttk.Label(refno_frame, text=self.ref_number_value, style="CustomLabel.TLabel")
        ref_number_label_value.grid(row=2, column=0, padx=(5,0), pady=(0, 0), sticky=E)




        # ----------------------------------[RAW MATERIAL CODE FIELD]----------------------------------#
        # RM CODE FRAME
        rmcode_frame = ttk.Frame(form_frame)
        rmcode_frame.grid(row=2, column=0, padx=5, pady=(0, 10), sticky="w")


        # Combobox for RM CODE Drop Down
        rm_codes_label = ttk.Label(rmcode_frame, text="Raw Material", bootstyle=SECONDARY, font=("Arial", 11, "bold"))
        rm_codes_label.grid(row=1, column=0, padx=(3, 10), pady=(0, 0), sticky=W)

        rm_codes_label_value = ttk.Label(rmcode_frame, text=self.rm_code_value, style="CustomLabel.TLabel")
        rm_codes_label_value.grid(row=2, column=0, pady=(0, 0), padx=(5, 10), sticky=W)



        # ----------------------------------[QUANTITY FIELD]----------------------------------#
        # Function to format numeric input dynamically with cursor preservation



        """
        Formats the input dynamically while preserving the cursor position.
        """
        formatted_value = f"{float(self.qty_value):,}"


        # Quantity Entry Field
        qty_label = ttk.Label(rmcode_frame, text="Quantity(kg)", bootstyle=SECONDARY, font=("Arial", 11, "bold"))
        qty_label.grid(row=1, column=2, padx=(3,10), pady=(0, 0), sticky=W)

        qty_label_value = ttk.Label(rmcode_frame, text=formatted_value, style="CustomLabel.TLabel")
        qty_label_value.grid(row=2, column=2, padx=(5,10), pady=(0, 0), sticky=W)


        # ----------------------------------[STATUS FIELD]----------------------------------#

        status_label = ttk.Label(rmcode_frame, text="Status", bootstyle=SECONDARY, font=("Arial", 11, "bold"))
        status_label.grid(row=1, column=3, padx=(3, 0), pady=(0, 0), sticky=W)

        status_label_value = ttk.Label(rmcode_frame, text=self.status_value, style="CustomLabel.TLabel")
        status_label_value.grid(row=2, column=3, padx=(5, 0), pady=(0, 0), sticky=W)


        # ----------------------------------[WAREHOUSE FIELD]----------------------------------#
        warehouse_frame = ttk.Frame(form_frame)
        warehouse_frame.grid(row=2, column=1, padx=5, pady=(0, 10), sticky="w")


        # Combobox for Warehouse Drop Down
        warehouse_label = ttk.Label(warehouse_frame, text="Warehouse", bootstyle=SECONDARY, font=("Arial", 11, "bold"))
        warehouse_label.grid(row=1, column=0, padx=(3, 0), pady=(0, 0), sticky=W)

        warehouse_label_value = ttk.Label(warehouse_frame, text=self.warehouse_value, style="CustomLabel.TLabel")
        warehouse_label_value.grid(row=2, column=0, padx=(5, 0), pady=(0, 0), sticky=W)




        # ----------------------------------[REFERENCED DOC FIELD]----------------------------------#
        # REFERENCED DOCUMENT FRAME (Left-aligned)
        referenced_doc_frame = ttk.Frame(form_frame)
        referenced_doc_frame.grid(row=3, column=0, padx=5, pady=(0, 10), sticky="w")

        label = ttk.Label(referenced_doc_frame, text="Referenced Doc.", bootstyle=SECONDARY, font=("Arial", 11, "bold"))
        label.grid(row=1, column=0, padx=(3,10), pady=0, sticky=W)

        ref_doc_label = ttk.Label(referenced_doc_frame, text=self.ref_doc_value, style="CustomLabel.TLabel")
        ref_doc_label.grid(row=2, column=0, padx=(5, 10), pady=0, sticky=W)




        # ----------------------------------[REFERENCED DOCUMENT NO FIELD]----------------------------------#
        label = ttk.Label(referenced_doc_frame, text="Doc. Reference #", bootstyle=SECONDARY, font=("Arial", 11, "bold"))
        label.grid(row=1, column=1, padx=5, pady=(0,0), sticky=W)

        ref_doc_number_label = ttk.Label(referenced_doc_frame, text=self.ref_doc_number_value, style="CustomLabel.TLabel")
        ref_doc_number_label.grid(row=2, column=1, padx=(5, 0), pady=0, sticky=W)




        # ----------------------------------[REASON FIELD]----------------------------------#
        label = ttk.Label(form_frame, text="Reason/Remarks",  bootstyle=SECONDARY, font=("Arial", 11, "bold"))
        label.grid(row=4, column=0, padx=(8,0), pady=0, sticky=W)

        reason_label = ttk.Label(form_frame, text=self.reason_value, style="CustomLabel.TLabel")
        reason_label.grid(row=5, column=0,columnspan=2 , padx=(10, 0), pady=0, sticky=NSEW)



        # Configure columns for even stretch
        form_frame.grid_columnconfigure(1, weight=1)

        # Submit button

        # **Cancel Button**
        cancel_button = ttk.Button(
            form_frame,
            text="Close",
            bootstyle=DANGER,
            command=self.view_record_window.destroy
        )
        cancel_button.grid(row=6, column=0, padx=5, pady=(20,0), sticky="w")




