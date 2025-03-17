


class EntryValidation:
    def entry_validation(entries: dict):
        text_list = []

        for key, value in entries.items():

            if key == "wh_number" and not value:
                text_list.append("Warehouse Number")

            elif key == "wh_name" and not value:
                text_list.append("Warehouse Name")


        return text_list

    # Validation function for numeric input
    def validate_numeric_input(input_value):
        """
        Validates that the input contains only numeric characters.
        """
        return input_value.isdigit() or input_value == ""  # Allow digits or empty input