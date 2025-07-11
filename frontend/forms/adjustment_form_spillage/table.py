import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import requests
from ttkbootstrap.tooltip import ToolTip
from tkinter import Toplevel, messagebox, StringVar
from backend.settings.database import server_ip
from datetime import datetime
from uuid import UUID
from tkinter import simpledialog
from ttkbootstrap.widgets import DateEntry
from .validation import EntryValidation
from ttkbootstrap.dialogs import Messagebox
from ..shared import SharedFunctions
from .add_record_form import Forms
from .edit_record_form import EditForm
from .view_record_form import ViewRecordForm



class AdjustmentFormTable:
    def __init__(self, root):
        self.original_data = None
        self.root = root
        # Instantiate the shared_function class
        self.shared_functions = SharedFunctions()

        self.get_status_api = self.shared_functions.get_status_api()
        self.get_warehouse_api = self.shared_functions.get_warehouse_api()
        self.get_rm_code_api = self.shared_functions.get_rm_code_api(force_refresh=True)
        self.form = Forms(self)
        self.edit_form = EditForm(self)
        self.view_form = ViewRecordForm(self)


        # Frame for search
        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill=X, padx=10, pady=(0, 0))
        ttk.Label(search_frame, text="Search:", style="CustomLabel.TLabel").pack(side=LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=50)
        self.search_entry.pack(side=LEFT)
        self.search_entry.bind("<Return>", self.search_data)


        # Add button to clear data
        btn_clear = ttk.Button(
            search_frame,
            text="Clear Data",
            command=self.confirmation_panel_clear,
            bootstyle=WARNING,
        )
        btn_clear.pack(side=RIGHT)
        ToolTip(btn_clear, text="Click the button to clear all the Adjustment Form data.")

        # Add button to refresh table
        btn_refresh = ttk.Button(
            search_frame,
            text="Refresh",
            command=self.refresh_table,
            bootstyle=SECONDARY,
        )
        btn_refresh.pack(side=RIGHT, padx=10)
        ToolTip(btn_refresh, text="Click the button to refresh the data table.")

        # Add button to clear data
        btn_add = ttk.Button(
            search_frame,
            text="+ Add Record",
            command=lambda: self.form.add_records(),
            bootstyle=PRIMARY,
        )
        btn_add.pack(side=RIGHT)
        ToolTip(btn_add, text="Click the button to add the Adjustment Form data.")

        # Create a frame to hold the Treeview and Scrollbars
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=(5,0))

        # First, define self.tree before using it
        self.tree = ttk.Treeview(
            master=tree_frame,
            columns=(   "Date Encoded",
                        "Ref#",
                        "Raw Material",
                        "Quantity Lost",
                        "Status",
                        "Warehouse",
                        "Spillage Report #",
                        "Responsible Person",
                        "Incident Date",
                        "Adjustment Date",
                        "Referenced Date"
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


        # Define column headings
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c, False), anchor=W)
            self.tree.column(col, width=150, anchor=W)

        self.tree.pack(fill=BOTH, expand=YES)
        self.tree.bind("<Button-3>", self.show_context_menu)  # Right-click menu

        self.refresh_table()

    def refresh_table(self):
        """Fetch data from API and populate Treeview."""
        url = server_ip + "/api/adjustment_form/spillage/v1/list/"
        self.original_data = []  # Store all records
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
                    item["status"],
                    item["wh_name"],
                    item["spillage_form_number"],
                    item["responsible_person"],
                    datetime.fromisoformat(item["incident_date"]).strftime("%m/%d/%Y"),
                    datetime.fromisoformat(item["adjustment_date"]).strftime("%m/%d/%Y"),
                    datetime.fromisoformat(item["reference_date"]).strftime("%m/%d/%Y"),
                    item["reason"],

                )

                self.original_data.append(record)  # Save record
                self.tree.insert("", END, iid=record[0], values=record[1:])

        except requests.exceptions.RequestException as e:
            return []

    def show_context_menu(self, event):
        """Show right-click menu with Edit/Delete options."""
        item = self.tree.identify_row(event.y)

        if item:
            menu = ttk.Menu(self.root, tearoff=0)
            menu.add_command(label="View", command=lambda: self.view_form.view_records(item))
            menu.add_command(label="Edit", command=lambda: self.edit_form.edit_records(item))
            # menu.add_command(label="Delete", command=lambda: self.confirm_delete(item))
            menu.add_command(label="Delete", command=lambda: self.delete_entry(item))
            menu.post(event.x_root, event.y_root)


    def delete_entry(self, entry_id):
        """Delete selected entry via API."""
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this entry?"):
            url = server_ip + f"/api/adjustment_form/spillage/v1/delete/{entry_id}/"
            response = requests.delete(url)
            if response.status_code == 200:
                self.tree.delete(entry_id)
                messagebox.showinfo("Success", "Entry deleted successfully.")
            else:
                messagebox.showerror("Error", "Failed to delete entry.")

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

    def confirmation_panel_clear(self):
        confirmation_window = ttk.Toplevel(self.root)
        confirmation_window.title("Confirm Action")

        # **Fixed Size** (Recommended for consistency)
        window_width = 500  # Fixed width
        window_height = 260  # Fixed height

        # **Center the window**
        screen_width = confirmation_window.winfo_screenwidth()
        screen_height = confirmation_window.winfo_screenheight()
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 3  # Slightly higher than center

        confirmation_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        confirmation_window.resizable(False, False)  # Disable resizing for consistency

        # **Make widgets expand properly**
        confirmation_window.grid_columnconfigure(0, weight=1)
        confirmation_window.grid_rowconfigure(0, weight=1)

        # **Message Label (Warning)**
        message_label = ttk.Label(
            confirmation_window,
            text="\n\nARE YOU SURE?",
            justify="center",
            font=("Arial", 13, "bold"),
            bootstyle=WARNING
        )
        message_label.pack(pady=5)

        # **Description Label**
        desc_label = ttk.Label(
            confirmation_window,
            text=(
                "This form's data will be cleared, but it won't be deleted from the database.\n"
                "Make sure the data you're clearing is unimportant before proceeding.\n"
            ),
            justify="center",  # Changed to center for better appearance
            font=("Arial", 11),
        )
        desc_label.pack(pady=5)

        # **Confirmation Instruction Label**
        confirm_label = ttk.Label(
            confirmation_window,
            text="To proceed, type 'YES' in the confirmation box.",
            justify="center",
            font=("Arial", 11, "bold"),
        )
        confirm_label.pack(pady=5)

        # **Entry Field (Validation)**
        confirm_entry = ttk.Entry(
            confirmation_window,
            font=("Arial", 12),
            justify="center"
        )
        confirm_entry.pack(padx=20, pady=5)

        # **Button Frame (Properly Aligned)**
        button_frame = ttk.Frame(confirmation_window)
        button_frame.pack(fill="x", padx=10, pady=10)

        # **Button Grid Configuration**
        button_frame.columnconfigure(0, weight=1)  # Cancel (Left)
        button_frame.columnconfigure(1, weight=1)  # Submit (Right)

        # **Cancel Button**
        cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            bootstyle=DANGER,
            command=confirmation_window.destroy
        )
        cancel_button.grid(row=0, column=0, padx=5, sticky="w")

        # **Submit Button (Initially Disabled)**
        submit_button = ttk.Button(
            button_frame,
            text="Submit",
            bootstyle=SUCCESS,
            state=DISABLED,
            command=lambda: [clear_all_notes_form_data(), confirmation_window.destroy()]
        )
        submit_button.grid(row=0, column=1, padx=5, sticky="e")

        # Function to validate entry field
        def validate_entry(event):
            if confirm_entry.get().strip() == "YES":
                submit_button.config(state=NORMAL)
            else:
                submit_button.config(state=DISABLED)

        confirm_entry.bind("<KeyRelease>", validate_entry)

        def clear_all_notes_form_data():
            """Fetch data from API and format for table rowdata."""
            url = f"{server_ip}/api/clear-table-data"
            params = {"tbl": "adjustment forms"}  # Send tbl as a query parameter
            try:
                # Send another POST request to clear data
                response = requests.post(url, params=params)
                if response.status_code == 200:  # Check if the stock view was successfully created
                    self.refresh_table()
                    Messagebox.show_info("Data is successfully cleared!", "Data Clearing")

                else:
                    Messagebox.show_error(f"There must be a mistake, the status code is {response.status_code}",
                                          "Data Clearing Error")

            except requests.exceptions.RequestException as e:
                return False