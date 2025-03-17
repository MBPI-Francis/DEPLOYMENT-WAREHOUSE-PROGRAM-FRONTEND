


class EntryValidation:
    def entry_validation(entries: dict):
        text_list = []

        for key, value in entries.items():

            if key == "rm_code" and not value:
                text_list.append("Raw Material Code")
        return text_list

    # Validation function for numeric input
    def validate_numeric_input(input_value):
        """
        Validates that the input contains only numeric characters.
        """
        return input_value.isdigit() or input_value == ""  # Allow digits or empty input