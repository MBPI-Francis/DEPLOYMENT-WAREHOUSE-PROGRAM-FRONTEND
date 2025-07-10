import requests
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

            elif key == "qty_kg" and not value:
                text_list.append("Quantity")

            elif key == "status_id" and not value:
                text_list.append("Status")

            elif key == "adjustment_date" and not value:
                text_list.append("Date of Adjustment")

            elif key == "reference_date" and not value:
                text_list.append("Referenced Date")

            elif key == "incident_date" and not value:
                text_list.append("Date of Incident")

            elif key == "spillage_form_number" and not value:
                text_list.append("Spillage Report #")

            elif key == "incident_date" and not value:
                text_list.append("Date of Incident")

            elif key == "person_responsible" and not value:
                text_list.append("Person Responsible")

        return text_list

    # Validation function for numeric input
    # def validate_numeric_input(input_value):
    #     """
    #     Validates that the input contains only numeric characters or a decimal point
    #     with up to two decimal places.
    #     """
    #     if input_value == "":
    #         return True  # Allow empty input
    #     try:
    #         # Convert input to float and ensure it has up to two decimal places
    #         float_value = float(input_value)
    #         parts = input_value.split(".")
    #         if len(parts) == 1:  # No decimal point
    #             return True
    #         elif len(parts) == 2 and len(parts[1]) <= 2:  # Check decimal places
    #             return True
    #         else:
    #             return False
    #     except ValueError:
    #         return False  # Reject invalid inputs

        # Function to validate numeric input (only numbers, commas, and one decimal point)
    @staticmethod
    def validate_numeric_input(input_value):
        if input_value.strip() == "":
            return True  # Allow empty input

        raw_value = input_value.replace(",", "").strip()  # Remove commas and whitespace

        # Allow just '+' or '-' as partial valid input while typing
        if raw_value in ("-", "+"):
            return True

        # Only one leading + or - sign is allowed
        if raw_value.startswith(("+", "-")):
            numeric_part = raw_value[1:]
        else:
            numeric_part = raw_value

        # Must be digits or one optional decimal point
        if numeric_part.count(".") > 1:
            return False

        try:
            float(raw_value)  # Check if fully convertible to float

            # Ensure max of two decimal places
            parts = numeric_part.split(".")
            if len(parts) == 2 and len(parts[1]) > 2:
                return False

            return True
        except ValueError:
            return False


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

            response = requests.get(f"{server_ip}/api/check/rm-stock-value/adjustment_form/", params=params)

            if response.status_code == 200:

                is_valid = response.json()

                if is_valid:
                    return is_valid

                else:
                    return False
        except requests.exceptions.RequestException as e:
            return None



    @staticmethod
    def validate_soh_value_for_update(rm_id, warehouse_id, old_qty: float, entered_qty: float, status_id=None):
        # Prepare parameters
        params = {
            "rm_id": rm_id,
            "warehouse_id": warehouse_id,
            "prev_entered_qty": old_qty,
            "new_entered_qty": float(entered_qty)
        }


        # Include status_id only if it's not None
        if status_id:
            params["status_id"] = status_id
        # Handle response
        try:
            # Make the GET request
            # response = requests.get(f"{server_ip}/api/check/rm-stock-value/for-update/adjustment_form/", params=params)
            response = requests.get(f"{server_ip}/api/check/rm-stock-value/for-update/", params=params)

            if response.status_code == 200:

                is_valid = response.json()

                if is_valid:
                    return is_valid

                else:
                    return False
        except requests.exceptions.RequestException as e:
            return None
