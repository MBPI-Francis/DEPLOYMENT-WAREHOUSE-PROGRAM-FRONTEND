import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from frontend.stock_on_hand.import_feature.core_function import ImportData

class ConfirmationMessage:
    def __init__(self, root):
        self.root = root

    def show_confirmation_message(self):
        # confirmation_window = ttk.Toplevel(form_frame)
        # confirmation_window.title("Confirm Action")
        # confirmation_window.geometry("450x410")
        # confirmation_window.resizable(True, True)

        confirmation_window = ttk.Toplevel(self.root)
        confirmation_window.title("Confirm Action")

        # Get the screen width and height
        screen_width = confirmation_window.winfo_screenwidth()
        screen_height = confirmation_window.winfo_screenheight()

        # Set a dynamic size (proportional to the screen size)
        window_width = int(screen_width * 0.38)  # Adjust width as needed
        window_height = int(screen_height * 0.36)  # Adjust height as needed

        # Calculate position for centering
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 3  # Position slightly higher

        # Apply geometry dynamically
        confirmation_window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Allow resizing but maintain proportions
        confirmation_window.resizable(True, True)

        # Expand and fill widgets inside the window
        confirmation_window.grid_columnconfigure(0, weight=1)
        confirmation_window.grid_rowconfigure(0, weight=1)

        # Message Label - Warning About Setting a New Beginning Balance
        message_label = ttk.Label(
            confirmation_window,
            text="\n\n⚠ WARNING",
            justify="center",
            font=("Arial", 15, "bold"),
            bootstyle=WARNING
        )
        message_label.pack(pady=5)

        # Message Label - Warning About Setting a New Beginning Balance
        message_label = ttk.Label(
            confirmation_window,
            text="This change is irreversible—altering the Beginning Balance will recalculate all future balances",
            justify="center",
            font=("Arial", 10, "bold"),
            bootstyle=WARNING
        )
        message_label.pack(pady=5)

        # Message Label - Detailed Explanation
        message_label = ttk.Label(
            confirmation_window,
            text=(
                "The Beginning Balance determines the accuracy of all future balance calculations.\n"
                "Modifying it will:\n"
                "   • Recalculate upcoming balances based on the new value.\n"
                "   • Reset existing calculations that depend on past entries.\n"
                "   • Potentially cause discrepancies in historical data.\n\n"
                "Ensure that modifying the Beginning Balance is necessary before proceeding.\n"
                "Once changed, previous calculations cannot be restored automatically."
            ),
            justify="left",
            font=("Arial", 10),
        )
        message_label.pack(pady=5)

        # Message Label
        message_label = ttk.Label(
            confirmation_window,
            text=("To proceed, type 'YES' in the confirmation box."),
            justify="center",
            font=("Arial", 10, "bold"),
        )
        message_label.pack(pady=5)

        # Entry field
        confirm_entry = ttk.Entry(confirmation_window, font=("Arial", 12),
                                  justify="center")
        confirm_entry.pack(padx=20, pady=5)

        # Frame for buttons
        button_frame = ttk.Frame(confirmation_window)
        button_frame.pack(fill="x", padx=10, pady=10)  # Expand the frame horizontally

        # Configure button frame columns
        button_frame.columnconfigure(0, weight=1)  # Left side (Cancel)
        button_frame.columnconfigure(1, weight=1)  # Right side (Submit)

        # Cancel Button (Left)
        cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            bootstyle=DANGER,
            command=confirmation_window.destroy
        )
        cancel_button.grid(row=0, column=0, padx=5, sticky="w")  # Align to left

        # Submit Button (Right, Initially Disabled)
        submit_button = ttk.Button(
            button_frame,
            text="Submit",
            bootstyle=SUCCESS,
            state=DISABLED,
            command=lambda: [ImportData(self.root).import_data(), confirmation_window.destroy()]
        )
        submit_button.grid(row=0, column=1, padx=5, sticky="e")  # Align to right

        # Function to validate entry field
        def validate_entry(event):
            if confirm_entry.get().strip() == "YES":
                submit_button.config(state=NORMAL)
            else:
                submit_button.config(state=DISABLED)

        confirm_entry.bind("<KeyRelease>", validate_entry)

