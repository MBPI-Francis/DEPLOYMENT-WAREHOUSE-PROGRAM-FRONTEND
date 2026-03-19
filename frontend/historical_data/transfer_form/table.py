import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import requests
from ttkbootstrap.tooltip import ToolTip
from tkinter import Toplevel, messagebox, filedialog, StringVar, IntVar
from backend.settings.database import server_ip
from datetime import datetime
from uuid import UUID
from ttkbootstrap.widgets import DateEntry, Combobox
from ttkbootstrap.dialogs import Messagebox
from .adjustment_form import AdjustmentForm
from frontend.historical_data.shared_confirmation_messages import ConfirmationMessage
from frontend.forms.shared import SharedFunctions
import os
import pandas as pd
from io import BytesIO
import xlsxwriter


# --- Column Selection Dialog Class ---
class ColumnSelectionDialog(Toplevel):
    def __init__(self, parent, columns_map):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.title("Select Columns for Export")
        self.parent = parent
        self.columns_map = columns_map
        self.selected_columns = {}

        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

        self._create_widgets()

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=BOTH, expand=YES) # Keep pack for the top-level frame within Toplevel

        # Configure main_frame to be responsive
        main_frame.grid_rowconfigure(2, weight=1)   # Row for canvas (checkboxes) expands vertically
        main_frame.grid_columnconfigure(0, weight=1) # Column for canvas expands horizontally

        ttk.Label(main_frame, text="Choose columns to include in the Excel report:",
                  font=("Helvetica", 11, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=W)

        # Frame for Select All / Deselect All buttons (above checkboxes)
        top_buttons_frame = ttk.Frame(main_frame)
        # Placed in row 1, spans 2 columns, and sticks to West for left alignment
        top_buttons_frame.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky=W)

        btn_select_all = ttk.Button(top_buttons_frame, text="Select All", command=self._select_all, bootstyle=INFO)
        btn_select_all.pack(side=LEFT, padx=5) # Keep pack within this sub-frame

        btn_deselect_all = ttk.Button(top_buttons_frame, text="Deselect All", command=self._deselect_all, bootstyle=INFO)
        btn_deselect_all.pack(side=LEFT, padx=5) # Keep pack within this sub-frame

        canvas = ttk.Canvas(main_frame)
        # Canvas takes row 2, spans 1 column (column 0), and sticks to all sides for responsiveness
        canvas.grid(row=2, column=0, sticky=NSEW)

        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        # Scrollbar in the second column (column 1) of row 2, sticky to all sides
        scrollbar.grid(row=2, column=1, sticky=NSEW)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion = canvas.bbox("all")))

        checkbox_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=checkbox_frame, anchor="nw")

        self.all_export_columns = {
            "Date Encoded": "created_at",
            "TF No.": "ref_number",
            "RM Code": "raw_material",
            "WHSE (FROM)": "from_warehouse",
            "WHSE (TO)": "to_warehouse",
            "Status": "status",
            "Quantity(kg)": "qty_kg",
            "Transfer Date": "transfer_date",
            "Date Computed": "date_computed"
        }

        # Checkboxes are packed within checkbox_frame (which is inside the canvas)
        # This is generally fine as pack and grid can be mixed in nested containers.
        for display_name in self.all_export_columns.keys():
            var = IntVar(value=1)
            cb = ttk.Checkbutton(checkbox_frame, text=display_name, variable=var, bootstyle="round-toggle")
            cb.pack(anchor=W, pady=2) # Retain pack for checkboxes inside checkbox_frame
            self.selected_columns[display_name] = var

        # Buttons frame for Export and Cancel (at the very bottom)
        bottom_buttons_frame = ttk.Frame(main_frame)
        # Placed in row 3, spans 2 columns, and sticks to East/West for horizontal filling
        bottom_buttons_frame.grid(row=3, column=0, columnspan=2, pady=(15, 0), sticky=EW)

        btn_cancel = ttk.Button(bottom_buttons_frame, text="Cancel", command=self.destroy, bootstyle=DANGER)
        btn_cancel.pack(side=LEFT, padx=5) # Pack to the right within this bottom frame

        btn_export = ttk.Button(bottom_buttons_frame, text="Export Selected", command=self._on_export, bootstyle=SUCCESS)
        btn_export.pack(side=RIGHT, padx=5) # Pack to the left within this bottom frame



    def _select_all(self):
        for var in self.selected_columns.values():
            var.set(1)

    def _deselect_all(self):
        for var in self.selected_columns.values():
            var.set(0)

    def _on_export(self):
        selected = []
        for display_name, var in self.selected_columns.items():
            if var.get() == 1:
                selected.append(display_name)
        if not selected:
            messagebox.showwarning("No Columns Selected", "Please select at least one column to export.", parent=self)
            return

        self.result_columns = selected
        self.destroy()

    def show(self):
        self.parent.wait_window(self)
        return getattr(self, 'result_columns', None)


class TransferFormTable:
    def __init__(self, root):
        self.root = root
        self.adjustment_form = AdjustmentForm(self)
        self.confirmation_message = ConfirmationMessage(self.root, self, "transfer")
        self.shared_functions = SharedFunctions()

        # Frame for filters and buttons
        filter_button_frame = ttk.Frame(self.root)
        filter_button_frame.pack(fill=X, padx=10, pady=(10, 0))

        # --- Filter Fields ---
        ttk.Label(filter_button_frame, text="Date FROM", style="CustomLabel.TLabel").grid(row=0, column=0, padx=5, pady=0, sticky=W)
        ttk.Label(filter_button_frame, text="Date TO", style="CustomLabel.TLabel").grid(row=0, column=1, padx=5, pady=0, sticky=W)
        ttk.Label(filter_button_frame, text="Raw Material", style="CustomLabel.TLabel").grid(row=0, column=2, padx=(8, 0), pady=0, sticky=W)
        ttk.Label(filter_button_frame, text="WHSE (FROM)", style="CustomLabel.TLabel").grid(row=0, column=3, padx=(8, 0), pady=0, sticky=W)
        ttk.Label(filter_button_frame, text="WHSE (TO)", style="CustomLabel.TLabel").grid(row=0, column=4, padx=(8, 0), pady=0, sticky=W)
        ttk.Label(filter_button_frame, text="Status", style="CustomLabel.TLabel").grid(row=0, column=5, padx=(8, 0), pady=0, sticky=W)

        self.date_from_entry = DateEntry(filter_button_frame, bootstyle=PRIMARY, dateformat="%m/%d/%Y", width=11)
        self.date_from_entry.grid(row=1, column=0, padx=5, pady=0, sticky=W)
        self.date_from_entry.entry.config(font=self.shared_functions.custom_font_size)
        self.date_from_entry.entry.delete(0, "end")
        ToolTip(self.date_from_entry, text="Filter by start transfer date")

        self.date_to_entry = DateEntry(filter_button_frame, bootstyle=PRIMARY, dateformat="%m/%d/%Y", width=11)
        self.date_to_entry.grid(row=1, column=1, padx=5, pady=0, sticky=W)
        self.date_to_entry.entry.config(font=self.shared_functions.custom_font_size)
        self.date_to_entry.entry.delete(0, "end")
        ToolTip(self.date_to_entry, text="Filter by end transfer date")

        rm_codes_data = self.shared_functions.get_rm_code_api(force_refresh=True)
        rm_names = ["All"] + [item["rm_code"] for item in rm_codes_data]
        self.rm_codes_combobox = Combobox(filter_button_frame, values=rm_names, state="normal", width=20, font=self.shared_functions.custom_font_size)
        self.rm_codes_combobox.set("All")
        self.rm_codes_combobox.grid(row=1, column=2, padx=(10, 0), pady=0, sticky=W)
        ToolTip(self.rm_codes_combobox, text="Filter by Raw Material Code")

        warehouses_data = self.shared_functions.get_warehouse_api()
        warehouse_names = ["All"] + [item["wh_name"] for item in warehouses_data]
        self.from_warehouse_combobox = Combobox(filter_button_frame, values=warehouse_names, state="readonly", width=13, font=self.shared_functions.custom_font_size)
        self.from_warehouse_combobox.set("All")
        self.from_warehouse_combobox.grid(row=1, column=3, padx=(10, 0), pady=0, sticky=W)
        ToolTip(self.from_warehouse_combobox, text="Filter by From Warehouse")

        self.to_warehouse_combobox = Combobox(filter_button_frame, values=warehouse_names, state="readonly", width=13, font=self.shared_functions.custom_font_size)
        self.to_warehouse_combobox.set("All")
        self.to_warehouse_combobox.grid(row=1, column=4, padx=(10, 0), pady=0, sticky=W)
        ToolTip(self.to_warehouse_combobox, text="Filter by To Warehouse")

        status_data = self.shared_functions.get_status_api()
        status_names = ["All"] + [item["name"] for item in status_data]
        self.status_combobox = Combobox(filter_button_frame, values=status_names, state="readonly", width=19, font=self.shared_functions.custom_font_size)
        self.status_combobox.set("All")
        self.status_combobox.grid(row=1, column=5, padx=(10, 0), pady=0, sticky=W)
        ToolTip(self.status_combobox, text="Filter by Status")

        # --- Buttons ---
        btn_filter = ttk.Button(
            filter_button_frame,
            text="Filter Data",
            command=self.filter_data,
            bootstyle=SECONDARY,
        )
        btn_filter.grid(row=1, column=6, padx=(10, 0), pady=0, sticky=W)
        ToolTip(btn_filter, text="Click to apply filters and update the table.")

        btn_export = ttk.Button(
            filter_button_frame,
            text="Export to Excel",
            command=self.export_data,
            bootstyle=SUCCESS,
        )
        btn_export.grid(row=1, column=7, padx=(10, 0), pady=0, sticky=W)
        ToolTip(btn_export, text="Click to export filtered data to an Excel file.")

        # Original search frame (kept for existing client-side search)
        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill=X, padx=10, pady=(10, 0))
        ttk.Label(search_frame, text="Search:", style="CustomLabel.TLabel").pack(side=LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=50)
        self.search_entry.pack(side=LEFT)
        self.search_entry.bind("<Return>", self.search_data)

        # Create a frame to hold the Treeview and Scrollbars
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        self.tree = ttk.Treeview(
            master=tree_frame,
            columns=(
                "Date Encoded",
                "TF No.",
                "Raw Material",
                "Quantity(kg)",
                "Status",
                "WHSE (FROM)",
                "WHSE (TO)",
                "Transfer Date",
                "Date Computed",
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

        # Define column headings for displayed columns
        displayed_col_names = [
            "Date Encoded",
            "TF No.",
            "Raw Material",
            "Quantity(kg)",
            "Status",
            "WHSE (FROM)",
            "WHSE (TO)",
            "Transfer Date",
            "Date Computed"
        ]
        for col in displayed_col_names:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c, False), anchor=W)
            self.tree.column(col, width=150, anchor="w")

        self.filter_data() # Initial load of data using the filter method

        self.tree.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            menu = ttk.Menu(self.root, tearoff=0)
            record_values = self.tree.item(item, 'values')
            # CORRECTED INDEX: 'Is Adjusted' is at index 9 in the 'values' tuple
            is_adjusted = record_values[9] # Access the 10th element (index 9)

            if is_adjusted == 'True':
                menu.add_command(label="Adjust",
                                 command=lambda: self.confirmation_message.show_confirmation_message_adjusted(item))
            else:
                menu.add_command(label="Adjust",
                                 command=lambda: self.confirmation_message.show_confirmation_message(item))
            menu.post(event.x_root, event.y_root)

    def _get_filter_params(self):
        params = {}
        try:
            date_from_str = self.date_from_entry.entry.get()
            params['date_from'] = datetime.strptime(date_from_str, "%m/%d/%Y").strftime("%Y-%m-%d") if date_from_str else None
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter 'Transfer Date FROM' in MM/DD/YYYY format.", parent=self.root)
            return None

        try:
            date_to_str = self.date_to_entry.entry.get()
            params['date_to'] = datetime.strptime(date_to_str, "%m/%d/%Y").strftime("%Y-%m-%d") if date_to_str else None
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter 'Transfer Date TO' in MM/DD/YYYY format.", parent=self.root)
            return None

        rm_code = self.rm_codes_combobox.get().strip()
        params['rm_code'] = rm_code if rm_code and rm_code.lower() != "all" else None

        from_wh = self.from_warehouse_combobox.get().strip()
        params['from_warehouse_name'] = from_wh if from_wh and from_wh.lower() != "all" else None

        to_wh = self.to_warehouse_combobox.get().strip()
        params['to_warehouse_name'] = to_wh if to_wh and to_wh.lower() != "all" else None

        status = self.status_combobox.get().strip()
        params['status_name'] = status if status and status.lower() != "all" else None

        return params

    def filter_data(self):
        params = self._get_filter_params()
        if params is None:
            return

        url = server_ip + "/api/transfer_forms/v1/list/historical/"

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
                qty_kg_formatted = "{:,.2f}".format(float(item.get("qty_kg", 0.0)))
                record = (
                    item.get("id"),
                    datetime.fromisoformat(item.get("created_at", "")).strftime("%m/%d/%Y %I:%M %p") if item.get("created_at") else "",
                    item.get("ref_number", ""),
                    item.get("raw_material", ""),
                    qty_kg_formatted,
                    item.get("status", ""),
                    item.get("from_warehouse", ""),
                    item.get("to_warehouse", ""),
                    datetime.fromisoformat(item.get("transfer_date", "")).strftime("%m/%d/%Y") if item.get("transfer_date") else "",
                    datetime.fromisoformat(item.get("date_computed", "")).strftime("%m/%d/%Y") if item.get("date_computed") else "",
                    item.get("is_adjusted", "")
                )
                self.original_data.append(record)
                self.tree.insert("", END, iid=record[0], values=record[1:])

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
        Opens a dialog for column selection, then fetches filtered data and exports
        only the selected columns to a single Excel sheet.
        """
        dialog = ColumnSelectionDialog(self.root, columns_map={})
        selected_display_names = dialog.show()

        if selected_display_names is None:
            return

        api_column_map = ColumnSelectionDialog(self.root, {}).all_export_columns
        selected_api_keys = [api_column_map[d_name] for d_name in selected_display_names if d_name in api_column_map]

        if not selected_api_keys:
            messagebox.showwarning("No Valid Columns", "No valid columns were selected for export. Please try again.", parent=self.root)
            return

        params = self._get_filter_params()
        if params is None:
            return

        api_url = f"{server_ip}/api/transfer_forms/v1/list/historical/"

        try:
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            raw_data = response.json()

            if not raw_data:
                messagebox.showinfo("No Data", "No records found matching the filter criteria to export.", parent=self.root)
                return

            processed_data_for_export = []
            for item in raw_data:
                row = {}
                for display_name in selected_display_names:
                    api_key = api_column_map.get(display_name)

                    if api_key:
                        value = item.get(api_key)

                        if api_key == "created_at":
                            row[display_name] = datetime.fromisoformat(value).strftime(
                                "%m/%d/%Y %I:%M %p") if value else ""

                        elif api_key == "date_computed":
                            row[display_name] = datetime.fromisoformat(value).strftime("%m/%d/%Y") if value else ""

                        elif api_key == "transfer_date":
                            row[display_name] = datetime.fromisoformat(value).strftime("%m/%d/%Y") if value else ""

                        elif api_key == "qty_kg":
                            row[display_name] = float(value) if value is not None else 0.00

                        elif api_key == "is_deleted" or api_key == "is_adjusted":
                            row[display_name] = "Yes" if value else "No"

                        else:
                            row[display_name] = value if value is not None else ""
                processed_data_for_export.append(row)

            df_export = pd.DataFrame(processed_data_for_export, columns=selected_display_names)

            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
                df_export.to_excel(writer, index=False, sheet_name="Transfer Form Report")

                workbook = writer.book
                worksheet = writer.sheets['Transfer Form Report']
                for i, col in enumerate(df_export.columns):
                    max_len = max(df_export[col].astype(str).map(len).max(), len(col)) + 2
                    worksheet.set_column(i, i, max_len)

            excel_buffer.seek(0)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"Transfer_Form_Report_{timestamp}.xlsx"

            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            reports_dir = os.path.join(desktop_path, "Transfer Form Reports")
            os.makedirs(reports_dir, exist_ok=True)

            save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialdir=reports_dir,
                initialfile=default_filename,
                title="Save Transfer Form Report"
            )

            if save_path:
                with open(save_path, "wb") as f:
                    f.write(excel_buffer.getvalue())
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

    def sort_column(self, col, reverse):
        """Sort Treeview column chronologically, numerically, or alphabetically."""
        # Get the items in the current column
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]

        def custom_sort(item):
            val = item[0]

            # Handle 'Date Encoded' format (includes time)
            if col == "Date Encoded":
                try:
                    return datetime.strptime(val, "%m/%d/%Y %I:%M %p")
                except ValueError:
                    return datetime.min  # Fallback if empty/invalid

            # Handle other Date formats (only date, no time)
            elif col in ("Transfer Date", "Date Computed"):
                try:
                    return datetime.strptime(val, "%m/%d/%Y")
                except ValueError:
                    return datetime.min  # Fallback if empty/invalid

            # Handle Quantity (remove commas before float conversion)
            elif col == "Quantity(kg)":
                try:
                    return float(val.replace(",", ""))
                except ValueError:
                    return 0.0  # Fallback for empty strings

            # Handle Mixed Types securely (prevents str vs float crash)
            else:
                try:
                    # Return a tuple (0, number) so it safely sorts numbers before strings
                    return (0, float(val.replace(",", "")))
                except ValueError:
                    # Return a tuple (1, string) for non-numeric data
                    return (1, val.lower())

        # Sort the items using the custom logic
        data.sort(key=custom_sort, reverse=reverse)

        # Rearrange the items in the Treeview
        for index, (_, k) in enumerate(data):
            self.tree.move(k, "", index)

        # Toggle the sorting direction for the next click
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

    def search_data(self, event=None):
        """Filter and display only matching records in the Treeview."""
        search_term = self.search_entry.get().strip().lower()
        self.tree.delete(*self.tree.get_children())
        if not search_term:
            self.populate_treeview(self.original_data)
            return

        filtered_data = [
            record for record in self.original_data
            if any(search_term in str(value).lower() for value in record[1:])
        ]
        if filtered_data:
            self.populate_treeview(filtered_data)
        else:
            messagebox.showinfo("Search", "No matching record found.")

    def populate_treeview(self, data):
        """Helper function to insert data into the Treeview."""
        for record in data:
            self.tree.insert("", END, iid=record[0], values=record[1:])