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

class NoteTable:
    def __init__(self, root):
        self.root = root

        shared_functions = SharedFunctions()

        self.get_status_api = shared_functions.get_status_api()
        self.get_warehouse_api = shared_functions.get_warehouse_api()
        self.get_rm_code_api = shared_functions.get_rm_code_api(force_refresh=True)

        # Frame for search
        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill=X, padx=10, pady=(15, 0))

        # Date Entry field
        date_label = ttk.Label(search_frame, text="Date FROM", style="CustomLabel.TLabel")
        date_label.grid(row=0, column=0, padx=5, pady=0, sticky=W)

        self.date_from_entry = ttk.DateEntry(
            search_frame,
            bootstyle=PRIMARY,
            dateformat="%m/%d/%Y",
            width=11
        )
        self.date_from_entry.grid(row=1, column=0, padx=5, pady=0, sticky=W)
        ToolTip(self.date_from_entry, text="Please enter the outgoing date")

        date_label = ttk.Label(search_frame, text="Date TO", style="CustomLabel.TLabel")
        date_label.grid(row=0, column=1, padx=5, pady=0, sticky=W)

        self.date_to_entry = ttk.DateEntry(
            search_frame,
            bootstyle=PRIMARY,
            dateformat="%m/%d/%Y",
            width=11
        )
        self.date_to_entry.grid(row=1, column=1, padx=5, pady=0, sticky=W)
        ToolTip(self.date_to_entry, text="Please enter the outgoing date")

        # RM Code Combobox
        rm_codes = self.get_rm_code_api
        rm_names = ["All"] + [item["rm_code"] for item in rm_codes]
        self.rm_codes_combobox = ttk.Combobox(search_frame, values=rm_names, state="normal", width=20)
        self.rm_codes_combobox.grid(row=1, column=2, padx=10, pady=0)
        self.rm_codes_combobox.set("All")

        # Warehouse Combobox
        warehouses = self.get_warehouse_api
        warehouse_names = ["All"] + [item["wh_name"] for item in warehouses]
        self.warehouse_combobox = ttk.Combobox(search_frame, values=warehouse_names, state="readonly", width=13)
        self.warehouse_combobox.grid(row=1, column=3, padx=10, pady=0)
        self.warehouse_combobox.set("All")

        # Status Combobox
        status = self.get_status_api
        status_names = ["All"] + [item["name"] for item in status]
        self.status_combobox = ttk.Combobox(search_frame, values=status_names, state="readonly", width=19)
        self.status_combobox.grid(row=1, column=4, padx=10, pady=0)
        self.status_combobox.set("All")

        # Document Type Combobox
        document_types = ["All", "Preparation Form", "Outgoing Form", "Receiving Form", "Adjustment Form", "Transfer Form", "Change Status Form"]
        self.document_type_combobox = ttk.Combobox(search_frame, values=document_types, state="readonly", width=15)
        self.document_type_combobox.grid(row=1, column=5, padx=10, pady=0)
        self.document_type_combobox.set("All")

        btn_filter = ttk.Button(search_frame, text="Filter Data", command=self.load_data, bootstyle=SECONDARY)
        btn_filter.grid(row=1, column=6, padx=10, pady=0)

        btn_export = ttk.Button(search_frame, text="Export to Excel", command=self.export_filtered_api_response, bootstyle=SUCCESS)
        btn_export.grid(row=1, column=7, padx=10, pady=0)

        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        self.tree = ttk.Treeview(tree_frame, columns=("Date Encoded", "Date Reported", "Document Type", "Document No.", "Rar Material", "QTY", "Location", "Status"), show='headings', bootstyle=PRIMARY)
        self.tree.pack(fill=BOTH, expand=YES)

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col, command=lambda _col=col: self.sort_treeview(_col, False))

        self.load_data()

    def get_api_params(self):
        params = {}
        if self.date_from_entry.entry.get().strip():
            params["date_from"] = self.date_from_entry.entry.get().strip()
        if self.date_to_entry.entry.get().strip():
            params["date_to"] = self.date_to_entry.entry.get().strip()
        if self.rm_codes_combobox.get() != "All":
            params["rm_code"] = self.rm_codes_combobox.get()
        if self.warehouse_combobox.get() != "All":
            params["warehouse"] = self.warehouse_combobox.get()
        if self.status_combobox.get() != "All":
            params["status"] = self.status_combobox.get()
        if self.document_type_combobox.get() != "All":
            params["document_type"] = self.document_type_combobox.get()
        return params

    def load_data(self):
        url = server_ip + "/api/reports/v1/form-entries/"
        params = self.get_api_params()
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            self.tree.delete(*self.tree.get_children())
            for item in data:
                self.tree.insert("", END, values=(
                    datetime.fromisoformat(item["date_encoded"]).strftime("%m/%d/%Y"),
                    datetime.fromisoformat(item["date_reported"]).strftime("%m/%d/%Y"),
                    item["document_type"], item["document_number"], item["mat_code"],
                    item["qty"], item["whse_no"], item["status"]
                ))
        except requests.RequestException as e:
            messagebox.showerror("Error", str(e))

    def export_filtered_api_response(self):
        url = server_ip + "/api/reports/v1/form-entries/"
        params = self.get_api_params()
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            records = [[
                datetime.fromisoformat(item["date_encoded"]).strftime("%m/%d/%Y"),
                datetime.fromisoformat(item["date_reported"]).strftime("%m/%d/%Y"),
                item["document_type"], item["document_number"], item["mat_code"],
                item["qty"], item["whse_no"], item["status"]
            ] for item in data]

            df = pd.DataFrame(records, columns=["Date Encoded", "Date Reported", "Document Type", "Document No.", "Rar Material", "QTY", "Location", "Status"])
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
            if file_path:
                df.to_excel(file_path, index=False)
                messagebox.showinfo("Success", f"File exported to {file_path}")
        except requests.RequestException as e:
            messagebox.showerror("Error", str(e))

    def sort_treeview(self, col, reverse):
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        items.sort(reverse=reverse)
        for index, (val, k) in enumerate(items):
            self.tree.move(k, "", index)
        self.tree.heading(col, command=lambda: self.sort_treeview(col, not reverse))
