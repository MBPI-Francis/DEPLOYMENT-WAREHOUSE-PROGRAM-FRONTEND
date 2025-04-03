import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk


class PaginatedTreeviewApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Paginated Treeview with Search")

        self.entries_per_page = 10  # Number of entries per page
        self.current_page = 1

        # Sample data
        self.data = [
            (f"Item {i}", f"Description {i}") for i in range(1, 101)
        ]

        # Frame for Search Bar and Buttons
        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill="x", padx=10, pady=(5, 0))

        # Search Entry
        ttk.Label(search_frame, text="Search:", style="CustomLabel.TLabel").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame, width=50, bootstyle=INFO)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self.filter_table)

        # Search Button
        search_button = ttk.Button(search_frame, text="Search", command=self.filter_table, bootstyle=PRIMARY)
        search_button.pack(side="left", padx=10)

        # Treeview for displaying data
        self.treeview = ttk.Treeview(self.root, columns=("Item", "Description"), show="headings")
        self.treeview.heading("Item", text="Item")
        self.treeview.heading("Description", text="Description")
        self.treeview.pack(fill="both", expand=True, padx=10, pady=(5, 0))

        # Pagination Frame
        pagination_frame = ttk.Frame(self.root)
        pagination_frame.pack(fill="x", padx=10, pady=(5, 10))

        # Previous and Next Buttons
        self.prev_button = ttk.Button(pagination_frame, text="<< Previous", command=self.prev_page, bootstyle=DANGER)
        self.prev_button.pack(side="left", padx=5)

        self.page_label = ttk.Label(pagination_frame, text="Page 1", style="CustomLabel.TLabel")
        self.page_label.pack(side="left", padx=5)

        self.next_button = ttk.Button(pagination_frame, text="Next >>", command=self.next_page, bootstyle=SUCCESS)
        self.next_button.pack(side="left", padx=5)

        # Load the initial data
        self.load_page_data()

    def load_page_data(self):
        # Clear current treeview data
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        # Get the data to display based on pagination
        start_index = (self.current_page - 1) * self.entries_per_page
        end_index = start_index + self.entries_per_page
        page_data = self.data[start_index:end_index]

        # Insert the data into the treeview
        for row in page_data:
            self.treeview.insert("", "end", values=row)

        # Update the page label
        self.page_label.config(text=f"Page {self.current_page}")

    def filter_table(self, event=None):
        # Get the search text
        search_text = self.search_entry.get().lower()

        # Filter the data based on search
        if search_text:
            filtered_data = [
                (item, description) for item, description in self.data if
                search_text in item.lower() or search_text in description.lower()
            ]
        else:
            filtered_data = self.data

        self.data = filtered_data
        self.current_page = 1  # Reset to the first page
        self.load_page_data()

    def prev_page(self):
        # Go to the previous page
        if self.current_page > 1:
            self.current_page -= 1
            self.load_page_data()

    def next_page(self):
        # Go to the next page
        if self.current_page * self.entries_per_page < len(self.data):
            self.current_page += 1
            self.load_page_data()


if __name__ == "__main__":
    root = ttk.Window(themename="darkly")  # Using darkly theme for better aesthetics
    app = PaginatedTreeviewApp(root)
    root.mainloop()
