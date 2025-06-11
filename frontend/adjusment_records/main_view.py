import ttkbootstrap as ttk
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from .iaf_entries.main_tab import entries_tab
from .iaf_spillage.main_tab import spillage_tab




class AdjustmentFormRecordsView:
    def __init__(self, parent):
        self.parent = parent

    def show(self):
        """Display the Raw Material content."""
        adjustment_form_frame = ttk.Frame(self.parent)
        adjustment_form_frame.grid(row=0, column=0, sticky=N + S + E + W)

        # Add widgets inside the adjustment_form_frame
        label = ttk.Label(adjustment_form_frame,
            text = "Inventory Adjustment Form Records",
            font = ("Arial", 14, "bold")
        )
        label.grid(row=0, column=0, sticky="nsew")
        



        # Create the Notebook widget
        notebook = ttk.Notebook(adjustment_form_frame)
        # notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)
        notebook.grid(row=1, column=0, sticky=N + S + E + W, padx=10, pady=10)  # Use grid instead of pack

        # Create the frames for each tab
        entries_tab(notebook)
        spillage_tab(notebook)


         # Configure rows and columns to be responsive
        adjustment_form_frame.grid_rowconfigure(0, weight=0)  # Label row does not resize
        adjustment_form_frame.grid_rowconfigure(1, weight=1)  # Content row should resize

        adjustment_form_frame.grid_columnconfigure(0, weight=1)  # Make column 0 responsive