import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime, timedelta

def format_date_while_typing(event):
    """Auto-formats the date entry while typing, ensuring valid MM/DD/YYYY format."""
    text = date_entry.entry.get().replace("/", "")  # Remove slashes to get raw number input
    formatted_date = ""

    if len(text) > 8:  # Prevent overflow of more than 8 characters (MMDDYYYY)
        text = text[:8]



    # Handle the case where the length is 2 (MD)
    if len(text) == 2:
        month = text[:1]
        day = text[1:]
        # Ensure the month is valid (01-12)
        if int(month) < 1 or int(month) > 12:
            month = str(datetime.now().month)  # Default to January if invalid month
        # Ensure the day is valid (01-31)
        if int(day) < 1 or int(day) > 31:
            day = str(datetime.now().day)  # Default to 1st if invalid day
        year = str(datetime.now().year)  # Assume the current year
        formatted_date = f"0{month}/0{day}/{year}"


    # Handle the case where the length is 3 (MDD)
    elif len(text) == 3:
        month = text[:1]
        day = text[1:]
        # Ensure the month is valid (01-12)
        if int(month) < 1 or int(month) > 12:
            month = str(datetime.now().month)  # Default to January if invalid month
        # Ensure the day is valid (01-31)
        if int(day) < 1 or int(day) > 31:
            day = str(datetime.now().day)  # Default to 1st if invalid day
            if len(str(day)) == 1:
                day = f"0{day}"

        year = str(datetime.now().year)  # Assume the current year
        formatted_date = f"0{month}/{day}/{year}"


    # Handle the case where the length is 4 (MMDD)
    elif len(text) == 4:
        month = text[:2]
        day = text[2:]
        # Ensure the month is valid (01-12)
        if int(month) < 1 or int(month) > 12:
            month = str(datetime.now().month)  # Default to January if invalid month
        # Ensure the day is valid (01-31)
        if int(day) < 1 or int(day) > 31:
            day = str(datetime.now().day)  # Default to 1st if invalid day
        year = str(datetime.now().year)  # Assume the current year
        formatted_date = f"{month}/{day}/{year}"

        # Handle the case where the length is 5 (MDDYY)
    elif len(text) == 5:
        month = text[:1]
        day = text[1:3]
        year = text[3:]

        # Ensure the month is valid (01-12)
        if int(month) < 1 or int(month) > 12:
            month = str(datetime.now().month)  # Default to January if invalid month
        # Ensure the day is valid (01-31)
        if int(day) < 1 or int(day) > 31:
            day = str(datetime.now().day)  # Default to 1st if invalid day
        formatted_date = f"0{month}/{day}/20{year}"

    # Handle the case where the length is 6 (MMDDYY)
    elif len(text) == 6:
        month = text[:2]
        day = text[2:4]
        year = text[4:]
        # Ensure the month is valid (01-12)
        if int(month) < 1 or int(month) > 12:
            month = str(datetime.now().month)  # Default to January if invalid month
        # Ensure the day is valid (01-31)
        if int(day) < 1 or int(day) > 31:
            day = str(datetime.now().day)  # Default to 1st if invalid day
        formatted_date = f"{month}/{day}/20{year}"  # Assume 20XX for 2-digit year

    # Handle the case where the length is 8 (MMDDYYYY)
    elif len(text) == 8:
        month = text[:2]
        day = text[2:4]
        year = text[4:]
        # Ensure the month is valid (01-12)
        if int(month) < 1 or int(month) > 12:
            month = str(datetime.now().month)  # Default to January if invalid month
        # Ensure the day is valid (01-31)
        if int(day) < 1 or int(day) > 31:
            day = str(datetime.now().day)  # Default to 1st if invalid day
        formatted_date = f"{month}/{day}/{year}"

    # Update entry field with formatted value
    date_entry.entry.delete(0, "end")
    date_entry.entry.insert(0, formatted_date)

# Create the ttkbootstrap window
root = ttk.Window(themename="cosmo")

# Frame for layout
form_frame = ttk.Frame(root, padding=10)
form_frame.pack()

# Date Label
date_label = ttk.Label(form_frame, text="Consumption Date", font=("Helvetica", 10, "bold"))
date_label.grid(row=0, column=0, padx=5, pady=(0, 0), sticky="w")

# Calculate yesterday's date
yesterday_date = datetime.now() - timedelta(days=1)

# ttkbootstrap DateEntry (with manual typing enabled)
date_entry = ttk.DateEntry(
    form_frame,
    bootstyle=PRIMARY,
    dateformat="%m/%d/%Y",
    startdate=yesterday_date,
    width=15
)

date_entry.grid(row=1, column=0, padx=5, pady=(0, 10), sticky="w")

# Bind keypress event to format dynamically
date_entry.entry.bind("<Return>", format_date_while_typing)
date_entry.entry.bind("<FocusOut>", format_date_while_typing)

# Run application
root.mainloop()
