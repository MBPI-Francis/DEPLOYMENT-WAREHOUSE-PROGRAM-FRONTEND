import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import requests
from backend.settings.database import server_ip
from ttkbootstrap.tooltip import ToolTip
from ttkbootstrap.dialogs.dialogs import Messagebox
from datetime import datetime, timedelta
from .table import SubmitEntriesTable
from tkinter.filedialog import asksaveasfilename
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.styles import numbers
from frontend.forms.shared import SharedFunctions
from frontend.constant import FormConstant
import os
import time

# Try to import win32com.client for full workbook encryption
try:
    import win32com.client as win32

    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

excel_password = FormConstant.EXCEL_SOH_PASSWORD.value


def entry_fields(note_form_tab):
    shared_functions = SharedFunctions()

    def export_data_to_excel():
        date_entry_value = date_entry.entry.get()
        try:
            date_entry_value = datetime.strptime(date_entry_value, "%m/%d/%Y").strftime("%Y-%m-%d")
        except ValueError:
            Messagebox.show_error("Invalid date format. Please use MM/DD/YYYY.", "Date Entry Error")
            return

        try:
            data = get_soh_data()
            create_soh_whse_excel(date_entry_value, data)
        except requests.exceptions.RequestException as e:
            Messagebox.show_info(e, "Data Entry Error")

    def update_stock():
        date_entry_value = date_entry.entry.get()
        try:
            date_entry_value = datetime.strptime(date_entry_value, "%m/%d/%Y").strftime("%Y-%m-%d")
        except ValueError:
            Messagebox.show_error("Invalid date format. Please use MM/DD/YYYY.", "Date Entry Error")
            return

        try:
            response = requests.post(f"{server_ip}/api/update_stock_on_hand/?params_date={date_entry_value}")
            if response.status_code == 200:
                try:
                    response = requests.post(f"{server_ip}/api/update-date-computed")
                except requests.exceptions.RequestException:
                    pass
                note_table.refresh_table()
                Messagebox.show_info("The new beginning balance has been successfully updated!", "Success")
        except requests.exceptions.RequestException as e:
            Messagebox.show_info(e, "Data Entry Error")

    def show_confirmation_panel():
        confirmation_window = ttk.Toplevel(form_frame)
        confirmation_window.title("Confirm Action")
        screen_width = confirmation_window.winfo_screenwidth()
        screen_height = confirmation_window.winfo_screenheight()
        window_width = int(screen_width * 0.42)
        window_height = int(screen_height * 0.43)
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 3
        confirmation_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        message_label = ttk.Label(confirmation_window, text="\n\nYou are about to set the new beginning balance",
                                  justify="center", font=("Arial", 14, "bold"), bootstyle=WARNING)
        message_label.pack(pady=5)

        ttk.Label(confirmation_window, text="Please review all data... Setting a new balance is permanent.",
                  justify="center").pack()

        confirm_entry = ttk.Entry(confirmation_window, font=("Arial", 12), justify="center")
        confirm_entry.pack(padx=20, pady=5)

        submit_button = ttk.Button(confirmation_window, text="Submit", bootstyle=SUCCESS, state=DISABLED,
                                   command=lambda: [update_stock(), confirmation_window.destroy()])
        submit_button.pack(pady=10)

        def validate_entry(event):
            submit_button.config(state=NORMAL if confirm_entry.get().strip() == "YES" else DISABLED)

        confirm_entry.bind("<KeyRelease>", validate_entry)

    def format_date_while_typing(event):
        text = date_entry.entry.get().replace("/", "")
        if len(text) == 8:
            formatted_date = f"{text[:2]}/{text[2:4]}/{text[4:]}"
            date_entry.entry.delete(0, "end")
            date_entry.entry.insert(0, formatted_date)

    form_frame = ttk.Frame(note_form_tab)
    form_frame.pack(fill=X, pady=10, padx=20)

    date_entry = ttk.DateEntry(form_frame, bootstyle=PRIMARY, dateformat="%m/%d/%Y",
                               startdate=datetime.now() - timedelta(days=1), width=30)
    date_entry.grid(row=2, column=0, padx=5, sticky=W)

    btn_export = ttk.Button(form_frame, text="EXPORT TO EXCEL", command=export_data_to_excel, bootstyle=SUCCESS)
    btn_export.grid(row=2, column=2, padx=5)

    btn_submit = ttk.Button(form_frame, text="MAKE NEW BEGINNING BALANCE", command=show_confirmation_panel,
                            bootstyle=INFO)
    btn_submit.grid(row=2, column=3, padx=5)

    note_table = SubmitEntriesTable(note_form_tab)


def create_soh_whse_excel(date_entry_value, data):
    notes_date = datetime.strptime(date_entry_value, "%Y-%m-%d").strftime("%B %d, %Y")
    wh_date = datetime.strptime(date_entry_value, "%Y-%m-%d").strftime("%m/%d/%Y")

    wb = Workbook()
    notes_sheet = wb.active
    notes_sheet.title = "NOTES"
    notes_sheet["A1"], notes_sheet["B1"] = "Daily Ending Inventory Report from:", notes_date
    notes_sheet.append(["PRODUCT CODE", "LOT#", "Product Kind"])

    try:
        api_data = requests.get(f"{server_ip}/api/notes/v1/list/").json()
        for record in api_data:
            notes_sheet.append(
                [record.get("product_code", ""), record.get("lot_number", ""), record.get("product_kind_id", "")])
    except:
        pass

    # Dynamic Warehouse Logic
    def create_whse_sheet(wh_num):
        sheet = wb.create_sheet(f"WHSE{wh_num}")
        header = ["Date", "No of bags", "qty per packing", f"WHSE #{wh_num} - Excess", "Total", "Status"]
        sheet.append(header)
        sheet["A1"] = wh_date

        for record in data:
            if str(record.get("warehousenumber")) == str(wh_num):
                row = [record.get("rmcode", ""), "", "", "", float(record.get("new_beginning_balance", 0.0)),
                       "" if record.get("status", "").lower() == "good" else record.get("status", "")]
                sheet.append(row)
                sheet.cell(row=sheet.max_row, column=5).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1

    # Find all unique warehouse numbers in the data
    whse_list = sorted(list(set(str(item.get("warehousenumber")) for item in data if item.get("warehousenumber"))))
    for wh_num in whse_list:
        create_whse_sheet(wh_num)

    file_path = asksaveasfilename(title="Save Excel File", defaultextension=".xlsx",
                                  filetypes=[("Excel files", "*.xlsx")])

    if file_path:
        # Convert path to absolute Windows format to prevent the 'Open Method Failed' error
        file_path = os.path.normpath(os.path.abspath(file_path))

        try:
            wb.save(file_path)
            wb.close()  # Ensure openpyxl releases the file
            time.sleep(1)  # Wait for OS to release file lock

            if excel_password and WIN32_AVAILABLE:
                excel_app = None
                try:
                    # DispatchEx creates a SEPARATE process (doesn't touch your open files)
                    excel_app = win32.DispatchEx("Excel.Application")
                    excel_app.Visible = False
                    excel_app.DisplayAlerts = False

                    workbook = excel_app.Workbooks.Open(file_path)
                    workbook.Password = excel_password
                    workbook.Save()
                    workbook.Close()
                except Exception as e:
                    Messagebox.show_error(f"Excel Automation Error: {e}")
                finally:
                    if excel_app:
                        excel_app.Quit()

            Messagebox.show_info(f"Saved successfully at:\n{file_path}", "Success")
        except Exception as e:
            Messagebox.show_error(f"Error: {e}")


def get_soh_data():
    try:
        return requests.get(f"{server_ip}/api/get/new_soh/").json()
    except:
        return []