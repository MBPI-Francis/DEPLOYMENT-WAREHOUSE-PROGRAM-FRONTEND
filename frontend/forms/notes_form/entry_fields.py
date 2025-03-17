import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import requests
from backend.settings.database import server_ip
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.dialogs.dialogs import Messagebox
from datetime import datetime, timedelta
from .table import NoteTable
from .validation import EntryValidation


def entry_fields(note_form_tab):

        # Function to clear all entry fields
    def clear_fields():

        product_code_entry.delete(0, ttk.END)
        lot_number_entry.delete(0, ttk.END)
        product_kind_combobox.set("")

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
            Messagebox.show_error("Error", "Invalid date format. Please use MM/DD/YYYY.")
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
        except requests.exceptions.RequestException as e:
            Messagebox.show_info(e, "Data Entry Error")

        # Function to get the selected item's ID




    # Function to send POST request

    # Create a frame for the form inputs
    form_frame = ttk.Frame(note_form_tab)
    form_frame.pack(fill=X, pady=10, padx=20)


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

    # Date Entry field
    date_label = ttk.Label(form_frame, text="Consumption Date", font=("Helvetica", 10, "bold"))
    date_label.grid(row=0, column=0, padx=5, pady=(0,0), sticky=W)

    # Calculate yesterday's date
    yesterday_date = datetime.now() - timedelta(days=1)

    date_entry = ttk.DateEntry(
        form_frame,
        bootstyle=PRIMARY,
        dateformat="%m/%d/%Y",
        startdate=yesterday_date,  # Set yesterday's date
        width=25
    )

    date_entry.grid(row=1, column=0, padx=5, pady=(0, 10), sticky=W)
    ToolTip(date_entry, text="This is the date when raw materials stock moved")


    # Product Code Entry Field

    product_code_var = ttk.StringVar(value="")
    product_code_label = ttk.Label(form_frame, text="Product Code", font=("Helvetica", 10, "bold"))
    product_code_label.grid(row=2, column=0, padx=5, pady=(0,0), sticky=W)
    product_code_entry = ttk.Entry(form_frame, width=30, textvariable=product_code_var)
    product_code_entry.grid(row=3, column=0, padx=5, pady=(0,5), sticky=W)
    ToolTip(product_code_entry, text="Enter the product code")
    # Bind the key release event to the combobox to trigger uppercase conversion
    product_code_entry.bind("<KeyRelease>", on_key_release)

    # Lot Number Entry Field
    lot_number_var = ttk.StringVar(value="")
    lot_number_label = ttk.Label(form_frame, text="Lot Number", font=("Helvetica", 10, "bold"))
    lot_number_label.grid(row=2, column=1, padx=5, pady=(0,0), sticky=W)
    lot_number_entry = ttk.Entry(form_frame, width=30, textvariable=lot_number_var)
    lot_number_entry.grid(row=3, column=1, padx=5, pady=(0,5))
    ToolTip(lot_number_entry, text="Enter the lot number")
    lot_number_entry.bind("<KeyRelease>", on_key_release)

    # Product Kind JSON-format choices (coming from the API)
    product_kinds = get_product_kinds_api()
    name_to_id = {item["name"]: item["id"] for item in product_kinds}
    product_kind_names = list(name_to_id.values())

    # Combobox for Product Kind Drop Down
    product_kind_label = ttk.Label(form_frame, text="Product Kind", font=("Helvetica", 10, "bold"))
    product_kind_label.grid(row=2, column=3, padx=5, pady=(0,0), sticky=W)
    product_kind_combobox = ttk.Combobox(
        form_frame,
        values=product_kind_names,
        state="readonly",
        width=15,
    )
    product_kind_combobox.grid(row=3, column=3, pady=(0,5), padx=5, sticky=W)
    ToolTip(product_kind_combobox, text="Choose a product kind")


    # Add button to submit data
    btn_submit = ttk.Button(
        form_frame,
        text="+ Add",
        command=submit_data,
        width=28
    )
    btn_submit.grid(row=4, column=0, columnspan=2, padx=5, pady=(5,0), sticky=W)
    ToolTip(btn_submit, text="Click this button to add your entry to the list")


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










