import ttkbootstrap as ttk
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.constants import *
from frontend.status.shared import status_api
from datetime import datetime


class StatusTable:

    def __init__(self, root):
        self.note_form_tab = root

        self.coldata = [
            # {"text": "ID", "stretch": True, "anchor": "w"},
            {"text": "Status Name", "stretch": True, "anchor": "w"},
            {"text": "Created by", "stretch": True},
            {"text": "Date Created", "stretch": True}
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
        # Format data for the table
        status_records = status_api()
        rowdata = [
            (
                # item["id"],
                item["name"],
                item["created_by"],
                datetime.fromisoformat(item["created_at"]).strftime("%m/%d/%Y %I:%M %p")
            )
            for item in status_records
        ]
        return rowdata


    def refresh_table(self):
        """Refresh the table with updated data."""
        self.rowdata = self.fetch_and_format_data()
        self.table.build_table_data(
            coldata=self.coldata,
            rowdata=self.rowdata
        )
        self.table.goto_last_page()

