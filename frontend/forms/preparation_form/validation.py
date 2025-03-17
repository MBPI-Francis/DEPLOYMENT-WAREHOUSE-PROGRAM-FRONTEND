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

    # Validation function for numeric input
    @staticmethod
    def validate_numeric_input(input_value):
        """
        Validates that the input contains only numeric characters or a decimal point
        with up to two decimal places.
        """
        if input_value == "":
            return True  # Allow empty input
        try:
            # Convert input to float and ensure it has up to two decimal places
            float_value = float(input_value)
            parts = input_value.split(".")
            if len(parts) == 1:  # No decimal point
                return True
            elif len(parts) == 2 and len(parts[1]) <= 2:  # Check decimal places
                return True
            else:
                return False
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
