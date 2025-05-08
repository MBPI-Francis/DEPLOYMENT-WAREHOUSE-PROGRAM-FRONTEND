import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import requests
from backend.settings.database import server_ip
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.dialogs.dialogs import Messagebox
from datetime import datetime, timedelta
import tkinter as tk
from .table import NoteTable
from .validation import EntryValidation
from frontend.forms.shared import SharedFunctions
from datetime import datetime, timedelta


def entry_fields(note_form_tab):
    shared_instance = SharedFunctions()

    # Function to clear all entry fields
    def clear_fields():

        if not checkbox_product_code_var.get():
            product_code_entry.delete(0, ttk.END)

        if not checkbox_product_kind_var.get():
            product_kind_combobox.set("")
        lot_number_entry.delete(0, ttk.END)

    def submit_data():

        # Collect the form data
        product_code = product_code_entry.get()
        lot_number = lot_number_entry.get()
        product_kind_id = product_kind_combobox.get()
        consumption_date = date_entry.entry.get()

        # Set focus to the Entry field
        product_code_entry.focus_set()


        # Convert date to YYYY-MM-DD
        try:
            consumption_date = datetime.strptime(consumption_date, "%m/%d/%Y").strftime("%Y-%m-%d")
        except ValueError:
            Messagebox.show_error("Invalid date format. Please use MM/DD/YYYY.", "Date Entry Error")
            return

        # Create a dictionary with the data
        data = {
            "product_code": product_code,
            "lot_number": lot_number,
            "product_kind_id": product_kind_id,
            "stock_change_date": consumption_date
        }

        # Validate the data entries in front-end side
        if EntryValidation.entry_validation(data):
            error_text = EntryValidation.entry_validation(data)
            Messagebox.show_error(f"There is no data in these fields {error_text}.", "Data Entry Error", alert=True)
            return

            # Send a POST request to the API
        try:
            response = requests.post(f"{server_ip}/api/notes/v1/create/", json=data)
            if response.status_code == 200:  # Successfully created
                clear_fields()

                note_table.load_data()
                # refresh_table()  # Refresh the table

                # Get the last inserted row ID
                last_row_id = note_table.tree.get_children()[0]  # Get the last row's ID

                # Highlight the last row
                note_table.tree.selection_set(last_row_id)  # Select the last row
                note_table.tree.focus(last_row_id)  # Focus on the last row
                note_table.tree.see(last_row_id)  # Scroll to make it visible
        except requests.exceptions.RequestException as e:
            Messagebox.show_info(e, "Data Entry Error")



    # Function to send POST request

    # Create a frame for the form inputs
    notes_form_frame = ttk.Frame(note_form_tab)
    notes_form_frame.pack(fill=X, pady=10, padx=20)

    # Configure grid columns to make them behave correctly
    notes_form_frame.grid_columnconfigure(0, weight=1)  # Left (Warehouse) stays at the left
    notes_form_frame.grid_columnconfigure(1, weight=1)  # Right (Ref Number) is pushed to the right

    first_field_frame = ttk.Frame(notes_form_frame)
    first_field_frame.grid(row=0, column=0, padx=5, pady=(0, 10), sticky=W)

    second_field_frame = ttk.Frame(notes_form_frame)
    second_field_frame.grid(row=0, column=1, padx=5, pady=(0, 10), sticky="e")

    # Function to convert typed input to uppercase
    def on_key_release(event):
        # Get the current text in the entry field
        prod_code_current_text = product_code_var.get()

        # Convert the text to uppercase and set it back
        product_code_var.set(prod_code_current_text.upper())

        # Get the current text in the combobox
        lot_num_current_text = lot_number_var.get()

        # Convert the text to uppercase and set it back
        lot_number_var.set(lot_num_current_text.upper())


    # Checkbox for Warehouse lock
    checkbox_product_code_var = ttk.IntVar()
    lock_product_code = ttk.Checkbutton(
        first_field_frame,
        variable=checkbox_product_code_var,
        bootstyle="round-toggle"
    )
    lock_product_code.grid(row=0, column=0, pady=(0, 0), padx=(0,0), sticky=E)
    ToolTip(lock_product_code, text="Lock the product code by clicking this")

    # Product Code Entry Field
    product_code_var = ttk.StringVar(value="")
    product_code_label = ttk.Label(first_field_frame, text="Product Code", style="CustomLabel.TLabel")
    product_code_label.grid(row=0, column=0, padx=5, pady=(0,0), sticky=W)
    product_code_entry = ttk.Entry(first_field_frame, width=30, textvariable=product_code_var, font=shared_instance.custom_font_size)
    product_code_entry.grid(row=1, column=0, padx=5, pady=(0,5), sticky=W)
    ToolTip(product_code_entry, text="Enter the product code")
    # Bind the key release event to the combobox to trigger uppercase conversion
    product_code_entry.bind("<KeyRelease>", on_key_release)


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
                if len(str(month)) == 1:
                    month = f"0{month}"

            # Ensure the day is valid (01-31)
            if int(day) < 1 or int(day) > 31:
                day = str(datetime.now().day)  # Default to 1st if invalid day
                if len(str(day)) == 1:
                    day = f"0{day}"

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
                if len(str(day)) == 1:
                    day = f"0{day}"
            formatted_date = f"0{month}/{day}/20{year}"


        # Handle the case where the length is 6 (MMDDYY)
        elif len(text) == 6:
            month = text[:2]
            day = text[2:4]
            year = text[4:]
            # Ensure the month is valid (01-12)
            if int(month) < 1 or int(month) > 12:
                month = str(datetime.now().month)  # Default to January if invalid month
                if len(str(month)) == 1:
                    month = f"0{month}"

            # Ensure the day is valid (01-31)
            if int(day) < 1 or int(day) > 31:
                day = str(datetime.now().day)  # Default to 1st if invalid day
                if len(str(day)) == 1:
                    day = f"0{day}"

            formatted_date = f"{month}/{day}/20{year}"  # Assume 20XX for 2-digit year


            # Handle the case where the length is 6 (MMDDYY)
        elif len(text) == 7:
            Messagebox.show_error("Invalid date format. Please use MM/DD/YYYY.", "Date Entry Error")


        # Handle the case where the length is 8 (MMDDYYYY)
        elif len(text) == 8:
            month = text[:2]
            day = text[2:4]
            year = text[4:]
            # Ensure the month is valid (01-12)
            if int(month) < 1 or int(month) > 12:
                month = str(datetime.now().month)  # Default to January if invalid month
                if len(str(month)) == 1:
                    month = f"0{month}"

            # Ensure the day is valid (01-31)
            if int(day) < 1 or int(day) > 31:
                day = str(datetime.now().day)  # Default to 1st if invalid day
                if len(str(day)) == 1:
                    day = f"0{day}"

            formatted_date = f"{month}/{day}/{year}"

        # Update entry field with formatted value
        date_entry.entry.delete(0, "end")
        date_entry.entry.insert(0, formatted_date)

    # Date Label
    date_label = ttk.Label(second_field_frame, text="Consumption Date", font=("Helvetica", 10, "bold"))
    date_label.grid(row=0, column=0, padx=5, pady=(0,0), sticky=W)

    # Calculate yesterday's date
    yesterday_date = datetime.now() - timedelta(days=1)

    # ttkbootstrap DateEntry (with manual typing enabled)
    date_entry = ttk.DateEntry(
            second_field_frame,
            bootstyle=PRIMARY,
            dateformat="%m/%d/%Y",
            startdate=yesterday_date,  # Set yesterday's date
            width=26,
    )

    date_entry.grid(row=1, column=0, padx=5, pady=(0, 0), sticky=W)

    # Bind keypress event to format dynamically
    date_entry.entry.bind("<Return>", format_date_while_typing)
    date_entry.entry.bind("<FocusOut>", format_date_while_typing)
    date_entry.entry.config(font=shared_instance.custom_font_size)


    #
    # # Date Entry field
    # date_label = ttk.Label(second_field_frame, text="Consumption Date", style="CustomLabel.TLabel")
    # date_label.grid(row=0, column=0, padx=5, pady=(0,0), sticky=W)
    #
    # # Calculate yesterday's date
    # yesterday_date = datetime.now() - timedelta(days=1)
    #
    # date_entry = ttk.DateEntry(
    #     second_field_frame,
    #     bootstyle=PRIMARY,
    #     dateformat="%m/%d/%Y",
    #     startdate=yesterday_date,  # Set yesterday's date
    #     width=26,
    # )
    #
    # date_entry.grid(row=1, column=0, padx=5, pady=(0, 0), sticky=W)
    # ToolTip(date_entry, text="This is the date when raw materials stock moved")
    # # Directly access the internal Entry widget of DateEntry and apply the font
    # date_entry.entry.config(font=shared_instance.custom_font_size)


    # Lot Number Entry Field
    lot_number_var = ttk.StringVar(value="")
    lot_number_label = ttk.Label(first_field_frame, text="Lot Number", style="CustomLabel.TLabel")
    lot_number_label.grid(row=2, column=0, padx=5, pady=(0,0), sticky=W)
    lot_number_entry = ttk.Entry(first_field_frame, width=30, textvariable=lot_number_var, font=shared_instance.custom_font_size)
    lot_number_entry.grid(row=3, column=0, padx=5, pady=(0,5))
    ToolTip(lot_number_entry, text="Enter the lot number")
    lot_number_entry.bind("<KeyRelease>", on_key_release)

    # Product Kind JSON-format choices (coming from the API)
    product_kinds = get_product_kinds_api()
    name_to_id = {item["name"]: item["id"] for item in product_kinds}
    product_kind_names = list(name_to_id.values())



    # Checkbox for Warehouse lock
    checkbox_product_kind_var = ttk.IntVar()
    lock_product_kind = ttk.Checkbutton(
        first_field_frame,
        variable=checkbox_product_kind_var,
        bootstyle="round-toggle"
    )
    lock_product_kind.grid(row=2, column=1, pady=(0, 0), padx=(0,0), sticky=E)
    ToolTip(lock_product_kind, text="Lock the product kind by clicking this")

    # Combobox for Product Kind Drop Down
    product_kind_label = ttk.Label(first_field_frame, text="Product Kind", style="CustomLabel.TLabel")
    product_kind_label.grid(row=2, column=1, padx=5, pady=(0,0), sticky=W)
    product_kind_combobox = ttk.Combobox(
        first_field_frame,
        values=product_kind_names,
        state="readonly",
        width=20,
        font=shared_instance.custom_font_size
    )
    product_kind_combobox.grid(row=3, column=1, pady=(0,5), padx=5, sticky=W)
    ToolTip(product_kind_combobox, text="Choose a product kind")


    # Add button to submit data
    btn_add_note = ttk.Button(
        notes_form_frame,
        text="+ Add",
        command=submit_data,
        width=28,
    )
    btn_add_note.grid(row=4, column=0, columnspan=3, pady=0, padx=400, sticky=NSEW)
    ToolTip(btn_add_note, text="Click this button to add your entry to the list")
    
    def bind_shift_enter_to_all_children(parent, callback):
        for child in parent.winfo_children():
            try:
                child.bind("<Shift-Return>", callback)
            except:
                pass
            # Recursively bind if the child is a container
            if isinstance(child, (ttk.Frame, tk.Frame)):
                bind_shift_enter_to_all_children(child, callback)

    # Bind Shift+Enter to all child widgets in this tab
    bind_shift_enter_to_all_children(notes_form_frame, lambda e: btn_add_note.invoke())


    def bind_shift_a_to_toggle_checkbox(parent, toggle_func):
        for child in parent.winfo_children():
            try:
                child.bind("<Control-Shift-A>", toggle_func)
                child.bind("<Control-Shift-a>", toggle_func)
            except:
                pass
            if isinstance(child, (ttk.Frame, tk.Frame)):
                bind_shift_a_to_toggle_checkbox(child, toggle_func)

    def toggle_warehouse_lock(event=None):
        current_state_kind = checkbox_product_kind_var.get()
        current_state_code = checkbox_product_code_var.get()

        # If any checkbox is unchecked, set all to True (1)
        if not all([current_state_kind, current_state_code]):
            checkbox_product_kind_var.set(1)
            checkbox_product_code_var.set(1)

        else:
            checkbox_product_kind_var.set(0)
            checkbox_product_code_var.set(0)


    bind_shift_a_to_toggle_checkbox(notes_form_frame, toggle_warehouse_lock)
    
    
    note_table = NoteTable(note_form_tab)
    



def get_product_kinds_api():
    url = server_ip + "/api/product_kinds/v1/list/"
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse JSON response
        data = response.json()
        return data
    else:
        return []










