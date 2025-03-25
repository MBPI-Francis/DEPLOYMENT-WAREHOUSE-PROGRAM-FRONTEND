import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import requests
from backend.settings.database import server_ip
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.dialogs.dialogs import Messagebox
from datetime import datetime, timedelta
from .table import NoteTable
import tkinter as tk
import os
from ttkbootstrap import Style
from tkinter.filedialog import asksaveasfilename
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.styles import numbers

def entry_fields(note_form_tab):

    # Function to clear all entry fields
    def clear_fields():
        if not checkbox_date_var.get():  # Clear only if checkbox_date_var is False
            date_entry.entry.delete(0, tk.END)


    def clear_all_data_from_forms():
        """Fetch data from API and format for table rowdata."""
        url = f"{server_ip}/api/clear-table-data"
        params = {"tbl": "all"}  # Send tbl as a query parameter
        try:
            # Send another POST request to clear data
            response = requests.post(url, params=params)
            if response.status_code == 200:  # Check if the stock view was successfully created
                Messagebox.show_info("Data is successfully cleared!", "Data Clearing")


            else:
                Messagebox.show_error(f"There must be a mistake, the status code is {response.status_code}", "Data Clearing Error")

        except requests.exceptions.RequestException as e:
            return False


    def export_data_to_excel():

        date_entry_value = date_entry.entry.get()

        # Convert date to YYYY-MM-DD
        try:
            date_entry_value = datetime.strptime(date_entry_value, "%m/%d/%Y").strftime("%Y-%m-%d")
        except ValueError:
            Messagebox.show_error("Error", "Invalid date format. Please use MM/DD/YYYY.")
            return

        try:

            # Call the function to get all the data from the view table
            data = get_soh_data()

            # Generate an Excel file for the stock-on-hand data
            create_soh_whse_excel(date_entry_value, data)

        except requests.exceptions.RequestException as e:
            # Show an error message if the first POST request fails
            Messagebox.show_info(e, "Data Entry Error")


    # Function to update stock
    def update_stock():
        date_entry_value = date_entry.entry.get()

        # Convert date to YYYY-MM-DD
        try:
            date_entry_value = datetime.strptime(date_entry_value, "%m/%d/%Y").strftime("%Y-%m-%d")
        except ValueError:
            Messagebox.show_error("Error", "Invalid date format. Please use MM/DD/YYYY.")
            return

        try:
            # Send another POST request to update the stocks
            response = requests.post(f"{server_ip}/api/update_stock_on_hand/?params_date={date_entry_value}")
            if response.status_code == 200:
                # print("Successfully Updated the Stocks.")

                try:
                    # Send a POST request to update the computed date in the API
                    response = requests.post(f"{server_ip}/api/update-date-computed")
                    if response.status_code == 200:
                        # print("Successfully Updated the Computed Date")
                        pass
                except requests.exceptions.RequestException as e:
                    Messagebox.show_error(e, "Data Entry Error")

                # Clear input fields after successful operation
                clear_fields()

                # Refresh the note table to display updated data
                note_table.refresh_table()

                # Show success message
                Messagebox.show_info("The new beginning balance has been successfully updated!", "Success")

        except requests.exceptions.RequestException as e:
            Messagebox.show_info(e, "Data Entry Error")


    # Function to show confirmation panel
    def show_confirmation_panel():
        # confirmation_window = ttk.Toplevel(form_frame)
        # confirmation_window.title("Confirm Action")
        # confirmation_window.geometry("490x290")
        # confirmation_window.resizable(False, False)

        confirmation_window = ttk.Toplevel(form_frame)
        confirmation_window.title("Confirm Action")

        # Get the screen width and height
        screen_width = confirmation_window.winfo_screenwidth()
        screen_height = confirmation_window.winfo_screenheight()

        # Set a dynamic size (proportional to the screen size)
        window_width = int(screen_width * 0.38)  # Adjust width as needed
        window_height = int(screen_height * 0.37)  # Adjust height as needed

        # Calculate position for centering
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 3  # Position slightly higher

        # Apply geometry dynamically
        confirmation_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Allow resizing but maintain proportions
        confirmation_window.resizable(True, True)

        # Expand and fill widgets inside the window
        confirmation_window.grid_columnconfigure(0, weight=1)
        confirmation_window.grid_rowconfigure(0, weight=1)


        # Message Label
        message_label = ttk.Label(
            confirmation_window,
            text="\n\nYou are about to set the new beginning balance",
            justify="center",
            font=("Helvetica", 14, "bold"),
            bootstyle=WARNING

        )
        message_label.pack(pady=5)

        # Message Label
        message_label = ttk.Label(
            confirmation_window,
            text=(
                "Please review all the data you have entered before proceeding.\n\n"
                "Setting a new beginning balance is a permanent action and cannot be undone.\n"
                "Ensure that all values are correct before confirming.\n\n"
                "To proceed, type 'YES' in the confirmation box."
            ),
            justify="center",
            font=("Helvetica", 10),
        )
        message_label.pack(pady=5)

        # Entry field
        confirm_entry = ttk.Entry(confirmation_window, font=("Arial", 12),
                                  justify = "center")
        confirm_entry.pack(padx=20, pady=5)

        # Frame for buttons
        button_frame = ttk.Frame(confirmation_window)
        button_frame.pack(fill="x", padx=10, pady=10)  # Expand the frame horizontally

        # Configure button frame columns
        button_frame.columnconfigure(0, weight=1)  # Left side (Cancel)
        button_frame.columnconfigure(1, weight=1)  # Right side (Submit)

        # Cancel Button (Left)
        cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            bootstyle=DANGER,
            command=confirmation_window.destroy
        )
        cancel_button.grid(row=0, column=0, padx=5, sticky="w")  # Align to left

        # Submit Button (Right, Initially Disabled)
        submit_button = ttk.Button(
            button_frame,
            text="Submit",
            bootstyle=SUCCESS,
            state=DISABLED,
            command=lambda: [update_stock(), confirmation_window.destroy()]
        )
        submit_button.grid(row=0, column=1, padx=5, sticky="e")  # Align to right

        # Function to validate entry field
        def validate_entry(event):
            if confirm_entry.get().strip() == "YES":
                submit_button.config(state=NORMAL)
            else:
                submit_button.config(state=DISABLED)

        confirm_entry.bind("<KeyRelease>", validate_entry)



        # Function to show confirmation panel
    def confirmation_panel_clear():
        # confirmation_window = ttk.Toplevel(form_frame)
        # confirmation_window.title("Confirm Action")
        # confirmation_window.geometry("450x410")
        # confirmation_window.resizable(True, True)

        confirmation_window = ttk.Toplevel(form_frame)
        confirmation_window.title("Confirm Action")

        # Get the screen width and height
        screen_width = confirmation_window.winfo_screenwidth()
        screen_height = confirmation_window.winfo_screenheight()

        # Set a dynamic size (proportional to the screen size)
        window_width = int(screen_width * 0.35)  # Adjust width as needed
        window_height = int(screen_height * 0.51)  # Adjust height as needed

        # Calculate position for centering
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 3  # Position slightly higher

        # Apply geometry dynamically
        confirmation_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Allow resizing but maintain proportions
        confirmation_window.resizable(True, True)

        # Expand and fill widgets inside the window
        confirmation_window.grid_columnconfigure(0, weight=1)
        confirmation_window.grid_rowconfigure(0, weight=1)

        # Message Label
        message_label = ttk.Label(
            confirmation_window,
            text="\n\nYou are about to clear ALL recently added data.",
            justify="center",
            font=("Helvetica", 12, "bold"),
            bootstyle=WARNING

        )
        message_label.pack(pady=5)

        # Message Label
        message_label = ttk.Label(
            confirmation_window,
            text=(
                "The recently added data from the following forms will be\ncleared or removed:\n"
                    "   - Notes Form\n"
                    "   - Receiving Form\n"
                    "   - Outgoing Form\n"
                    "   - Tranfer Form\n"
                    "   - Preparation Form\n"
                    "   - Change Status Form\n\n"
                
                "Please ensure that the data that will be cleared are unimportant\nbefore clearing all of it.\n"
            ),
            justify="left",
            font=("Helvetica", 10),
        )
        message_label.pack(pady=5)

        # Message Label
        message_label = ttk.Label(
            confirmation_window,
            text=("To proceed, type 'YES' in the confirmation box."),
            justify="center",
            font=("Helvetica", 10),
        )
        message_label.pack(pady=5)


        # Entry field
        confirm_entry = ttk.Entry(confirmation_window, font=("Arial", 12),
                                  justify="center")
        confirm_entry.pack(padx=20, pady=5)

        # Frame for buttons
        button_frame = ttk.Frame(confirmation_window)
        button_frame.pack(fill="x", padx=10, pady=10)  # Expand the frame horizontally

        # Configure button frame columns
        button_frame.columnconfigure(0, weight=1)  # Left side (Cancel)
        button_frame.columnconfigure(1, weight=1)  # Right side (Submit)

        # Cancel Button (Left)
        cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            bootstyle=DANGER,
            command=confirmation_window.destroy
        )
        cancel_button.grid(row=0, column=0, padx=5, sticky="w")  # Align to left

        # Submit Button (Right, Initially Disabled)
        submit_button = ttk.Button(
            button_frame,
            text="Submit",
            bootstyle=SUCCESS,
            state=DISABLED,
            command=lambda: [clear_all_data_from_forms(), confirmation_window.destroy()]
        )
        submit_button.grid(row=0, column=1, padx=5, sticky="e")  # Align to right


        # Function to validate entry field
        def validate_entry(event):
            if confirm_entry.get().strip() == "YES":
                submit_button.config(state=NORMAL)
            else:
                submit_button.config(state=DISABLED)

        confirm_entry.bind("<KeyRelease>", validate_entry)



    # Create a frame for the form inputs
    form_frame = ttk.Frame(note_form_tab)
    form_frame.pack(fill=X, pady=10, padx=20)

    # Add button to clear data
    btn_clear = ttk.Button(
        form_frame,
        text="Clear All Data",
        command=confirmation_panel_clear,
        bootstyle=WARNING,
    )
    btn_clear.grid(row=0, column=0, pady=20, padx=5, sticky=W)
    ToolTip(btn_clear, text="Click the button to clear all the data.")

    # Checkbox for Warehouse lock
    checkbox_date_var = ttk.BooleanVar(value=False)  # Integer variable to store checkbox state (0 or 1)
    lock_warehouse = ttk.Checkbutton(
        form_frame,
        text="Lock Date",
        variable=checkbox_date_var,
        bootstyle="round-toggle"
    )
    lock_warehouse.grid(row=1, column=0, padx=5, pady=0, sticky=W)  # Position the checkbox next to the combobox
    ToolTip(lock_warehouse, text="Lock the date")


    # Calculate yesterday's date
    yesterday_date = datetime.now() - timedelta(days=1)

    # Create the DateEntry widget with yesterday's date as the default value
    date_entry = ttk.DateEntry(
        form_frame,
        bootstyle=PRIMARY,
        dateformat="%m/%d/%Y",
        startdate=yesterday_date,  # Set yesterday's date
        width=40
    )
    date_entry.grid(row=2, column=0, padx=5, sticky=W)

    ToolTip(date_entry, text=f"This is the default consumption date. You can manually change it.")


    # Add button to export data into excel
    btn_export = ttk.Button(
        form_frame,
        text="EXPORT TO EXCEL",
        command=export_data_to_excel,
        bootstyle=SUCCESS
    )
    btn_export.grid(row=2, column=2, pady=10)
    ToolTip(btn_export, text="Click the button to export the data into excel.")


    # Add button to submit data
    btn_submit = ttk.Button(
        form_frame,
        text="MAKE THIS DATA AS THE NEW BEGINNING BALANCE",
        command=show_confirmation_panel,
        bootstyle=INFO
    )
    btn_submit.grid(row=3, column=0, pady=10,padx=5,)
    ToolTip(btn_submit, text="Click the button to make this data as the new beginning balance")


    # Calling the table
    note_table = NoteTable(note_form_tab)

def create_soh_whse_excel(date_entry_value, data):
    # Convert the string into a datetime object
    notes_date_object = datetime.strptime(date_entry_value, "%Y-%m-%d")
    notes_formatted_date = notes_date_object.strftime("%B %d, %Y")
    notes_date = notes_formatted_date

    wh_date_object = datetime.strptime(date_entry_value, "%Y-%m-%d")
    wh_formatted_date = wh_date_object.strftime("%m/%d/%Y")
    wh_date = wh_formatted_date

    # Create a new workbook
    wb = Workbook()

    # Sheet 1: NOTES
    notes_sheet = wb.active
    notes_sheet.title = "NOTES"

    # Populate the NOTES sheet
    notes_sheet["A1"] = "Daily Ending Inventory Report from:"
    notes_sheet["B1"] = f"{notes_date}"  # Sample date
    notes_sheet["A2"] = "List of Batches Included in Report"
    notes_sheet["A3"] = "MASTERBATCH"
    notes_sheet.append(["PRODUCT CODE", "LOT#", "Product Kind"])

    # Fetch data from the API
    try:
        api_url = f"{server_ip}/api/notes/v1/list/"
        response = requests.get(api_url)
        response.raise_for_status()
        api_data = response.json()

        # Insert data into the NOTES sheet
        for record in api_data:
            notes_sheet.append([
                record["product_code"],
                record["lot_number"],
                record["product_kind_id"]
            ])

    except requests.exceptions.RequestException as e:
        # print(f"Error fetching data from API: {e}")
        return

    # Apply formatting
    for col in ["A", "B", "C"]:
        for cell in notes_sheet[col]:
            cell.alignment = Alignment(horizontal="center", vertical="center")
    notes_sheet["A4"].font = Font(bold=True)

    # Function to create a WHSE sheet
    def create_whse_sheet(sheet_name):
        sheet = wb.create_sheet(sheet_name)

        # Set header based on warehouse number
        if sheet_name == "WHSE1":
            wh_header = "WHSE #1 - Excess"
        elif sheet_name == "WHSE2":
            wh_header = "WHSE #2 - Excess"
        elif sheet_name == "WHSE4":
            wh_header = "WHSE #4 - Excess"

        # Populate the header
        header = [
            "Date", "No of bags", "qty per packing",
            f"{wh_header}", "Total", "Status"
        ]
        sheet.append(header)
        sheet["A1"] = f"{wh_date}"  # Example date
        sheet["A1"].font = Font(bold=True)

        # Insert data into the respective warehouse sheet
        for record in data:
            if record["warehousenumber"] == int(sheet_name[-1]):  # Match warehouse number to sheet

                row = [
                    record["rmcode"],  # rmcode
                    "",  # No of bags (blank)
                    "",  # qty per packing (blank)
                    "",  # Excess column (blank)
                    float(record["new_beginning_balance"]),  # Total
                    "" if record["status"].lower() == "good" else record["status"],  # Store blank if status is 'good'
                    ""  # Drop list (blank)
                ]
                sheet.append(row)

                # Apply number format (thousands separator)
                qty_cell = sheet.cell(row=sheet.max_row, column=5)  # Column 5 is qty_value
                qty_cell.number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1  # Apply Excel formatting

        # Create a dropdown list for the "drop list" column
        dv = DataValidation(
            type="list",
            formula1='"held : under evaluation,held : reject,held : contaminated"',
            allow_blank=True,
            showDropDown=True
        )
        # Apply the data validation to the G column for rows 2 to 100
        for row in range(2, 101):
            cell = f"G{row}"  # Example: G2, G3, ..., G100
            dv.add(sheet[cell])
        sheet.add_data_validation(dv)

    # Create sheets for WHSE1, WHSE2, and WHSE4
    create_whse_sheet("WHSE1")
    create_whse_sheet("WHSE2")
    create_whse_sheet("WHSE4")


    # Use tkinter's asksaveasfilename for file dialog
    file_path = asksaveasfilename(
        title="Save Excel File",
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")]
    )

    # Save the workbook
    if file_path:
        try:
            wb.save(file_path)
            Messagebox.show_info(f"Excel file saved successfully at {file_path}", "The File is Successfully Saved")
        except Exception as e:
            Messagebox.show_error(f"Error saving file: {e}", "Success")

    else:
        # Saving the file was cancelled
        pass

def get_soh_data():

    """Fetch data from API and format for table rowdata."""
    url = f"{server_ip}/api/get/new_soh/"
    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        return []

    # Return both buttons as a tuple
    return []







