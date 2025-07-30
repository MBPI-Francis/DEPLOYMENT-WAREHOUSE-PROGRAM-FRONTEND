import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import requests
from ttkbootstrap.dialogs import Messagebox
from backend.settings.database import server_ip
from tkinter import Toplevel, messagebox
from datetime import datetime
from ttkbootstrap.tooltip import ToolTip


class StocksPerWHSE:
    def __init__(self, root):
        self.root = root
        self.original_data = {}  # <-- 1. Dictionary to store data for each warehouse

        # --- 2. Create the main notebook for the tabs ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=BOTH, expand=YES, padx=10, pady=5)

        # --- 3. Define the warehouses and create a tab for each one ---
        warehouses = ["Warehouse #1", "Warehouse #2", "Warehouse #4"]
        self.tabs = {}  # To hold widgets for each tab

        for wh_name in warehouses:
            # Create a dedicated frame for the tab's content
            tab_frame = ttk.Frame(self.notebook)
            self.notebook.add(tab_frame, text=wh_name)

            # Use a helper function to create the content for each tab
            widgets = self.create_warehouse_tab(tab_frame, wh_name)
            self.tabs[wh_name] = widgets

        # Initial data load
        self.refresh_all_tables()

    def create_warehouse_tab(self, parent_tab, warehouse_name):
        """Helper function to create the widgets for a single warehouse tab."""

        # Frame for search and buttons
        search_frame = ttk.Frame(parent_tab)
        search_frame.pack(fill=X, padx=10, pady=(5, 0))

        ttk.Label(search_frame, text="Search:", style="CustomLabel.TLabel").pack(side=LEFT, padx=5)

        search_entry = ttk.Entry(search_frame, width=50)
        search_entry.pack(side=LEFT)

        # --- 4. Bind the search function with the specific warehouse name ---
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

        # Return a dictionary of the created widgets for this tab
        return {"tree": tree, "search_entry": search_entry}

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

    # --- 5. Modified refresh method to handle all tables ---
    def refresh_all_tables(self):
        """Fetch fresh data and populate all warehouse tables."""
        all_data = self.fetch_data()

        for wh_name, widgets in self.tabs.items():
            # Clear existing data in the tree and original data storage
            widgets["tree"].delete(*widgets["tree"].get_children())
            self.original_data[wh_name] = []

            # Filter data for the current warehouse
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

    # --- 6. Unified search function that works for the correct tab ---
    def search_data(self, event, warehouse_name):
        """Filter data for the specified warehouse tab."""
        widgets = self.tabs[warehouse_name]
        tree = widgets["tree"]
        search_entry = widgets["search_entry"]
        search_term = search_entry.get().strip().lower()

        tree.delete(*tree.get_children())

        if not search_term:
            # If search is empty, reload original data for that tab
            for record in self.original_data[warehouse_name]:
                tree.insert("", END, values=record)
            return

        # Filter and display matching records
        filtered_data = [
            record for record in self.original_data[warehouse_name]
            if any(search_term in str(value).lower() for value in record)
        ]

        if filtered_data:
            for record in filtered_data:
                tree.insert("", END, values=record)
        else:
            messagebox.showinfo("Search", "No matching record found in this warehouse.")