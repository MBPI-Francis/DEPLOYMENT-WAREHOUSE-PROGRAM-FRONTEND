import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .change_status_form.main_tab import held_form_tab
from .notes_form.main_tab import notes_form_tab
from .transfer_form.main_tab import transfer_form_tab
from .preparation_form.main_tab import preparation_form_tab
from .outgoing_form.main_tab import outgoing_form_tab
from .receiving_form.main_tab import receiving_report_tab

class HistoricalDataView:
    def __init__(self, parent):
        self.parent = parent

    def show(self):
        """Display the Raw Material content."""
        historical_data_frame = ttk.Frame(self.parent)
        historical_data_frame.grid(row=0, column=0, sticky=N + S + E + W)

        # Add widgets inside the historical_data_frame
        label = ttk.Label(historical_data_frame,
                          text="Historical Data",
                          font=("Arial", 14, "bold")
                          )
        label.grid(row=0, column=0, sticky="nsew")
        
        
        
        # Create the Notebook widget
        notebook = ttk.Notebook(historical_data_frame)
        # notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)
        notebook.grid(row=1, column=0, sticky=N + S + E + W, padx=10, pady=10)  # Use grid instead of pack

        # Create the frames for each tab
        notes_form_tab(notebook)
        receiving_report_tab(notebook)
        outgoing_form_tab(notebook)
        transfer_form_tab(notebook)
        preparation_form_tab(notebook)
        held_form_tab(notebook)


         # Configure rows and columns to be responsive
        historical_data_frame.grid_rowconfigure(0, weight=0)  # Label row does not resize
        historical_data_frame.grid_rowconfigure(1, weight=1)  # Content row should resize

        historical_data_frame.grid_columnconfigure(0, weight=1)  # Make column 0 responsive