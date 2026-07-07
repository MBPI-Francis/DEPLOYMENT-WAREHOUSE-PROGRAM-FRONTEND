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
                    requests.post(f"{server_ip}/api/update-date-computed")
                except:
                    pass
                note_table.refresh_table()
                Messagebox.show_info("Successfully updated!", "Success")
        except requests.exceptions.RequestException as e:
            Messagebox.show_info(e, "Data Entry Error")

    form_frame = ttk.Frame(note_form_tab)
    form_frame.pack(fill=X, pady=10, padx=20)

    date_entry = ttk.DateEntry(form_frame, bootstyle=PRIMARY, dateformat="%m/%d/%Y",
                               startdate=datetime.now() - timedelta(days=1), width=30)
    date_entry.grid(row=2, column=0, padx=5, sticky=W)

    btn_export = ttk.Button(form_frame, text="EXPORT TO EXCEL", command=export_data_to_excel, bootstyle=SUCCESS)
    btn_export.grid(row=2, column=2, padx=5)

    def show_confirmation():
        # (Your original confirmation logic remains here)
        pass

    btn_submit = ttk.Button(form_frame, text="MAKE THIS DATA AS THE NEW BEGINNING BALANCE", command=show_confirmation,
                            bootstyle=INFO)
    btn_submit.grid(row=2, column=3, padx=5)

    note_table = SubmitEntriesTable(note_form_tab)


def create_soh_whse_excel(date_entry_value, data):
    notes_date = datetime.strptime(date_entry_value, "%Y-%m-%d").strftime("%B %d, %Y")
    wh_date = datetime.strptime(date_entry_value, "%Y-%m-%d").strftime("%m/%d/%Y")

    wb = Workbook()

    # --- RESTORED NOTES SHEET STRUCTURE ---
    notes_sheet = wb.active
    notes_sheet.title = "NOTES"
    notes_sheet["A1"] = "Daily Ending Inventory Report from:"
    notes_sheet["B1"] = f"{notes_date}"
    notes_sheet["A2"] = "List of Batches Included in Report"
    notes_sheet["A3"] = "MASTERBATCH"
    notes_sheet.append(["PRODUCT CODE", "LOT#", "Product Kind"])  # Row 4

    try:
        api_data = requests.get(f"{server_ip}/api/notes/v1/list/").json()
        for record in api_data:
            notes_sheet.append(
                [record.get("product_code", ""), record.get("lot_number", ""), record.get("product_kind_id", "")])
    except:
        pass

    # Restore NOTES Alignment and Font
    for col in ["A", "B", "C"]:
        for cell in notes_sheet[col]:
            cell.alignment = Alignment(horizontal="center", vertical="center")
    notes_sheet["A4"].font = Font(bold=True)

    # --- RESTORED DYNAMIC WHSE SHEET STRUCTURE ---
    def create_whse_sheet(whse_num):
        sheet = wb.create_sheet(f"WHSE{whse_num}")
        wh_header = f"WHSE #{whse_num} - Excess"

        header = ["Date", "No of bags", "qty per packing", f"{wh_header}", "Total", "Status"]
        sheet.append(header)  # Becomes Row 2 because A1 is set below

        sheet["A1"] = f"{wh_date}"
        # Restore Bold Formatting for Row 1
        for col_letter in ["A", "B", "C", "D", "E", "F"]:
            sheet[f"{col_letter}1"].font = Font(bold=True)

        for record in data:
            if str(record.get("warehousenumber")) == str(whse_num):
                row = [
                    record.get("rmcode", ""), "", "", "",
                    float(record.get("new_beginning_balance", 0.0)),
                    "" if record.get("status", "").lower() == "good" else record.get("status", ""),
                    ""
                ]
                sheet.append(row)
                sheet.cell(row=sheet.max_row, column=5).number_format = numbers.FORMAT_NUMBER_COMMA_SEPARATED1

        # Restore Data Validation
        dv = DataValidation(type="list", formula1='"held : under evaluation,held : reject,held : contaminated"',
                            allow_blank=True, showDropDown=True)
        for row_num in range(3, sheet.max_row + 1):
            dv.add(sheet[f"G{row_num}"])
        sheet.add_data_validation(dv)

    # Automatically detect all warehouse numbers from data
    unique_whse_nums = sorted(list(set(str(r.get("warehousenumber")) for r in data if r.get("warehousenumber"))))
    for wh_num in unique_whse_nums:
        create_whse_sheet(wh_num)

    file_path = asksaveasfilename(title="Save Excel File", defaultextension=".xlsx",
                                  filetypes=[("Excel files", "*.xlsx")])

    if file_path:
        file_path = os.path.normpath(os.path.abspath(file_path))
        try:
            wb.save(file_path)
            wb.close()
            time.sleep(1)

            if excel_password and WIN32_AVAILABLE:
                excel_app = None
                try:
                    excel_app = win32.DispatchEx("Excel.Application")
                    excel_app.Visible, excel_app.DisplayAlerts = False, False
                    workbook = excel_app.Workbooks.Open(file_path)
                    workbook.Password = excel_password
                    workbook.Save()
                    workbook.Close()
                except Exception as e:
                    Messagebox.show_error(f"Password Error: {e}")
                finally:
                    if excel_app: excel_app.Quit()

            Messagebox.show_info(f"Saved successfully at:\n{file_path}", "File Saved")
        except Exception as e:
            Messagebox.show_error(f"Error: {e}")


def get_soh_data():
    try:
        return requests.get(f"{server_ip}/api/get/new_soh/").json()
    except:
        return []