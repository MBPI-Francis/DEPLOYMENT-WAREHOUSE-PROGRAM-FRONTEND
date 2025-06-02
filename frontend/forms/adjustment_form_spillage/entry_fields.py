import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import requests
from backend.settings.database import server_ip
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.dialogs.dialogs import Messagebox
from datetime import datetime, timedelta
from .table import AdjustmentFormTable
from .validation import EntryValidation
from ..shared import SharedFunctions
from tkinter import StringVar

def entry_fields(note_form_tab):

    # Instantiate the shared_function class
    shared_functions = SharedFunctions()

    get_status_api = shared_functions.get_status_api()
    get_warehouse_api = shared_functions.get_warehouse_api()
    get_rm_code_api = shared_functions.get_rm_code_api(force_refresh=True)
    


    adjustment_form_table = AdjustmentFormTable(note_form_tab)







