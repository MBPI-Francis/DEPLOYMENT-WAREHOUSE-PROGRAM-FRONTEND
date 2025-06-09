import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import requests
from ttkbootstrap.tooltip import ToolTip
from tkinter import messagebox
from backend.settings.database import server_ip
from datetime import datetime
from .adjustment_form import AdjustmentForm
from frontend.historical_data.change_status_form.adjustment_confirmation_messages import ConfirmationMessage



class ChangeStatusFormTable:
    def __init__(self, root):
        self.root = root
        self.adjustment_form = AdjustmentForm(self)
        self.confirmation_message = ConfirmationMessage(self.root, self)

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
                    "CSF No.",
                    "Raw Material",
                    "Quantity(kg)",
                    "Previous Status",
                    "Present Status",
                    "Warehouse",
                    "Change Date",
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



        # Define column headings
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c, False), anchor=W)
            self.tree.column(col, width=150, anchor="w")

        self.tree.pack(fill=BOTH, expand=YES)

        self.refresh_table()

        self.tree.bind("<Button-3>", self.show_context_menu)  # Right-click menu

    def show_context_menu(self, event):
        """Show right-click menu with Edit/Delete options."""
        item = self.tree.identify_row(event.y)

        if item:
            menu = ttk.Menu(self.root, tearoff=0)
            # menu.add_command(label="View", command=lambda: self.view_form.view_records(item))
            # menu.add_command(label="Adjust", command=lambda: self.adjustment_form.add_records(item))
            # menu.add_command(label="Adjust", command=lambda: self.adjustment_form.add_records(item))
            menu.add_command(label="Adjust", command=lambda: self.confirmation_message.show_confirmation_message(item))
            # menu.add_command(label="Delete", command=lambda: self.confirm_delete(item))
            # menu.add_command(label="Delete", command=lambda: self.delete_entry(item))
            menu.post(event.x_root, event.y_root)

    def refresh_table(self):
        """Fetch data from API and populate Treeview."""
        url = server_ip + "/api/change_status_form/v1/list/historical/"
        self.original_data = []

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            self.tree.delete(*self.tree.get_children())  # Clear existing data
            for item in data:
                qty_kg_formatted = "{:,.2f}".format(float(item["qty_kg"]))  # Format qty_kg with commas
                record = (
                    item["id"],  # Store ID
                    datetime.fromisoformat(item["created_at"]).strftime("%m/%d/%Y %I:%M %p"),
                    item["ref_number"],
                    item["raw_material"],
                    qty_kg_formatted,
                    item["current_status"],
                    item["new_status"],
                    item["wh_name"],
                    datetime.fromisoformat(item["change_status_date"]).strftime("%m/%d/%Y"),
                    datetime.fromisoformat(item["date_computed"]).strftime("%m/%d/%Y"),
                )
                self.original_data.append(record)  # Save record
                self.tree.insert("", END, iid=record[0], values=record[1:])
        except requests.exceptions.RequestException as e:
            return []



    def sort_column(self, col, reverse):
        """Sort Treeview column in ascending/descending order."""
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        data.sort(reverse=reverse)
        for index, (_, k) in enumerate(data):
            self.tree.move(k, "", index)
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))


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
