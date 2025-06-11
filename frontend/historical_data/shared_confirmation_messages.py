import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from frontend.historical_data.receiving_form.adjustment_form import AdjustmentForm as ReceivingAdjustment
from frontend.historical_data.outgoing_form.adjustment_form import AdjustmentForm as OutgoingAdjustment
from frontend.historical_data.preparation_form.adjustment_form import AdjustmentForm as PreparationAdjustment
from frontend.historical_data.transfer_form.adjustment_form import AdjustmentForm as TransferAdjustment
from frontend.historical_data.change_status_form.adjustment_form import AdjustmentForm as ChangeStatusAdjustment

class ConfirmationMessage:
    def __init__(self, root, table_self, form_type):
        self.table_self = table_self
        self.root = root

        if form_type == "receiving":
            self.adjustment_form = ReceivingAdjustment(self.table_self)


        elif form_type == "outgoing":
            self.adjustment_form = OutgoingAdjustment(self.table_self)

        elif form_type == "preparation":
            self.adjustment_form = PreparationAdjustment(self.table_self)

        elif form_type == "transfer":
            self.adjustment_form = TransferAdjustment(self.table_self)

        elif form_type == "change status":
            self.adjustment_form = ChangeStatusAdjustment(self.table_self)




    def show_confirmation_message_adjusted(self, item):

        confirmation_window = ttk.Toplevel(self.root)
        confirmation_window.title("Confirm Action")

        # Get the screen width and height
        screen_width = confirmation_window.winfo_screenwidth()
        screen_height = confirmation_window.winfo_screenheight()

        # Set a dynamic size (proportional to the screen size)
        window_width = int(screen_width * 0.35)  # Adjust width as needed
        window_height = int(screen_height * 0.35)  # Adjust height as needed

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
            text="You're about to readjust this raw material's ending balance.",
            justify="center",
            font=("Arial", 13, "bold"),
            bootstyle=WARNING
        )
        message_label.pack(pady=5)

        # Message Label - Detailed Explanation
        message_label1 = ttk.Label(
            confirmation_window,
            text=(
                "Please take note of the below details before proceeding:\n\n"
                "1. This record has already been adjusted before.\n\n"
                "2. Proceeding will void the previous adjustment and recalculate the ending balance.\n\n"

            ),
            font=("Arial", 11),
        )
        message_label1.pack(pady=5)


        # Message Label
        message_label = ttk.Label(
            confirmation_window,
            text=("To proceed with the readjustment, type 'YES' in the confirmation box."),
            justify="center",
            font=("Arial", 11, "bold"),
        )
        message_label.pack(pady=5, padx=0)

        # Entry field
        confirm_entry = ttk.Entry(confirmation_window, font=("Arial", 12, "bold"),
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
            text="Proceed",
            bootstyle=SUCCESS,
            state=DISABLED,
            command=lambda: [self.adjustment_form.add_records(item), confirmation_window.destroy()]
        )
        submit_button.grid(row=0, column=1, padx=5, sticky="e")  # Align to right

        # Function to validate entry field
        def validate_entry(event):
            if confirm_entry.get().strip() == "YES":
                submit_button.config(state=NORMAL)
            else:
                submit_button.config(state=DISABLED)

        confirm_entry.bind("<KeyRelease>", validate_entry)



    def show_confirmation_message(self, item):

        confirmation_window = ttk.Toplevel(self.root)
        confirmation_window.title("Confirm Action")

        # Get the screen width and height
        screen_width = confirmation_window.winfo_screenwidth()
        screen_height = confirmation_window.winfo_screenheight()

        # Set a dynamic size (proportional to the screen size)
        window_width = int(screen_width * 0.35)  # Adjust width as needed
        window_height = int(screen_height * 0.38)  # Adjust height as needed

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
            text="You're about to adjust this raw material's ending balance.",
            justify="center",
            font=("Arial", 13, "bold"),
            bootstyle=WARNING
        )
        message_label.pack(pady=5)

        # Message Label - Detailed Explanation
        message_label1 = ttk.Label(
            confirmation_window,
            text=(
                "Please take note of the below details before proceeding:\n\n"
                "1. You will be adjusting the raw material's ending balance.\n\n"
                "2. Be cautious in doing this action and ensure that all details are accurate, \n"
                "    as this will affect the current ending balance and may also impact future ending balances.\n\n"

            ),
            font=("Arial", 11),
        )
        message_label1.pack(pady=5)


        # Message Label
        message_label = ttk.Label(
            confirmation_window,
            text=("To proceed with the readjustment, type 'YES' in the confirmation box."),
            justify="center",
            font=("Arial", 11, "bold"),
        )
        message_label.pack(pady=5, padx=0)

        # Entry field
        confirm_entry = ttk.Entry(confirmation_window, font=("Arial", 12, "bold"),
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
            text="Proceed",
            bootstyle=SUCCESS,
            state=DISABLED,
            command=lambda: [self.adjustment_form.add_records(item), confirmation_window.destroy()]
        )
        submit_button.grid(row=0, column=1, padx=5, sticky="e")  # Align to right

        # Function to validate entry field
        def validate_entry(event):
            if confirm_entry.get().strip() == "YES":
                submit_button.config(state=NORMAL)
            else:
                submit_button.config(state=DISABLED)

        confirm_entry.bind("<KeyRelease>", validate_entry)

