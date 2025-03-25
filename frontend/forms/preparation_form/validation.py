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


    @staticmethod
    def validate_soh_value(rm_id, warehouse_id, entered_qty: float, status_id=None):
        # Prepare parameters
        params = {
            "rm_id": rm_id,
            "warehouse_id": warehouse_id,
            "entered_qty": float(entered_qty),
        }

        # Include status_id only if it's not None
        if status_id:
            params["status_id"] = status_id
        # Handle response

        try:
            # Make the GET request

            response = requests.get(f"{server_ip}/api/check/rm-stock-value/", params=params)

            if response.status_code == 200:

                is_valid = response.json()

                if is_valid:
                    return is_valid

                else:
                    return False
        except requests.exceptions.RequestException as e:
            return None

    @staticmethod
    def validate_soh_value_for_update(rm_id, warehouse_id, entered_qty: float, status_id=None):
        # Prepare parameters
        params = {
            "rm_id": rm_id,
            "warehouse_id": warehouse_id,
            "entered_qty": float(entered_qty),
        }

        # Include status_id only if it's not None
        if status_id:
            params["status_id"] = status_id
        # Handle response
        try:
            # Make the GET request
            response = requests.get(f"{server_ip}/api/check/rm-stock-value/for-update/", params=params)

            if response.status_code == 200:

                is_valid = response.json()

                if is_valid:
                    return is_valid

                else:
                    return False
        except requests.exceptions.RequestException as e:
            return None
