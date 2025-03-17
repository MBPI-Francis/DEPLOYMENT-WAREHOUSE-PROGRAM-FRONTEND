import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog, Toplevel
from ttkbootstrap import ttk
import requests
from ttkbootstrap.dialogs import Messagebox
from backend.settings.database import server_ip

class GenerateStatus:
    def __init__(self, root):
        self.root = root
        self.loader_window = None  # Loader window reference

    def generate_status(self):
        statuses = ["good", "held : under evaluation", "held : contaminated", "held : reject"]

        url = f"{server_ip}/api/status/v1/create/"

        try:
            for status in statuses:
                data = { "name": status }
                response = requests.post(url, json=data)
                if response.status_code == 200:
                    pass

                else:
                    break

            messagebox.showinfo("Success message", f"The following status is successfully genereated:\n"
                                                   f"-   {statuses[0]}\n"
                                                   f"-   {statuses[1]}\n"
                                                   f"-   {statuses[2]}\n"
                                                   f"-   {statuses[3]}")

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Error during: {e}")


