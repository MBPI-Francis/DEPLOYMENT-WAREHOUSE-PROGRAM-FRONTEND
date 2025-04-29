


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

            elif key == "outgoing_date" and not value:
                text_list.append("Outgoing Date")
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