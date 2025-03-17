class EntryValidation:
    def entry_validation(entries: dict):
        text_list = []

        for key, value in entries.items():

            if key == "product_code" and not value:
                text_list.append("Product Code")

            elif key == "lot_number" and not value:
                text_list.append("Lot Number")

            elif key == "product_kind_id" and not value:
                text_list.append("Product Kind")

            elif key == "consumption_date" and not value:
                text_list.append("Consumption Date")
        return text_list