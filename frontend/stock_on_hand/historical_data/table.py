# import ttkbootstrap as ttk
# from ttkbootstrap.tableview import Tableview
# from ttkbootstrap.constants import *
# import requests
# from backend.settings.database import server_ip
# from datetime import datetime
#
#
# class HistoricalSOHTable:
#
#     def __init__(self, root):
#         self.note_form_tab = root
#
#         self.coldata = [
#             {"text": "Raw Material Code", "stretch": True, "anchor": "w"},
#             {"text": "Warehouse", "stretch": True},
#             {"text": "Stocks", "stretch": True},
#             {"text": "Status", "stretch": True},
#             {"text": "Inventory Report Date", "stretch": True}
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
#         url = server_ip + "/api/rm_stock_on_hand/v1/list/historical/"
#         try:
#             response = requests.get(url)
#             response.raise_for_status()
#
#             data = response.json()
#
#             # Format data for the table
#             rowdata = [
#                 (
#                     item["rm_code"],
#                     item["wh_name"],
#                     "{:,.2f}".format(float(item["qty"])),  # Format with commas
#                     item["status_name"],
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
from ttkbootstrap import DateEntry, Combobox
from ttkbootstrap.constants import *
import requests
from backend.settings.database import server_ip
from tkinter import messagebox, filedialog, StringVar
from datetime import datetime
from ttkbootstrap.tooltip import ToolTip
from frontend.stock_on_hand.import_feature.confirm_messages import ConfirmationMessage
from frontend.forms.shared import SharedFunctions
import os
import pandas as pd # NEW: Import pandas for local Excel generation
from io import BytesIO # NEW: Import BytesIO for in-memory file handling


class HistoricalSOHTable:
    def __init__(self, root):
        self.root = root
        self.confirmation_message = ConfirmationMessage(self.root)
        self.shared_functions = SharedFunctions()



        filter_button_frame = ttk.Frame(self.root)
        filter_button_frame.pack(fill=X, padx=10, pady=(10, 0))

        # --- Filter Fields ---
        ttk.Label(filter_button_frame, text="Date FROM", style="CustomLabel.TLabel").grid(row=0, column=0, padx=5, pady=0, sticky=W)
        ttk.Label(filter_button_frame, text="Date TO", style="CustomLabel.TLabel").grid(row=0, column=1, padx=5, pady=0, sticky=W)
        ttk.Label(filter_button_frame, text="Raw Material", style="CustomLabel.TLabel").grid(row=0, column=2, padx=(8, 0), pady=0, sticky=W)
        ttk.Label(filter_button_frame, text="Warehouse", style="CustomLabel.TLabel").grid(row=0, column=3, padx=(8, 0), pady=0, sticky=W)
        ttk.Label(filter_button_frame, text="Status", style="CustomLabel.TLabel").grid(row=0, column=4, padx=(8, 0), pady=0, sticky=W)

        self.date_from_entry = DateEntry(filter_button_frame, bootstyle=PRIMARY, dateformat="%m/%d/%Y", width=11)
        self.date_from_entry.grid(row=1, column=0, padx=5, pady=0, sticky=W)
        self.date_from_entry.entry.config(font=self.shared_functions.custom_font_size)
        ToolTip(self.date_from_entry, text="Filter by start date of inventory report")

        self.date_to_entry = DateEntry(filter_button_frame, bootstyle=PRIMARY, dateformat="%m/%d/%Y", width=11)
        self.date_to_entry.grid(row=1, column=1, padx=5, pady=0, sticky=W)
        self.date_to_entry.entry.config(font=self.shared_functions.custom_font_size)
        ToolTip(self.date_to_entry, text="Filter by end date of inventory report")

        rm_codes_data = self.shared_functions.get_rm_code_api(force_refresh=True)
        rm_names = ["All"] + [item["rm_code"] for item in rm_codes_data]
        self.rm_codes_combobox = Combobox(filter_button_frame, values=rm_names, state="normal", width=20, font=self.shared_functions.custom_font_size)
        self.rm_codes_combobox.set("All")
        self.rm_codes_combobox.grid(row=1, column=2, padx=(10, 0), pady=0, sticky=W)
        ToolTip(self.rm_codes_combobox, text="Filter by Raw Material Code")

        warehouses_data = self.shared_functions.get_warehouse_api()
        warehouse_names = ["All"] + [item["wh_name"] for item in warehouses_data]
        self.warehouse_combobox = Combobox(filter_button_frame, values=warehouse_names, state="readonly", width=13, font=self.shared_functions.custom_font_size)
        self.warehouse_combobox.set("All")
        self.warehouse_combobox.grid(row=1, column=3, padx=(10, 0), pady=0, sticky=W)
        ToolTip(self.warehouse_combobox, text="Filter by Warehouse Location")

        status_data = self.shared_functions.get_status_api()
        status_names = ["All"] + [item["name"] for item in status_data]
        self.status_combobox = Combobox(filter_button_frame, values=status_names, state="readonly", width=19, font=self.shared_functions.custom_font_size)
        self.status_combobox.set("All")
        self.status_combobox.grid(row=1, column=4, padx=(10, 0), pady=0, sticky=W)
        ToolTip(self.status_combobox, text="Filter by Raw Material Status")

        # --- Buttons ---
        btn_filter = ttk.Button(
            filter_button_frame,
            text="Filter Data",
            command=self.filter_data,
            bootstyle=SECONDARY,
        )
        btn_filter.grid(row=1, column=5, padx=(10, 0), pady=0, sticky=W)
        ToolTip(btn_filter, text="Click to apply filters and update the table.")

        btn_export = ttk.Button(
            filter_button_frame,
            text="Export to Excel",
            command=self.export_data, # This will now trigger local Excel generation
            bootstyle=SUCCESS,
        )
        btn_export.grid(row=1, column=6, padx=(10, 0), pady=0, sticky=W)
        ToolTip(btn_export, text="Click to export filtered data to an Excel file.")


        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill=X, padx=10, pady=(10, 0))
        ttk.Label(search_frame, text="Search (Client-side):", style="CustomLabel.TLabel").pack(side=LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=50)
        self.search_entry.pack(side=LEFT)
        self.search_entry.bind("<Return>", self.search_data)


        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)

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
            style="Custom.Treeview",
            bootstyle=PRIMARY
        )

        tree_scroll_y = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=self.tree.yview)
        tree_scroll_y.pack(side=RIGHT, fill=Y)

        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=HORIZONTAL, command=self.tree.xview)
        tree_scroll_x.pack(side=BOTTOM, fill=X)

        self.tree.pack(fill=BOTH, expand=YES)
        self.tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

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

        self.filter_data()

    def _get_filter_params(self):
        """Helper to collect and format filter parameters from GUI widgets."""
        params = {}

        try:
            date_from_str = self.date_from_entry.entry.get()
            params['date_from'] = datetime.strptime(date_from_str, "%m/%d/%Y").strftime("%Y-%m-%d") if date_from_str else None
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter 'Date FROM' in MM/DD/YYYY format.", parent=self.root)
            return None

        try:
            date_to_str = self.date_to_entry.entry.get()
            params['date_to'] = datetime.strptime(date_to_str, "%m/%d/%Y").strftime("%Y-%m-%d") if date_to_str else None
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter 'Date TO' in MM/DD/YYYY format.", parent=self.root)
            return None

        mat_code = self.rm_codes_combobox.get().strip()
        params['mat_code'] = mat_code if mat_code and mat_code.lower() != "all" else None

        location = self.warehouse_combobox.get().strip()
        params['location'] = location if location and location.lower() != "all" else None

        status = self.status_combobox.get().strip()
        params['status'] = status if status and status.lower() != "all" else None

        return params

    def filter_data(self):
        """Fetch filtered data from API and populate treeview."""
        params = self._get_filter_params()
        if params is None:
            return

        url = server_ip + "/api/rm_stock_on_hand/v1/list/historical/"

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            self.tree.delete(*self.tree.get_children())
            self.original_data = []

            if not data:
                messagebox.showinfo("No Data", "No records found matching the filter criteria.", parent=self.root)
                return

            for item in data:
                record = (
                    item.get("rm_code", ""),
                    item.get("wh_name", ""),
                    "{:,.2f}".format(float(item.get("qty", 0.0))),
                    item.get("status_name", ""),
                    datetime.fromisoformat(item.get("date_computed", "")).strftime("%m/%d/%Y") if item.get("date_computed") else ""
                )
                self.original_data.append(record)
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
        """
        Fetch filtered data from API, generate Excel file locally using pandas,
        and prompt user to save.
        """
        params = self._get_filter_params()
        if params is None:
            return

        # Use the same API endpoint as filter_data to get the raw JSON data
        api_url = f"{server_ip}/api/rm_stock_on_hand/v1/list/historical/"

        try:
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            raw_data = response.json() # Get the raw JSON data

            if not raw_data:
                messagebox.showinfo("No Data", "No records found matching the filter criteria to export.", parent=self.root)
                return

            # --- Local Excel Generation Logic (Moved from Backend) ---
            df_detailed = pd.DataFrame(raw_data)

            # Ensure 'date_computed' is a datetime object for proper grouping and formatting
            df_detailed['date_computed'] = pd.to_datetime(df_detailed['date_computed'], errors='coerce')
            df_detailed.dropna(subset=['date_computed'], inplace=True)

            if df_detailed.empty:
                messagebox.showinfo("No Valid Dates", "No valid date entries found for aggregation in the export data.", parent=self.root)
                return

            # Create the long format summary
            df_long_summary = df_detailed.groupby(['rm_code', df_detailed['date_computed'].dt.date])['qty'].sum().reset_index()
            df_long_summary = df_long_summary.rename(columns={'date_computed': 'Date'})
            df_long_summary['Date'] = df_long_summary['Date'].apply(lambda x: x.strftime('%m/%d/%Y'))

            # Pivot the table
            df_pivot_summary = df_long_summary.pivot_table(
                index='rm_code',
                columns='Date',
                values='qty',
                fill_value=0
            )

            df_pivot_summary = df_pivot_summary.sort_index(ascending=True)
            sorted_date_cols = pd.to_datetime(df_pivot_summary.columns, format='%m/%d/%Y', errors='coerce').sort_values()
            sorted_date_cols = sorted_date_cols.dropna()
            sorted_date_col_names = sorted_date_cols.strftime('%m/%d/%Y').tolist()
            df_pivot_summary = df_pivot_summary[sorted_date_col_names]
            df_pivot_summary = df_pivot_summary.reset_index()

            # Create an in-memory binary stream for the Excel file
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
                df_detailed.to_excel(writer, index=False, sheet_name="Detailed Data")
                df_pivot_summary.to_excel(writer, index=False, sheet_name="Daily RM Summary")

                # Optional: Adjust column widths for better readability
                workbook = writer.book
                if 'Daily RM Summary' in writer.sheets:
                    summary_sheet = writer.sheets['Daily RM Summary']
                    summary_sheet.set_column(0, 0, 20)
                    for i, col_name in enumerate(df_pivot_summary.columns[1:]):
                        summary_sheet.set_column(i + 1, i + 1, 12)

            excel_buffer.seek(0) # Rewind the buffer

            # --- Prompt user to save the file ---
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"Historical_SOH_Report_{timestamp}.xlsx"

            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            warehouse_reports_dir = os.path.join(desktop_path, "Warehouse Reports")
            os.makedirs(warehouse_reports_dir, exist_ok=True)

            save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialdir=warehouse_reports_dir,
                initialfile=default_filename,
                title="Save Historical SOH Report"
            )

            if save_path:
                with open(save_path, "wb") as f:
                    f.write(excel_buffer.getvalue()) # Write the content from BytesIO
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
        """Filter and display only matching records in the Treeview (client-side)."""
        search_term = self.search_entry.get().strip().lower()

        self.tree.delete(*self.tree.get_children())

        if not search_term:
            self.populate_treeview(self.original_data)
            return

        filtered_data = [
            record for record in self.original_data
            if any(search_term in str(value).lower() for value in record)
        ]

        if filtered_data:
            self.populate_treeview(filtered_data)
        else:
            messagebox.showinfo("Search", "No matching record found.", parent=self.root)

    def populate_treeview(self, data):
        """Helper function to insert data into the Treeview."""
        for record in data:
            self.tree.insert("", END, values=record)




