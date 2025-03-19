import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog, Toplevel
from ttkbootstrap import ttk
import requests
import threading
from ttkbootstrap.dialogs import Messagebox
from backend.settings.database import server_ip
from frontend.stock_on_hand.table import BeginningBalanceTable
import os


class ImportData:
    def __init__(self, root):
        self.root = root
        self.loader_window = None  # Loader window reference

    # def import_data(self):
    #     """Handles file selection and starts the import process."""
    #     file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    #
    #     print(file_path)
    #
    #     if not file_path:
    #         messagebox.showwarning("Warning", "No file selected.")
    #         # print("No file selected.")
    #         return
    #
    #     # Show loader while uploading
    #     self.root.after(0, self.show_loader)
    #
    #     # Run API request in a separate thread
    #     thread = threading.Thread(target=self.upload_file, args=(file_path,))
    #     thread.start()

    def import_data(self):
        """Handles file selection and starts the import process."""
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])

        if not file_path:
            messagebox.showwarning("Warning", "No file selected.")
            return

        # Fix network path format
        if file_path.startswith("//"):
            file_path = file_path.replace("/", "\\")  # Convert to UNC path correctly

        print(f"Selected file: {file_path}")  # Debugging

        try:
            # Show loader while uploading
            self.root.after(0, self.show_loader)

            # Run API request in a separate thread
            thread = threading.Thread(target=self.upload_file, args=(file_path,))
            thread.daemon = True
            thread.start()

        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")

    def upload_file(self, file_path):
        """Uploads the file to the FastAPI backend."""
        url = f"{server_ip}/api/rm_stock_on_hand/v1/import_stock_data/"

        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                response = requests.post(url, files=files)

            # Hide loader from the main thread
            self.root.after(0, self.hide_loader)

            if response.status_code == 200:
                self.root.after(0, lambda: messagebox.showinfo("Success", "File uploaded successfully!"))

            else:
                error_message = response.json().get("detail", "Unknown error")
                self.root.after(0, lambda: messagebox.showerror("Error",
                    f"Failed to import data. {error_message}"))


        except Exception as e:
            self.root.after(0, self.hide_loader)
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error during file upload: {e}"))

    def show_loader(self):
        """Creates a popup message box with a progress loader."""
        self.loader_window = Toplevel(self.root)
        self.loader_window.title("Processing...")
        self.loader_window.geometry("250x100")
        self.loader_window.resizable(False, False)
        self.loader_window.attributes("-topmost", True)

        # Get screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate position for centering
        x = (screen_width // 2) - (250 // 2)  # Center horizontally
        y = (screen_height // 2) - (100 // 2)  # Center vertically

        # Set window position
        self.loader_window.geometry(f"250x100+{x}+{y}")

        ttk.Label(self.loader_window, text="Processing, please wait...", bootstyle="primary").pack(pady=10)
        progress_bar = ttk.Progressbar(self.loader_window, mode="indeterminate", length=200, bootstyle="info")
        progress_bar.pack(pady=10)
        progress_bar.start()

    def hide_loader(self):
        """Closes the loader window."""
        if self.loader_window:
            self.loader_window.destroy()
            self.loader_window = None
