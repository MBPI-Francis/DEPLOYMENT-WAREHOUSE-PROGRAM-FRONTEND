
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .entry_fields import entry_fields
import requests
from backend.settings.database import server_ip
from ttkbootstrap.tooltip import ToolTip
from frontend.warehouse.generate_warehouse.confirm_messages import ConfirmationMessage


def warehouse_tab(notebook):
    url = server_ip + "/api/warehouses/v1/transformed_list/"
    response = requests.get(url)
    response.raise_for_status()
    warehouse_records = response.json()

    warehouse_tab = ttk.Frame(notebook)
    notebook.add(warehouse_tab, text="Warehouses")
    # Populate the Raw Materials Tab
    warehouse_label = ttk.Label(
        warehouse_tab,
        text="Warehouses",
        font=("Helvetica", 14, 'bold'),
        bootstyle=PRIMARY,
    )
    warehouse_label.pack(pady=(20,0), padx=20)

    if warehouse_records:
        status_label = ttk.Label(
            warehouse_tab,
            text="The warehouses listed below are essential for the system's functionality. Modifying them may lead to errors.",
            font=("Helvetica", 10),
            bootstyle=SECONDARY
        )
        status_label.pack(pady=0, padx=20)

    else:
        status_label = ttk.Label(
            warehouse_tab,
            text="Click the 'Generate all the required Warehouses' button to generate warehouses automatically.",
            font=("Helvetica", 10),
            bootstyle=SECONDARY
        )
        status_label.pack(pady=0, padx=20)



    btn_generate = ttk.Button(
        warehouse_tab,
        text="Generate all the required Warehouses",
        bootstyle=WARNING,
        command=lambda: ConfirmationMessage(warehouse_tab).show_confirmation_message()
    )
    btn_generate.pack(pady=(30, 0), padx=(12, 0), anchor="w")  # Use pack() instead of grid()


    if warehouse_records:
        btn_generate.configure(state="disabled")
        ToolTip(btn_generate, text="You can't generate new warehouses because warehouses already exist.")

    else:
        ToolTip(btn_generate, text="Click to generate the required warehouses.")

    entry_fields(warehouse_tab)

