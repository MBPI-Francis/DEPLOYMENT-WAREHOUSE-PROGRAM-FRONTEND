import ttkbootstrap as tb
from ttkbootstrap.constants import *
from datetime import datetime, timedelta
import re


def format_date_while_typing(event):
    """Auto-formats the date entry while typing, keeping the structure intact and ensuring valid MM/DD."""
    text = re.sub(r"[^\d]", "", date_entry.entry.get())  # Remove non-numeric characters
    cursor_pos = date_entry.entry.index("insert")  # Get cursor position
    key_pressed = event.keysym  # Capture key event

    # Ensure we only allow up to 8 digits (MMDDYYYY)
    if len(text) > 8:
        text = text[:8]

    # Extract month, day, and year
    month = text[:2] if len(text) >= 2 else text
    day = text[2:4] if len(text) >= 4 else text[2:]
    year = text[4:] if len(text) > 4 else ""

    # Ensure month is valid (1-12)
    if len(month) == 2 and (int(month) < 1 or int(month) > 12):
        month = "12"

    # Ensure day is valid (1-31)
    if len(day) == 2 and (int(day) < 1 or int(day) > 31):
        day = "31"

    # Format MM/DD/YYYY
    formatted_date = f"{month}"
    if len(text) >= 3:
        formatted_date += f"/{day}"
    if len(text) > 4:
        formatted_date += f"/{year}"

    # Update entry field with formatted date
    date_entry.entry.delete(0, "end")
    date_entry.entry.insert(0, formatted_date)

    # Adjust cursor position naturally
    if key_pressed == "BackSpace":
        cursor_pos -= 1
    elif cursor_pos in [2, 5] and key_pressed not in ["Left", "Right", "BackSpace"]:
        cursor_pos += 1  # Skip slash `/` when typing

    date_entry.entry.icursor(cursor_pos)


def complete_year(event):
    """Completes the year when the user presses Tab, Enter, or loses focus, ensuring MM/DD/YYYY validity."""
    text = date_entry.entry.get()
    parts = text.split("/")

    if len(parts) == 3:
        month, day, year = parts

        # Ensure MM and DD have leading zeros
        month = month.zfill(2)
        day = day.zfill(2)

        # Convert 2-digit year to 4-digit (assumes 2000+)
        if len(year) == 2:
            year = "20" + year

        # Validate the date (handle months with different max days)
        try:
            datetime(int(year), int(month), int(day))  # Checks if it's a real date
        except ValueError:
            day = "28"  # Default to last valid day in case of invalid input

        # Update formatted date
        formatted_date = f"{month}/{day}/{year}"
        date_entry.entry.delete(0, "end")
        date_entry.entry.insert(0, formatted_date)


# Create the ttkbootstrap window
root = tb.Window(themename="cosmo")

# Frame for layout
form_frame = tb.Frame(root, padding=10)
form_frame.pack()

# Date Label
date_label = tb.Label(form_frame, text="Consumption Date", style="CustomLabel.TLabel")
date_label.grid(row=0, column=0, padx=5, pady=(0, 0), sticky="w")

# Calculate yesterday's date
yesterday_date = datetime.now() - timedelta(days=1)

# ttkbootstrap DateEntry (allows both typing & calendar selection)
date_entry = tb.DateEntry(
    form_frame,
    bootstyle=PRIMARY,
    dateformat="%m/%d/%Y",
    startdate=yesterday_date,
    width=15
)
date_entry.grid(row=1, column=0, padx=5, pady=(0, 10), sticky="w")

# Bind events
date_entry.entry.bind("<KeyRelease>", format_date_while_typing)  # Format while typing
date_entry.entry.bind("<Tab>", complete_year)  # Complete year on Tab
date_entry.entry.bind("<Return>", complete_year)  # Complete year on Enter

# Run application
root.mainloop()
