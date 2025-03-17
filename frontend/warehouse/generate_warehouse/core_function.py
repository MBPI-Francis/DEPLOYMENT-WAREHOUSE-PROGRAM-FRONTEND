import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog, Toplevel
from ttkbootstrap import ttk
import requests
from ttkbootstrap.dialogs import Messagebox
from backend.settings.database import server_ip

class GenerateWarehouse:
    def __init__(self, root):
        self.root = root
        self.loader_window = None  # Loader window reference

    def generate_warehouse(self):

        warehouses = [
            {
                "wh_number": 1,
                "wh_name": "Warehouse #1",
            },
            {
                "wh_number": 2,
                "wh_name": "Warehouse #2",
            },
            {
                "wh_number": 4,
                "wh_name": "Warehouse #4",
            }
        ]

        url = f"{server_ip}/api/warehouses/v1/create/"
        try:
            for warehouse in warehouses:

                response = requests.post(url, json=warehouse)
                if response.status_code == 200:
                    pass

                else:
                    break

            messagebox.showinfo("Success message", f"The warehouses is successfully generated.")


        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Error during: {e}")


