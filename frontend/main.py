import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from frontend.status.main_view import StatusView
from frontend.historical_data.main_view import HistoricalDataView   
from frontend.sidebar import Sidebar
from frontend.warehouse.main_view import WarehouseView
from frontend.user.user_view import UserView
from frontend.raw_material.main_view import RawMaterialView
from frontend.forms.main_view import ConsumptionEntryView
from frontend.stock_on_hand.main_view import StockOnHandView
from tkinter import StringVar, N, S, E, W, VERTICAL


class App(ttk.Window):
    def __init__(self, theme_name="litera"):
        super().__init__(themename=theme_name)  # Choose the ttkbootstrap theme
        self.title("Warehouse RM Stock Movement Program")
        self.geometry("1300x700")

        # Store the selected theme in a StringVar
        self.selected_theme = StringVar(value=theme_name)

        # Configure grid
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=0)  # Sidebar should not stretch
        self.columnconfigure(1, weight=0)  # Separator should not stretch
        self.columnconfigure(2, weight=1)  # Content area should stretch

        # Sidebar
        # self.sidebar = Sidebar(self, self.navigate_to_view)
        self.sidebar = Sidebar(self, self.navigate_to_view, self)
        self.sidebar.grid(row=0, column=0, sticky=N + S)

        # Vertical Separator
        self.separator = ttk.Separator(self, orient=VERTICAL)
        self.separator.grid(row=0, column=1, sticky=N + S)

        # Main Content Frame (with padding)
        self.content_frame = ttk.Frame(self, padding=10)
        self.content_frame.grid(row=0, column=2, sticky=N + S + E + W)

        # Configure grid for content frame
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Initialize Views
        self.views = {
            "status": StatusView(self.content_frame),
            "warehouse": WarehouseView(self.content_frame),
            "raw_material": RawMaterialView(self.content_frame),
            "user": UserView(self.content_frame),
            "consumption_entry": ConsumptionEntryView(self.content_frame),
            "stock_on_hand": StockOnHandView(self.content_frame),
            "historical_data": HistoricalDataView(self.content_frame)
        }

        # Default View
        self.navigate_to_view("consumption_entry")


    def navigate_to_view(self, view_name):
        """Navigate to the selected view."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if view_name in self.views:
            self.views[view_name].show()


    def change_theme(self):
        """Applies the selected theme dynamically."""
        new_theme = self.selected_theme.get()
        self.style.theme_use(new_theme)  # Change the theme


if __name__ == "__main__":
    app = App()
    app.mainloop()
