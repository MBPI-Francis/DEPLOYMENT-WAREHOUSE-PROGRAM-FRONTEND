from backend.settings.database import server_ip
import requests
from tkinter import messagebox



def status_api():
    url = server_ip + "/api/status/v1/transformed_list/"
    try:
        response = requests.get(url)

        if response.status_code == 200:
            status_records = response.json()
            return status_records
        else:
            status_records = []
            messagebox.showerror("Error",f"Failed to access the API endpoint: {url}. Status code: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Error during: {e}")

    return []