import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from frontend.stock_on_hand.main_tab import beginning_balance_tab
from frontend.stock_on_hand.historical_data.main_tab import historical_data_tab

class StockOnHandView:
    def __init__(self, parent):
        self.parent = parent

    def show(self):
        """Display the content."""

        soh_frame = ttk.Frame(self.parent)
        soh_frame.grid(row=0, column=0, sticky=N + S + E + W)

        # Add widgets inside the soh_frame
        label = ttk.Label(soh_frame,
            text = "Latest Stocks of Raw Materials",
            font = ("Arial", 14, "bold")
        )
        label.grid(row=0, column=0, sticky="nsew")

        # Create the Notebook widget
        notebook = ttk.Notebook(soh_frame)
        notebook.grid(row=1, column=0, sticky=N + S + E + W, padx=10, pady=10)  # Use grid instead of pack

        # Create the frames for each tab
        beginning_balance_tab(notebook)
        historical_data_tab(notebook)

         # Configure rows and columns to be responsive
        soh_frame.grid_rowconfigure(0, weight=0)  # Label row does not resize
        soh_frame.grid_rowconfigure(1, weight=1)  # Content row should resize

        soh_frame.grid_columnconfigure(0, weight=1)  # Make column 0 responsive


