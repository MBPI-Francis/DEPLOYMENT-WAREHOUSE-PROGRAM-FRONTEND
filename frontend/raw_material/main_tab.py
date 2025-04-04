
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .entry_fields import entry_fields
from ttkbootstrap.tableview import Tableview
import requests
from backend.settings.database import server_ip
from datetime import datetime
from ttkbootstrap.tooltip import ToolTip
from frontend.raw_material.generate_rawmaterial.confirm_messages import ConfirmationMessage


def rm_code_tab(notebook):


    url = server_ip + "/api/raw_materials/v1/transformed_list/"
    response = requests.get(url)
    response.raise_for_status()

    raw_material_records = response.json()
        
        
    raw_material_tab = ttk.Frame(notebook)
    notebook.add(raw_material_tab, text="Raw Materials")
    # Populate the Raw Materials Tab
    raw_material_label = ttk.Label(
        raw_material_tab,
        text="Raw Materials",
        font=("Arial", 14, "bold"),
        bootstyle=PRIMARY,
    )
    raw_material_label.pack(pady=(20,0), padx=20)
    
    if raw_material_records:
        status_label = ttk.Label(
            raw_material_tab,
            text="The raw material codes listed below are essential for the system's functionality. Modifying them may lead to errors.",
            font=("Arial", 11, "bold"),
            bootstyle=SECONDARY
        )
        status_label.pack(pady=0, padx=20)

    else:
        status_label = ttk.Label(
            raw_material_tab,
            text="Click the 'Generate all the required raw material codes' button to generate raw material codes automatically.",
            font=("Arial", 11, "bold"),
            bootstyle=SECONDARY
        )
        status_label.pack(pady=0, padx=20)



    btn_generate = ttk.Button(
        raw_material_tab,
        text="Generate all the required raw material codes",
        bootstyle=WARNING,
        command=lambda: ConfirmationMessage(raw_material_tab).show_confirmation_message()
    )
    btn_generate.pack(pady=(30, 0), padx=(12, 0), anchor="w")  # Use pack() instead of grid()


    if raw_material_records:
        btn_generate.configure(state="disabled")
        ToolTip(btn_generate, text="Raw material codes have already been generated. You can only generate them once.")

    else:
        ToolTip(btn_generate, text="Click to generate the required raw material codes.")
    
    
    entry_fields(raw_material_tab)




