# import ttkbootstrap as ttk
# from ttkbootstrap.tableview import Tableview
# from ttkbootstrap.constants import *
# import requests
# from backend.settings.database import server_ip
# from datetime import datetime


# class BeginningBalanceTable:
#
#     def __init__(self, root):
#         self.note_form_tab = root
#
#         self.coldata = [
#             {"text": "Raw Material Code", "stretch": True, "anchor": "w"},
#             {"text": "Warehouse", "stretch": True},
#             {"text": "Stocks", "stretch": True},
#             {"text": "Status", "stretch": True},
#             {"text": "Date Created", "stretch": True},
#             {"text": "Inventory Report Date", "stretch": True},
#         ]
#         self.rowdata = self.fetch_and_format_data()
#
#         # Create Tableview
#         self.table = Tableview(
#             master=self.note_form_tab,
#             coldata=self.coldata,
#             rowdata=self.rowdata,
#             paginated=True,
#             searchable=True,
#             bootstyle=PRIMARY,
#             pagesize=20,
#             autofit=True,  # Auto-size columns
#             autoalign=False,  # Auto-align columns based on data
#         )
#         self.table.pack(fill=BOTH, expand=YES, padx=10, pady=10)
#
#     def fetch_and_format_data(self):
#         """Fetch data from API and format for table rowdata."""
#         url = server_ip + "/api/get/beginning_balance/"
#         try:
#             response = requests.get(url)
#             response.raise_for_status()
#
#             data = response.json()
#
#
#             # Format data for the table
#             rowdata = [
#                 (
#                     item["rmcode"],
#                     item["warehousename"],
#                     "{:,.2f}".format(float(item["beginningbalance"])),  # Format with commas
#                     item["statusname"],
#                     datetime.fromisoformat(item["stockchangedate"]).strftime("%m/%d/%Y %I:%M %p"),
#                     datetime.fromisoformat(item["date_computed"]).strftime("%m/%d/%Y"),
#                 )
#                 for item in data
#             ]
#             return rowdata
#         except requests.exceptions.RequestException as e:
#             return []
#
#     def refresh_table(self):
#         """Refresh the table with updated data."""
#         self.rowdata = self.fetch_and_format_data()
#         self.table.build_table_data(
#             coldata=self.coldata,
#             rowdata=self.rowdata
#         )
#         self.table.goto_last_page()



import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import requests
from backend.settings.database import server_ip
from tkinter import messagebox
from datetime import datetime
from ttkbootstrap.tooltip import ToolTip
from frontend.stock_on_hand.import_feature.confirm_messages import ConfirmationMessage



class BeginningBalanceTable:
    def __init__(self, root):
        self.root = root
        self.confirmation_message = ConfirmationMessage(self.root)


        # Frame for search
        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill=X, padx=10, pady=(10, 0))
        ttk.Label(search_frame, text="Search:", style="CustomLabel.TLabel").pack(side=LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=50)
        self.search_entry.pack(side=LEFT)
        self.search_entry.bind("<Return>", self.search_data)

        # Button to trigger the import process
        import_button = ttk.Button(
            search_frame,
            text="Generate New Beginning Balance",
            bootstyle=WARNING,
            command=self.confirmation_message.show_confirmation_message
        )

        import_button.pack(side=RIGHT)

        # Add Tooltip
        ToolTip(import_button, text="Import or generate a new beginning balance for raw materials.")


        # Create a frame to hold the Treeview and Scrollbars
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # First, define self.tree before using it
        self.tree = ttk.Treeview(
            master=tree_frame,
            columns=(
                "Raw Material Code",
                "Warehouse",
                "Stocks",
                "Status",
                "Inventory Report Date",
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
                "Raw Material Code",
                "Warehouse",
                "Stocks",
                "Status",
                "Inventory Report Date",
             ]
        for col in col_names:
            self.tree.heading(col, text=col, command=lambda _col=col: self.sort_treeview(_col, False), anchor=W)
            self.tree.column(col, anchor=W)

    def fetch_data(self):
        """Fetch data from API."""
        url = server_ip + "/api/get/beginning_balance/"
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
            record = (
                item["rmcode"],
                item["warehousename"],
                "{:,.2f}".format(float(item["beginningbalance"])),  # Format with commas
                item["statusname"],
                datetime.fromisoformat(item["date_computed"]).strftime("%m/%d/%Y"),
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







