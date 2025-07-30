import ttkbootstrap as ttk
from ttkbootstrap import Style
from ttkbootstrap.constants import *

from .rm_summary.main_tab import rm_summary_tab
from .stocks_per_whse.main_tab import stock_per_whse_tab
from .adjustment_form_spillage.main_tab import adjustment_form_tab



class ConsumptionEntryView:
    def __init__(self, parent):
        self.parent = parent

    def show(self):
        """Display the Raw Material content."""
        consumption_entry_frame = ttk.Frame(self.parent)
        consumption_entry_frame.grid(row=0, column=0, sticky=N + S + E + W)

        # Add widgets inside the consumption_entry_frame
        label = ttk.Label(consumption_entry_frame,
            text = "Real-Time Inventory Changes – Raw Materials",
            font = ("Arial", 14, "bold")
        )
        label.grid(row=0, column=0, sticky="nsew")
        



        # Create the Notebook widget
        notebook = ttk.Notebook(consumption_entry_frame)
        # notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)
        notebook.grid(row=1, column=0, sticky=N + S + E + W, padx=10, pady=10)  # Use grid instead of pack

        rm_summary_tab(notebook)
        stock_per_whse_tab(notebook)



         # Configure rows and columns to be responsive
        consumption_entry_frame.grid_rowconfigure(0, weight=0)  # Label row does not resize
        consumption_entry_frame.grid_rowconfigure(1, weight=1)  # Content row should resize

        consumption_entry_frame.grid_columnconfigure(0, weight=1)  # Make column 0 responsive