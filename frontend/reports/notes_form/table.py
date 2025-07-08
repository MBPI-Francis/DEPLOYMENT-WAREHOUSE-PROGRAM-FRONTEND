# import ttkbootstrap as ttk
# from ttkbootstrap import DateEntry
# from ttkbootstrap.constants import *
# import requests
# from tkinter import Menu, Toplevel, Label, Entry, Button, messagebox, filedialog
# import tkinter as tk
# from ttkbootstrap.dialogs import Messagebox
# from backend.settings.database import server_ip # Assuming this contains your server's base URL
# from datetime import datetime, timedelta
# from ttkbootstrap.tooltip import ToolTip
# from frontend.forms.shared import SharedFunctions # Assuming this class provides necessary helpers
#
#
# class NoteTable:
#     def __init__(self, root):
#         self.root = root
#
#         # Instantiate the shared_function class
#         self.shared_functions = SharedFunctions() # Make it an instance variable
#
#         get_status_api = self.shared_functions.get_status_api()
#         get_warehouse_api = self.shared_functions.get_warehouse_api()
#         get_rm_code_api = self.shared_functions.get_rm_code_api(force_refresh=True)
#
#
#         # Frame for search
#         search_frame = ttk.Frame(self.root)
#         search_frame.pack(fill=X, padx=10, pady=(15, 0))
#
#         # Date Entry field FROM
#         date_label_from = ttk.Label(search_frame, text="Date FROM", style="CustomLabel.TLabel")
#         date_label_from.grid(row=0, column=0, padx=5, pady=0, sticky=W)
#
#         self.date_from_entry = ttk.DateEntry(
#             search_frame,
#             bootstyle=PRIMARY,
#             dateformat="%m/%d/%Y",
#             width=11
#         )
#         self.date_from_entry.grid(row=1, column=0, padx=5, pady=0, sticky=W)
#         self.date_from_entry.entry.delete(0, "end")
#         self.date_from_entry.entry.config(font=self.shared_functions.custom_font_size)
#         ToolTip(self.date_from_entry, text="Please enter the outgoing date")
#
#         # Date Entry field TO
#         date_label_to = ttk.Label(search_frame, text="Date TO", style="CustomLabel.TLabel")
#         date_label_to.grid(row=0, column=1, padx=5, pady=0, sticky=W)
#
#         self.date_to_entry = ttk.DateEntry(
#             search_frame,
#             bootstyle=PRIMARY,
#             dateformat="%m/%d/%Y",
#             width=11
#         )
#         self.date_to_entry.grid(row=1, column=1, padx=5, pady=0, sticky=W)
#         self.date_to_entry.entry.delete(0, "end")
#         self.date_to_entry.entry.config(font=self.shared_functions.custom_font_size)
#         ToolTip(self.date_to_entry, text="Please enter the outgoing date")
#
#         # Initialize date entries with default values if desired (e.g., current date)
#         # self.date_from_entry.set_date(datetime.now() - timedelta(days=7)) # Example: last 7 days
#         # self.date_to_entry.set_date(datetime.now())
#
#
#         # RM CODE JSON-format choices (coming from the API)
#         # Make these accessible for helper functions or methods if needed
#         self.rm_codes = get_rm_code_api
#         self.code_to_id = {item["rm_code"]: item["id"] for item in self.rm_codes}
#         rm_names = ["All"] + list(self.code_to_id.keys())
#
#         def on_combobox_key_release(event):
#             current_text = self.rm_codes_combobox.get()
#             self.rm_codes_combobox.set(current_text.upper())
#
#         rm_codes_label = ttk.Label(search_frame, text="Raw Material", style="CustomLabel.TLabel")
#         rm_codes_label.grid(row=0, column=2, padx=(8, 0), pady=(0, 0), sticky=W)
#
#         self.rm_codes_combobox = ttk.Combobox(
#             search_frame,
#             values=rm_names,
#             state="normal", # Can be typed in
#             width=20,
#             font=self.shared_functions.custom_font_size
#         )
#         self.rm_codes_combobox.bind("<KeyRelease>", on_combobox_key_release)
#         self.rm_codes_combobox.set("All")
#         self.rm_codes_combobox.grid(row=1, column=2, pady=(0, 0), padx=(10, 0))
#         ToolTip(self.rm_codes_combobox, text="Choose a raw material")
#
#         # Warehouse JSON-format choices (coming from the API)
#         self.warehouses = get_warehouse_api
#         self.warehouse_to_id = {item["wh_name"]: item["id"] for item in self.warehouses}
#         warehouse_names = ["All"] + list(self.warehouse_to_id.keys())
#
#         warehouse_label = ttk.Label(search_frame, text="Location", style="CustomLabel.TLabel")
#         warehouse_label.grid(row=0, column=3, padx=(8, 0), pady=(0, 0), sticky=W)
#
#         self.warehouse_combobox = ttk.Combobox(search_frame,
#                                           values=warehouse_names,
#                                           state="readonly",
#                                           width=13,
#                                           font=self.shared_functions.custom_font_size
#                                           )
#         self.warehouse_combobox.grid(row=1, column=3, padx=(10, 0), pady=(0, 0), sticky=W)
#         self.warehouse_combobox.set("All")
#
#         # Status JSON-format choices (coming from the API)
#         self.status_list = get_status_api # Renamed to avoid conflict with `status` variable in global scope
#         self.status_to_id = {item["name"]: item["id"] for item in self.status_list}
#         status_names = ["All"] + list(self.status_to_id.keys())
#
#         status_label = ttk.Label(search_frame, text="Status", style="CustomLabel.TLabel")
#         status_label.grid(row=0, column=4, padx=(10, 0), pady=(0, 0), sticky=W)
#
#         self.status_combobox = ttk.Combobox(
#             search_frame,
#             values=status_names,
#             state="readonly",
#             width=19,
#             font=self.shared_functions.custom_font_size
#         )
#         self.status_combobox.grid(row=1, column=4, padx=(10, 0), pady=(0, 0), sticky=W)
#         self.status_combobox.set("All")
#
#         # Document types (hardcoded in your GUI, but could also come from API)
#         self.document_types_data = [ # Renamed to avoid conflict
#             {"id": "all", "document_type_name": "All"},
#             {"id": "preparation_form_report", "document_type_name": "Preparation Form"},
#             {"id": "outgoing_form_report", "document_type_name": "Outgoing Form"},
#             {"id": "receiving_form_report", "document_type_name": "Receiving Form"},
#             {"id": "adjustment_form_report", "document_type_name": "Adjustment Form"},
#             {"id": "transfer_form_report", "document_type_name": "Transfer Form"},
#             {"id": "change_status_form_report", "document_type_name": "Change Status Form"},
#         ]
#         self.document_type_to_id = {item["document_type_name"]: item["id"] for item in self.document_types_data}
#         document_type_names = list(self.document_type_to_id.keys())
#
#         document_type_label = ttk.Label(search_frame, text="Document Type", style="CustomLabel.TLabel")
#         document_type_label.grid(row=0, column=5, padx=(8, 0), pady=(0, 0), sticky=W)
#
#         self.document_type_combobox = ttk.Combobox(search_frame,
#                                               values=document_type_names,
#                                               state="readonly",
#                                               width=15,
#                                               font=self.shared_functions.custom_font_size
#                                               )
#         self.document_type_combobox.grid(row=1, column=5, padx=(10, 0), pady=(0, 0), sticky=W)
#         self.document_type_combobox.set("All")
#
#
#         # Filter button
#         btn_filter = ttk.Button(
#             search_frame,
#             text="Filter Data",
#             command=self.filter_data, # Changed to new method
#             bootstyle=SECONDARY,
#         )
#         btn_filter.grid(row=1, column=6, padx=(10, 0), pady=(0, 0), sticky=W)
#         ToolTip(btn_filter, text="Click the button to filter the data table.")
#
#         # Export button
#         btn_export = ttk.Button(
#             search_frame,
#             text="Export to Excel",
#             command=self.export_data, # Changed to new method
#             bootstyle=SUCCESS,
#         )
#         btn_export.grid(row=1, column=7, padx=(10, 0), pady=(0, 0), sticky=E)
#         ToolTip(btn_export, text="Click the button to export the data into excel.")
#
#
#         # Create a frame to hold the Treeview and Scrollbars
#         tree_frame = ttk.Frame(self.root)
#         tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)
#
#         # First, define self.tree before using it
#         self.tree = ttk.Treeview(
#             master=tree_frame,
#             columns=(
#                     "Date Encoded",
#                     "Date Reported",
#                     "Document Type",
#                     "Document No.",
#                     "Raw Material", # Corrected "Rar Material" typo
#                     "QTY",
#                     "Location",
#                     "Status"
#                      ),
#             show='headings',
#             style="Custom.Treeview",
#             bootstyle=PRIMARY
#         )
#
#         # Create a vertical scrollbar and attach it to the treeview
#         tree_scroll_y = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=self.tree.yview)
#         tree_scroll_y.pack(side=RIGHT, fill=Y)
#
#         # Create a horizontal scrollbar (optional)
#         tree_scroll_x = ttk.Scrollbar(tree_frame, orient=HORIZONTAL, command=self.tree.xview)
#         tree_scroll_x.pack(side=BOTTOM, fill=X)
#
#         self.tree.pack(fill=BOTH, expand=YES)
#
#         self.tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
#
#         # Define column headers
#         col_names = ["Date Encoded",
#                     "Date Reported",
#                     "Document Type",
#                     "Document No.",
#                     "Raw Material",
#                     "QTY",
#                     "Location",
#                     "Status"]
#         for col in col_names:
#             self.tree.heading(col, text=col, command=lambda _col=col: self.sort_treeview(_col, False), anchor=W)
#             self.tree.column(col, anchor=W)
#
#         # Initial load of data (can be all data or default filters)
#         self.filter_data() # Call filter_data on initial load
#
#
#     def _get_filter_params(self):
#         """Helper to collect and format filter parameters from GUI widgets."""
#         params = {}
#
#         # Date FROM
#         try:
#             date_from_str = self.date_from_entry.entry.get()
#             if date_from_str:
#                 params['date_from'] = datetime.strptime(date_from_str, "%m/%d/%Y").strftime("%Y-%m-%d")
#         except ValueError:
#             messagebox.show_error("Invalid Date", "Please enter 'Date FROM' in MM/DD/YYYY format.", parent=self.root)
#             return None
#
#         # Date TO
#         try:
#             date_to_str = self.date_to_entry.entry.get()
#             if date_to_str:
#                 params['date_to'] = datetime.strptime(date_to_str, "%m/%d/%Y").strftime("%Y-%m-%d")
#         except ValueError:
#             messagebox.show_error("Invalid Date", "Please enter 'Date TO' in MM/DD/YYYY format.", parent=self.root)
#             return None
#
#         # Raw Material Code
#         mat_code = self.rm_codes_combobox.get().strip()
#         if mat_code and mat_code != "All":
#             params['mat_code'] = mat_code
#         else:
#             params['mat_code'] = None # Send None for 'All' or empty
#
#         # Document Type
#         document_type_name = self.document_type_combobox.get()
#         if document_type_name and document_type_name != "All":
#             # Find the corresponding ID for the document type name
#             doc_type_id = self.document_type_to_id.get(document_type_name)
#             if doc_type_id:
#                 params['document_type'] = doc_type_id
#             else:
#                 params['document_type'] = None # Should not happen if 'All' is handled
#         else:
#             params['document_type'] = None
#
#         # Location
#         location = self.warehouse_combobox.get()
#         if location and location != "All":
#             params['location'] = location
#         else:
#             params['location'] = None
#
#         # Status
#         status = self.status_combobox.get()
#         if status and status != "All":
#             params['status'] = status
#         else:
#             params['status'] = None
#
#         return params
#
#
#     def filter_data(self):
#         """Fetch filtered data from API and populate treeview."""
#         params = self._get_filter_params()
#         if params is None: # Error in parsing dates
#             return
#
#         url = f"{server_ip}/api/reports/v1/form-entries/"
#
#         try:
#             # Send GET request with parameters
#             if params:
#                 response = requests.get(url, params=params)
#             else:
#                 response = requests.get(url)
#             response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
#             data = response.json()
#
#             self.tree.delete(*self.tree.get_children())  # Clear existing data
#
#             if not data:
#                 messagebox.showinfo("No Data", "No records found matching the filter criteria.", parent=self.root)
#                 return
#
#             for item in data:
#                 # Ensure all fields are present and handle potential missing keys gracefully
#                 date_encoded = datetime.fromisoformat(item.get("date_encoded", "")).strftime("%m/%d/%Y") if item.get("date_encoded") else ""
#                 date_reported = datetime.fromisoformat(item.get("date_reported", "")).strftime("%m/%d/%Y") if item.get("date_reported") else ""
#
#                 record = (
#                     date_encoded,
#                     date_reported,
#                     item.get("document_type", ""),
#                     item.get("document_number", ""),
#                     item.get("mat_code", ""),
#                     item.get("qty", ""),
#                     item.get("whse_no", ""),
#                     item.get("status", ""),
#                 )
#                 self.tree.insert("", END, values=record)
#
#         except requests.exceptions.ConnectionError:
#             messagebox.showerror("Connection Error", "Could not connect to the API server. Please check your network or server status.", parent=self.root)
#         except requests.exceptions.Timeout:
#             messagebox.showerror("Timeout Error", "The request to the API server timed out.", parent=self.root)
#         except requests.exceptions.HTTPError as e:
#             messagebox.showerror("API Error", f"HTTP Error: {e.response.status_code} - {e.response.text}", parent=self.root)
#         except requests.exceptions.RequestException as e:
#             messagebox.showerror("Request Error", f"An error occurred during the API request: {e}", parent=self.root)
#         except Exception as e:
#             messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=self.root)
#
#
#     def export_data(self):
#         """Fetch filtered data and trigger export via API."""
#         params = self._get_filter_params()
#         if params is None: # Error in parsing dates
#             return
#
#         export_url = f"{server_ip}/api/reports/v1/form-entries/export-to-file/"
#
#         try:
#             response = requests.get(export_url, params=params)
#             response.raise_for_status()
#
#             export_response = response.json()
#
#             if export_response.get("message") == "Exported successfully" and export_response.get("file_path"):
#                 server_file_path = export_response["file_path"]
#                 # Informs the user that the file has been generated on the server.
#                 # For a more robust solution, you might want to modify your FastAPI
#                 # endpoint to return the file directly using FileResponse or StreamingResponse
#                 # so the GUI can prompt the user to save it locally.
#                 messagebox.showinfo(
#                     "Export Successful",
#                     f"Report generated on the server at: \n'{server_file_path}'\n\nYou may need to access the server to retrieve it.",
#                     parent=self.root
#                 )
#                 # --- Optional: If FastAPI returns the file directly (better user experience) ---
#                 # Example for direct download (requires FastAPI to return FileResponse):
#                 # file_data = response.content
#                 # file_name = "report.xlsx" # Or get from Content-Disposition header
#                 # save_path = filedialog.asksaveasfilename(
#                 #     defaultextension=".xlsx",
#                 #     filetypes=[("Excel files", "*.xlsx")],
#                 #     initialfile=file_name
#                 # )
#                 # if save_path:
#                 #     with open(save_path, "wb") as f:
#                 #         f.write(file_data)
#                 #     messagebox.showinfo("Export Successful", f"File saved to: {save_path}", parent=self.root)
#                 # else:
#                 #     messagebox.showinfo("Export Cancelled", "File save operation cancelled.", parent=self.root)
#             else:
#                 messagebox.showerror("Export Failed", f"API response error: {export_response.get('message', 'Unknown error')}", parent=self.root)
#
#         except requests.exceptions.ConnectionError:
#             messagebox.showerror("Connection Error", "Could not connect to the API server. Please check your network or server status.", parent=self.root)
#         except requests.exceptions.Timeout:
#             messagebox.showerror("Timeout Error", "The request to the API server timed out.", parent=self.root)
#         except requests.exceptions.HTTPError as e:
#             messagebox.showerror("API Error", f"HTTP Error: {e.response.status_code} - {e.response.text}", parent=self.root)
#         except requests.exceptions.RequestException as e:
#             messagebox.showerror("Request Error", f"An error occurred during the API request: {e}", parent=self.root)
#         except Exception as e:
#             messagebox.showerror("Error", f"An unexpected error occurred during export: {e}", parent=self.root)
#
#     def sort_treeview(self, col, reverse):
#         """Sort treeview column data."""
#         # This function operates on the currently displayed data, which is fine.
#         items = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
#         items.sort(reverse=reverse)
#         for index, (val, k) in enumerate(items):
#             self.tree.move(k, "", index)
#         self.tree.heading(col, command=lambda: self.sort_treeview(col, not reverse))
#
#     # The search_data and populate_treeview methods are now less critical
#     # as filtering is handled by the API, but I'll keep them if you have
#     # a separate client-side search functionality. If not, they can be removed.
#     def search_data(self, event=None):
#         """Filter and display only matching records in the Treeview."""
#         # This method is for client-side search. If you only want API-side filtering,
#         # you can remove calls to this method or remove the method itself.
#         # It currently relies on self.original_data, which is no longer populated
#         # by filter_data. You would need to store the last fetched API data
#         # in a class variable like self._current_api_data if you still want
#         # local search on top of API filtering.
#         pass # Placeholder: Implement if local search is still desired
#
#     def populate_treeview(self, data):
#         """Helper function to insert data into the Treeview."""
#         # This helper is now largely replaced by the logic within filter_data.
#         # It's kept for consistency if other parts of your code use it.
#         for record in data:
#             self.tree.insert("", END, values=record)


import ttkbootstrap as ttk
from ttkbootstrap import DateEntry
from ttkbootstrap.constants import *
import requests
from tkinter import Menu, Toplevel, Label, Entry, Button, messagebox, filedialog # Make sure filedialog is imported
import tkinter as tk
from ttkbootstrap.dialogs import Messagebox
from backend.settings.database import server_ip
from datetime import datetime, timedelta
from ttkbootstrap.tooltip import ToolTip
from frontend.forms.shared import SharedFunctions
import os # Import os for path manipulation


class NoteTable:
    def __init__(self, root):
        self.root = root

        # Instantiate the shared_function class
        self.shared_functions = SharedFunctions()

        get_status_api = self.shared_functions.get_status_api()
        get_warehouse_api = self.shared_functions.get_warehouse_api()
        get_rm_code_api = self.shared_functions.get_rm_code_api(force_refresh=True)


        # Frame for search
        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill=X, padx=10, pady=(15, 0))

        # Date Entry field FROM
        date_label_from = ttk.Label(search_frame, text="Date FROM", style="CustomLabel.TLabel")
        date_label_from.grid(row=0, column=0, padx=5, pady=0, sticky=W)

        self.date_from_entry = ttk.DateEntry(
            search_frame,
            bootstyle=PRIMARY,
            dateformat="%m/%d/%Y",
            width=11
        )
        self.date_from_entry.grid(row=1, column=0, padx=5, pady=0, sticky=W)
        self.date_from_entry.entry.delete(0, "end")
        self.date_from_entry.entry.config(font=self.shared_functions.custom_font_size)
        ToolTip(self.date_from_entry, text="Please enter the outgoing date")

        # Date Entry field TO
        date_label_to = ttk.Label(search_frame, text="Date TO", style="CustomLabel.TLabel")
        date_label_to.grid(row=0, column=1, padx=5, pady=0, sticky=W)

        self.date_to_entry = ttk.DateEntry(
            search_frame,
            bootstyle=PRIMARY,
            dateformat="%m/%d/%Y",
            width=11
        )
        self.date_to_entry.grid(row=1, column=1, padx=5, pady=0, sticky=W)
        self.date_to_entry.entry.delete(0, "end")
        self.date_to_entry.entry.config(font=self.shared_functions.custom_font_size)
        ToolTip(self.date_to_entry, text="Please enter the outgoing date")

        # Initialize date entries with default values if desired (e.g., current date)
        # self.date_from_entry.set_date(datetime.now() - timedelta(days=7)) # Example: last 7 days
        # self.date_to_entry.set_date(datetime.now())


        # RM CODE JSON-format choices (coming from the API)
        # Make these accessible for helper functions or methods if needed
        self.rm_codes = get_rm_code_api
        self.code_to_id = {item["rm_code"]: item["id"] for item in self.rm_codes}
        rm_names = ["All"] + list(self.code_to_id.keys())

        def on_combobox_key_release(event):
            current_text = self.rm_codes_combobox.get()
            self.rm_codes_combobox.set(current_text.upper())

        rm_codes_label = ttk.Label(search_frame, text="Raw Material", style="CustomLabel.TLabel")
        rm_codes_label.grid(row=0, column=2, padx=(8, 0), pady=(0, 0), sticky=W)

        self.rm_codes_combobox = ttk.Combobox(
            search_frame,
            values=rm_names,
            state="normal", # Can be typed in
            width=20,
            font=self.shared_functions.custom_font_size
        )
        self.rm_codes_combobox.bind("<KeyRelease>", on_combobox_key_release)
        self.rm_codes_combobox.set("All")
        self.rm_codes_combobox.grid(row=1, column=2, pady=(0, 0), padx=(10, 0))
        ToolTip(self.rm_codes_combobox, text="Choose a raw material")

        # Warehouse JSON-format choices (coming from the API)
        self.warehouses = get_warehouse_api
        self.warehouse_to_id = {item["wh_name"]: item["id"] for item in self.warehouses}
        warehouse_names = ["All"] + list(self.warehouse_to_id.keys())

        warehouse_label = ttk.Label(search_frame, text="Location", style="CustomLabel.TLabel")
        warehouse_label.grid(row=0, column=3, padx=(8, 0), pady=(0, 0), sticky=W)

        self.warehouse_combobox = ttk.Combobox(search_frame,
                                          values=warehouse_names,
                                          state="readonly",
                                          width=13,
                                          font=self.shared_functions.custom_font_size
                                          )
        self.warehouse_combobox.grid(row=1, column=3, padx=(10, 0), pady=(0, 0), sticky=W)
        self.warehouse_combobox.set("All")

        # Status JSON-format choices (coming from the API)
        self.status_list = get_status_api # Renamed to avoid conflict with `status` variable in global scope
        self.status_to_id = {item["name"]: item["id"] for item in self.status_list}
        status_names = ["All"] + list(self.status_to_id.keys())

        status_label = ttk.Label(search_frame, text="Status", style="CustomLabel.TLabel")
        status_label.grid(row=0, column=4, padx=(10, 0), pady=(0, 0), sticky=W)

        self.status_combobox = ttk.Combobox(
            search_frame,
            values=status_names,
            state="readonly",
            width=19,
            font=self.shared_functions.custom_font_size
        )
        self.status_combobox.grid(row=1, column=4, padx=(10, 0), pady=(0, 0), sticky=W)
        self.status_combobox.set("All")

        # Document types (hardcoded in your GUI, but could also come from API)
        self.document_types_data = [ # Renamed to avoid conflict
            {"id": "all", "document_type_name": "All"},
            {"id": "preparation_form_report", "document_type_name": "Preparation Form"},
            {"id": "outgoing_form_report", "document_type_name": "Outgoing Form"},
            {"id": "receiving_form_report", "document_type_name": "Receiving Form"},
            {"id": "adjustment_form_report", "document_type_name": "Adjustment Form"},
            {"id": "transfer_form_report", "document_type_name": "Transfer Form"},
            {"id": "change_status_form_report", "document_type_name": "Change Status Form"},
        ]
        self.document_type_to_id = {item["document_type_name"]: item["id"] for item in self.document_types_data}
        document_type_names = list(self.document_type_to_id.keys())

        document_type_label = ttk.Label(search_frame, text="Document Type", style="CustomLabel.TLabel")
        document_type_label.grid(row=0, column=5, padx=(8, 0), pady=(0, 0), sticky=W)

        self.document_type_combobox = ttk.Combobox(search_frame,
                                              values=document_type_names,
                                              state="readonly",
                                              width=15,
                                              font=self.shared_functions.custom_font_size
                                              )
        self.document_type_combobox.grid(row=1, column=5, padx=(10, 0), pady=(0, 0), sticky=W)
        self.document_type_combobox.set("All")


        # Filter button
        btn_filter = ttk.Button(
            search_frame,
            text="Filter Data",
            command=self.filter_data,
            bootstyle=SECONDARY,
        )
        btn_filter.grid(row=1, column=6, padx=(10, 0), pady=(0, 0), sticky=W)
        ToolTip(btn_filter, text="Click the button to filter the data table.")

        # Export button
        btn_export = ttk.Button(
            search_frame,
            text="Export to Excel",
            command=self.export_data,
            bootstyle=SUCCESS,
        )
        btn_export.grid(row=1, column=7, padx=(10, 0), pady=(0, 0), sticky=E)
        ToolTip(btn_export, text="Click the button to export the data into excel.")


        # Create a frame to hold the Treeview and Scrollbars
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # First, define self.tree before using it
        self.tree = ttk.Treeview(
            master=tree_frame,
            columns=(
                    "Date Encoded",
                    "Date Reported",
                    "Document Type",
                    "Document No.",
                    "Raw Material",
                    "QTY",
                    "Location",
                    "Status"
                     ),
            show='headings',
            style="Custom.Treeview",
            bootstyle=PRIMARY
        )

        # Create a vertical scrollbar and attach it to the treeview
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=self.tree.yview)
        tree_scroll_y.pack(side=RIGHT, fill=Y)

        # Create a horizontal scrollbar (optional)
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=HORIZONTAL, command=self.tree.xview)
        tree_scroll_x.pack(side=BOTTOM, fill=X)

        self.tree.pack(fill=BOTH, expand=YES)

        self.tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

        # Define column headers
        col_names = ["Date Encoded",
                    "Date Reported",
                    "Document Type",
                    "Document No.",
                    "Raw Material",
                    "QTY",
                    "Location",
                    "Status"]
        for col in col_names:
            self.tree.heading(col, text=col, command=lambda _col=col: self.sort_treeview(_col, False), anchor=W)
            self.tree.column(col, anchor=W)

        # Initial load of data (can be all data or default filters)
        self.filter_data()


    def _get_filter_params(self):
        """Helper to collect and format filter parameters from GUI widgets."""
        params = {}

        # Date FROM
        try:
            date_from_str = self.date_from_entry.entry.get()
            if date_from_str:
                params['date_from'] = datetime.strptime(date_from_str, "%m/%d/%Y").strftime("%Y-%m-%d")
            else:
                params['date_from'] = None # Ensure None if empty
        except ValueError:
            messagebox.show_error("Invalid Date", "Please enter 'Date FROM' in MM/DD/YYYY format.", parent=self.root)
            return None

        # Date TO
        try:
            date_to_str = self.date_to_entry.entry.get()
            if date_to_str:
                params['date_to'] = datetime.strptime(date_to_str, "%m/%d/%Y").strftime("%Y-%m-%d")
            else:
                params['date_to'] = None # Ensure None if empty
        except ValueError:
            messagebox.show_error("Invalid Date", "Please enter 'Date TO' in MM/DD/YYYY format.", parent=self.root)
            return None

        # Raw Material Code
        mat_code = self.rm_codes_combobox.get().strip()
        if mat_code and mat_code.lower() != "all": # Explicitly handle empty string too
            params['mat_code'] = mat_code
        else:
            params['mat_code'] = None

        # Document Type
        document_type_name = self.document_type_combobox.get()
        if document_type_name and document_type_name.lower() != "all":
            doc_type_id = self.document_type_to_id.get(document_type_name)
            params['document_type'] = doc_type_id if doc_type_id else None
        else:
            params['document_type'] = None

        # Location
        location = self.warehouse_combobox.get()
        if location and location.lower() != "all":
            params['location'] = location
        else:
            params['location'] = None

        # Status
        status = self.status_combobox.get()
        if status and status.lower() != "all":
            params['status'] = status
        else:
            params['status'] = None

        return params


    def filter_data(self):
        """Fetch filtered data from API and populate treeview."""
        params = self._get_filter_params()
        if params is None: # Error in parsing dates
            return

        url = f"{server_ip}/api/reports/v1/form-entries/"

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            self.tree.delete(*self.tree.get_children())

            if not data:
                messagebox.showinfo("No Data", "No records found matching the filter criteria.", parent=self.root)
                return

            for item in data:
                date_encoded = datetime.fromisoformat(item.get("date_encoded", "")).strftime("%m/%d/%Y") if item.get("date_encoded") else ""
                date_reported = datetime.fromisoformat(item.get("date_reported", "")).strftime("%m/%d/%Y") if item.get("date_reported") else ""

                record = (
                    date_encoded,
                    date_reported,
                    item.get("document_type", ""),
                    item.get("document_number", ""),
                    item.get("mat_code", ""),
                    item.get("qty", ""),
                    item.get("whse_no", ""),
                    item.get("status", ""),
                )
                self.tree.insert("", END, values=record)

        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Could not connect to the API server. Please check your network or server status.", parent=self.root)
        except requests.exceptions.Timeout:
            messagebox.showerror("Timeout Error", "The request to the API server timed out.", parent=self.root)
        except requests.exceptions.HTTPError as e:
            messagebox.showerror("API Error", f"HTTP Error: {e.response.status_code} - {e.response.text}", parent=self.root)
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Request Error", f"An error occurred during the API request: {e}", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=self.root)


    def export_data(self):
        """Fetch filtered data and trigger export via API, then save to user's local disk."""
        params = self._get_filter_params()
        if params is None: # Error in parsing dates
            return

        export_url = f"{server_ip}/api/reports/v1/form-entries/export-to-file/"

        try:
            # Send GET request to get the file content directly
            response = requests.get(export_url, params=params, stream=True) # Use stream=True for potentially large files
            response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)

            # Get suggested filename from headers, or use a default
            filename = "report.xlsx"
            if "Content-Disposition" in response.headers:
                cd = response.headers["Content-Disposition"]
                if "filename=" in cd:
                    # Extract filename, handling potential quotes
                    filename_part = cd.split("filename=")[-1].strip()
                    if filename_part.startswith('"') and filename_part.endswith('"'):
                        filename = filename_part[1:-1]
                    else:
                        filename = filename_part

            # Determine the default directory on the user's desktop
            # For Windows: C:\Users\Username\Desktop\Warehouse Reports
            # For macOS/Linux: /home/Username/Desktop/Warehouse Reports
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            warehouse_reports_dir = os.path.join(desktop_path, "Warehouse Reports")

            # Create the directory if it doesn't exist on the user's machine
            os.makedirs(warehouse_reports_dir, exist_ok=True)

            # Open a "Save As" dialog for the user
            save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialdir=warehouse_reports_dir, # Default to the Warehouse Reports folder
                initialfile=filename,           # Suggest the filename from the API
                title="Save Warehouse Report"
            )

            if save_path:
                # Read content in chunks and write to the chosen file
                with open(save_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk: # filter out keep-alive new chunks
                            f.write(chunk)
                messagebox.showinfo("Export Successful", f"Report saved to:\n{save_path}", parent=self.root)
            else:
                messagebox.showinfo("Export Cancelled", "File save operation cancelled.", parent=self.root)

        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", "Could not connect to the API server. Please check your network or server status.", parent=self.root)
        except requests.exceptions.Timeout:
            messagebox.showerror("Timeout Error", "The request to the API server timed out.", parent=self.root)
        except requests.exceptions.HTTPError as e:
            messagebox.showerror("API Error", f"HTTP Error: {e.response.status_code} - {e.response.text}", parent=self.root)
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Request Error", f"An error occurred during the API request: {e}", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred during export: {e}", parent=self.root)

    def sort_treeview(self, col, reverse):
        """Sort treeview column data."""
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        items.sort(reverse=reverse)
        for index, (val, k) in enumerate(items):
            self.tree.move(k, "", index)
        self.tree.heading(col, command=lambda: self.sort_treeview(col, not reverse))

    def search_data(self, event=None):
        pass # This method is now likely obsolete given API-side filtering

    def populate_treeview(self, data):
        pass # This helper is now largely replaced by the logic within filter_data.