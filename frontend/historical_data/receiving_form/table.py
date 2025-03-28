import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import requests
from backend.settings.database import server_ip
from tkinter import Toplevel, messagebox, StringVar
from ttkbootstrap.dialogs import Querybox, Messagebox
from ttkbootstrap.widgets import DateEntry
from uuid import UUID
from datetime import datetime
from ttkbootstrap.tooltip import ToolTip


class NoteTable:
    def __init__(self, root):
        self.root = root

        # Frame for search
        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill=X, padx=10, pady=(15, 0))
        ttk.Label(search_frame, text="Search:").pack(side=LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=50)
        self.search_entry.pack(side=LEFT)
        self.search_entry.bind("<Return>", self.search_data)


        # Add button to restore data
        btn_clear = ttk.Button(
            search_frame,
            text="Recycle Bin",
            # command,
            bootstyle=SECONDARY,
        )
        btn_clear.pack(side=RIGHT)
        ToolTip(btn_clear, text="Click the button to recycle deleted records.")

        # Create a frame to hold the Treeview and Scrollbars
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # First, define self.tree before using it
        self.tree = ttk.Treeview(
            master=tree_frame,
            columns=("Raw Material", "Warehouse", "Ref No.", "Quantity(kg)", "Receiving Date", "Date Encoded", "Date Computed"),
            show='headings',
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

        self.tree.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.refresh_table()

        # Define column headers
        col_names = ["Raw Material", "Warehouse", "Ref No.", "Quantity(kg)", "Receiving Date", "Date Encoded", "Date Computed"]
        for col in col_names:
            self.tree.heading(col, text=col, command=lambda _col=col: self.sort_treeview(_col, False), anchor=W)
            self.tree.column(col, anchor=W)

    def fetch_data(self):
        """Fetch data from API."""
        url = server_ip + "/api/receiving_reports/v1/list/historical/"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return []

    def refresh_table(self):
        """Refresh Treeview with data."""
        self.tree.delete(*self.tree.get_children())
        self.original_data = []  # Store all records

        for item in self.fetch_data():
            qty_kg_formatted = "{:,.2f}".format(float(item["qty_kg"]))  # Format qty_kg with commas
            record = (
                item["id"],  # Store ID
                item["raw_material"],
                item["wh_name"],
                item["ref_number"],
                qty_kg_formatted,
                datetime.fromisoformat(item["receiving_date"]).strftime("%m/%d/%Y"),
                datetime.fromisoformat(item["created_at"]).strftime("%m/%d/%Y %I:%M %p"),
                datetime.fromisoformat(item["date_computed"]).strftime("%m/%d/%Y")

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


    def show_context_menu(self, event):
        """Show right-click menu."""
        item = self.tree.identify_row(event.y)
        if item:
            menu = ttk.Menu(self.root, tearoff=0)
            menu.add_command(label="Delete", command=lambda: self.confirm_delete(item))
            menu.post(event.x_root, event.y_root)


    def confirm_delete(self, item_id):
        """Show confirmation before deleting record."""
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this record?"):
            self.delete_record(item_id)

    def delete_record(self, item_id):
        """Send DELETE request to API."""
        url = server_ip + f"/api/receiving_reports/v1/delete/{item_id}/"
        response = requests.delete(url)
        if response.status_code == 200:
            self.refresh_table()
            messagebox.showinfo("Success", "Record deleted successfully")

        else:
            messagebox.showerror("Error", "Failed to delete record")



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
