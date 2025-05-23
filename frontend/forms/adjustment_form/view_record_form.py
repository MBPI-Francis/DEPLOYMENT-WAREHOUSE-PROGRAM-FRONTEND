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
        self.incident_date_value = None
        self.responsible_person_value = None
        self.spillage_form_no_value = None
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
        self.spillage_form_no_value = self.record[6]
        self.responsible_person_value = self.record[7]
        self.incident_date_value = self.record[8]
        self.adj_date_value = self.record[9]
        self.ref_date_value = self.record[10]

        self.view_record_window = ttk.Toplevel(self.root)
        self.view_record_window.title("Inventory Adjustment Form View Modal")

        # **Fixed Size** (Recommended for consistency)
        window_width = 550  # Fixed width
        window_height = 450  # Fixed height

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


        # ----------------------------------[REFERENCED NUMBER]----------------------------------#

        # REF Number Entry Field
        ref_number_label = ttk.Label(form_frame, text="Ref#.", bootstyle=SECONDARY, font=("Arial", 11, "bold"))
        ref_number_label.grid(row=0, column=0, padx=(3,0), pady=5, sticky=W)

        ref_number_label_value = ttk.Label(form_frame, text=self.ref_number_value, style="CustomLabel.TLabel")
        ref_number_label_value.grid(row=0, column=1, padx=(5,0), pady=5, sticky=W)



        # ----------------------------------[ADJUSTMENT DATE]----------------------------------#
        date_label = ttk.Label(form_frame, text="Date of Adjustment",  bootstyle=SECONDARY, font=("Arial", 11, "bold"))
        date_label.grid(row=1, column=0, padx=(3,10), pady=5, sticky=W)

        adj_date_label = ttk.Label(form_frame, text=self.adj_date_value, style="CustomLabel.TLabel")
        adj_date_label.grid(row=1, column=1, padx=(5,10), pady=5, sticky=W)



        # ----------------------------------[REFERENCED DATE]----------------------------------#
        date_label = ttk.Label(form_frame, text="Referenced Date", bootstyle=SECONDARY, font=("Arial", 11, "bold"))
        date_label.grid(row=2, column=0, padx=(3, 0), pady=5, sticky=W)

        ref_date_label = ttk.Label(form_frame, text=self.ref_date_value, style="CustomLabel.TLabel")
        ref_date_label.grid(row=2, column=1, padx=(5, 0), pady=5, sticky=W)



        # ----------------------------------[Spillage Incident Report]----------------------------------#
        label = ttk.Label(form_frame, text="Spillage Incident Report #", bootstyle=SECONDARY, font=("Arial", 11, "bold"))
        label.grid(row=3, column=0, padx=(3,10), pady=5, sticky=W)

        spillage_report_label = ttk.Label(form_frame, text=self.spillage_form_no_value, style="CustomLabel.TLabel")
        spillage_report_label.grid(row=3, column=1, padx=(5, 10), pady=5, sticky=W)


        # ----------------------------------[INCIDENT DATE]----------------------------------#
        date_label = ttk.Label(form_frame, text="Incident Date", bootstyle=SECONDARY, font=("Arial", 11, "bold"))
        date_label.grid(row=4, column=0, padx=(3, 0), pady=5, sticky=W)

        incident_date_label = ttk.Label(form_frame, text=self.incident_date_value, style="CustomLabel.TLabel")
        incident_date_label.grid(row=4, column=1, padx=(5, 0), pady=5, sticky=W)


        # ----------------------------------[WAREHOUSE]----------------------------------#
        # Combobox for Warehouse Drop Down
        warehouse_label = ttk.Label(form_frame, text="Warehouse", bootstyle=SECONDARY, font=("Arial", 11, "bold"))
        warehouse_label.grid(row=5, column=0, padx=(3, 0), pady=5, sticky=W)

        warehouse_label_value = ttk.Label(form_frame, text=self.warehouse_value, style="CustomLabel.TLabel")
        warehouse_label_value.grid(row=5, column=1, padx=(5, 0), pady=5, sticky=W)


        # ----------------------------------[STATUS]----------------------------------#
        status_label = ttk.Label(form_frame, text="Status", bootstyle=SECONDARY, font=("Arial", 11, "bold"))
        status_label.grid(row=6, column=0, padx=(3, 0), pady=5, sticky=W)

        status_label_value = ttk.Label(form_frame, text=self.status_value, style="CustomLabel.TLabel")
        status_label_value.grid(row=6, column=1, padx=(5, 0), pady=5, sticky=W)


        # ----------------------------------[RAW MATERIAL CODE]----------------------------------#
        # Combobox for RM CODE Drop Down
        rm_codes_label = ttk.Label(form_frame, text="Raw Material", bootstyle=SECONDARY, font=("Arial", 11, "bold"))
        rm_codes_label.grid(row=7, column=0, padx=(3, 10), pady=5, sticky=W)

        rm_codes_label_value = ttk.Label(form_frame, text=self.rm_code_value, style="CustomLabel.TLabel")
        rm_codes_label_value.grid(row=7, column=1, padx=(5, 10),  pady=5, sticky=W)


        # ----------------------------------[QUANTITY]----------------------------------#
        # Function to format numeric input dynamically with cursor preservation

        """
        Formats the input dynamically while preserving the cursor position.
        """
        formatted_value = f"{float(self.qty_value):,}"

        # Quantity Entry Field
        qty_label = ttk.Label(form_frame, text="Quantity(kg)", bootstyle=SECONDARY, font=("Arial", 11, "bold"))
        qty_label.grid(row=8, column=0, padx=(3, 10), pady=5, sticky=W)

        qty_label_value = ttk.Label(form_frame, text=formatted_value, style="CustomLabel.TLabel")
        qty_label_value.grid(row=8, column=1, padx=(5, 10), pady=5, sticky=W)


        # ----------------------------------[RESPONSIBLE PERSON]----------------------------------#
        date_label = ttk.Label(form_frame, text="Responsible Person", bootstyle=SECONDARY, font=("Arial", 11, "bold"))
        date_label.grid(row=9, column=0, padx=(3, 0), pady=5, sticky=W)

        responsible_person_label = ttk.Label(form_frame, text=self.responsible_person_value, style="CustomLabel.TLabel")
        responsible_person_label.grid(row=9, column=1, padx=(5, 0), pady=5, sticky=W)


        # **Cancel Button**
        cancel_button = ttk.Button(
            form_frame,
            text="Close",
            bootstyle=DANGER,
            command=self.view_record_window.destroy
        )
        cancel_button.grid(row=10, column=0, padx=5, pady=(20,0), sticky="w")




