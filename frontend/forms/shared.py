# This where all the shared variable stored
# All the variables functions we're used by the program.

import requests
from backend.settings.database import server_ip
import threading
import time


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

    def get_rm_code_api(self):
        """Return cached raw materials data."""
        return self._cache["raw_materials"]["data"] or []

    def get_status_api(self):
        """Return cached status data."""
        return self._cache["status"]["data"] or []

