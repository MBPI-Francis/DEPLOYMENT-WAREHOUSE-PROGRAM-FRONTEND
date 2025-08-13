import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import requests
from backend.settings.database import server_ip
from .table import RMSummaryTable
from frontend.forms.shared import SharedFunctions

# Try to import win32com.client for full workbook encryption
try:
    import win32com.client as win32
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    # Messagebox.show_warning(
    #     "pywin32 library not found. Full workbook encryption will not be available. "
    #     "Only sheet protection will be applied (if password is set). "
    #     "Install with: pip install pywin32",
    #     "Library Missing"
    # )




def entry_fields(note_form_tab):
    shared_functions = SharedFunctions()

    # Create a frame for the form inputs
    form_frame = ttk.Frame(note_form_tab)
    form_frame.pack(fill=X, pady=10, padx=20)

    # Calling the table
    note_table = RMSummaryTable(note_form_tab)



def get_soh_data():

    """Fetch data from API and format for table rowdata."""
    url = f"{server_ip}/api/get/new_soh/"
    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        return []

    # Return both buttons as a tuple
    return []







