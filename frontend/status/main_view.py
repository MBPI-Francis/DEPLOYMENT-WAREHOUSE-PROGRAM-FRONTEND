

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .main_tab import status_tab

class StatusView:
    def __init__(self, parent):
        self.parent = parent

    def show(self):
        """Display the Raw Material content."""

        # Create the Notebook widget
        notebook = ttk.Notebook(self.parent)
        notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Create the frames for each tab
        status_tab(notebook)


