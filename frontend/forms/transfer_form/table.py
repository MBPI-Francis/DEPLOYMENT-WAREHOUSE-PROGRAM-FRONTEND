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
from ttkbootstrap.dialogs import Messagebox
from frontend.forms.preparation_form.validation import EntryValidation as PrepValidation
from frontend.forms.shared import SharedFunctions
from frontend.forms.transfer_form.validation import EntryValidation as TranferValidation


class TransferFormTable:
    def __init__(self, root):
        self.root = root
        # Instantiate the shared_function class
        shared_functions = SharedFunctions()

        self.get_warehouse_api = shared_functions.get_warehouse_api()
        self.get_rm_code_api = shared_functions.get_rm_code_api()    # Instantiate the shared_function class
        self.get_status_api = shared_functions.get_status_api()    # Instantiate the shared_function class


        # Frame for search
        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill=X, padx=10, pady=(10, 0))
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

        # Create a frame to hold the Treeview and Scrollbars
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # First, define self.tree before using it
        self.tree = ttk.Treeview(
            master=tree_frame,
            columns=(
                    "Raw Material",
                    "TF No.",
                    "Quantity(kg)",
                    "Warehouse (FROM)",
                    "Warehouse (TO)",
                    "Status",
                    "Transfer Date",
                    "Date Encoded"),
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

        self.tree.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        self.tree.bind("<Button-3>", self.show_context_menu)  # Right-click menu

        self.refresh_table()


    def refresh_table(self):
        """Fetch data from API and populate Treeview."""
        url = server_ip + "/api/transfer_forms/v1/list/"
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
                    item["raw_material"],
                    item["ref_number"],
                    qty_kg_formatted,
                    item["from_warehouse"],
                    item["to_warehouse"],
                    item["status"],
                    datetime.fromisoformat(item["transfer_date"]).strftime("%m/%d/%Y"),
                    datetime.fromisoformat(item["created_at"]).strftime("%m/%d/%Y %I:%M %p"),

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
            menu.add_command(label="Edit", command=lambda: self.edit_record(item))
            # menu.add_command(label="Delete", command=lambda: self.confirm_delete(item))
            menu.add_command(label="Delete", command=lambda: self.delete_entry(item))
            menu.post(event.x_root, event.y_root)

    def edit_record(self, item):
        """Open edit form."""
        record = self.tree.item(item, 'values')
        if not record:
            return

        edit_window = Toplevel(self.root)
        edit_window.title("Edit Record")

        fields = ["Raw Material",
                  "TF No.",
                  "Quantity(kg)",
                  "Warehouse (FROM)",
                  "Warehouse (TO)",
                  "Status",
                  "Transfer Date"
                  ]

        entries = {}

        for idx, field in enumerate(fields):
            ttk.Label(edit_window, text=field).grid(row=idx, column=0, padx=10, pady=5, sticky=W)

            if field == "Raw Material":
                # Fetch Raw Material Data from API
                rm_codes = self.get_rm_code_api
                code_to_id = {item["rm_code"]: item["id"] for item in rm_codes}
                rm_names = list(code_to_id.keys())

                entry = ttk.Combobox(edit_window, values=rm_names, state="normal", width=30)
                entry.set(record[idx])  # Set current value in the combobox
                ToolTip(entry, text="Choose a raw material")  # Tooltip


            elif field == "Warehouse (FROM)":
                # Warehouse JSON-format choices (coming from the API)
                warehouses = self.get_warehouse_api
                warehouse_to_id = {item["wh_name"]: item["id"] for item in warehouses}
                warehouse_names = list(warehouse_to_id.keys())

                entry = ttk.Combobox(edit_window, values=warehouse_names, state="disabled", width=30)
                entry.set(record[idx])  # Set current value in the combobox
                ToolTip(entry, text="Select a warehouse")  # Tooltip


            elif field == "Warehouse (TO)":
                # Warehouse JSON-format choices (coming from the API)
                warehouses = self.get_warehouse_api
                warehouse_to_id = {item["wh_name"]: item["id"] for item in warehouses}
                warehouse_names = list(warehouse_to_id.keys())

                entry = ttk.Combobox(edit_window, values=warehouse_names, state="disabled", width=30)
                entry.set(record[idx])  # Set current value in the combobox
                ToolTip(entry, text="Select a warehouse")  # Tooltip


            elif field == "Status":
                # Warehouse JSON-format choices (coming from the API)
                status = self.get_status_api
                status_to_id = {item["name"]: item["id"] for item in status}
                status_names = list(status_to_id.keys())

                entry = ttk.Combobox(edit_window, values=status_names, state="readonly", width=30,)
                entry.set(record[idx])  # Set current value in the combobox
                ToolTip(entry, text="Choose a status")  # Tooltip


            elif field == "Transfer Date":
                entry = DateEntry(edit_window, dateformat="%m/%d/%Y", width=30)
                entry.entry.delete(0, "end")
                formatted_date = record[idx]
                entry.entry.insert(0, formatted_date)


            elif field == "Quantity(kg)":

                validate_numeric_command = edit_window.register(TranferValidation.validate_numeric_input)
                entry = ttk.Entry(edit_window,
                                      width=30,
                                      validate="key",  # Trigger validation on keystrokes
                                      validatecommand=(validate_numeric_command, "%P")
                                      # Pass the current widget content ("%P")
                                      )
                entry.insert(0, record[idx])
                ToolTip(entry, text="Enter the Quantity(kg)")


            else:
                entry = ttk.Entry(edit_window, width=30)
                entry.insert(0, record[idx])


            entries[field] = entry
            entry.grid(row=idx, column=1, padx=10, pady=5, sticky=W)


        def get_selected_rm_code_id():
            selected_name = entries["Raw Material"].get()
            selected_id = code_to_id.get(selected_name)
            return selected_id if selected_id else None

        def get_selected_warehouse_from_id():
            selected_name = entries["Warehouse (FROM)"].get()
            selected_id = warehouse_to_id.get(selected_name)  # Get the corresponding ID
            if selected_id:
                return selected_id
            else:
                return None

        def get_selected_warehouse_to_id():
            selected_name = entries["Warehouse (TO)"].get()
            selected_id = warehouse_to_id.get(selected_name)  # Get the corresponding ID
            if selected_id:
                return selected_id
            else:
                return None

        def get_selected_status_id():
            selected_name = entries["Status"].get()
            selected_id = status_to_id.get(selected_name)  # Get the corresponding ID
            if selected_id:
                return selected_id
            else:
                return None

        def update_record():
            # Convert date to YYYY-MM-DD
            try:
                transfer_date = datetime.strptime(entries["Transfer Date"].entry.get(), "%m/%d/%Y").strftime("%Y-%m-%d")
            except ValueError:
                Messagebox.show_error("Error", "Invalid date format. Please use MM/DD/YYYY.")
                return

            # Create a dictionary with the data
            data = {
                "rm_code_id": get_selected_rm_code_id(),
                "from_warehouse_id": get_selected_warehouse_from_id(),
                "to_warehouse_id": get_selected_warehouse_to_id(),
                "ref_number": entries["TF No."].get(),
                "status_id": get_selected_status_id(),
                "transfer_date": transfer_date,
                "qty_kg": entries["Quantity(kg)"].get(),
            }

            # Validate the data entries in front-end side
            if TranferValidation.entry_validation(data):
                error_text = TranferValidation.entry_validation(data)
                Messagebox.show_error(f"There is no data in these fields {error_text}.", "Data Entry Error", alert=True)
                return

                # Check if the record is existing in the inventory
                # Call the check_raw_material function
            result = self.check_raw_material(get_selected_rm_code_id(),
                                             get_selected_warehouse_from_id(),
                                             get_selected_status_id())
            # Display the result in the GUI
            if result:

                # Validate if the entry value exceeds the stock
                validatation_result = PrepValidation.validate_soh_value(
                    get_selected_rm_code_id(),
                    get_selected_warehouse_from_id(),
                    float(entries["Quantity(kg)"].get()),
                    get_selected_status_id()

                )

                if validatation_result:

                    try:
                        url = server_ip + f"/api/transfer_forms/v1/update/{item}/"
                        response = requests.put(url, json=data)
                        if response.status_code == 200:
                            self.refresh_table()
                            edit_window.destroy()
                            messagebox.showinfo("Success", "Record updated successfully")

                        else:
                            messagebox.showerror("Error", f"Failed to update record - {response.status_code}")
                    except requests.exceptions.RequestException as e:
                        messagebox.showerror("Error", f"Failed to update: {e}")

                else:
                    Messagebox.show_error(
                        "The entered quantity in 'Quantity' exceeds the available stock in the database.",
                        "Data Entry Error")
                    return

            else:
                Messagebox.show_error(f"The raw material record is not existing in the database.", "Failed Transfer.", alert=True)
                return

        save_button = ttk.Button(edit_window,
                                 text="Save",
                                 command=update_record,
                                 width=20)
        save_button.grid(row=len(fields), column=0, columnspan=2,pady=10)

    def delete_entry(self, entry_id):
        """Delete selected entry via API."""
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this entry?"):
            url = server_ip + f"/api/transfer_forms/v1/delete/{entry_id}/"
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


    def check_raw_material(self, rm_id: UUID, warehouse_id: UUID, status_id: UUID = None):
        url = f"{server_ip}/api/check/raw_material/"

        # Construct the query parameters
        params = {
            "rm_id": str(rm_id),  # Convert UUID to string for query parameter
            "warehouse_id": str(warehouse_id),
        }

        # Include status_id only if it's not None
        if status_id:
            params["status_id"] = status_id
        # Handle response

        try:
            # Send the GET request
            response = requests.get(url, params=params)

            # Check if the response was successful
            if response.status_code == 200:
                # Parse the response data (True or False)
                return response.json()  # This will return either True or False
            else:
                # Handle errors
                print(f"Error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return False

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
            params = {"tbl": "transfer forms"}  # Send tbl as a query parameter
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

