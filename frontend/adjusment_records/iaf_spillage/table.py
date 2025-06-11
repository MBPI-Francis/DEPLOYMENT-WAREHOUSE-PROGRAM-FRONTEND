import ttkbootstrap as ttk
from ttkbootstrap import DateEntry
from ttkbootstrap.constants import *
import requests
from tkinter import Menu, Toplevel, Label, Entry, Button, messagebox
import tkinter as tk
from ttkbootstrap.dialogs import Messagebox
from backend.settings.database import server_ip
from datetime import datetime
from ttkbootstrap.tooltip import ToolTip


class AdjustmentSpillageTable:
    def __init__(self, root):
        self.root = root

        # Frame for search
        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill=X, padx=10, pady=(15, 0))
        ttk.Label(search_frame, text="Search:", style="CustomLabel.TLabel").pack(side=LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=50)
        self.search_entry.pack(side=LEFT)
        self.search_entry.bind("<Return>", self.search_data)


        # Add button to clear data
        btn_refresh = ttk.Button(
            search_frame,
            text="Refresh",
            command=self.load_data,
            bootstyle=SECONDARY,
        )
        btn_refresh.pack(side=RIGHT, padx=10)
        ToolTip(btn_refresh, text="Click the button to refresh the data table.")

        # Create a frame to hold the Treeview and Scrollbars
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # First, define self.tree before using it
        self.tree = ttk.Treeview(
            master=tree_frame,
            columns=(
                "Date Encoded",
                "Reference No.",
                "Raw Material (RM)",
                "Quantity (QTY)",
                "Status",
                "Warehouse",
                "Adjustment Date",
                "Referenced Date",
                "Responsible Person",
                "Date Computed"
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
        col_names = [
                "Date Encoded",
                "Reference No.",
                "Raw Material (RM)",
                "Quantity (QTY)",
                "Status",
                "Warehouse",
                "Adjustment Date",
                "Referenced Date",
                "Responsible Person",
                "Date Computed"]
        for col in col_names:
            self.tree.heading(col, text=col, command=lambda _col=col: self.sort_treeview(_col, False), anchor=W)
            self.tree.column(col, anchor=W)


        # Load Data
        self.load_data()

    def load_data(self):
        """Fetch data from API and populate treeview."""
        url = server_ip + "/api/notes/v1/list/historical/"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            self.original_data = []  # Store all records

            self.tree.delete(*self.tree.get_children())  # Clear existing data
            for item in data:
                record = (
                    item["id"],  # Store ID
                    datetime.fromisoformat(item["created_at"]).strftime("%m/%d/%Y %I:%M %p"),
                    item["ref_number"],
                    item["raw_material"],
                    item["incorrect_preparation_id"],
                    item["incorrect_receiving_id"],
                    item["incorrect_outgoing_id"],
                    item["incorrect_transfer_id"],
                    item["incorrect_change_status_id"],
                    item["responsible_person"],
                    item["qty_prepared"],
                    item["qty_return"],
                    item["wh_name"],
                    item["from_warehouse"],
                    item["to_warehouse"],
                    item["status"],
                    item["current_status"],
                    item["new_status"],
                    datetime.fromisoformat(item["adjustment_date"]).strftime("%m/%d/%Y"),
                    datetime.fromisoformat(item["referenced_date"]).strftime("%m/%d/%Y"),
                    datetime.fromisoformat(item["date_computed"]).strftime("%m/%d/%Y"),

                )
                self.original_data.append(record)  # Save record
                self.tree.insert("", END, iid=record[0], values=record[1:])
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
            if any(search_term in str(value).lower() for value in record[1:])  # Ignore ID
        ]

        if filtered_data:
            self.populate_treeview(filtered_data)
        else:
            messagebox.showinfo("Search", "No matching record found.")

    def populate_treeview(self, data):
        """Helper function to insert data into the Treeview."""
        for record in data:
            self.tree.insert("", END, iid=record[0], values=record[1:])

