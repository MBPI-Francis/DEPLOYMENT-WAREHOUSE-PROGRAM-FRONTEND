import ttkbootstrap as ttk
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.constants import *
import requests
from backend.settings.database import server_ip
from datetime import datetime


class BeginningBalanceTable:

    def __init__(self, root):
        self.note_form_tab = root

        self.coldata = [
            {"text": "Raw Material Code", "stretch": True, "anchor": "w"},
            {"text": "Warehouse", "stretch": True},
            {"text": "Stocks", "stretch": True},
            {"text": "Status", "stretch": True},
            {"text": "Date Created", "stretch": True},
            {"text": "Date Computed", "stretch": True},
        ]
        self.rowdata = self.fetch_and_format_data()

        # Create Tableview
        self.table = Tableview(
            master=self.note_form_tab,
            coldata=self.coldata,
            rowdata=self.rowdata,
            paginated=True,
            searchable=True,
            bootstyle=PRIMARY,
            pagesize=20,
            autofit=True,  # Auto-size columns
            autoalign=False,  # Auto-align columns based on data
        )
        self.table.pack(fill=BOTH, expand=YES, padx=10, pady=10)

    def fetch_and_format_data(self):
        """Fetch data from API and format for table rowdata."""
        url = server_ip + "/api/get/beginning_balance/"
        try:
            response = requests.get(url)
            response.raise_for_status()

            data = response.json()

            # Format data for the table
            rowdata = [
                (
                    item["rmcode"],
                    item["warehousename"],
                    "{:,.2f}".format(float(item["beginningbalance"])),  # Format with commas
                    item["statusname"],
                    datetime.fromisoformat(item["stockchangedate"]).strftime("%m/%d/%Y %I:%M %p"),
                    datetime.fromisoformat(item["date_computed"]).strftime("%m/%d/%Y"),
                )
                for item in data
            ]
            return rowdata
        except requests.exceptions.RequestException as e:
            return []

    def refresh_table(self):
        """Refresh the table with updated data."""
        self.rowdata = self.fetch_and_format_data()
        self.table.build_table_data(
            coldata=self.coldata,
            rowdata=self.rowdata
        )
        self.table.goto_last_page()


