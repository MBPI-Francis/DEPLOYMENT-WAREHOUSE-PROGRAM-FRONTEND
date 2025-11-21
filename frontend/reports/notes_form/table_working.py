# -- VERSION 2 (Final with Centered Dialogs)
import ttkbootstrap as ttk
from ttkbootstrap import DateEntry
from ttkbootstrap.constants import *
import requests
from tkinter import Menu, Toplevel, Label, Entry, Button, messagebox, filedialog
import tkinter as tk
from ttkbootstrap.dialogs import Messagebox
from backend.settings.database import server_ip
from datetime import datetime, timedelta
from ttkbootstrap.tooltip import ToolTip
from frontend.forms.shared import SharedFunctions
import os
import pandas as pd
import threading  # For running the export in the background
import sys  # For checking the operating system
import subprocess  # For opening files on macOS/Linux


class NoteTable:
    def __init__(self, root):
        self.root = root
        self.shared_functions = SharedFunctions()
        get_status_api = self.shared_functions.get_status_api()
        get_warehouse_api = self.shared_functions.get_warehouse_api()
        get_rm_code_api = self.shared_functions.get_rm_code_api(force_refresh=True)

        # Frame for search
        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill=X, padx=10, pady=(15, 0))

        # --- (All your GUI widget definitions remain here, unchanged) ---

        # Date Entry field FROM
        date_label_from = ttk.Label(search_frame, text="Date FROM", style="CustomLabel.TLabel")
        date_label_from.grid(row=0, column=0, padx=5, pady=0, sticky=W)
        self.date_from_entry = ttk.DateEntry(search_frame, bootstyle=PRIMARY, dateformat="%m/%d/%Y", width=11)
        self.date_from_entry.grid(row=1, column=0, padx=5, pady=0, sticky=W)
        self.date_from_entry.entry.delete(0, "end")
        self.date_from_entry.entry.config(font=self.shared_functions.custom_font_size)
        ToolTip(self.date_from_entry, text="Please enter the outgoing date")

        # Date Entry field TO
        date_label_to = ttk.Label(search_frame, text="Date TO", style="CustomLabel.TLabel")
        date_label_to.grid(row=0, column=1, padx=5, pady=0, sticky=W)
        self.date_to_entry = ttk.DateEntry(search_frame, bootstyle=PRIMARY, dateformat="%m/%d/%Y", width=11)
        self.date_to_entry.grid(row=1, column=1, padx=5, pady=0, sticky=W)
        self.date_to_entry.entry.delete(0, "end")
        self.date_to_entry.entry.config(font=self.shared_functions.custom_font_size)
        ToolTip(self.date_to_entry, text="Please enter the outgoing date")

        # RM CODE
        self.rm_codes = get_rm_code_api
        self.code_to_id = {item["rm_code"]: item["id"] for item in self.rm_codes}
        rm_names = ["All"] + list(self.code_to_id.keys())

        def on_combobox_key_release(event):
            current_text = self.rm_codes_combobox.get()
            self.rm_codes_combobox.set(current_text.upper())

        rm_codes_label = ttk.Label(search_frame, text="Raw Material", style="CustomLabel.TLabel")
        rm_codes_label.grid(row=0, column=2, padx=(8, 0), pady=(0, 0), sticky=W)
        self.rm_codes_combobox = ttk.Combobox(search_frame, values=rm_names, state="normal", width=20,
                                              font=self.shared_functions.custom_font_size)
        self.rm_codes_combobox.bind("<KeyRelease>", on_combobox_key_release)
        self.rm_codes_combobox.set("All")
        self.rm_codes_combobox.grid(row=1, column=2, pady=(0, 0), padx=(10, 0))
        ToolTip(self.rm_codes_combobox, text="Choose a raw material")

        # Warehouse
        self.warehouses = get_warehouse_api
        self.warehouse_to_id = {item["wh_name"]: item["id"] for item in self.warehouses}
        warehouse_names = ["All"] + list(self.warehouse_to_id.keys())
        warehouse_label = ttk.Label(search_frame, text="Location", style="CustomLabel.TLabel")
        warehouse_label.grid(row=0, column=3, padx=(8, 0), pady=(0, 0), sticky=W)
        self.warehouse_combobox = ttk.Combobox(search_frame, values=warehouse_names, state="readonly", width=13,
                                               font=self.shared_functions.custom_font_size)
        self.warehouse_combobox.grid(row=1, column=3, padx=(10, 0), pady=(0, 0), sticky=W)
        self.warehouse_combobox.set("All")

        # Status
        self.status_list = get_status_api
        self.status_to_id = {item["name"]: item["id"] for item in self.status_list}
        status_names = ["All"] + list(self.status_to_id.keys())
        status_label = ttk.Label(search_frame, text="Status", style="CustomLabel.TLabel")
        status_label.grid(row=0, column=4, padx=(10, 0), pady=(0, 0), sticky=W)
        self.status_combobox = ttk.Combobox(search_frame, values=status_names, state="readonly", width=19,
                                            font=self.shared_functions.custom_font_size)
        self.status_combobox.grid(row=1, column=4, padx=(10, 0), pady=(0, 0), sticky=W)
        self.status_combobox.set("All")

        # Document types
        self.document_types_data = [
            {"id": "all", "document_type_name": "All"},
            {"id": "preparation_form_report", "document_type_name": "Preparation Form"},
            {"id": "rm_outgoing_form_report", "document_type_name": "RM Outgoing Form"},
            {"id": "supply_outgoing_form_report", "document_type_name": "Supply Outgoing Form"},
            {"id": "receiving_form_report", "document_type_name": "Receiving Form"},
            {"id": "adjustment_form_entries", "document_type_name": "Adjustment Form Entries"},
            {"id": "adjustment_form_spillage", "document_type_name": "Adjustment Form Spillage"},
            {"id": "transfer_form_report", "document_type_name": "Transfer Form"},
            {"id": "change_status_form_report", "document_type_name": "Change Status Form"},
        ]
        self.document_type_to_id = {item["document_type_name"]: item["id"] for item in self.document_types_data}
        document_type_names = list(self.document_type_to_id.keys())
        document_type_label = ttk.Label(search_frame, text="Document Type", style="CustomLabel.TLabel")
        document_type_label.grid(row=0, column=5, padx=(8, 0), pady=(0, 0), sticky=W)
        self.document_type_combobox = ttk.Combobox(search_frame, values=document_type_names, state="readonly", width=25,
                                                   font=self.shared_functions.custom_font_size)
        self.document_type_combobox.grid(row=1, column=5, padx=(10, 0), pady=(0, 0), sticky=W)
        self.document_type_combobox.set("All")

        # Filter button
        btn_filter = ttk.Button(search_frame, text="Filter Data", command=self.filter_data, bootstyle=SECONDARY)
        btn_filter.grid(row=1, column=6, padx=(10, 0), pady=(0, 0), sticky=W)
        ToolTip(btn_filter, text="Click the button to filter the data table.")

        # Export button
        btn_export = ttk.Button(search_frame, text="Export to Excel", command=self.export_data, bootstyle=SUCCESS)
        btn_export.grid(row=1, column=7, padx=(10, 0), pady=(0, 0), sticky=E)
        ToolTip(btn_export, text="Click the button to export the data into excel.")

        # --- (Treeview setup remains here, unchanged) ---
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)
        self.tree = ttk.Treeview(master=tree_frame, columns=(
        "Date Encoded", "Date Reported", "Document Type", "Document No.", "Raw Material", "QTY", "Location", "Status"),
                                 show='headings', style="Custom.Treeview", bootstyle=PRIMARY)
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=self.tree.yview)
        tree_scroll_y.pack(side=RIGHT, fill=Y)
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=HORIZONTAL, command=self.tree.xview)
        tree_scroll_x.pack(side=BOTTOM, fill=X)
        self.tree.pack(fill=BOTH, expand=YES)
        self.tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        col_names = ["Date Encoded", "Date Reported", "Document Type", "Document No.", "Raw Material", "QTY",
                     "Location", "Status"]
        for col in col_names:
            self.tree.heading(col, text=col, command=lambda _col=col: self.sort_treeview(_col, False), anchor=W)
            self.tree.column(col, anchor=W)

        self.filter_data()

    # --- (Previous helper functions are unchanged) ---
    def _get_filter_params(self):
        params = {}
        try:
            date_from_str = self.date_from_entry.entry.get()
            params['date_from'] = datetime.strptime(date_from_str, "%m/%d/%Y").strftime(
                "%Y-%m-%d") if date_from_str else None
            date_to_str = self.date_to_entry.entry.get()
            params['date_to'] = datetime.strptime(date_to_str, "%m/%d/%Y").strftime("%Y-%m-%d") if date_to_str else None
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter dates in MM/DD/YYYY format.", parent=self.root)
            return None
        mat_code = self.rm_codes_combobox.get().strip()
        params['mat_code'] = mat_code if mat_code and mat_code.lower() != "all" else None
        document_type_name = self.document_type_combobox.get()
        params['document_type'] = self.document_type_to_id.get(
            document_type_name) if document_type_name and document_type_name.lower() != "all" else None
        location = self.warehouse_combobox.get()
        params['location'] = location if location and location.lower() != "all" else None
        status = self.status_combobox.get()
        params['status'] = status if status and status.lower() != "all" else None
        return params

    def filter_data(self):
        params = self._get_filter_params()
        if params is None: return
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
                date_encoded = datetime.fromisoformat(item.get("date_encoded", "")).strftime("%m/%d/%Y") if item.get(
                    "date_encoded") else ""
                date_reported = datetime.fromisoformat(item.get("date_reported", "")).strftime("%m/%d/%Y") if item.get(
                    "date_reported") else ""
                record = (date_encoded, date_reported, item.get("document_type", ""), item.get("document_number", ""),
                          item.get("mat_code", ""), item.get("qty", ""), item.get("whse_no", ""),
                          item.get("status", ""))
                self.tree.insert("", END, values=record)
        except requests.exceptions.RequestException as e:
            messagebox.showerror("API Error", f"An error occurred during the API request: {e}", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=self.root)

    # --- NEW HELPER FUNCTIONS ---
    def _center_window(self, win):
        """Helper function to center a Toplevel window over the main application window."""
        win.update_idletasks()
        main_win = self.root.winfo_toplevel()
        main_width = main_win.winfo_width()
        main_height = main_win.winfo_height()
        main_x = main_win.winfo_x()
        main_y = main_win.winfo_y()
        win_width = win.winfo_width()
        win_height = win.winfo_height()
        x = main_x + (main_width - win_width) // 2
        y = main_y + (main_height - win_height) // 2
        win.geometry(f'+{x}+{y}')

    def _open_file(self, path):
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.call(["open", path])
            else:
                subprocess.call(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open the file: {e}\n\nIt is saved at:\n{path}", parent=self.root)

    def _show_completion_dialog(self, save_path):
        response = Messagebox.show_question(
            title="Export Successful",
            message=f"Report saved successfully!\n\nDo you want to open the file?",
            buttons=["Yes:primary", "No:secondary"],
            parent=self.root,
            alert=True
        )
        if response == "Yes":
            self._open_file(save_path)

    # --- MODIFIED export_data and worker functions ---
    def export_data(self):
        params = self._get_filter_params()
        if params is None:
            return

        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        warehouse_reports_dir = os.path.join(desktop_path, "Warehouse Reports")
        os.makedirs(warehouse_reports_dir, exist_ok=True)

        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialdir=warehouse_reports_dir,
            initialfile="RM_Transaction_Report.xlsx",
            title="Save Warehouse Report"
        )

        if not save_path:
            messagebox.showinfo("Export Cancelled", "File save operation cancelled.", parent=self.root)
            return

        # --- SETUP AND RUN LOADER + THREAD ---
        loader = Toplevel(self.root)
        loader.title("Exporting...")
        loader.geometry("300x100")
        loader.resizable(False, False)
        loader.transient(self.root)
        loader.grab_set()

        # Center the loader window
        self._center_window(loader)

        ttk.Label(loader, text="Exporting report, please wait...", bootstyle=INFO).pack(pady=10)
        progress = ttk.Progressbar(loader, mode='indeterminate', bootstyle=STRIPED + SUCCESS)
        progress.pack(pady=10, padx=20, fill=X)
        progress.start()

        export_thread = threading.Thread(
            target=self._perform_export_worker,
            args=(params, save_path, loader)
        )
        export_thread.start()

    def _perform_export_worker(self, params, save_path, loader):
        try:
            export_url = f"{server_ip}/api/reports/v1/form-entries/export-to-file/"
            response = requests.get(export_url, params=params, stream=True)
            response.raise_for_status()
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            data_url = f"{server_ip}/api/reports/v1/form-entries/"
            response = requests.get(data_url, params=params)
            response.raise_for_status()
            data = response.json()

            if not data:
                self.root.after(0, self._show_completion_dialog, save_path)
                return

            df = pd.DataFrame(data)

            # Correctly restored consolidation logic
            def get_category(doc_type):
                if not isinstance(doc_type, str):
                    return None
                if doc_type == 'adjustment_form_spillage':
                    return 'adjustment_form_spillage'
                if 'adjustment_form' in doc_type:
                    return 'adjustment_form_entries'
                if doc_type in ['preparation_form_report', 'receiving_form_report', 'rm_outgoing_form_report',
                                'transfer_form_report', 'change_status_form_report', 'supply_outgoing_form_report']:
                    return doc_type
                return None

            df['category'] = df['document_type'].apply(get_category)
            df_categorized = df.dropna(subset=['category'])

            skipped_numbers_data = {}
            for category, group in df_categorized.groupby('category'):
                doc_numbers = pd.to_numeric(group['document_number'], errors='coerce').dropna().unique()
                if len(doc_numbers) > 1:
                    min_num, max_num = int(doc_numbers.min()), int(doc_numbers.max())
                    full_range = set(range(min_num, max_num + 1))
                    existing_numbers = set(doc_numbers.astype(int))
                    skipped = sorted(list(full_range - existing_numbers))
                    if skipped:
                        skipped_numbers_data[category] = skipped

            df_skipped = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in skipped_numbers_data.items()]))

            if not df_skipped.empty:
                with pd.ExcelWriter(save_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    df_skipped.to_excel(writer, sheet_name='Skipped Numbers', index=False)

            self.root.after(0, self._show_completion_dialog, save_path)

        except requests.exceptions.RequestException as e:
            self.root.after(0, lambda: messagebox.showerror("Export Failed", f"An error occurred during export: {e}",
                                                            parent=self.root))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An unexpected error occurred: {e}",
                                                            parent=self.root))
        finally:
            self.root.after(0, loader.destroy)

    # --- (sort_treeview and other methods remain unchanged) ---
    def sort_treeview(self, col, reverse):
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        items.sort(reverse=reverse)
        for index, (val, k) in enumerate(items):
            self.tree.move(k, "", index)
        self.tree.heading(col, command=lambda: self.sort_treeview(col, not reverse))

    def search_data(self, event=None):
        pass

    def populate_treeview(self, data):
        pass