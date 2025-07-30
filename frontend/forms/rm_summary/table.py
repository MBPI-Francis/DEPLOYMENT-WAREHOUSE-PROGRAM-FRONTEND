import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import requests
from ttkbootstrap.dialogs import Messagebox
from backend.settings.database import server_ip
from tkinter import Toplevel, messagebox
from datetime import datetime
from ttkbootstrap.tooltip import ToolTip
import pandas as pd


class RMSummaryTable:
    def __init__(self, root):
        self.root = root
        self.raw_api_data = []  # <-- 1. To store the original, unsummarized data

        # Frame for search
        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill=X, padx=10, pady=(0, 0))

        ttk.Label(search_frame, text="Search:", style="CustomLabel.TLabel").pack(side=LEFT, padx=(0, 5))

        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side=LEFT)
        self.search_entry.bind("<Return>", self.search_data)

        # --- 2. New label to display the search summary ---
        self.summary_label = ttk.Label(search_frame, text="", font=("Helvetica", 9, "bold"))
        self.summary_label.pack(side=LEFT, padx=(10, 0))
        # --- End of new feature ---

        # Add button to refresh data
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
        tree_frame.pack(fill=BOTH, expand=YES, padx=10, pady=(5, 0))

        self.columns = (
            "Raw Material",
            "Total Ending Balance",
            "Status",
        )

        self.tree = ttk.Treeview(
            master=tree_frame,
            columns=self.columns,
            show='headings',
            style="Custom.Treeview",
            bootstyle=PRIMARY
        )

        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=self.tree.yview)
        tree_scroll_y.pack(side=RIGHT, fill=Y)
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=HORIZONTAL, command=self.tree.xview)
        tree_scroll_x.pack(side=BOTTOM, fill=X)

        self.tree.pack(fill=BOTH, expand=YES)
        self.tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)

        for col in self.columns:
            self.tree.heading(col, text=col, command=lambda _col=col: self.sort_treeview(_col, False), anchor=W)
            self.tree.column(col, anchor=W, width=150)

        self.refresh_table()

    def fetch_data(self):
        """Fetch data from API."""
        url = server_ip + "/api/get/new_soh/with_zero/"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            Messagebox.show_error("Data Fetch Error",
                                  "Failed to retrieve data from the server. Please check your connection.")
            return []

    def refresh_table(self):
        """Fetch, summarize, and refresh Treeview with data."""
        self.tree.delete(*self.tree.get_children())
        self.original_data = []
        self.search_entry.delete(0, END)
        self.summary_label.config(text="")  # Clear summary on refresh

        # 3. Store raw data before it gets summarized
        self.raw_api_data = self.fetch_data()
        if not self.raw_api_data:
            return

        df = pd.DataFrame(self.raw_api_data)
        df['new_beginning_balance'] = pd.to_numeric(df['new_beginning_balance'], errors='coerce').fillna(0)

        summarized_df = df.groupby(['rmcode', 'status'])['new_beginning_balance'].sum().reset_index()

        for index, row in summarized_df.iterrows():
            record = (
                row["rmcode"],
                "{:,.2f}".format(row["new_beginning_balance"]),
                row["status"],
            )
            self.original_data.append(record)
            self.tree.insert("", END, values=record)

    def sort_treeview(self, col, reverse):
        """Sort treeview column data."""
        if col == "Total Ending Balance":
            items = [(float(self.tree.set(k, col).replace(',', '')), k) for k in self.tree.get_children('')]
        else:
            items = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]

        items.sort(reverse=reverse)
        for index, (val, k) in enumerate(items):
            self.tree.move(k, "", index)
        self.tree.heading(col, command=lambda: self.sort_treeview(col, not reverse))

    # --- 4. Heavily modified search function ---
    def search_data(self, event=None):
        """Filter records by RM Code and show a total summary for that RM."""
        search_term = self.search_entry.get().strip().lower()

        # Clear previous results and summary
        self.tree.delete(*self.tree.get_children())
        self.summary_label.config(text="")

        if not search_term:
            self.populate_treeview(self.original_data)
            return

        # --- Logic for calculating and displaying the total summary ---
        # Use the unsummarized raw data for an accurate total across all statuses/locations
        if self.raw_api_data:
            df = pd.DataFrame(self.raw_api_data)
            df['new_beginning_balance'] = pd.to_numeric(df['new_beginning_balance'], errors='coerce').fillna(0)

            # Filter for rows matching the searched RM Code
            rm_code_matches = df[df['rmcode'].str.lower() == search_term]

            # If matches are found, it's a valid RM Code search
            if not rm_code_matches.empty:
                total_sum = rm_code_matches['new_beginning_balance'].sum()
                # Update the summary label
                summary_text = f"Total for {search_term.upper()} = {total_sum:,.2f} KG"
                self.summary_label.config(text=summary_text, bootstyle="SUCCESS")

                # Added the font argument to make the text bigger and bold
                self.summary_label.config(
                    text=summary_text,
                    bootstyle="SUCCESS",
                    font=("Helvetica", 11, "bold") # <-- Added this line
                )

        # --- Logic for filtering the Treeview ---
        # Only show results if the search term is a specific RM Code
        # This prevents showing results when searching for a status or quantity
        filtered_data = [
            record for record in self.original_data
            if search_term == str(record[0]).lower()  # Match only the RM Code column
        ]

        if filtered_data:
            self.populate_treeview(filtered_data)
        else:
            # If nothing is found, the tree remains empty
            messagebox.showinfo("Search", f"No record found for RM Code: '{search_term}'")

    def populate_treeview(self, data):
        """Helper function to insert data into the Treeview."""
        self.tree.delete(*self.tree.get_children())
        for record in data:
            self.tree.insert("", END, values=record)