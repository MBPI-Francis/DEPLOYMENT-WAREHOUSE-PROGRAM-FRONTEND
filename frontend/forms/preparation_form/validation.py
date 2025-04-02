import requests
from uuid import UUID
from backend.settings.database import server_ip


class EntryValidation:
    @staticmethod
    def entry_validation(entries: dict):
        text_list = []

        for key, value in entries.items():

            if key == "warehouse_id" and not value:
                text_list.append("Warehouse")

            elif key == "ref_number" and not value:
                text_list.append("Reference Number")

            elif key == "rm_code_id" and not value:
                text_list.append("Raw Material")

            elif key == "status_id" and not value:
                text_list.append("Status")

            elif key == "qty_prepared" and not value:
                text_list.append("Quantity (Prepared)")

            # elif key == "qty_return" and not value:
            #     text_list.append("Quantity (Return")

            elif key == "outgoing_date" and not value:
                text_list.append("Outgoing Date")
        return text_list



    @staticmethod
    def validate_numeric_input(input_value):
        if input_value == "":
            return True  # Allow empty input

        raw_value = input_value.replace(",", "")  # Remove commas for validation

        if raw_value.count(".") > 1:  # Ensure only one decimal point
            return False

        try:
            float_value = float(raw_value)  # Check if it's a valid float

            # Ensure only two decimal places
            parts = raw_value.split(".")
            if len(parts) == 2 and len(parts[1]) > 2:
                return False

            return True
        except ValueError:
            return False  # Reject invalid inputs



