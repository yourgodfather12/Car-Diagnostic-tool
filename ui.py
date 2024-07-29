import tkinter as tk
from tkinter import ttk
import gettext
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    filename='application.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Tooltip:
    def __init__(self, widget: tk.Widget, text: str, delay: int = 500, bg: str = '#ffffe0',
                 fg: str = 'black', font: tuple = ("Helvetica", "9", "normal"),
                 borderwidth: int = 1, wraplength: int = 180):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.bg = bg
        self.fg = fg
        self.font = font
        self.borderwidth = borderwidth
        self.wraplength = wraplength
        self.tooltip = None
        self._create_tooltip()

    def _create_tooltip(self):
        try:
            self.tooltip = tk.Toplevel(self.widget, bg=self.bg, padx=1, pady=1)
            self.tooltip.overrideredirect(True)
            self.tooltip.withdraw()
            label = tk.Label(self.tooltip, text=self.text, background=self.bg, foreground=self.fg,
                             relief=tk.SOLID, borderwidth=self.borderwidth, font=self.font, wraplength=self.wraplength)
            label.pack()

            def enter(event):
                self.widget.after(self.delay, self.show_tooltip)

            def leave(event):
                self.tooltip.withdraw()

            self.widget.bind("<Enter>", enter)
            self.widget.bind("<Leave>", leave)
        except Exception as e:
            logging.error(f"Error creating tooltip: {e}", exc_info=True)

    def show_tooltip(self):
        try:
            x, y, _, _ = self.widget.bbox("insert")
            x += self.widget.winfo_rootx() + 25
            y += self.widget.winfo_rooty() + 25
            screen_width = self.widget.winfo_screenwidth()
            screen_height = self.widget.winfo_screenheight()
            if x + 200 > screen_width:
                x = screen_width - 200
            if y + 100 > screen_height:
                y = screen_height - 100
            self.tooltip.wm_geometry(f"+{x}+{y}")
            self.tooltip.deiconify()
        except Exception as e:
            logging.error(f"Error displaying tooltip: {e}", exc_info=True)

def set_status(style: ttk.Style, status_bar: ttk.Label, message: str, status_type: str = "info", icon: Optional[str] = None) -> None:
    '''Set the status bar message with the appropriate style and optional icon.'''
    try:
        color_map = {
            "info": "blue",
            "success": "green",
            "warning": "orange",
            "error": "red"
        }
        icon_map = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌"
        }
        icon_display = icon if icon else icon_map.get(status_type, '')
        style.configure('Statusbar.TLabel', foreground=color_map.get(status_type, "blue"))
        status_bar.config(text=f"{icon_display} {message}", style='Statusbar.TLabel')
        status_bar.update_idletasks()
    except Exception as e:
        logging.error(f"Error setting status: {e}", exc_info=True)

def apply_theme(style: ttk.Style, theme_name: str = "default") -> None:
    '''Apply the selected theme to the application.'''
    try:
        if theme_name == "dark":
            style.theme_use("clam")
            style.configure(".", background="#333333", foreground="white")
            style.configure("TLabel", background="#333333", foreground="white")
            style.configure("TButton", background="#555555", foreground="white")
            style.map("TButton", background=[("active", "#777777")])
        elif theme_name == "light":
            style.theme_use("default")
            style.configure(".", background="#F0F0F0", foreground="black")
            style.configure("TLabel", background="#F0F0F0", foreground="black")
            style.configure("TButton", background="#E0E0E0", foreground="black")
            style.map("TButton", background=[("active", "#D0D0D0")])
        else:
            logging.warning(f"Theme '{theme_name}' not recognized. Applying default theme.")
            style.theme_use("default")
        style.configure("TStatusbar", background="#333333" if theme_name == "dark" else "#F0F0F0")
        style.configure("TStatusbar.Label", background="#333333" if theme_name == "dark" else "#F0F0F0")
    except Exception as e:
        logging.error(f"Error applying theme: {e}", exc_info=True)
        style.theme_use("default")

def setup_translation(lang: str) -> None:
    '''Setup language translation and allow dynamic switching.'''
    try:
        t = gettext.translation('base', localedir='locales', languages=[lang])
        t.install()
        logging.info(f"Language set to {lang}")
    except FileNotFoundError:
        gettext.install('base')
        logging.warning(f"No translation file found for language '{lang}', using default.")
    except Exception as e:
        logging.error(f"Error setting up translation for language '{lang}': {e}", exc_info=True)
        gettext.install('base')
