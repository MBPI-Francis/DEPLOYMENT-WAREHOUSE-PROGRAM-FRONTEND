import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class UserView:
    def __init__(self, parent):
        self.parent = parent

    def show(self):
        """Display the User content."""
        label = ttk.Label(
            self.parent,
            text="User Content",
            font=("Helvetica", 18),
            bootstyle=INFO,
        )
        label.pack(pady=20)
