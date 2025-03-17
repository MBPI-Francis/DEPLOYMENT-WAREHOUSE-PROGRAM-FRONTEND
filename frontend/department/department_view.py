import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class DepartmentView:
    def __init__(self, parent):
        self.parent = parent

    def show(self):
        """Display the Department content."""
        label = ttk.Label(
            self.parent,
            text="Department Content",
            font=("Helvetica", 18),
            bootstyle=SUCCESS,
        )
        label.pack(pady=20)
