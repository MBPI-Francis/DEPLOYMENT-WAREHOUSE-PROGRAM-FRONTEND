# This where all the shared variable stored
# All the variables functions we're used by the program.

import requests
from backend.settings.database import server_ip
import threading
import time
from tkinter.font import Font
import tkinter as tk
from tkinter import ttk, StringVar, W

# class SharedFunctions:
#     _instance = None
#     _cache = {
#         "warehouses": {"data": None, "timestamp": 0},
#         "raw_materials": {"data": None, "timestamp": 0},
#         "status": {"data": None, "timestamp": 0},
#     }
#     CACHE_TIMEOUT = 60  # Cache duration in seconds
#
#     def __new__(cls):
#         """Ensure only one instance exists (Singleton)."""
#         if cls._instance is None:
#             cls._instance = super(SharedFunctions, cls).__new__(cls)
#             cls._instance.start_cache_refresh()  # Start background cache updates
#         return cls._instance
#
#     def _fetch_data(self, endpoint):
#         """Fetch data from API."""
#         url = server_ip + endpoint
#         try:
#             response = requests.get(url, timeout=5)
#             if response.status_code == 200:
#                 return response.json()
#         except requests.RequestException:
#             pass
#         return []
#
#     def refresh_cache(self):
#         """Fetch data periodically and update cache."""
#         while True:
#             self._cache["warehouses"]["data"] = self._fetch_data("/api/warehouses/v1/list/")
#             self._cache["warehouses"]["timestamp"] = time.time()
#
#             self._cache["raw_materials"]["data"] = self._fetch_data("/api/raw_materials/v1/list/")
#             self._cache["raw_materials"]["timestamp"] = time.time()
#
#             self._cache["status"]["data"] = self._fetch_data("/api/status/v1/list/")
#             self._cache["status"]["timestamp"] = time.time()
#
#             time.sleep(self.CACHE_TIMEOUT)  # Refresh every 60 seconds
#
#     def start_cache_refresh(self):
#         """Start a background thread to update cache."""
#         threading.Thread(target=self.refresh_cache, daemon=True).start()
#
#     def get_warehouse_api(self):
#         """Return cached warehouse data."""
#         return self._cache["warehouses"]["data"] or []
#
#     def get_rm_code_api(self):
#         """Return cached raw materials data."""
#         return self._cache["raw_materials"]["data"] or []
#
#     def get_status_api(self):
#         """Return cached status data."""
#         return self._cache["status"]["data"] or []


# This is the improved version the SharedFunction class
# This improvement removed the redundancy of the api request (e.g. this api /api/warehouses/v1/list/ was called 10 times)
class SharedFunctions:
    _instance = None
    _cache = {
        "warehouses": {"data": None},
        "raw_materials": {"data": None},
        "status": {"data": None},
    }

    def __init__(self):
        """Initialize the SharedFunctions instance."""
        self.custom_font_size = Font(family="Arial", size=10)

    def __new__(cls):
        """Ensure only one instance exists (Singleton)."""
        if cls._instance is None:
            cls._instance = super(SharedFunctions, cls).__new__(cls)
            cls._instance._initialize_cache()  # Load cache once at startup
        return cls._instance





    def _fetch_data(self, endpoint):
        """Fetch data from API."""
        url = server_ip + endpoint
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return response.json()
        except requests.RequestException:
            pass
        return []

    def _initialize_cache(self):
        """Fetch data once and store it in cache."""
        self._cache["warehouses"]["data"] = self._fetch_data("/api/warehouses/v1/list/")
        self._cache["raw_materials"]["data"] = self._fetch_data("/api/raw_materials/v1/list/")
        self._cache["status"]["data"] = self._fetch_data("/api/status/v1/list/")

    def get_warehouse_api(self):
        """Return cached warehouse data."""
        return self._cache["warehouses"]["data"] or []

    # def get_rm_code_api(self):
    #     """Return cached raw materials data."""
    #     return self._cache["raw_materials"]["data"] or []
    def get_rm_code_api(self, force_refresh=False):
        """Return raw materials data, with optional forced refresh."""
        if force_refresh or self._cache["raw_materials"]["data"] is None:
            self._cache["raw_materials"]["data"] = self._fetch_data("/api/raw_materials/v1/list/")
        return self._cache["raw_materials"]["data"] or []

    def get_status_api(self):
        """Return cached status data."""
        return self._cache["status"]["data"] or []



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
            response = requests.get(f"{server_ip}/api/check/rm-stock-value/for-update/", params=params)

            if response.status_code == 200:

                is_valid = response.json()

                if is_valid:
                    return is_valid

                else:
                    return False
        except requests.exceptions.RequestException as e:
            return None

    @staticmethod
    def focus_next_widget(event, next_widget):
        next_widget.focus_set()
        return "break"  # Prevent default Tab behavior



class NumericInputFormatter:
    def __init__(self, entry_widget: ttk.Entry, string_var: StringVar):
        """
        Initializes the formatter for a specific Tkinter Entry widget.

        Args:
            entry_widget: The ttk.Entry widget to format.
            string_var: The Tkinter StringVar associated with the entry_widget.
        """
        self.entry_widget = entry_widget
        self.string_var = string_var
        # Initialize the previous_raw_value for this specific entry
        self._previous_raw_value = ""

        # Bind the formatting method to the KeyRelease event of the entry widget
        self.entry_widget.bind("<KeyRelease>", self.format_input_event)

    def format_input_event(self, event):
        """
        Formats the input dynamically while preserving the cursor position.
        This method is designed to be bound to a Tkinter KeyRelease event.
        It uses the exact formatting and cursor logic provided by the user.
        """
        input_value = self.string_var.get()

        # Get current cursor position from the specific entry widget
        cursor_position = self.entry_widget.index("insert")

        # Remove commas for processing
        raw_value = input_value.replace(",", "")

        # Store the previous value to detect decimal removal (from instance attribute)
        previous_raw_value_local = self._previous_raw_value
        self._previous_raw_value = raw_value  # Store current for next iteration

        if raw_value == "":
            # Clear the entry and return if empty
            self.entry_widget.delete(0, "end")
            self.string_var.set("") # Also clear the StringVar
            return

        try:
            # Automatically fix "." to "0."
            if raw_value == ".":
                raw_value = "0."
                cursor_position += 1  # Move cursor after '0'
            elif raw_value.startswith("."):
                raw_value = "0" + raw_value
                cursor_position += 1

            # Check if a decimal was just removed
            decimal_was_removed = (
                    '.' in previous_raw_value_local and # Use the local previous value
                    '.' not in raw_value and
                    (len(raw_value) == len(previous_raw_value_local) - 1 or
                     (previous_raw_value_local.startswith("0.") and len(raw_value) == len(previous_raw_value_local) - 2)
                    )
            )

            # Allow typing like '123.'
            if raw_value[-1] == "." and raw_value.count(".") == 1:
                float_value = float(raw_value[:-1])  # parse without trailing dot
                formatted_value = "{:,}".format(int(float_value)) + "."

            elif "." in raw_value:
                float_value = float(raw_value)
                integer_part, decimal_part = raw_value.split(".")
                formatted_integer = "{:,}".format(int(integer_part))
                formatted_value = f"{formatted_integer}.{decimal_part}"

            else:
                float_value = float(raw_value)
                formatted_value = "{:,}".format(int(float_value))

            # Recalculate cursor position based on commas added/removed
            num_commas_before = input_value[:cursor_position].count(",")
            num_commas_after = formatted_value[:cursor_position].count(",")
            new_cursor_position = cursor_position + (num_commas_after - num_commas_before)

            # Adjust cursor position if decimal was removed and the new position should be at the start
            if decimal_was_removed:
                if previous_raw_value_local.startswith("0."):
                    if raw_value == "0":
                        new_cursor_position = 1
                    else:
                        new_cursor_position = 0
                # else: (Original code had a pass here, keeping it as is)
                #     pass

            # Apply formatted text and restore cursor
            self.entry_widget.delete(0, "end")
            self.entry_widget.insert(0, formatted_value)
            self.entry_widget.icursor(new_cursor_position)

        except ValueError:
            # If input is invalid (e.g., "abc"), do not format, just pass.
            # The validation command should ideally prevent such inputs anyway.
            pass



class AdjustmentNumericInputFormatter:
    def __init__(self, entry_widget: ttk.Entry, string_var: StringVar):
        """
        Initializes the formatter for a specific Tkinter Entry widget.

        Args:
            entry_widget: The ttk.Entry widget to format.
            string_var: The Tkinter StringVar associated with the entry_widget.
        """
        self.entry_widget = entry_widget
        self.string_var = string_var
        self._previous_raw_value = ""

        self.entry_widget.bind("<KeyRelease>", self.format_input_event)

    def format_input_event(self, event):
        """
        Formats the input dynamically while preserving the cursor position.
        """
        input_value = self.string_var.get()
        current_cursor_position = self.entry_widget.index("insert")

        previous_raw_value_local = self._previous_raw_value
        raw_value = input_value.replace(",", "")

        # --- Step 1: Handle "0." and "-0." auto-conversion and initial cursor adjustment ---
        modified_raw_value = raw_value
        initial_cursor_adjustment = 0

        if raw_value == ".":
            modified_raw_value = "0."
            initial_cursor_adjustment = 1
        elif raw_value.startswith("."):
            modified_raw_value = "0" + raw_value
            initial_cursor_adjustment = 1
        elif raw_value == "-.": # <--- NEW LOGIC HERE!
            modified_raw_value = "-0."
            initial_cursor_adjustment = 1 # Cursor moves after '0' (e.g., -0|)
        elif raw_value.startswith("-."): # Handles cases like -.123
            modified_raw_value = "-0" + raw_value[1:]
            initial_cursor_adjustment = 1


        self._previous_raw_value = raw_value # Store original raw_value for next iteration

        # --- Step 2: Early exit for incomplete/unformattable states ---
        if modified_raw_value == "":
            self.string_var.set("")
            self.entry_widget.delete(0, "end")
            return
        elif modified_raw_value in {"-"} or modified_raw_value.endswith("."):
            # Note: "-." is now handled by the new logic above, so it's removed from here
            return

        raw_value = modified_raw_value
        cursor_position = current_cursor_position + initial_cursor_adjustment

        try:
            # --- Step 3: Core formatting logic ---
            sign = "-" if raw_value.startswith("-") else ""
            value = raw_value.lstrip("-")

            formatted_value = ""
            if "." in value:
                integer_part, decimal_part = value.split(".", 1)
                formatted_integer = "{:,}".format(int(integer_part)) if integer_part else "0"
                formatted_value = f"{sign}{formatted_integer}.{decimal_part}"
            else:
                formatted_value = f"{sign}{int(value):,}"

            # --- Step 4: Recalculate cursor position based on commas ---
            num_commas_before = input_value[:current_cursor_position].count(",")
            num_commas_after = formatted_value[:cursor_position].count(",")
            new_cursor_position = cursor_position + (num_commas_after - num_commas_before)

            # --- Step 5: Decimal Removal Cursor Logic ---
            decimal_was_removed = (
                    '.' in previous_raw_value_local and
                    '.' not in raw_value and
                    (len(raw_value) == len(previous_raw_value_local) - 1 or
                     (previous_raw_value_local.startswith("0.") and len(raw_value) == len(previous_raw_value_local) - 2)
                    )
            )

            if decimal_was_removed:
                if previous_raw_value_local.startswith("0."):
                    if raw_value == "0":
                        new_cursor_position = 1
                    else:
                        new_cursor_position = 0

            # --- Step 6: Apply formatted text and restore cursor ---
            self.entry_widget.delete(0, "end")
            self.entry_widget.insert(0, formatted_value)
            self.entry_widget.icursor(new_cursor_position)

        except ValueError:
            pass # Ignore formatting if still invalid input
