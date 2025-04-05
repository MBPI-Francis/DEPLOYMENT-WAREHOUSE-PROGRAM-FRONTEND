import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import StringVar

# Sample RM Codes (this can be fetched from an API)
rm_codes = ["K907", "Y98", "AO8"]

class ComboBoxExample(tb.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid(padx=10, pady=10)

        # Label to show selected RM Code
        self.label = tb.Label(self, text="Selected RM Code: None", font=("Helvetica", 12))
        self.label.grid(row=0, column=0, padx=5, pady=10, sticky="w")

        # StringVar to handle combobox input dynamically
        self.input_var = StringVar()

        # Combobox for RM Codes (Editable)
        self.rm_codes_combobox = tb.Combobox(
            self,
            values=rm_codes,
            textvariable=self.input_var,
            width=25,
            font=("Helvetica", 12),
            state="normal"  # Set combobox to be editable
        )
        self.rm_codes_combobox.grid(row=1, column=0, padx=5, pady=10, sticky="w")

        # Bind key event for dynamic filtering
        self.rm_codes_combobox.bind("<KeyRelease>", self.filter_combobox)

        # Set focus to the combobox when the application starts
        self.rm_codes_combobox.focus()  # Set focus to the combobox

    def filter_combobox(self, event):
        """Filter the combobox options based on the entered text."""
        current_text = self.input_var.get().upper()  # Get the current text entered
        filtered_options = [code for code in rm_codes if code.startswith(current_text)]  # Filter

        # Update the combobox with filtered options
        self.rm_codes_combobox.set("")  # Reset combobox selection
        self.rm_codes_combobox["values"] = filtered_options

        # Show dropdown if there are matching options
        if filtered_options:
            self.rm_codes_combobox.event_generate('<Down>')  # Show the dropdown

        # Optionally update the label with selected text
        self.label.config(text=f"Selected RM Code: {self.rm_codes_combobox.get()}")

# Create ttkbootstrap window
root = tb.Window(themename="cosmo")

# Initialize the ComboBoxExample frame
app = ComboBoxExample(master=root)

# Run the application
root.mainloop()
