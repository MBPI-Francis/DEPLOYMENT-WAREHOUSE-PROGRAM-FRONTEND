import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk


class ZoomableApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("600x400")
        self.default_font_size = 10  # Default font size
        self.font_name = "Helvetica"

        # Create a ttk.Style object
        self.style = ttk.Style()

        # Sample Label
        self.label = ttk.Label(root, text="Zoomable Text", font=(self.font_name, self.default_font_size))
        self.label.pack(pady=20)



        # Sample Button with Custom Style
        self.button = ttk.Button(root, text="Click Me", command=self.dummy_action, style="Zoom.TButton")
        self.button.pack(pady=10)

        # Bind Zooming Events
        self.root.bind("<Control-MouseWheel>", self.zoom_text)

        # Apply initial button style
        self.update_button_style()

    def dummy_action(self):
        print("Button Clicked!")

    def zoom_text(self, event):
        """Dynamically adjusts the font size when Ctrl + Mouse Wheel is used."""
        if event.delta > 0:  # Zoom in
            self.default_font_size += 1
        elif event.delta < 0 and self.default_font_size > 6:  # Zoom out (limit min size)
            self.default_font_size -= 1

        # Apply new font size to widgets
        self.label.config(font=(self.font_name, self.default_font_size))

        # Update button size dynamically
        self.update_button_style()

    def update_button_style(self):
        """Updates the button font and padding dynamically."""
        self.style.configure(
            "Zoom.TButton",
            font=(self.font_name, self.default_font_size),
            padding=(self.default_font_size, self.default_font_size // 2)  # Adjust padding dynamically
        )


if __name__ == "__main__":
    root = ttk.Window(themename="cosmo")  # Choose a theme
    app = ZoomableApp(root)
    root.mainloop()
