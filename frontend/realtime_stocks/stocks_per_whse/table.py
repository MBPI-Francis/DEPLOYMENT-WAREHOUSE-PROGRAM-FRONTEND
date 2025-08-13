# table.py

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import requests
from ttkbootstrap.dialogs import Messagebox
from backend.settings.database import server_ip
from tkinter import messagebox
from ttkbootstrap.tooltip import ToolTip


class StocksPerWHSE:
    # The 'root' parameter will now be the main notebook from ConsumptionEntryView
    def __init__(self, main_notebook):
        self.main_notebook = main_notebook
        self.original_data = {}
        self.tabs = {}

        # --- KEY CHANGE ---
        # Instead of creating its own notebook, this class will now
        # add its tabs directly to the main_notebook it received.

        # 1. Define the warehouses you want to create tabs for.
        warehouses = ["Warehouse #1", "Warehouse #2", "Warehouse #4"]

        # 2. Loop through the warehouses and create a tab for each one
        for wh_name in warehouses:
            # Create a frame that will be the content of the tab
            tab_frame = ttk.Frame(self.main_notebook)

            # Add this frame as a new tab to the main notebook
            self.main_notebook.add(tab_frame, text=wh_name)

            # Use the helper function to fill the tab with widgets (search, table, etc.)
            widgets = self.create_warehouse_tab(tab_frame, wh_name)
            self.tabs[wh_name] = widgets

        # 3. Load the initial data into the newly created tables
        self.refresh_all_tables()

    def create_warehouse_tab(self, parent_tab, warehouse_name):
        """Helper function to create the widgets for a single warehouse tab. (This function remains the same)"""

        # Populate the Raw Materials Tab
        submit_entries_label = ttk.Label(
            parent_tab,
            text=f"This table provides real-time updates on the daily stock of raw materials for {warehouse_name}",
            font=("Arial", 14, "bold"),
            bootstyle=PRIMARY,
        )
        submit_entries_label.pack(pady=(10, 0), padx=20)

        # Frame for search and buttons
        search_frame = ttk.Frame(parent_tab)
        search_frame.pack(fill=X, padx=10, pady=(20, 0))

        ttk.Label(search_frame, text="Search:", style="CustomLabel.TLabel").pack(side=LEFT, padx=(0, 5))

        search_entry = ttk.Entry(search_frame, width=50)
        search_entry.pack(side=LEFT)

        search_entry.bind("<Return>", lambda event, wh=warehouse_name: self.search_data(event, wh))

        btn_refresh = ttk.Button(
            search_frame,
            text="Refresh",
            command=self.refresh_all_tables,
            bootstyle=SECONDARY,
        )
        btn_refresh.pack(side=RIGHT, padx=10)
        ToolTip(btn_refresh, text="Click to refresh data for all warehouses.")

        # Frame for the Treeview and scrollbars
        tree_frame = ttk.Frame(parent_tab)
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=5)

        columns = ("Raw Material", "Warehouse Name", "Ending Balance", "Status")

        tree = ttk.Treeview(
            master=tree_frame,
            columns=columns,
            show='headings',
            style="Custom.Treeview",
            bootstyle=PRIMARY
        )

        tree_scroll_y = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=tree.yview)
        tree_scroll_y.pack(side=RIGHT, fill=Y)
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=HORIZONTAL, command=tree.xview)
        tree_scroll_x.pack(side=BOTTOM, fill=X)

        tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

        for col in columns:
            tree.heading(col, text=col, anchor=W, command=lambda c=col, t=tree: self.sort_treeview(c, t, False))
            tree.column(col, width=150, anchor=W)

        tree.pack(fill=BOTH, expand=YES)

        return {"tree": tree, "search_entry": search_entry}

    # The rest of the methods (fetch_data, refresh_all_tables, sort_treeview, search_data)
    # remain unchanged as their logic is correct.
    def fetch_data(self):
        """Fetch all data from the API."""
        url = server_ip + "/api/get/new_soh/with_zero/"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            Messagebox.showerror("API Error", "Failed to fetch data from the server.")
            return []

    def refresh_all_tables(self):
        """Fetch fresh data and populate all warehouse tables."""
        all_data = self.fetch_data()

        for wh_name, widgets in self.tabs.items():
            widgets["tree"].delete(*widgets["tree"].get_children())
            self.original_data[wh_name] = []

            warehouse_specific_data = [item for item in all_data if item["warehousename"] == wh_name]

            for item in warehouse_specific_data:
                record = (
                    item["rmcode"],
                    item["warehousename"],
                    "{:,.2f}".format(float(item["new_beginning_balance"])),
                    item["status"],
                )
                self.original_data[wh_name].append(record)
                widgets["tree"].insert("", END, values=record)

    def sort_treeview(self, col, tree, reverse):
        """Sort a specific treeview's column data."""
        items = [(tree.set(k, col), k) for k in tree.get_children('')]
        items.sort(reverse=reverse)
        for index, (val, k) in enumerate(items):
            tree.move(k, "", index)
        tree.heading(col, command=lambda: self.sort_treeview(col, tree, not reverse))

    def search_data(self, event, warehouse_name):
        """Filter data for the specified warehouse tab."""
        widgets = self.tabs[warehouse_name]
        tree = widgets["tree"]
        search_entry = widgets["search_entry"]
        search_term = search_entry.get().strip().lower()

        tree.delete(*tree.get_children())

        if not search_term:
            for record in self.original_data[warehouse_name]:
                tree.insert("", END, values=record)
            return

        filtered_data = [
            record for record in self.original_data[warehouse_name]
            if any(search_term in str(value).lower() for value in record)
        ]

        if filtered_data:
            for record in filtered_data:
                tree.insert("", END, values=record)
        else:
            messagebox.showinfo("Search", "No matching record found in this warehouse.")