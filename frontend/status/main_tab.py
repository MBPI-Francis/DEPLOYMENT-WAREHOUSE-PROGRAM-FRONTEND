
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from .table import StatusTable
from frontend.status.shared import status_api
from frontend.status.generate_status.confirm_messages import ConfirmationMessage
import requests

def status_tab(notebook):
    status_records = status_api()
    status_tab = ttk.Frame(notebook)
    notebook.add(status_tab, text="Statuses")
    # Populate the Raw Materials Tab
    status_label = ttk.Label(
        status_tab,
        text="List of Status",
        font=("Arial", 14, "bold"),
        bootstyle=PRIMARY,
    )
    status_label.pack(pady=(20,0), padx=20)


    if status_records:
        status_label = ttk.Label(
            status_tab,
            text="The statuses listed below are essential for the system's functionality. Modifying them may lead to errors.",
            font=("Arial", 10),
            bootstyle=SECONDARY
        )
        status_label.pack(pady=0, padx=20)

    else:
        status_label = ttk.Label(
            status_tab,
            text="Click the 'Generate all the required Statuses' button to generate statuses automatically.",
            font=("Arial", 10),
            bootstyle=SECONDARY
        )
        status_label.pack(pady=0, padx=20)


    btn_generate = ttk.Button(
        status_tab,
        text="Generate all the required Statuses",
        bootstyle=WARNING,
        command=lambda: ConfirmationMessage(status_tab).show_confirmation_message()
    )
    btn_generate.pack(pady=(30,0), padx=(12, 0), anchor="w")  # Use pack() instead of grid()


    if status_records:
        btn_generate.configure(state="disabled")
        ToolTip(btn_generate, text="You can't generate new statuses because statuses already exist.")

    else:
        ToolTip(btn_generate, text="Click to generate the required statuses.")


    # Calling the table
    status_table = StatusTable(status_tab)


