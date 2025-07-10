import ttkbootstrap as ttk
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from frontend.status.main_view import StatusView
from frontend.historical_data.main_view import HistoricalDataView   
from frontend.sidebar import Sidebar
from frontend.warehouse.main_view import WarehouseView
from frontend.user.user_view import UserView
from frontend.raw_material.main_view import RawMaterialView
from frontend.forms.main_view import ConsumptionEntryView
from frontend.stock_on_hand.main_view import StockOnHandView
from frontend.adjusment_records.main_view import AdjustmentFormRecordsView
from frontend.reports.main_view import ReportView
from tkinter import StringVar, N, S, E, W, VERTICAL
from tkinter import font

class App(ttk.Window):
    def __init__(self, theme_name="litera"):
        super().__init__(themename=theme_name)  # Choose the ttkbootstrap theme
        self.title("Warehouse RM Stock Movement Program")
        self.geometry("1300x700")

        # ----------- [FONTSTYLE FOR THE TABLES] ----------
        # Define a custom font
        # self.tree_font = font.Font(family="Tahoma", size=10)  # Adjust size
        # self.header_font = font.Font(family="Tahoma", size=10, weight="bold")  # Bold for headers
        #
        # # Create a custom style for the Treeview
        # style = ttk.Style()
        # style.configure("Treeview", font=self.tree_font)  # Apply font to table rows
        # style.configure("Treeview.Heading", font=self.header_font)  # Apply font to column headers


        # ---------------------------[Font style for the TAB FONTS]---------------------------
        # Initialize ttkbootstrap style
        style = Style()
        def apply_custom_styles():
            """Function to reapply styles after theme change."""
            style.configure("Custom.Treeview", rowheight=25, font=("Arial", 10))  # Set row height
            style.configure("Treeview.Heading", background=style.colors.primary, foreground="white",
                            font=("Arial", 10, "bold"))  # Set header background to PRIMARY



            # Style for the radio button
            style.configure("Custom.TRadiobutton", font=("Arial", 12, "bold"))  # Define a custom style with desired font size


            # style.configure("Toolbutton", font=("Arial", 12, "bold"))  # Define a custom style with desired font size

            # Increase tab font size
            style.configure("TNotebook.Tab", font=("Arial", 11, "bold"))  # Change font and size
            style.configure("CustomLabel.TLabel", font=("Arial", 11, "bold"))

        # Apply styles initially
        apply_custom_styles()

        # Listen for theme changes and reapply styles
        style.master.bind("<<ThemeChanged>>", lambda event: apply_custom_styles())



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
            "historical_data": HistoricalDataView(self.content_frame),
            "adjustment_records": AdjustmentFormRecordsView(self.content_frame),
            "reports": ReportView(self.content_frame)
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
