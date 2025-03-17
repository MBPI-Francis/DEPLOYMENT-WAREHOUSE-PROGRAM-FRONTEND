import tkinter as tk
from tkinter import messagebox, filedialog, Toplevel
from ttkbootstrap import ttk
import requests
import threading
from backend.settings.database import server_ip

class GenerateRawMaterial:
    def __init__(self, root):
        self.root = root
        self.loader_window = None  # Loader window reference

    def generate_raw_material(self):
        """Handles file selection and starts the import process."""
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])

        if not file_path:
            messagebox.showwarning("Warning", "No file selected.")
            return

        # Ensure the file is an Excel file
        if not file_path.endswith(".xlsx"):
            messagebox.showerror("Error", "Invalid file type. Please upload an Excel (.xlsx) file.")
            return

        # Show loader while uploading
        self.root.after(0, self.show_loader)

        # Run API request in a separate thread
        thread = threading.Thread(target=self.upload_file, args=(file_path,))
        thread.start()

    def upload_file(self, file_path):
        """Uploads the file to the FastAPI backend."""
        url = f"{server_ip}/api/raw_materials/v1/import_raw_materials/"

        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                response = requests.post(url, files=files)

            # Hide loader from the main thread
            self.root.after(0, self.hide_loader)

            if response.status_code == 200:
                result = response.json()
                success_count = result.get("successful_inserts", 0)
                skipped_count = result.get("skipped_duplicates", 0)

                message = f"Successfully inserted {success_count} raw material codes.\n"
                message += f"Skipped {skipped_count} duplicate raw material codes."
                self.root.after(0, lambda: messagebox.showinfo("Success", message))

            else:
                error_msg = response.json().get("detail", "Unknown error occurred.")
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to import data: {error_msg}"))
                text = response.text
                print(text)

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
