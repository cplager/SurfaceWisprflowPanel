import tkinter as tk
from tkinter import ttk
import threading
import queue
import sys
import os
import json
import ctypes

try:
    import pystray
    from PIL import Image, ImageDraw
except ImportError:
    pystray = None
    Image = None
    ImageDraw = None

try:
    import keyboard
except ImportError as exc:
    raise SystemExit(
        "This app requires the 'keyboard' package. Install with: pip install keyboard pystray pillow"
    ) from exc


DEFAULT_CONFIG = {
    "button_width": 10,
    "button_height": 2,
    "font_family": "Segoe UI",
    "font_size": 11,
    "window_padding": 8,
    "button_padx": 4,
    "button_pady": 4,
    "topmost": True,
    "start_hidden": False,
    "window_x": None,
    "window_y": None,
}

if os.name == "nt":
    GWL_EXSTYLE = -20
    WS_EX_NOACTIVATE = 0x08000000
    WS_EX_TOOLWINDOW = 0x00000080
    SW_SHOWNOACTIVATE = 4


def get_base_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def load_config() -> dict:
    config = DEFAULT_CONFIG.copy()
    config_path = os.path.join(get_base_dir(), "touch_shortcuts_config.json")

    if not os.path.exists(config_path):
        return config

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            user_config = json.load(f)
        if isinstance(user_config, dict):
            config.update(user_config)
    except Exception:
        pass

    return config


class ShortcutPanel:
    def __init__(self, root: tk.Tk, config: dict):
        self.root = root
        self.config = config
        self.root.title("Touch Shortcuts")
        self.root.attributes("-topmost", bool(self.config.get("topmost", True)))
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.hide_to_tray)

        self.ctrl_shift_armed = False
        self.tray_icon = None
        self.ui_queue = queue.Queue()

        self._build_ui()
        self._configure_window_behavior()
        self._apply_window_position()
        self._poll_ui_queue()
        self._setup_tray()

        if bool(self.config.get("start_hidden", False)):
            self.root.after(150, self.hide_to_tray)

    def _build_ui(self):
        container = ttk.Frame(self.root, padding=int(self.config.get("window_padding", 8)))
        container.grid(row=0, column=0, sticky="nsew")

        style = ttk.Style()
        try:
            style.theme_use("vista")
        except Exception:
            pass

        top = ttk.Frame(container)
        top.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self._make_button(top, "Ctrl+Win", self.send_ctrl_win, 0, 0, width=12)
        self.ctrl_shift_btn = self._make_button(top, "Ctrl+Shift", self.toggle_ctrl_shift, 0, 1, width=12)

        edit = ttk.LabelFrame(container, text="Edit")
        edit.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        shortcuts = [
            ("Ctrl+Z", "ctrl+z"),
            ("Ctrl+X", "ctrl+x"),
            ("Ctrl+C", "ctrl+c"),
            ("Ctrl+V", "ctrl+v"),
            ("Ctrl+Y", "ctrl+y"),
        ]
        for col, (label, combo) in enumerate(shortcuts):
            self._make_button(edit, label, lambda c=combo: self.send_combo(c), 0, col, width=9)

        arrows = ttk.LabelFrame(container, text="Arrows")
        arrows.grid(row=2, column=0, sticky="ew")

        self._make_button(arrows, "↑", lambda: self.send_arrow("up"), 0, 1, width=6)
        self._make_button(arrows, "←", lambda: self.send_arrow("left"), 1, 0, width=6)
        self._make_button(arrows, "↓", lambda: self.send_arrow("down"), 1, 1, width=6)
        self._make_button(arrows, "→", lambda: self.send_arrow("right"), 1, 2, width=6)

        bottom = ttk.Frame(container)
        bottom.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        self._make_button(bottom, "Hide", self.hide_to_tray, 0, 0, width=10)

        for i in range(5):
            edit.grid_columnconfigure(i, weight=1)
        for i in range(3):
            arrows.grid_columnconfigure(i, weight=1)

    def _configure_window_behavior(self):
        if os.name != "nt":
            return

        # Mark the window as non-activating so tapping its buttons does not
        # steal focus from the app currently receiving keyboard input.
        self.root.update_idletasks()
        hwnd = self.root.winfo_id()
        ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(
            hwnd,
            GWL_EXSTYLE,
            ex_style | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW,
        )

    def _make_button(self, parent, text, command, row, col, width=None):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            takefocus=0,
            width=int(width if width is not None else self.config.get("button_width", 10)),
            height=int(self.config.get("button_height", 2)),
            font=(
                str(self.config.get("font_family", "Segoe UI")),
                int(self.config.get("font_size", 11)),
            ),
        )
        btn.grid(
            row=row,
            column=col,
            padx=int(self.config.get("button_padx", 4)),
            pady=int(self.config.get("button_pady", 4)),
            sticky="nsew",
        )
        return btn

    def _apply_window_position(self):
        x = self.config.get("window_x")
        y = self.config.get("window_y")
        if x is None or y is None:
            return
        try:
            self.root.geometry(f"+{int(x)}+{int(y)}")
        except Exception:
            pass

    def send_combo(self, combo: str):
        keyboard.send(combo)

    def send_ctrl_win(self):
        keyboard.press("ctrl")
        keyboard.press("windows")
        keyboard.release("windows")
        keyboard.release("ctrl")

    def toggle_ctrl_shift(self):
        self.ctrl_shift_armed = not self.ctrl_shift_armed
        self.ctrl_shift_btn.configure(
            relief=tk.SUNKEN if self.ctrl_shift_armed else tk.RAISED,
            bg="#b7d7ff" if self.ctrl_shift_armed else "SystemButtonFace",
        )

    def send_arrow(self, direction: str):
        if self.ctrl_shift_armed:
            keyboard.press("ctrl")
            keyboard.press("shift")
            keyboard.press(direction)
            keyboard.release(direction)
            keyboard.release("shift")
            keyboard.release("ctrl")
        else:
            keyboard.send(direction)

    def hide_to_tray(self):
        self.root.withdraw()

    def show_window(self):
        self.root.deiconify()
        self.root.attributes("-topmost", bool(self.config.get("topmost", True)))
        if os.name == "nt":
            ctypes.windll.user32.ShowWindow(self.root.winfo_id(), SW_SHOWNOACTIVATE)
        self.root.lift()

    def quit_app(self):
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.after(0, self.root.destroy)

    def _poll_ui_queue(self):
        try:
            while True:
                action = self.ui_queue.get_nowait()
                action()
        except queue.Empty:
            pass
        self.root.after(100, self._poll_ui_queue)

    def _setup_tray(self):
        if pystray is None or Image is None or ImageDraw is None:
            return

        def create_image():
            image = Image.new("RGB", (64, 64), color=(30, 30, 30))
            dc = ImageDraw.Draw(image)
            dc.rounded_rectangle((8, 8, 56, 56), radius=10, fill=(70, 130, 180))
            dc.text((18, 20), "KB", fill=(255, 255, 255))
            return image

        def on_show(icon, item):
            self.ui_queue.put(self.show_window)

        def on_exit(icon, item):
            self.ui_queue.put(self.quit_app)

        menu = pystray.Menu(
            pystray.MenuItem("Show", on_show),
            pystray.MenuItem("Exit", on_exit),
        )
        self.tray_icon = pystray.Icon("touch_shortcuts", create_image(), "Touch Shortcuts", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()


def main():
    root = tk.Tk()
    config = load_config()
    ShortcutPanel(root, config)
    root.mainloop()


if __name__ == "__main__":
    main()
