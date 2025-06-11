import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import requests
from backend.settings.database import server_ip
from tkinter import Toplevel, messagebox
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.widgets import DateEntry
from datetime import datetime
from ttkbootstrap.tooltip import ToolTip
from .adjustment_form import AdjustmentForm
from frontend.historical_data.shared_confirmation_messages import ConfirmationMessage


class PreparationFormTable:
    def __init__(self, root):
        self.root = root
        self.adjustment_form = AdjustmentForm(self)
        self.confirmation_message = ConfirmationMessage(self.root, self, "preparation")

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
            command=self.refresh_table,
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
                    "PF ID No.",
                    "Raw Material",
                    "QTY (Prepared)",
                    "QTY (Return)",
                    "Consumption",
                    "Status",
                    "Warehouse",
                    "Date Reported",
                    "Date Computed"),

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


        # Define columns
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        self.tree.pack(fill=BOTH, expand=YES)
        self.refresh_table()

        # Define column headers
        col_names = [
            "Date Encoded",
            "PF ID No.",
            "Raw Material",
            "QTY (Prepared)",
            "QTY (Return)",
            "Consumption",
            "Status",
            "Warehouse",
            "Date Reported",
            "Date Computed"
        ]
        for col in col_names:
            self.tree.heading(col, text=col, command=lambda _col=col: self.sort_treeview(_col, False), anchor=W)
            self.tree.column(col, anchor=W)

        self.tree.bind("<Button-3>", self.show_context_menu)  # Right-click menu

    def show_context_menu(self, event):
        """Show right-click menu with Edit/Delete options."""
        item = self.tree.identify_row(event.y)

        if item:
            menu = ttk.Menu(self.root, tearoff=0)

            self.record = self.tree.item(item, 'values')
            is_adjusted = self.record[10]

            if is_adjusted == 'True':
                menu.add_command(label="Adjust",
                                 command=lambda: self.confirmation_message.show_confirmation_message_adjusted(item))

            else:
                menu.add_command(label="Adjust",
                                 command=lambda: self.confirmation_message.show_confirmation_message(item))

            menu.post(event.x_root, event.y_root)

    def fetch_data(self):
        """Fetch data from API."""
        url = server_ip + "/api/preparation_forms/v1/list/historical/"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return []

    def refresh_table(self):
        """Refresh Treeview with data."""

        self.original_data = []

        self.tree.delete(*self.tree.get_children())
        for item in self.fetch_data():
            qty_prepared_formatted = "{:,.2f}".format(float(item["qty_prepared"]))  # Format qty_kg with commas
            qty_return_formatted = "{:,.2f}".format(float(item["qty_return"]))  # Format qty_kg with commas

            consumption = float(item["qty_prepared"]) - float(item["qty_return"])
            consumption_formatted = "{:,.2f}".format(consumption)

            record = (
                item["id"],  # Store ID
                datetime.fromisoformat(item["created_at"]).strftime("%m/%d/%Y %I:%M %p"),
                item["ref_number"],
                item["raw_material"],
                qty_prepared_formatted,
                qty_return_formatted,
                consumption_formatted,
                item["status"],
                item["wh_name"],
                datetime.fromisoformat(item["preparation_date"]).strftime("%m/%d/%Y"),
                datetime.fromisoformat(item["date_computed"]).strftime("%m/%d/%Y"),
                item["is_adjusted"],
            )
            self.original_data.append(record)  # Save record
            self.tree.insert("", END, iid=record[0], values=record[1:])

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

