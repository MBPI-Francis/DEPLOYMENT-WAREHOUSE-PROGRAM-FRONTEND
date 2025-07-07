import ttkbootstrap as ttk
from ttkbootstrap import DateEntry
from ttkbootstrap.constants import *
import requests
from tkinter import Menu, Toplevel, Label, Entry, Button, messagebox
import tkinter as tk
from ttkbootstrap.dialogs import Messagebox
from backend.settings.database import server_ip
from datetime import datetime, timedelta
from ttkbootstrap.tooltip import ToolTip
from frontend.forms.shared import SharedFunctions



class NoteTable:
    def __init__(self, root):
        self.root = root

        # Instantiate the shared_function class
        shared_functions = SharedFunctions()

        get_status_api = shared_functions.get_status_api()
        get_warehouse_api = shared_functions.get_warehouse_api()
        get_rm_code_api = shared_functions.get_rm_code_api(force_refresh=True)


        # Frame for search
        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill=X, padx=10, pady=(15, 0))

        # # REF Number Entry Field
        # ref_number_label = ttk.Label(search_frame, text="OGR No.", style="CustomLabel.TLabel")
        # ref_number_label.grid(row=0, column=0, padx=5, pady=(0, 0), sticky=W)
        # ref_number_entry = ttk.Entry(search_frame, width=30, font=shared_functions.custom_font_size)
        # ref_number_entry.grid(row=1, column=0, padx=5, pady=(0, 0), sticky=W)
        # ToolTip(ref_number_entry, text="Enter the Reference Number")


        # Date Entry field
        date_label = ttk.Label(search_frame, text="Date FROM", style="CustomLabel.TLabel")
        date_label.grid(row=0, column=0, padx=5, pady=0, sticky=W)



        # Create the DateEntry widget with yesterday's date as the default value
        date_from_entry = ttk.DateEntry(
            search_frame,
            bootstyle=PRIMARY,
            dateformat="%m/%d/%Y",
            width=11
        )
        date_from_entry.grid(row=1, column=0, padx=5, pady=0, sticky=W)
        date_from_entry.entry.delete(0, "end")
        date_from_entry.entry.config(font=shared_functions.custom_font_size)
        #date_from_entry.entry.bind("<FocusOut>", format_date_while_typing)
        #date_from.entry.bind("<Return>", format_date_while_typing)
        ToolTip(date_from_entry, text="Please enter the outgoing date")


        # Date Entry field
        date_label = ttk.Label(search_frame, text="Date TO", style="CustomLabel.TLabel")
        date_label.grid(row=0, column=1, padx=5, pady=0, sticky=W)



        # Create the DateEntry widget with yesterday's date as the default value
        date_to_entry = ttk.DateEntry(
            search_frame,
            bootstyle=PRIMARY,
            dateformat="%m/%d/%Y",
            width=11
        )
        date_to_entry.grid(row=1, column=1, padx=5, pady=0, sticky=W)
        date_to_entry.entry.delete(0, "end")
        date_to_entry.entry.config(font=shared_functions.custom_font_size)
        # date_to_entry.entry.bind("<FocusOut>", format_date_while_typing)
        # date_to_entry.entry.bind("<Return>", format_date_while_typing)
        ToolTip(date_to_entry, text="Please enter the outgoing date")

        # RM CODE JSON-format choices (coming from the API)
        rm_codes = get_rm_code_api
        code_to_id = {item["rm_code"]: item["id"] for item in rm_codes}
        rm_names = ["All"] + list(code_to_id.keys())

        # Function to convert typed input to uppercase
        def on_combobox_key_release(event):
            # Get the current text in the combobox
            current_text = rm_codes_combobox.get()
            # Convert the text to uppercase and set it back
            rm_codes_combobox.set(current_text.upper())

        # Combobox for RM CODE Drop Down
        rm_codes_label = ttk.Label(search_frame, text="Raw Material", style="CustomLabel.TLabel")
        rm_codes_label.grid(row=0, column=2, padx=(8, 0), pady=(0, 0), sticky=W)

        rm_codes_combobox = ttk.Combobox(
            search_frame,
            values=rm_names,
            state="normal",
            width=20,
            font=shared_functions.custom_font_size
        )

        # Bind the key release event to the combobox to trigger uppercase conversion
        rm_codes_combobox.bind("<KeyRelease>", on_combobox_key_release)
        rm_codes_combobox.set("All")
        rm_codes_combobox.grid(row=1, column=2, pady=(0, 0), padx=(10, 0))
        ToolTip(rm_codes_combobox, text="Choose a raw material")

        # Warehouse JSON-format choices (coming from the API)
        warehouses = get_warehouse_api
        warehouse_to_id = {item["wh_name"]: item["id"] for item in warehouses}
        warehouse_names = ["All"] + list(warehouse_to_id.keys())

        # Combobox for Warehouse Drop Down
        warehouse_label = ttk.Label(search_frame, text="Location", style="CustomLabel.TLabel")
        warehouse_label.grid(row=0, column=3, padx=(8, 0), pady=(0, 0), sticky=W)


        # Warehouse Combobox field
        warehouse_combobox = ttk.Combobox(search_frame,
                                          values=warehouse_names,
                                          state="readonly",
                                          width=13,
                                          font=shared_functions.custom_font_size
                                          )
        warehouse_combobox.grid(row=1, column=3, padx=(10, 0), pady=(0, 0), sticky=W)
        warehouse_combobox.set("All")



        # Status JSON-format choices (coming from the API)
        status = get_status_api
        status_to_id = {item["name"]: item["id"] for item in status}
        status_names = ["All"] + list(status_to_id.keys())  # Add "All" at the beginning

        status_label = ttk.Label(search_frame, text="Status", style="CustomLabel.TLabel")
        status_label.grid(row=0, column=4, padx=(10, 0), pady=(0, 0), sticky=W)

        status_combobox = ttk.Combobox(
            search_frame,
            values=status_names,
            state="readonly",
            width=19,
            font=shared_functions.custom_font_size
        )
        status_combobox.grid(row=1, column=4, padx=(10, 0), pady=(0, 0), sticky=W)

        status_combobox.set("All")


        document_types = [
            {"id": "all", "document_type_name": "All"},
            {"id": "preparation_form_report", "document_type_name": "Preparation Form"},
            {"id": "outgoing_form_report", "document_type_name": "Outgoing Form"},
            {"id": "receiving_form_report", "document_type_name": "Receiving Form"},
            {"id": "adjustment_form_report", "document_type_name": "Adjustment Form"},
            {"id": "transfer_form_report", "document_type_name": "Transfer Form"},
            {"id": "change_status_form_report", "document_type_name": "Change Status Form"},
        ]


        # Example API call to get document types
        document_types = document_types
        document_type_to_id = {item["document_type_name"]: item["id"] for item in document_types}
        document_type_names = list(document_type_to_id.keys())


        # Document Type Label
        document_type_label = ttk.Label(search_frame, text="Document Type", style="CustomLabel.TLabel")
        document_type_label.grid(row=0, column=5, padx=(8, 0), pady=(0, 0), sticky=W)

        # Document Type Combobox field
        document_type_combobox = ttk.Combobox(search_frame,
                                              values=document_type_names,
                                              state="readonly",
                                              width=15,
                                              font=shared_functions.custom_font_size
                                              )
        document_type_combobox.grid(row=1, column=5, padx=(10, 0), pady=(0, 0), sticky=W)

        # Default selection (optional)
        document_type_combobox.set("All")


        # Add button to clear data
        btn_filter = ttk.Button(
            search_frame,
            text="Filter Data",
            command=self.load_data,
            bootstyle=SECONDARY,
        )
        btn_filter.grid(row=1, column=6, padx=(10, 0), pady=(0, 0), sticky=W)
        ToolTip(btn_filter, text="Click the button to filter the data table.")




        # Add button to clear data
        btn_export = ttk.Button(
            search_frame,
            text="Export to Excel",
            command=self.load_data,
            bootstyle=SUCCESS,
        )
        btn_export.grid(row=1, column=7, padx=(10, 0), pady=(0, 0), sticky=E)
        ToolTip(btn_export, text="Click the button to export the data into excel.")



        # Create a frame to hold the Treeview and Scrollbars
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # First, define self.tree before using it
        self.tree = ttk.Treeview(
            master=tree_frame,
            columns=(
                    "Date Encoded",
                    "Date Reported",
                    "Document Type",
                    "Document No.",
                    "Rar Material",
                    "QTY",
                    "Location",
                    "Status"
                     ),
            show='headings',
            style="Custom.Treeview",  # Apply row height adjustment
            bootstyle=PRIMARY
        )

        # Create a vertical scrollbar and attach it to the treeview
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=self.tree.yview)
        tree_scroll_y.pack(side=RIGHT, fill=Y)

        # Create a horizontal scrollbar (optional)
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=HORIZONTAL, command=self.tree.xview)
        tree_scroll_x.pack(side=BOTTOM, fill=X)

        # Pack the Treeview inside the frame
        self.tree.pack(fill=BOTH, expand=YES)

        # Configure the Treeview to use the scrollbars
        self.tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)


        # Define column headers
        col_names = ["Date Encoded",
                    "Date Reported",
                    "Document Type",
                    "Document No.",
                    "Rar Material",
                    "QTY",
                    "Location",
                    "Status"]
        for col in col_names:
            self.tree.heading(col, text=col, command=lambda _col=col: self.sort_treeview(_col, False), anchor=W)
            self.tree.column(col, anchor=W)


        # Load Data
        self.load_data()

    def load_data(self):
        """Fetch data from API and populate treeview."""
        url = server_ip + "/api/reports/v1/form-entries/"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            self.original_data = []  # Store all records

            self.tree.delete(*self.tree.get_children())  # Clear existing data
            for item in data:
                record = (
                    datetime.fromisoformat(item["date_encoded"]).strftime("%m/%d/%Y"),
                    datetime.fromisoformat(item["date_reported"]).strftime("%m/%d/%Y"),
                    item["document_type"],
                    item["document_number"],
                    item["mat_code"],
                    item["qty"],
                    item["whse_no"],
                    item["status"],

                )
                self.original_data.append(record)  # Save record
                self.tree.insert("", END, values=record[0:])
        except requests.exceptions.RequestException as e:
            return []

    def sort_treeview(self, col, reverse):
        """Sort treeview column data."""
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        items.sort(reverse=reverse)
        for index, (val, k) in enumerate(items):
            self.tree.move(k, "", index)
        self.tree.heading(col, command=lambda: self.sort_treeview(col, not reverse))

    def search_data(self, event=None):
        """Filter and display only matching records in the Treeview."""
        search_term = self.search_entry.get().strip().lower()

        # Clear current records
        self.tree.delete(*self.tree.get_children())

        # If search is empty, reload original data
        if not search_term:
            self.populate_treeview(self.original_data)
            return

        # Filter and display matching records
        filtered_data = [
            record for record in self.original_data
            if any(search_term in str(value).lower() for value in record[0:])  # Ignore ID
        ]

        if filtered_data:
            self.populate_treeview(filtered_data)
        else:
            messagebox.showinfo("Search", "No matching record found.")

    def populate_treeview(self, data):
        """Helper function to insert data into the Treeview."""
        for record in data:
            self.tree.insert("", END, iid=record[0], values=record[1:])

