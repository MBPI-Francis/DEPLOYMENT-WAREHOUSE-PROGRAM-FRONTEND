# import ttkbootstrap as ttk
# from ttkbootstrap.dialogs import Messagebox
# from ttkbootstrap.tableview import Tableview
# from ttkbootstrap.constants import *
# import requests
# from ttkbootstrap.tooltip import ToolTip
# from backend.settings.database import server_ip
#
# class NoteTable:
#     def __init__(self, root):
#         self.root = root
#
#         # Search Bar Frame
#         search_frame = ttk.Frame(self.root)
#         search_frame.pack(fill="x", padx=10, pady=(5,0))
#
#         # Search Entry
#         ttk.Label(search_frame, text="Search:", style="CustomLabel.TLabel").pack(side=LEFT, padx=5, pady=(0,0))
#         self.search_entry = ttk.Entry(search_frame, width=50)
#         self.search_entry.pack(side="left", padx=5)
#         self.search_entry.bind("<Return>", self.filter_table)  # Live filtering
#
#         # Add button to clear data
#         btn_clear = ttk.Button(
#             search_frame,
#             text="Clear All Data",
#             command=self.confirmation_panel_clear,
#             bootstyle=WARNING,
#         )
#         btn_clear.pack(side=RIGHT)
#         ToolTip(btn_clear, text="Click the button to clear all the data.")
#
#
#         # Add button to clear data
#         btn_refresh = ttk.Button(
#             search_frame,
#             text="Refresh",
#             command=self.refresh_table,
#             bootstyle=SECONDARY,
#         )
#         btn_refresh.pack(side=RIGHT, padx=10)
#         ToolTip(btn_refresh, text="Click the button to refresh the data table.")
#
#         # Table Columns
#         self.coldata = [
#             {"text": "Raw Material", "stretch": True, "anchor": "w"},
#             {"text": "Warehouse Name", "stretch": True},
#             {"text": "Ending Balance", "stretch": True},
#             {"text": "Status", "stretch": True},
#         ]
#
#         # Fetch Data
#         self.rowdata = self.fetch_and_format_data()
#
#         # Create Table
#         self.table = Tableview(
#             master=self.root,
#             coldata=self.coldata,
#             rowdata=self.rowdata,
#             paginated=True,
#             bootstyle=PRIMARY,
#             pagesize=20,
#             autofit=True,  # Auto-size columns
#             autoalign=True,  # Auto-align columns based on data
#
#         )
#         self.table.pack(fill=BOTH, expand=YES, padx=10, pady=(5,0))
#
#     def filter_table(self, event=None):
#         """Filters table based on search input."""
#         search_text = self.search_entry.get().lower()
#
#         if not search_text:
#             self.refresh_table()  # Reset table when search is cleared
#             return
#
#         # Filter across all columns
#         filtered_data = [
#             row for row in self.rowdata if any(search_text in str(cell).lower() for cell in row)
#         ]
#
#         # Update table data using `build_table_data`
#         self.table.build_table_data(coldata=self.coldata, rowdata=filtered_data)
#         self.search_entry.focus_set()
#
#     def fetch_and_format_data(self):
#         """Fetch data from API and format it for the table."""
#         url = server_ip + "/api/get/new_soh/with_zero/"
#         try:
#             response = requests.get(url)
#             response.raise_for_status()
#             data = response.json()
#
#             # Ensure each row is a LIST, not a tuple
#             return [
#                 [
#                     item["rmcode"],
#                     item["warehousename"],
#                     "{:,.2f}".format(float(item["new_beginning_balance"])),  # Format numbers
#                     item["status"],
#                 ]
#                 for item in data
#             ]
#         except requests.exceptions.RequestException:
#             return []
#
#     def refresh_table(self):
#         """Refresh the table with updated data."""
#         self.rowdata = self.fetch_and_format_data()
#         self.table.build_table_data(coldata=self.coldata, rowdata=self.rowdata)
#         self.table.goto_first_page()
#         self.search_entry.focus_set()
#
#         # Function to show confirmation panel
#
#     def confirmation_panel_clear(self):
#         # confirmation_window = ttk.Toplevel(form_frame)
#         # confirmation_window.title("Confirm Action")
#         # confirmation_window.geometry("450x410")
#         # confirmation_window.resizable(True, True)
#
#         confirmation_window = ttk.Toplevel(self.root)
#         confirmation_window.title("Confirm Action")
#
#         # Get the screen width and height
#         screen_width = confirmation_window.winfo_screenwidth()
#         screen_height = confirmation_window.winfo_screenheight()
#
#         # Set a dynamic size (proportional to the screen size)
#         window_width = int(screen_width * 0.35)  # Adjust width as needed
#         window_height = int(screen_height * 0.51)  # Adjust height as needed
#
#         # Calculate position for centering
#         x_position = (screen_width - window_width) // 2
#         y_position = (screen_height - window_height) // 3  # Position slightly higher
#
#         # Apply geometry dynamically
#         confirmation_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
#
#         # Allow resizing but maintain proportions
#         confirmation_window.resizable(True, True)
#
#         # Expand and fill widgets inside the window
#         confirmation_window.grid_columnconfigure(0, weight=1)
#         confirmation_window.grid_rowconfigure(0, weight=1)
#
#         # Message Label
#         message_label = ttk.Label(
#             confirmation_window,
#             text="\n\nYou are about to clear ALL recently added data.",
#             justify="center",
#             font=("Arial", 12, "bold"),
#             bootstyle=WARNING
#
#         )
#         message_label.pack(pady=5)
#
#         # Message Label
#         message_label = ttk.Label(
#             confirmation_window,
#             text=(
#                 "The recently added data from the following forms will be\ncleared or removed:\n"
#                 "   - Notes Form\n"
#                 "   - Receiving Form\n"
#                 "   - Outgoing Form\n"
#                 "   - Transfer Form\n"
#                 "   - Preparation Form\n"
#                 "   - Change Status Form\n\n"
#
#                 "Please ensure that the data that will be cleared are unimportant\nbefore clearing all of it.\n"
#             ),
#             justify="left",
#             font=("Arial", 11),
#         )
#         message_label.pack(pady=5)
#
#         # Message Label
#         message_label = ttk.Label(
#             confirmation_window,
#             text=("To proceed, type 'YES' in the confirmation box."),
#             justify="center",
#             font=("Arial", 11),
#         )
#         message_label.pack(pady=5)
#
#         # Entry field
#         confirm_entry = ttk.Entry(confirmation_window, font=("Arial", 12),
#                                   justify="center")
#         confirm_entry.pack(padx=20, pady=5)
#
#         # Frame for buttons
#         button_frame = ttk.Frame(confirmation_window)
#         button_frame.pack(fill="x", padx=10, pady=10)  # Expand the frame horizontally
#
#         # Configure button frame columns
#         button_frame.columnconfigure(0, weight=1)  # Left side (Cancel)
#         button_frame.columnconfigure(1, weight=1)  # Right side (Submit)
#
#         # Cancel Button (Left)
#         cancel_button = ttk.Button(
#             button_frame,
#             text="Cancel",
#             bootstyle=DANGER,
#             command=confirmation_window.destroy
#         )
#         cancel_button.grid(row=0, column=0, padx=5, sticky="w")  # Align to left
#
#         # Submit Button (Right, Initially Disabled)
#         submit_button = ttk.Button(
#             button_frame,
#             text="Submit",
#             bootstyle=SUCCESS,
#             state=DISABLED,
#             command=lambda: [clear_all_data_from_forms(), confirmation_window.destroy()]
#         )
#         submit_button.grid(row=0, column=1, padx=5, sticky="e")  # Align to right
#
#         # Function to validate entry field
#         def validate_entry(event):
#             if confirm_entry.get().strip() == "YES":
#                 submit_button.config(state=NORMAL)
#             else:
#                 submit_button.config(state=DISABLED)
#
#         confirm_entry.bind("<KeyRelease>", validate_entry)
#
#         def clear_all_data_from_forms():
#             """Fetch data from API and format for table rowdata."""
#             url = f"{server_ip}/api/clear-table-data"
#             params = {"tbl": "all"}  # Send tbl as a query parameter
#             try:
#                 # Send another POST request to clear data
#                 response = requests.post(url, params=params)
#                 if response.status_code == 200:  # Check if the stock view was successfully created
#                     Messagebox.show_info("Data is successfully cleared!", "Data Clearing")
#
#
#                 else:
#                     Messagebox.show_error(f"There must be a mistake, the status code is {response.status_code}",
#                                           "Data Clearing Error")
#
#             except requests.exceptions.RequestException as e:
#                 return False


import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import requests
from ttkbootstrap.dialogs import Messagebox

from backend.settings.database import server_ip
from tkinter import Toplevel, messagebox
from datetime import datetime
from ttkbootstrap.tooltip import ToolTip


class SubmitEntriesTable:
    def __init__(self, root):
        self.root = root

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
            text="Clear All Data",
            command=self.confirmation_panel_clear,
            bootstyle=WARNING,
        )
        btn_clear.pack(side=RIGHT)
        ToolTip(btn_clear, text="Click the button to clear all the data.")


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
                "Raw Material",
                "Warehouse Name",
                "Ending Balance",
                "Status",
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
        self.refresh_table()

        # Define column headers
        col_names = [
                "Raw Material",
                "Warehouse Name",
                "Ending Balance",
                "Status",
                     ]
        for col in col_names:
            self.tree.heading(col, text=col, command=lambda _col=col: self.sort_treeview(_col, False), anchor=W)
            self.tree.column(col, anchor=W)

    def fetch_data(self):
        """Fetch data from API."""
        url = server_ip + "/api/get/new_soh/with_zero/"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Ensure each row is a LIST, not a tuple
            return data

        except requests.exceptions.RequestException:
            return []

    def refresh_table(self):
        """Refresh Treeview with data."""
        self.tree.delete(*self.tree.get_children())
        self.original_data = []  # Store all records

        for item in self.fetch_data():
            record = (
                item["rmcode"],
                item["warehousename"],
                "{:,.2f}".format(float(item["new_beginning_balance"])),  # Format numbers
                item["status"],
            )

            self.original_data.append(record)  # Save record
            self.tree.insert("", END, values=record[0:])

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
            self.tree.insert("", END, values=record[0:])

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
        window_width = int(screen_width * 0.35)  # Adjust width as needed
        window_height = int(screen_height * 0.51)  # Adjust height as needed

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
            text="\n\nYou are about to clear ALL recently added data.",
            justify="center",
            font=("Arial", 12, "bold"),
            bootstyle=WARNING

        )
        message_label.pack(pady=5)

        # Message Label
        message_label = ttk.Label(
            confirmation_window,
            text=(
                "The recently added data from the following forms will be\ncleared or removed:\n"
                "   - Notes Form\n"
                "   - Receiving Form\n"
                "   - Outgoing Form\n"
                "   - Transfer Form\n"
                "   - Preparation Form\n"
                "   - Change Status Form\n\n"

                "Please ensure that the data that will be cleared are unimportant\nbefore clearing all of it.\n"
            ),
            justify="left",
            font=("Arial", 11),
        )
        message_label.pack(pady=5)

        # Message Label
        message_label = ttk.Label(
            confirmation_window,
            text=("To proceed, type 'YES' in the confirmation box."),
            justify="center",
            font=("Arial", 11),
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
            command=lambda: [clear_all_data_from_forms(), confirmation_window.destroy()]
        )
        submit_button.grid(row=0, column=1, padx=5, sticky="e")  # Align to right

        # Function to validate entry field
        def validate_entry(event):
            if confirm_entry.get().strip() == "YES":
                submit_button.config(state=NORMAL)
            else:
                submit_button.config(state=DISABLED)

        confirm_entry.bind("<KeyRelease>", validate_entry)

        def clear_all_data_from_forms():
            """Fetch data from API and format for table rowdata."""
            url = f"{server_ip}/api/clear-table-data"
            params = {"tbl": "all"}  # Send tbl as a query parameter
            try:
                # Send another POST request to clear data
                response = requests.post(url, params=params)
                if response.status_code == 200:  # Check if the stock view was successfully created
                    Messagebox.show_info("Data is successfully cleared!", "Data Clearing")


                else:
                    Messagebox.show_error(f"There must be a mistake, the status code is {response.status_code}",
                                          "Data Clearing Error")

            except requests.exceptions.RequestException as e:
                return False




# import ttkbootstrap as ttk
# from ttkbootstrap.dialogs import Messagebox
# from ttkbootstrap.tableview import Tableview
# from ttkbootstrap.constants import *
# import requests
# from ttkbootstrap.tooltip import ToolTip
#
# from backend.settings.database import server_ip
#
# class NoteTable:
#     def __init__(self, root):
#         self.root = root
#
#         # Search Bar Frame
#         search_frame = ttk.Frame(self.root)
#         search_frame.pack(fill="x", padx=10, pady=(5,0))
#
#         # Search Entry
#         ttk.Label(search_frame, text="Search:", style="CustomLabel.TLabel").pack(side=LEFT, padx=5, pady=(0,0))
#         self.search_entry = ttk.Entry(search_frame, width=50)
#         self.search_entry.pack(side="left", padx=5)
#         self.search_entry.bind("<Return>", self.filter_table)  # Live filtering
#
#         # Add button to clear data
#         btn_clear = ttk.Button(
#             search_frame,
#             text="Clear All Data",
#             command=self.confirmation_panel_clear,
#             bootstyle=WARNING,
#         )
#         btn_clear.pack(side=RIGHT)
#         ToolTip(btn_clear, text="Click the button to clear all the data.")
#
#         # Add button to clear data
#         btn_refresh = ttk.Button(
#             search_frame,
#             text="Refresh",
#             command=self.refresh_table,
#             bootstyle=SECONDARY,
#         )
#         btn_refresh.pack(side=RIGHT, padx=10)
#         ToolTip(btn_refresh, text="Click the button to refresh the data table.")
#
#         # Table Columns
#         self.coldata = [
#             {"text": "Raw Material", "stretch": True, "anchor": "w"},
#             {"text": "Warehouse Name", "stretch": True},
#             {"text": "Ending Balance", "stretch": True},
#             {"text": "Status", "stretch": True},
#         ]
#
#
#         # Tabbed Structure
#         self.notebook = ttk.Notebook(self.root)
#         self.notebook.pack(fill=BOTH, expand=YES, padx=10, pady=5)
#
#         # Create empty tabs for Warehouse #1, #2, #4
#         self.tab_whse_1 = ttk.Frame(self.notebook)
#         self.tab_whse_2 = ttk.Frame(self.notebook)
#         self.tab_whse_4 = ttk.Frame(self.notebook)
#
#         # Add tabs to the notebook
#         self.notebook.add(self.tab_whse_1, text="WHSE #1")
#         self.notebook.add(self.tab_whse_2, text="WHSE #2")
#         self.notebook.add(self.tab_whse_4, text="WHSE #4")
#
#         # Fetch and Categorize Data
#         self.rowdata = self.fetch_and_format_data()
#
#         # Categorize data into warehouse specific data
#         self.whse_1_data = [row for row in self.rowdata if row[1] == 'Warehouse #1']
#         self.whse_2_data = [row for row in self.rowdata if row[1] == 'Warehouse #2']
#         self.whse_4_data = [row for row in self.rowdata if row[1] == 'Warehouse #4']
#
#         # Create Tableviews for each warehouse
#         self.table_whse_1 = Tableview(
#             master=self.tab_whse_1,
#             coldata=self.coldata,
#             rowdata=self.whse_1_data,
#             paginated=True,
#             bootstyle=PRIMARY,
#             pagesize=20,
#             autofit=True,
#             autoalign=True,
#         )
#         self.table_whse_1.pack(fill=BOTH, expand=YES, padx=10, pady=5)
#
#         self.table_whse_2 = Tableview(
#             master=self.tab_whse_2,
#             coldata=self.coldata,
#             rowdata=self.whse_2_data,
#             paginated=True,
#             bootstyle=PRIMARY,
#             pagesize=20,
#             autofit=True,
#             autoalign=True,
#         )
#         self.table_whse_2.pack(fill=BOTH, expand=YES, padx=10, pady=5)
#
#         self.table_whse_4 = Tableview(
#             master=self.tab_whse_4,
#             coldata=self.coldata,
#             rowdata=self.whse_4_data,
#             paginated=True,
#             bootstyle=PRIMARY,
#             pagesize=20,
#             autofit=True,
#             autoalign=True,
#         )
#         self.table_whse_4.pack(fill=BOTH, expand=YES, padx=10, pady=5)
#
#     def filter_table(self, event=None):
#         """Filters table based on search input."""
#         search_text = self.search_entry.get().lower()
#
#         if not search_text:
#             self.refresh_table()  # Reset table when search is cleared
#             return
#
#         # Filter across all warehouses
#         filtered_data_1 = [row for row in self.whse_1_data if any(search_text in str(cell).lower() for cell in row)]
#         filtered_data_2 = [row for row in self.whse_2_data if any(search_text in str(cell).lower() for cell in row)]
#         filtered_data_4 = [row for row in self.whse_4_data if any(search_text in str(cell).lower() for cell in row)]
#
#         # Update table data for each warehouse tab
#         self.table_whse_1.build_table_data(coldata=self.coldata, rowdata=filtered_data_1)
#         self.table_whse_2.build_table_data(coldata=self.coldata, rowdata=filtered_data_2)
#         self.table_whse_4.build_table_data(coldata=self.coldata, rowdata=filtered_data_4)
#         self.search_entry.focus_set()
#
#     def fetch_and_format_data(self):
#         """Fetch data from API and format it for the table."""
#         url = server_ip + "/api/get/new_soh/with_zero/"
#         try:
#             response = requests.get(url)
#             response.raise_for_status()
#             data = response.json()
#
#             # Ensure each row is a LIST, not a tuple
#             return [
#                 [
#                     item["rmcode"],
#                     item["warehousename"],
#                     "{:,.2f}".format(float(item["new_beginning_balance"])),  # Format numbers
#                     item["status"],
#                 ]
#                 for item in data
#             ]
#         except requests.exceptions.RequestException:
#             return []
#
#     def refresh_table(self):
#         """Refresh the table with updated data."""
#         self.rowdata = self.fetch_and_format_data()
#
#         # Categorize data into warehouse specific data
#         self.whse_1_data = [row for row in self.rowdata if row[1] == 'WHSE #1']
#         self.whse_2_data = [row for row in self.rowdata if row[1] == 'WHSE #2']
#         self.whse_4_data = [row for row in self.rowdata if row[1] == 'WHSE #4']
#
#         # Refresh data for each warehouse tab
#         self.table_whse_1.build_table_data(coldata=self.coldata, rowdata=self.whse_1_data)
#         self.table_whse_2.build_table_data(coldata=self.coldata, rowdata=self.whse_2_data)
#         self.table_whse_4.build_table_data(coldata=self.coldata, rowdata=self.whse_4_data)
#
#         self.table_whse_1.goto_first_page()
#         self.table_whse_2.goto_first_page()
#         self.table_whse_4.goto_first_page()
#
#         self.search_entry.focus_set()
#
#     def confirmation_panel_clear(self):
#         """Function to show confirmation panel before clearing all data."""
#         # The logic remains the same as the previous one, nothing changes.
#         pass
