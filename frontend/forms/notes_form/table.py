import ttkbootstrap as ttk
from ttkbootstrap import DateEntry
from ttkbootstrap.constants import *
import requests
from tkinter import Menu, Toplevel, Label, Entry, Button, messagebox
import tkinter as tk
from ttkbootstrap.dialogs import Messagebox
from .validation import EntryValidation
from backend.settings.database import server_ip
from datetime import datetime
from ttkbootstrap.tooltip import ToolTip
from tkinter import font
from ttkbootstrap.style import Style


class NoteTable:
    def __init__(self, root):
        self.root = root

        # Frame for search
        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill=X, padx=10, pady=(10, 0))
        ttk.Label(search_frame, text="Search:").pack(side=LEFT, padx=5)
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
        ToolTip(btn_clear, text="Click the button to clear all the Note Form data.")


        # Create a frame to hold the Treeview and Scrollbars
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # First, define self.tree before using it
        self.tree = ttk.Treeview(
            master=tree_frame,
            columns=("Product Code",
                     "Lot No.",
                     "Product Kind",
                     "Consumption Date",
                     "Date Encoded"),
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


        # Define column headers
        col_names = ["Product Code", "Lot No.", "Product Kind", "Consumption Date", "Date Encoded"]
        for col in col_names:
            self.tree.heading(col, text=col, command=lambda _col=col: self.sort_treeview(_col, False), anchor=W)
            self.tree.column(col, anchor=W)

        # Load Data
        self.load_data()


        # Bind right-click
        self.tree.bind("<Button-3>", self.show_context_menu)

    def load_data(self):
        """Fetch data from API and populate treeview."""
        url = server_ip + "/api/notes/v1/list/"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            self.original_data = []  # Store all records

            self.tree.delete(*self.tree.get_children())  # Clear existing data
            for item in data:
                record = (
                    item["id"],  # Store ID
                    item["product_code"],
                    item["lot_number"],
                    item["product_kind_id"],
                    datetime.fromisoformat(item["stock_change_date"]).strftime("%m/%d/%Y"),
                    datetime.fromisoformat(item["created_at"]).strftime("%m/%d/%Y %I:%M %p"),
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

    def show_context_menu(self, event):
        """Show right-click context menu."""
        item = self.tree.identify_row(event.y)
        if item:
            menu = Menu(self.tree, tearoff=0)
            menu.add_command(label="Edit", command=lambda: self.edit_record(item))
            menu.add_command(label="Delete", command=lambda: self.confirm_delete(item))
            menu.post(event.x_root, event.y_root)

    def edit_record(self, item):
        record = self.tree.item(item, "values")
        if not record:
            return

        edit_window = Toplevel(self.root)
        edit_window.title("Edit Record")
        edit_window.geometry("300x225")

        # Fetch product kinds from API
        product_kinds = self.get_product_kinds_api()
        name_to_id = {item["name"]: item["id"] for item in product_kinds}
        product_kind_names = list(name_to_id.keys())

        fields = ["Product Code",
                  "Lot No.",
                  "Product Kind",
                  "Consumption Date"
                  ]
        entries = {}

        for i, label_text in enumerate(fields):
            Label(edit_window, text=label_text).grid(row=i, column=0, padx=10, pady=5, sticky='w')
            if label_text == "Product Kind":
                # Mapping MB -> 'Masterbatch Color' and DC -> 'Dry Color'
                kind_mapping = {
                    "MB": product_kind_names[1],  # 'Masterbatch Color'
                    "DC": product_kind_names[0]  # 'Dry Color'
                }

                entry = ttk.Combobox(edit_window, values=product_kind_names, state="readonly", width=20)

                # Get the mapped value or use record[i] if it's not MB/DC
                entry_value = kind_mapping.get(record[i], record[i])
                entry.set(entry_value)


            elif label_text == "Consumption Date":
                entry = DateEntry(edit_window, dateformat="%m/%d/%Y", width=20)
                entry.entry.delete(0, "end")
                entry.entry.insert(0, datetime.strptime(record[i], "%m/%d/%Y").strftime("%m/%d/%Y"))

            else:
                entry = ttk.Entry(edit_window, width=22)
                entry.insert(0, record[i])

            entry.grid(row=i, column=1, padx=5, pady=5, sticky=W)
            entries[label_text] = entry
        def update_data():

            def get_selected_product_kind_id():
                selected_name = entries["Product Kind"].get()
                selected_id = name_to_id.get(selected_name)  # Get the corresponding ID
                if selected_id:
                    return selected_id
                else:
                    return None

            def get_product_kinds_api():
                url = server_ip + "/api/product_kinds/v1/list/"
                response = requests.get(url)

                # Check if the request was successful
                if response.status_code == 200:
                    # Parse JSON response
                    data = response.json()
                    return data
                else:
                    return []


            # Product Kind JSON-format choices (coming from the API)
            product_kinds = get_product_kinds_api()
            name_to_id = {kind_item["name"]: kind_item["id"] for kind_item in product_kinds}
            product_kind_names = list(name_to_id.keys())

            # Convert date to YYYY-MM-DD
            try:
                consumption_date = datetime.strptime(entries["Consumption Date"].entry.get(), "%m/%d/%Y").strftime("%Y-%m-%d")
            except ValueError:
                Messagebox.show_error("Error", "Invalid date format. Please use MM/DD/YYYY.")
                return

            data = {
                "product_code": entries["Product Code"].get(),
                "lot_number": entries["Lot No."].get(),
                "product_kind_id": get_selected_product_kind_id(),
                "stock_change_date": consumption_date,
            }

            # Validate the data entries in front-end side
            if EntryValidation.entry_validation(data):
                error_text = EntryValidation.entry_validation(data)
                Messagebox.show_error(f"There is no data in these fields {error_text}.", "Data Entry Error", alert=True)
                return

            note_id = item
            url = f"{server_ip}/api/notes/v1/update/{note_id}/"
            response = requests.put(url, json=data)
            if response.status_code == 200:
                messagebox.showinfo("Success", "Record updated successfully")
                self.load_data()
                edit_window.destroy()
            else:
                messagebox.showerror("Error", "Failed to update record")

        ttk.Button(edit_window, text="Update", command=update_data, width=30).grid(row=len(fields), columnspan=2, pady=10)

    def confirm_delete(self, note_id):
        """Show confirmation before deleting record."""
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this record?"):
            self.delete_record(note_id)

    def delete_record(self, note_id):
        """Send DELETE request to API."""
        url = f"{server_ip}/api/notes/v1/delete/{note_id}/"
        response = requests.delete(url)
        if response.status_code == 200:
            messagebox.showinfo("Success", "Record deleted successfully")
            self.load_data()
        else:
            messagebox.showerror("Error", "Failed to delete record")

    def get_product_kinds_api(self):
        url = server_ip + "/api/product_kinds/v1/list/"
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse JSON response
            data = response.json()
            return data
        else:
            return []


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
        # confirmation_window = ttk.Toplevel(form_frame)
        # confirmation_window.title("Confirm Action")
        # confirmation_window.geometry("450x410")
        # confirmation_window.resizable(True, True)

        confirmation_window = ttk.Toplevel(self.root)
        confirmation_window.title("Confirm Action")

        # Get the screen width and height
        screen_width = confirmation_window.winfo_screenwidth()
        screen_height = confirmation_window.winfo_screenheight()

        # Set a dynamic size (proportional to the screen size)
        window_width = int(screen_width * 0.38)  # Adjust width as needed
        window_height = int(screen_height * 0.32)  # Adjust height as needed

        # Calculate position for centering
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 3  # Position slightly higher

        # Apply geometry dynamically
        confirmation_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Allow resizing but maintain proportions
        confirmation_window.resizable(True, True)

        # Expand and fill widgets inside the window
        confirmation_window.grid_columnconfigure(0, weight=1)
        confirmation_window.grid_rowconfigure(0, weight=1)

        # Message Label
        message_label = ttk.Label(
            confirmation_window,
            text="\n\nARE YOU SURE?",
            justify="center",
            font=("Helvetica", 12, "bold"),
            bootstyle=WARNING

        )
        message_label.pack(pady=5)

        # Message Label
        message_label = ttk.Label(
            confirmation_window,
            text=(
                "This form's data will be cleared, but it won't be deleted from the database.\n"
                "Make sure the data you're clearing is unimportant before proceeding.\n"
            ),
            justify="left",
            font=("Helvetica", 10),
        )
        message_label.pack(pady=5)

        # Message Label
        message_label = ttk.Label(
            confirmation_window,
            text=("To proceed, type 'YES' in the confirmation box."),
            justify="center",
            font=("Helvetica", 10),
        )
        message_label.pack(pady=5)

        # Entry field
        confirm_entry = ttk.Entry(confirmation_window, font=("Arial", 12),
                                  justify="center")
        confirm_entry.pack(padx=20, pady=5)

        # Frame for buttons
        button_frame = ttk.Frame(confirmation_window)
        button_frame.pack(fill="x", padx=10, pady=10)  # Expand the frame horizontally

        # Configure button frame columns
        button_frame.columnconfigure(0, weight=1)  # Left side (Cancel)
        button_frame.columnconfigure(1, weight=1)  # Right side (Submit)

        # Cancel Button (Left)
        cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            bootstyle=DANGER,
            command=confirmation_window.destroy
        )
        cancel_button.grid(row=0, column=0, padx=5, sticky="w")  # Align to left

        # Submit Button (Right, Initially Disabled)
        submit_button = ttk.Button(
            button_frame,
            text="Submit",
            bootstyle=SUCCESS,
            state=DISABLED,
            command=lambda: [clear_all_notes_form_data(), confirmation_window.destroy()]
        )
        submit_button.grid(row=0, column=1, padx=5, sticky="e")  # Align to right

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
            params = {"tbl": "notes"}  # Send tbl as a query parameter
            try:
                # Send another POST request to clear data
                response = requests.post(url, params=params)
                if response.status_code == 200:  # Check if the stock view was successfully created
                    self.load_data()
                    Messagebox.show_info("Data is successfully cleared!", "Data Clearing")


                else:
                    Messagebox.show_error(f"There must be a mistake, the status code is {response.status_code}", "Data Clearing Error")

            except requests.exceptions.RequestException as e:
                return False
