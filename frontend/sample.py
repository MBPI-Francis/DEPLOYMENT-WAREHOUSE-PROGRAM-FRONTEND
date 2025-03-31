import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import DateEntry
from datetime import datetime, timedelta

class CustomDateEntry(DateEntry):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.entry.bind("<KeyRelease>", self.auto_format)  # Trigger auto-format on key press
        self.entry.bind("<FocusOut>", self.complete_date)  # Ensure correct format when leaving the field
        self.entry.bind("<Return>", self.complete_date)  # Ensure correct format when leaving the field

    def auto_format(self, event=None):
        """Automatically formats date while typing."""
        raw_date = self.entry.get().replace(" ", "").replace("-", "/")  # Normalize input
        digits = [c for c in raw_date if c.isdigit()]  # Extract only numbers

        if not digits:
            return  # No numbers, exit

        formatted_date = ""
        if len(digits) >= 1:  # MM
            formatted_date += digits[0]
        if len(digits) >= 2:  # MM/
            formatted_date += digits[1] + "/"
        if len(digits) >= 3:  # MM/DD
            formatted_date += digits[2]
        if len(digits) >= 4:  # MM/DD/
            formatted_date += digits[3] + "/"
        if len(digits) >= 5:  # MM/DD/YY
            formatted_date += digits[4]
        if len(digits) >= 6:  # MM/DD/YYYY
            formatted_date += digits[5]

        # Update entry field
        self.entry.delete(0, "end")
        self.entry.insert(0, formatted_date)

    def complete_date(self, event=None):
        """Ensures correct MM/DD/YYYY format when pressing Enter or leaving focus."""
        raw_date = self.entry.get().strip()

        try:
            # Try parsing with full year first
            date_obj = datetime.strptime(raw_date, "%m/%d/%Y")
        except ValueError:
            try:
                # If the user entered a two-digit year, assume 20XX
                date_obj = datetime.strptime(raw_date, "%m/%d/%y")
            except ValueError:
                return  # Exit if invalid

        # Format to MM/DD/YYYY with leading zeros
        formatted_date = date_obj.strftime("%m/%d/%Y")
        self.entry.delete(0, "end")
        self.entry.insert(0, formatted_date)

# Create the application window
app = ttk.Window(themename="flatly")
app.title("Auto-Formatted Date Entry")

yesterday_date = datetime.today() - timedelta(days=1)

frame = ttk.Frame(app, padding=20)
frame.pack(pady=20)

ttk.Label(frame, text="Enter Date (MM/DD/YYYY):", font=("Arial", 12)).pack(anchor="w")

date_entry = CustomDateEntry(
    frame,
    bootstyle=PRIMARY,
    dateformat="%m/%d/%Y",
    startdate=yesterday_date,
    width=25
)
date_entry.pack(pady=5)

app.mainloop()
