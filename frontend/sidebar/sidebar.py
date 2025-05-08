import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import StringVar

class Sidebar(ttk.Frame):
    def __init__(self, parent, navigate_callback, app):
        super().__init__(parent, width=300, padding=20, style="Sidebar.TFrame")
        self.app = app  # Store reference to the main app window

        # Custom Style for Sidebar
        style = ttk.Style()
        style.configure("Sidebar.TFrame", background="#8B4513")  # Brown color

        # Navigation Buttons
        # ttk.Button(
        #     self,
        #     text="Statuses",
        #     command=lambda: navigate_callback("status"),
        #     bootstyle="primary",
        #     width=18,
        # ).pack(pady=10)
        #
        # # Navigation Buttons
        # ttk.Button(
        #     self,
        #     text="Warehouse",
        #     command=lambda: navigate_callback("warehouse"),
        #     bootstyle="primary",
        #     width=18,
        # ).pack(pady=10)

        ttk.Button(
            self,
            text="Raw Materials",
            command=lambda: navigate_callback("raw_material"),
            bootstyle="primary",
            width=18,
        ).pack(pady=10)

        ttk.Button(
            self,
            text="Stock On Hand",
            command=lambda: navigate_callback("stock_on_hand"),
            bootstyle="primary",
            width=18,
        ).pack(pady=10)


        ttk.Button(
            self,
            text="Historical Data",
            command=lambda: navigate_callback("historical_data"),
            bootstyle="primary",
            width=18,
        ).pack(pady=10)

        ttk.Button(
            self,
            text="Consumption Entry",
            command=lambda: navigate_callback("consumption_entry"),
            bootstyle="primary",
            width=18,
        ).pack(pady=10)

        # Theme Selection UI
        self.theme_names = ("litera",
                            "cosmo",
                            "flatly",
                            "lumen",
                            "minty",
                            "pulse",
                            "sandstone",
                            "united",
                            "yeti",
                            "simplex",
                            "cerculean",
                            "cyborg",
                            "vapor",
                            "superhero",
                            "darkly",
                            "journal",
                            "solar",
                            "morph")
        self.selected_theme = StringVar(value=self.theme_names[0])  # Default to first theme

        # Dropdown for theme selection
        self.theme_dropdown = ttk.Combobox(
            self,
            textvariable=self.selected_theme,
            values=self.theme_names,
            state="readonly",
            width=18
        )
        self.theme_dropdown.pack(pady=(15, 0))

        # Button to change theme
        ttk.Button(
            self,
            text="Change Theme",
            command=self.change_theme,
            bootstyle="primary",
            width=19,
        ).pack(pady=5)

    def change_theme(self):
        """Applies the selected theme dynamically."""
        new_theme = self.selected_theme.get()
        self.app.style.theme_use(new_theme)  # Change the app theme dynamically