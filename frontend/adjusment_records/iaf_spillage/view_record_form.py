import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.constants import *
import requests
from backend.settings.database import server_ip
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.dialogs.dialogs import Messagebox
from datetime import datetime, timedelta
from frontend.forms.shared import SharedFunctions
from tkinter import StringVar, messagebox



class ViewForm:
    def __init__(self, root):
        self.spillage_form_no_value = None
        self.responsible_person_value = None
        self.incident_date_value = None
        self.spillage_no_entry = None
        self.incident_date_entry = None
        self.person_responsible_entry = None
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
        self.edit_window = None



    def on_edit_window_close(self):
        """Reset the edit_window reference when it is closed."""
        self.edit_window.destroy()
        self.edit_window = None



    def view_record(self,item):
        # If the window already exists, bring it to the front and return
        if self.edit_window and self.edit_window.winfo_exists():
            self.edit_window.lift()
            return



        # Get the data from the record and assign each data to its corresponding variable
        self.item = item
        self.record = self.root.tree.item(item, 'values')
        self.ref_number_value = self.record[1]
        self.rm_code_value = self.record[2]
        self.qty_value = self.record[3]
        self.status_value = self.record[4]
        self.warehouse_value = self.record[5]
        self.spillage_form_no_value = self.record[6]
        self.responsible_person_value = self.record[7]
        self.incident_date_value = self.record[8]
        self.adj_date_value = self.record[9]
        self.ref_date_value = self.record[10]
        self.reason_value = self.record[11]
        
        self.edit_window = ttk.Toplevel(self.root)
        self.edit_window.title("View Spillage Adjustment Record")

        # **Fixed Size** (Recommended for consistency)
        window_width = 490  # Fixed width
        window_height = 550  # Fixed height

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
            text="View Spillage Adjustment Record",
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
        date_label = ttk.Label(form_frame, text="Date of Adjustment", style="CustomLabel.TLabel")
        date_label.grid(row=0, column=0, padx=(3,0), pady=0, sticky=W)

        # Create the DateEntry widget with yesterday's date as the default value
        self.adj_date_entry = ttk.Entry(
            form_frame,
            bootstyle=SECONDARY,
            width=25
        )
        self.adj_date_entry.grid(row=1, column=0, padx=(5,0), pady=0, sticky=W)
        self.adj_date_entry.config(font=self.shared_functions.custom_font_size)
        self.adj_date_entry.insert(0, self.adj_date_value)
        self.adj_date_entry.config(state="disabled")

        # ----------------------------------[REFERENCED NUMBER FIELD]----------------------------------#


        # REF Number Entry Field
        ref_number_label = ttk.Label(form_frame, text="Ref#.", style="CustomLabel.TLabel")
        ref_number_label.grid(row=0, column=1, padx=(8, 0), pady=(0, 0), sticky=W)
        self.ref_number_entry = ttk.Entry(form_frame, width=29, font=self.shared_functions.custom_font_size)
        self.ref_number_entry.grid(row=1, column=1, padx=(10, 0), pady=(0, 0), sticky=W)
        self.ref_number_entry.insert(0, self.ref_number_value)
        self.ref_number_entry.config(state="disabled")


        # ----------------------------------[REFERENCED DATE FIELD]----------------------------------#
        date_label = ttk.Label(form_frame, text="Referenced Date Affected", style="CustomLabel.TLabel")
        date_label.grid(row=2, column=0, padx=(3, 0), pady=(10, 0), sticky=W)

        # Create the DateEntry widget with yesterday's date as the default value
        self.ref_date_entry = ttk.Entry(
            form_frame,
            bootstyle=SECONDARY,
            width=57
        )
        self.ref_date_entry.grid(row=3, column=0, columnspan=2, padx=(5, 0), pady=(0, 0), sticky=W)
        self.ref_date_entry.config(font=self.shared_functions.custom_font_size)
        self.ref_date_entry.insert(0, self.ref_date_value)
        self.ref_date_entry.config(state="disabled")

        # ----------------------------------[SPILLAGE REPORT # FIELD]----------------------------------#
        label = ttk.Label(form_frame, text="Spillage Report #", style="CustomLabel.TLabel")
        label.grid(row=4, column=0, padx=5,  pady=(10, 0), sticky=W)

        self.spillage_no_entry = ttk.Entry(form_frame, width=29, font=self.shared_functions.custom_font_size)
        self.spillage_no_entry.grid(row=5, column=0, padx=(5, 0), pady=0, sticky=W)
        self.spillage_no_entry.insert(0, self.spillage_form_no_value)
        self.spillage_no_entry.config(state="disabled")
   

        # ----------------------------------[INCIDENT REPORT DATE FIELD]----------------------------------#
        date_label = ttk.Label(form_frame, text="Date of Incident", style="CustomLabel.TLabel")
        date_label.grid(row=4, column=1, padx=(3, 0),  pady=(10, 0), sticky=W)


        # Create the DateEntry widget with yesterday's date as the default value
        self.incident_date_entry = ttk.Entry(
            form_frame,
            bootstyle=SECONDARY,
            width=25
        )


        self.incident_date_entry.grid(row=5, column=1, padx=(5, 0), pady=(0, 0), sticky=W)
        self.incident_date_entry.config(font=self.shared_functions.custom_font_size)
        self.incident_date_entry.insert(0, self.incident_date_value)
        self.incident_date_entry.config(state="disabled")

        # ----------------------------------[WAREHOUSE FIELD]----------------------------------#


        # Combobox for Warehouse Drop Down
        warehouse_label = ttk.Label(form_frame, text="Warehouse", style="CustomLabel.TLabel")
        warehouse_label.grid(row=6, column=0, padx=(3, 0),  pady=(10, 0), sticky=W)


        # Warehouse Combobox field
        self.warehouse_combobox = ttk.Combobox(form_frame,
                                          state="disabled",
                                          width=27,
                                          font=self.shared_functions.custom_font_size
                                          )
        self.warehouse_combobox.grid(row=7, column=0, padx=(5, 0), pady=(0, 0), sticky=W)
        self.warehouse_combobox.set(self.warehouse_value)

        # ----------------------------------[STATUS FIELD]----------------------------------
        status_label = ttk.Label(form_frame, text="Status", style="CustomLabel.TLabel")
        status_label.grid(row=6, column=1, padx=(3, 0), pady=(10, 0), sticky=W)

        self.status_combobox = ttk.Combobox(
            form_frame,
            state="disabled",
            width=27,
            font=self.shared_functions.custom_font_size
        )
        self.status_combobox.grid(row=7, column=1, padx=(5, 0), pady=(0, 0), sticky=W)
        self.status_combobox.set(self.status_value)

        # ----------------------------------[RM CODE FIELD]----------------------------------#

        # Combobox for RM CODE Drop Down
        rm_codes_label = ttk.Label(form_frame, text="Raw Material", style="CustomLabel.TLabel")
        rm_codes_label.grid(row=8, column=0, padx=(3, 0),  pady=(10, 0), sticky=W)

        self.rm_codes_combobox = ttk.Combobox(
            form_frame,
            state="disabled",
            width=27,
            font=self.shared_functions.custom_font_size
        )

        # Bind the key release event to the combobox to trigger uppercase conversion
        self.rm_codes_combobox.set(self.rm_code_value)
        self.rm_codes_combobox.grid(row=9, column=0, pady=(0, 0), padx=(5, 0), sticky=W)


        # ----------------------------------[QUANTITY FIELD]----------------------------------#
        # Quantity Entry Field
        qty_label = ttk.Label(form_frame, text="Quantity Lost", style="CustomLabel.TLabel")
        qty_label.grid(row=8, column=1, padx=(3,0),  pady=(10, 0), sticky=W)

        self.qty_entry = ttk.Entry(form_frame,
                              width=29,
                              font=self.shared_functions.custom_font_size)
        cleaned_qty_value = self.qty_value.replace("-", "").strip()
        self.qty_entry.insert(0, cleaned_qty_value)
        self.qty_entry.config(state="disabled")
        self.qty_entry.grid(row=9, column=1, padx=(5,0), pady=(0, 0), sticky=W)


        # ----------------------------------[REASON FOR DISCREPANCY]----------------------------------#
        # Quantity Entry Field
        reason_label = ttk.Label(form_frame, text="Reason for Discrepancy", style="CustomLabel.TLabel")
        reason_label.grid(row=10, column=0, padx=(3,0),  pady=(10, 0), sticky=W)

        self.reason = ttk.Entry(form_frame,
                              width=61,
                              font=self.shared_functions.custom_font_size)
        self.reason.insert(0, self.reason_value)
        self.reason.config(state="disabled")
        self.reason.grid(row=11, column=0, columnspan=2, padx=(5, 0), pady=0, sticky=W)


        # ----------------------------------[PERSON RESPONSIBLE FIELD]----------------------------------#
        label = ttk.Label(form_frame, text="Responsible Person", style="CustomLabel.TLabel")
        label.grid(row=12, column=0, padx=5,  pady=(10, 0), sticky=W)

        self.person_responsible_entry = ttk.Entry(form_frame, width=61, font=self.shared_functions.custom_font_size)
        self.person_responsible_entry.grid(row=13, column=0, columnspan=2, padx=(5, 0), pady=0, sticky=W)
        self.person_responsible_entry.insert(0, self.responsible_person_value)
        self.person_responsible_entry.config(state='disabled')

        # Submit button

        # **Cancel Button**
        cancel_button = ttk.Button(
            form_frame,
            text="Close",
            bootstyle=DANGER,
            command=self.edit_window.destroy
        )
        cancel_button.grid(row=14, column=0, padx=5, pady=(20, 0), sticky="w")
