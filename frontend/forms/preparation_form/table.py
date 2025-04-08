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
from .validation import EntryValidation
from ..shared import SharedFunctions


class PreparationFormTable:
    def __init__(self, root):
        self.root = root
        self.shared_functions = SharedFunctions()

        self.edit_window = None
        self.get_status_api = self.shared_functions.get_status_api()
        self.get_rm_code_api = self.shared_functions.get_rm_code_api()
        self.get_warehouse_api = self.shared_functions.get_warehouse_api()


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
        ToolTip(btn_clear, text="Click the button to clear all the Note Form data.")

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
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=(5,0))

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
                "Report Date",
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


        # Define columns
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        self.tree.pack(fill=BOTH, expand=YES)
        self.tree.bind("<Button-3>", self.show_context_menu)
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
                "Report Date",
                        ]
        for col in col_names:
            self.tree.heading(col, text=col, command=lambda _col=col: self.sort_treeview(_col, False), anchor=W)
            self.tree.column(col, anchor=W)

    def fetch_data(self):
        """Fetch data from API."""
        url = server_ip + "/api/preparation_forms/v1/list/"
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
            qty_return_formatted = "{:,.2f}".format(float(item["qty_return"]))  # Format qty_kg with commas
            qty_prepared_formatted = "{:,.2f}".format(float(item["qty_prepared"]))  # Format qty_kg with commas

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
            menu.add_command(label="Edit", command=lambda: self.edit_record(item))
            menu.add_command(label="Delete", command=lambda: self.confirm_delete(item))
            menu.post(event.x_root, event.y_root)


    def on_edit_window_close(self):
        """Reset the edit_window reference when it is closed."""
        self.edit_window.destroy()
        self.edit_window = None

    def edit_record(self, item):
        # If the window already exists, bring it to the front and return
        if self.edit_window and self.edit_window.winfo_exists():
            self.edit_window.lift()
            return

        """Open edit form."""
        record = self.tree.item(item, 'values')
        print(record)
        if not record:
            return

        # Remove "Beginning Balance" (index 4) and "Date Encoded" (index 6)
        record = (record[1], record[2], record[3], record[4], record[6], record[7], record[8])


        # Get the main window position and size
        self.root.update_idletasks()  # Ensure updated dimensions
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()

        # Define edit window size
        window_width = 320
        window_height = 340

        # Calculate the position (center relative to main window)
        x = root_x + (root_width // 2) - (window_width // 2)
        y = root_y + (root_height // 2) - (window_height // 2)

        # Create the window **with position already set**
        self.edit_window = Toplevel(self.root)
        self.edit_window.title("Edit Record")
        self.edit_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Prevent opening multiple windows
        self.edit_window.protocol("WM_DELETE_WINDOW", self.on_edit_window_close)

        fields = [
                "PF ID No.",
                "Raw Material",
                "QTY (Prepared)",
                "QTY (Return)",
                "Status",
                "Warehouse",
                "Report Date",
                   ]
        entries = {}


        for idx, field in enumerate(fields):
            ttk.Label(self.edit_window, text=field, font=self.shared_functions.custom_font_size).grid(row=idx, column=0, padx=10, pady=5, sticky=W)

            if field == "Raw Material":
                # Fetch Raw Material Data from API
                rm_codes = self.get_rm_code_api
                code_to_id = {item["rm_code"]: item["id"] for item in rm_codes}
                rm_names = list(code_to_id.keys())

                rm_entry = ttk.Combobox(self.edit_window, values=rm_names, state="normal", width=20,
                                        font=self.shared_functions.custom_font_size)
                rm_entry.set(record[idx])  # Set current value in the combobox
                rm_entry.grid(row=idx, column=1, padx=10, pady=5, sticky=W)
                ToolTip(rm_entry, text="Choose a raw material")  # Tooltip


            elif field == "Warehouse":
                # Warehouse JSON-format choices (coming from the API)
                warehouses = self.get_warehouse_api
                warehouse_to_id = {item["wh_name"]: item["id"] for item in warehouses}
                warehouse_names = list(warehouse_to_id.keys())

                wh_entry = ttk.Combobox(self.edit_window, values=warehouse_names, state="readonly", width=20,
                                     font=self.shared_functions.custom_font_size)
                wh_entry.grid(row=idx, column=1, padx=10, pady=5, sticky=W)
                wh_entry.set(record[idx])  # Set current value in the combobox

                ToolTip(wh_entry, text="Select a warehouse")  # Tooltip

            elif field == "Status":
                # Warehouse JSON-format choices (coming from the API)
                status = self.get_status_api
                status_to_id = {item["name"]: item["id"] for item in status}
                status_names = list(status_to_id.keys())

                status_entry = ttk.Combobox(self.edit_window, values=status_names, state="readonly", width=20,
                                            font=self.shared_functions.custom_font_size)
                status_entry.set(record[idx])  # Set current value in the combobox
                status_entry.grid(row=idx, column=1, padx=10, pady=5, sticky=W)
                ToolTip(status_entry, text="Choose a status")  # Tooltip


            elif field == "Report Date":
                date_entry = DateEntry(self.edit_window, dateformat="%m/%d/%Y", width=18)
                date_entry.entry.delete(0, "end")
                formatted_date = record[idx]
                date_entry.entry.insert(0, formatted_date)
                date_entry.grid(row=idx, column=1, padx=10, pady=5, sticky=W)
                date_entry.entry.config(font=self.shared_functions.custom_font_size)


            elif field == "QTY (Prepared)":
                # Function to format numeric input dynamically with cursor preservation
                def format_numeric_input_prepared(event):
                    """
                    Formats the input dynamically while preserving the cursor position.
                    """
                    input_value = qty_prepared_var.get()

                    # Get current cursor position
                    cursor_position = qty_prepared_entry.index("insert")

                    # Remove commas for processing
                    raw_value = input_value.replace(",", "")

                    if raw_value == "" or raw_value == ".":
                        return  # Prevent formatting when only `.` is typed

                    try:
                        if "." in raw_value and raw_value[-1] == ".":
                            return  # Allow user to manually enter decimal places

                        # Convert input to float and format
                        float_value = float(raw_value)

                        if "." in raw_value:
                            integer_part, decimal_part = raw_value.split(".")
                            formatted_integer = "{:,}".format(int(integer_part))  # Format integer part with commas
                            formatted_value = f"{formatted_integer}.{decimal_part}"  # Preserve user-entered decimal part
                        else:
                            formatted_value = "{:,}".format(int(float_value))  # Format whole number

                        # Adjust cursor position based on new commas added
                        num_commas_before = input_value[:cursor_position].count(",")
                        num_commas_after = formatted_value[:cursor_position].count(",")

                        new_cursor_position = cursor_position + (num_commas_after - num_commas_before)

                        # Prevent cursor jumping by resetting the value and restoring cursor position
                        qty_prepared_entry.delete(0, "end")
                        qty_prepared_entry.insert(0, formatted_value)
                        qty_prepared_entry.icursor(new_cursor_position)  # Restore cursor position
                    except ValueError:
                        pass  # Ignore invalid input

                qty_prepared_var = StringVar()
                validate_numeric_command = self.edit_window.register(EntryValidation.validate_numeric_input)
                qty_prepared_entry = ttk.Entry(self.edit_window,
                                               width=22,
                                               font=self.shared_functions.custom_font_size,
                                               textvariable=qty_prepared_var,
                                               validate="key",  # Trigger validation on keystrokes
                                               validatecommand=(validate_numeric_command, "%P")
                                               # Pass the current widget content ("%P")
                                               )
                qty_prepared_entry.insert(0, record[idx])
                qty_prepared_entry.grid(row=idx, column=1, padx=10, pady=5, sticky=W)
                ToolTip(qty_prepared_entry, text="Enter the QTY (Prepared)")
                qty_prepared_entry.bind("<KeyRelease>", format_numeric_input_prepared)

                old_qty_prepared = float(record[idx].replace(",", ""))


            elif field == "QTY (Return)":

                # Function to format numeric input dynamically with cursor preservation
                def format_numeric_input_return(event):
                    """
                    Formats the input dynamically while preserving the cursor position.
                    """
                    input_value = qty_return_var.get()

                    # Get current cursor position
                    cursor_position = qty_return_entry.index("insert")

                    # Remove commas for processing
                    raw_value = input_value.replace(",", "")

                    if raw_value == "" or raw_value == ".":
                        return  # Prevent formatting when only `.` is typed

                    try:
                        if "." in raw_value and raw_value[-1] == ".":
                            return  # Allow user to manually enter decimal places

                        # Convert input to float and format
                        float_value = float(raw_value)

                        if "." in raw_value:
                            integer_part, decimal_part = raw_value.split(".")
                            formatted_integer = "{:,}".format(int(integer_part))  # Format integer part with commas
                            formatted_value = f"{formatted_integer}.{decimal_part}"  # Preserve user-entered decimal part
                        else:
                            formatted_value = "{:,}".format(int(float_value))  # Format whole number

                        # Adjust cursor position based on new commas added
                        num_commas_before = input_value[:cursor_position].count(",")
                        num_commas_after = formatted_value[:cursor_position].count(",")

                        new_cursor_position = cursor_position + (num_commas_after - num_commas_before)

                        # Prevent cursor jumping by resetting the value and restoring cursor position
                        qty_return_entry.delete(0, "end")
                        qty_return_entry.insert(0, formatted_value)
                        qty_return_entry.icursor(new_cursor_position)  # Restore cursor position
                    except ValueError:
                        pass  # Ignore invalid input

                qty_return_var = StringVar()
                validate_numeric_command = self.edit_window.register(EntryValidation.validate_numeric_input)
                qty_return_entry = ttk.Entry(self.edit_window,
                                             width=22,
                                             font=self.shared_functions.custom_font_size,
                                             textvariable=qty_return_var,
                                             validate="key",  # Trigger validation on keystrokes
                                             validatecommand=(validate_numeric_command, "%P")
                                             # Pass the current widget content ("%P")
                                             )
                qty_return_entry.insert(0, record[idx])
                qty_return_entry.bind("<KeyRelease>", format_numeric_input_return)
                qty_return_entry.grid(row=idx, column=1, padx=10, pady=5, sticky=W)
                ToolTip(qty_return_entry, text="Enter the value for the Quantity (Return) in KG")


            elif field == "PF ID No.":
                ref_entry = ttk.Entry(self.edit_window, width=22,
                                      font=self.shared_functions.custom_font_size,
                                      )
                ref_entry.insert(0, record[idx])
                ref_entry.grid(row=idx, column=1, padx=10, pady=5, sticky=W)


        def get_selected_rm_code_id():
            selected_name = rm_entry.get()
            selected_id = code_to_id.get(selected_name)
            return selected_id if selected_id else None


        def get_selected_warehouse_id():
            selected_name = wh_entry.get()
            selected_id = warehouse_to_id.get(selected_name)  # Get the corresponding ID
            if selected_id:
                return selected_id
            else:
                return None


        def get_selected_status_id():
            selected_name = status_entry.get()
            selected_id = status_to_id.get(selected_name)  # Get the corresponding ID
            if selected_id:
                return selected_id
            else:
                return None

        def update_record():
            qty_return = qty_return_entry.get()
            qty_prepared = qty_prepared_entry.get()

            if qty_return is None or qty_return == '':
                qty_return = float(0.00)

            # This code removes the commas in the qty value
            cleaned_qty_prepared = float(qty_prepared.replace(",", ""))
            cleaned_qty_return = float(qty_return.replace(",", ""))


            # Convert date to YYYY-MM-DD
            try:
                preparation_date = datetime.strptime(date_entry.entry.get(), "%m/%d/%Y").strftime("%Y-%m-%d")
            except ValueError:
                Messagebox.show_error("Invalid date format. Please use MM/DD/YYYY.", "Date Entry Error")
                return
            data = {
                "rm_code_id": get_selected_rm_code_id(),
                "warehouse_id": get_selected_warehouse_id(),
                "ref_number": ref_entry.get(),
                "status_id": get_selected_status_id(),
                "preparation_date":  preparation_date,
                "qty_prepared": cleaned_qty_prepared,
                "qty_return": cleaned_qty_return,
            }

            # Validate the data entries in front-end side
            if EntryValidation.entry_validation(data):
                error_text = EntryValidation.entry_validation(data)
                Messagebox.show_error(f"There is no data in these fields {error_text}.", "Data Entry Error", alert=True)
                return

            validation_result = self.shared_functions.validate_soh_value_for_update(
                get_selected_rm_code_id(),
                get_selected_warehouse_id(),
                old_qty_prepared,
                cleaned_qty_prepared,
                get_selected_status_id()
            )

            if validation_result:
                try:
                    url = server_ip + f"/api/preparation_forms/v1/update/{item}/"
                    response = requests.put(url, json=data)
                    if response.status_code == 200:
                        self.refresh_table()
                        self.edit_window.destroy()
                        messagebox.showinfo("Success", "Record updated successfully")


                    else:
                        messagebox.showerror("Error", "Failed to update record - ", response.status_code)
                except requests.exceptions.RequestException as e:
                    messagebox.showerror("Error", f"Failed to update: {e}")

            else:
                Messagebox.show_error(
                    "The entered value in 'QTY (Prepared)' exceeds the available stock in the database.",
                    "Data Entry Error")
                return

        ttk.Button(self.edit_window, text="Save", command=update_record, width=30).grid(row=len(fields), column=0, columnspan=2,
                                                                         pady=10)
    def confirm_delete(self, item_id):
        """Show confirmation before deleting record."""
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this record?"):
            self.delete_record(item_id)

    def delete_record(self, item_id):
        """Send DELETE request to API."""
        url = server_ip + f"/api/preparation_forms/v1/delete/{item_id}/"
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
            params = {"tbl": "preparation forms"}  # Send tbl as a query parameter
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