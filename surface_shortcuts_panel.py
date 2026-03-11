import ctypes
from ctypes import wintypes
import json
import os
import queue
import sys
import threading
import time

try:
    import keyboard
except ImportError as exc:
    raise SystemExit(
        "This app requires the 'keyboard' package. Install with: pip install keyboard pystray pillow"
    ) from exc

try:
    import pystray
    from PIL import Image, ImageDraw
except ImportError:
    pystray = None
    Image = None
    ImageDraw = None


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


user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
kernel32 = ctypes.windll.kernel32

if not hasattr(wintypes, "LRESULT"):
    wintypes.LRESULT = ctypes.c_ssize_t
if not hasattr(wintypes, "ULONG_PTR"):
    wintypes.ULONG_PTR = ctypes.c_size_t
if not hasattr(wintypes, "HCURSOR"):
    wintypes.HCURSOR = wintypes.HANDLE
if not hasattr(wintypes, "HICON"):
    wintypes.HICON = wintypes.HANDLE
if not hasattr(wintypes, "HBRUSH"):
    wintypes.HBRUSH = wintypes.HANDLE
if not hasattr(wintypes, "HGDIOBJ"):
    wintypes.HGDIOBJ = wintypes.HANDLE
if not hasattr(wintypes, "HFONT"):
    wintypes.HFONT = wintypes.HANDLE
if not hasattr(wintypes, "HMENU"):
    wintypes.HMENU = wintypes.HANDLE

WNDPROC = ctypes.WINFUNCTYPE(
    wintypes.LRESULT,
    wintypes.HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM,
)

WS_CHILD = 0x40000000
WS_VISIBLE = 0x10000000
WS_BORDER = 0x00800000
WS_CAPTION = 0x00C00000
WS_SYSMENU = 0x00080000
WS_CLIPCHILDREN = 0x02000000
WS_EX_TOPMOST = 0x00000008
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_NOACTIVATE = 0x08000000

BS_PUSHBUTTON = 0x00000000
BS_AUTOCHECKBOX = 0x00000003
BS_OWNERDRAW = 0x0000000B
BS_PUSHLIKE = 0x00001000

SW_HIDE = 0
SW_SHOWNOACTIVATE = 4
SW_RESTORE = 9

WM_DESTROY = 0x0002
WM_CLOSE = 0x0010
WM_COMMAND = 0x0111
WM_SETFONT = 0x0030
WM_MOUSEACTIVATE = 0x0021
WM_CTLCOLORBTN = 0x0135
WM_CTLCOLOREDIT = 0x0133
WM_CTLCOLORSTATIC = 0x0138
WM_DRAWITEM = 0x002B
WM_APP = 0x8000
WM_APP_QUEUE = WM_APP + 1

BN_CLICKED = 0
BM_GETCHECK = 0x00F0
BM_SETCHECK = 0x00F1
BST_UNCHECKED = 0
BST_CHECKED = 1

COLOR_WINDOW = 5
COLOR_BTNFACE = 15
MA_NOACTIVATE = 3
TRANSPARENT = 1

INPUT_KEYBOARD = 1
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002

VK_LCONTROL = 0xA2
VK_LSHIFT = 0xA0
VK_LWIN = 0x5B
VK_RETURN = 0x0D
VK_DELETE = 0x2E
VK_LEFT = 0x25
VK_UP = 0x26
VK_RIGHT = 0x27
VK_DOWN = 0x28
VK_X = 0x58
VK_C = 0x43
VK_V = 0x56
VK_Y = 0x59
VK_Z = 0x5A

DT_CALCRECT = 0x00000400
DEFAULT_GUI_FONT = 17
MAPVK_VK_TO_VSC = 0
SM_CYCAPTION = 4

DT_CENTER = 0x00000001
DT_VCENTER = 0x00000004
DT_SINGLELINE = 0x00000020

ODS_SELECTED = 0x0001
ODS_FOCUS = 0x0010

CW_USEDEFAULT = 0x80000000

BUTTON_ID_CTRL_WIN = 1001
BUTTON_ID_CTRL_SHIFT = 1002
BUTTON_ID_CTRL_Z = 1003
BUTTON_ID_CTRL_X = 1004
BUTTON_ID_CTRL_C = 1005
BUTTON_ID_CTRL_V = 1006
BUTTON_ID_CTRL_Y = 1007
BUTTON_ID_UP = 1008
BUTTON_ID_LEFT = 1009
BUTTON_ID_DOWN = 1010
BUTTON_ID_RIGHT = 1011
BUTTON_ID_HIDE = 1012
BUTTON_ID_QUIT = 1013
BUTTON_ID_DELETE = 1014
BUTTON_ID_ENTER = 1015


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt_x", wintypes.LONG),
        ("pt_y", wintypes.LONG),
        ("lPrivate", wintypes.DWORD),
    ]


class PAINTSTRUCT(ctypes.Structure):
    _fields_ = [
        ("hdc", wintypes.HDC),
        ("fErase", wintypes.BOOL),
        ("rcPaint", RECT),
        ("fRestore", wintypes.BOOL),
        ("fIncUpdate", wintypes.BOOL),
        ("rgbReserved", ctypes.c_char * 32),
    ]


class WNDCLASSW(ctypes.Structure):
    _fields_ = [
        ("style", wintypes.UINT),
        ("lpfnWndProc", WNDPROC),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", wintypes.HINSTANCE),
        ("hIcon", wintypes.HICON),
        ("hCursor", wintypes.HCURSOR),
        ("hbrBackground", wintypes.HBRUSH),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
    ]


class DRAWITEMSTRUCT(ctypes.Structure):
    _fields_ = [
        ("CtlType", wintypes.UINT),
        ("CtlID", wintypes.UINT),
        ("itemID", wintypes.UINT),
        ("itemAction", wintypes.UINT),
        ("itemState", wintypes.UINT),
        ("hwndItem", wintypes.HWND),
        ("hDC", wintypes.HDC),
        ("rcItem", RECT),
        ("itemData", wintypes.ULONG_PTR),
    ]


user32.DefWindowProcW.restype = wintypes.LRESULT
user32.DefWindowProcW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.RegisterClassW.argtypes = [ctypes.POINTER(WNDCLASSW)]
user32.RegisterClassW.restype = wintypes.ATOM
user32.CreateWindowExW.restype = wintypes.HWND
user32.CreateWindowExW.argtypes = [
    wintypes.DWORD,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    wintypes.DWORD,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.HWND,
    wintypes.HMENU,
    wintypes.HINSTANCE,
    wintypes.LPVOID,
]
user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
user32.UpdateWindow.argtypes = [wintypes.HWND]
user32.PostQuitMessage.argtypes = [ctypes.c_int]
user32.GetMessageW.argtypes = [ctypes.POINTER(MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
user32.TranslateMessage.argtypes = [ctypes.POINTER(MSG)]
user32.DispatchMessageW.argtypes = [ctypes.POINTER(MSG)]
user32.SetWindowPos.argtypes = [
    wintypes.HWND,
    wintypes.HWND,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.UINT,
]
user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(RECT)]
user32.IsWindow.argtypes = [wintypes.HWND]
user32.IsIconic.argtypes = [wintypes.HWND]
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetDC.argtypes = [wintypes.HWND]
user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
user32.GetSystemMetrics.argtypes = [ctypes.c_int]
user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.DestroyWindow.argtypes = [wintypes.HWND]
user32.keybd_event.argtypes = [wintypes.BYTE, wintypes.BYTE, wintypes.DWORD, wintypes.ULONG_PTR]
user32.MapVirtualKeyW.argtypes = [wintypes.UINT, wintypes.UINT]
user32.MapVirtualKeyW.restype = wintypes.UINT
user32.FillRect.argtypes = [wintypes.HDC, ctypes.POINTER(RECT), wintypes.HBRUSH]
user32.DrawTextW.argtypes = [wintypes.HDC, wintypes.LPCWSTR, ctypes.c_int, ctypes.POINTER(RECT), wintypes.UINT]
gdi32.CreateFontW.restype = wintypes.HFONT
gdi32.CreateFontW.argtypes = [
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.LPCWSTR,
]
gdi32.CreateSolidBrush.argtypes = [wintypes.COLORREF]
gdi32.CreateSolidBrush.restype = wintypes.HBRUSH
gdi32.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
gdi32.DeleteObject.argtypes = [wintypes.HGDIOBJ]
gdi32.SetTextColor.argtypes = [wintypes.HDC, wintypes.COLORREF]
gdi32.SetBkMode.argtypes = [wintypes.HDC, ctypes.c_int]


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
        with open(config_path, "r", encoding="utf-8") as handle:
            user_config = json.load(handle)
        if isinstance(user_config, dict):
            config.update(user_config)
    except Exception:
        pass

    return config


def loword(value: int) -> int:
    return value & 0xFFFF


def hiword(value: int) -> int:
    return (value >> 16) & 0xFFFF


class ShortcutPanel:
    CLASS_NAME = "SurfaceShortcutPanelWindow"

    def __init__(self, config: dict):
        self.config = config
        self.hinstance = kernel32.GetModuleHandleW(None)
        self.hwnd = None
        self.font = None
        self.tray_icon = None
        self.ui_queue = queue.Queue()
        self.last_target_hwnd = None
        self.buttons = {}
        self.button_labels = {}
        self.ctrl_shift_checked = False
        self.ctrl_win_held = False
        self.window_brush = gdi32.CreateSolidBrush(0x202020)
        self.button_brush = gdi32.CreateSolidBrush(0x343434)
        self.button_active_brush = gdi32.CreateSolidBrush(0x7A4B19)
        self.button_pressed_brush = gdi32.CreateSolidBrush(0x4A4A4A)
        self.border_brush = gdi32.CreateSolidBrush(0x5A5A5A)
        self.wndproc = WNDPROC(self._wndproc)

        self._register_window_class()
        self._create_window()
        self._create_controls()
        self._setup_tray()

        if bool(self.config.get("start_hidden", False)):
            self.hide_to_tray()
        else:
            self.show_window()

    def _register_window_class(self):
        wnd_class = WNDCLASSW()
        wnd_class.style = 0
        wnd_class.lpfnWndProc = self.wndproc
        wnd_class.cbClsExtra = 0
        wnd_class.cbWndExtra = 0
        wnd_class.hInstance = self.hinstance
        wnd_class.hIcon = None
        wnd_class.hCursor = user32.LoadCursorW(None, ctypes.c_wchar_p(32512))
        wnd_class.hbrBackground = self.window_brush
        wnd_class.lpszMenuName = None
        wnd_class.lpszClassName = self.CLASS_NAME
        atom = user32.RegisterClassW(ctypes.byref(wnd_class))
        if atom == 0 and ctypes.GetLastError() != 1410:
            raise ctypes.WinError()

    def _create_window(self):
        width, height = self._compute_window_size()
        x = self.config.get("window_x")
        y = self.config.get("window_y")
        if x is None:
            x = CW_USEDEFAULT
        if y is None:
            y = CW_USEDEFAULT

        ex_style = WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE
        if bool(self.config.get("topmost", True)):
            ex_style |= WS_EX_TOPMOST

        self.hwnd = user32.CreateWindowExW(
            ex_style,
            self.CLASS_NAME,
            "Touch Shortcuts",
            WS_CAPTION | WS_SYSMENU | WS_BORDER | WS_CLIPCHILDREN,
            int(x),
            int(y),
            width,
            height,
            None,
            None,
            self.hinstance,
            None,
        )
        if not self.hwnd:
            raise ctypes.WinError()

        if bool(self.config.get("topmost", True)):
            user32.SetWindowPos(self.hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002)

    def _create_controls(self):
        font_name = str(self.config.get("font_family", "Segoe UI"))
        font_size = int(self.config.get("font_size", 11))
        hdc = user32.GetDC(self.hwnd)
        dpi = gdi32.GetDeviceCaps(hdc, 90)
        user32.ReleaseDC(self.hwnd, hdc)
        font_height = -int(font_size * dpi / 72)
        self.font = gdi32.CreateFontW(
            font_height,
            0,
            0,
            0,
            400,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            font_name,
        )

        padding = int(self.config.get("window_padding", 8))
        padx = int(self.config.get("button_padx", 4))
        pady = int(self.config.get("button_pady", 4))
        button_w = self._button_width_px()
        button_h = self._button_height_px()
        label_h = font_size + 10

        top_y = padding + label_h
        edit_label_y = top_y + button_h + pady + 8
        edit_y = edit_label_y + label_h
        arrows_label_y = edit_y + button_h + pady + 8
        arrows_y = arrows_label_y + label_h
        hide_y = arrows_y + (button_h * 2) + pady + 12

        self._make_button(BUTTON_ID_CTRL_WIN, "Wispr Hold", padding, top_y, button_w, button_h, toggle=True)
        self._make_button(BUTTON_ID_CTRL_SHIFT, "Ctrl+Shift", padding + button_w + padx, top_y, button_w, button_h, toggle=True)

        edit_labels = [
            (BUTTON_ID_CTRL_Z, "Ctrl+Z"),
            (BUTTON_ID_CTRL_X, "Ctrl+X"),
            (BUTTON_ID_CTRL_C, "Ctrl+C"),
            (BUTTON_ID_CTRL_V, "Ctrl+V"),
            (BUTTON_ID_CTRL_Y, "Ctrl+Y"),
        ]
        for index, (button_id, text) in enumerate(edit_labels):
            x = padding + index * (button_w + padx)
            self._make_button(button_id, text, x, edit_y, button_w, button_h)

        arrow_x = padding + button_w
        self._make_button(BUTTON_ID_UP, "Up", arrow_x, arrows_y, button_w, button_h)
        self._make_button(BUTTON_ID_LEFT, "Left", padding, arrows_y + button_h + pady, button_w, button_h)
        self._make_button(BUTTON_ID_DOWN, "Down", arrow_x, arrows_y + button_h + pady, button_w, button_h)
        self._make_button(BUTTON_ID_RIGHT, "Right", padding + (button_w + padx) * 2, arrows_y + button_h + pady, button_w, button_h)
        self._make_button(BUTTON_ID_ENTER, "Enter", padding, hide_y, button_w, button_h)
        self._make_button(BUTTON_ID_DELETE, "Delete", padding + button_w + padx, hide_y, button_w, button_h)
        self._make_button(BUTTON_ID_HIDE, "Hide", padding + (button_w + padx) * 2, hide_y, button_w, button_h)
        self._make_button(BUTTON_ID_QUIT, "Quit", padding + (button_w + padx) * 3, hide_y, button_w, button_h)

        labels = [
            ("Edit", padding, edit_label_y),
            ("Arrows", padding, arrows_label_y),
        ]
        for text, x, y in labels:
            self._make_static(text, x, y, 120, label_h)

    def _make_button(self, button_id: int, text: str, x: int, y: int, width: int, height: int, toggle: bool = False):
        style = WS_CHILD | WS_VISIBLE
        style |= BS_OWNERDRAW
        style |= BS_AUTOCHECKBOX | BS_PUSHLIKE if toggle else BS_PUSHBUTTON
        hwnd = user32.CreateWindowExW(
            0,
            "BUTTON",
            text,
            style,
            x,
            y,
            width,
            height,
            self.hwnd,
            button_id,
            self.hinstance,
            None,
        )
        if not hwnd:
            raise ctypes.WinError()
        user32.SendMessageW(hwnd, WM_SETFONT, self.font, 1)
        self.buttons[button_id] = hwnd
        self.button_labels[button_id] = text

    def _make_static(self, text: str, x: int, y: int, width: int, height: int):
        hwnd = user32.CreateWindowExW(
            0,
            "STATIC",
            text,
            WS_CHILD | WS_VISIBLE,
            x,
            y,
            width,
            height,
            self.hwnd,
            None,
            self.hinstance,
            None,
        )
        if hwnd:
            user32.SendMessageW(hwnd, WM_SETFONT, self.font, 1)

    def _compute_window_size(self):
        padding = int(self.config.get("window_padding", 8))
        pady = int(self.config.get("button_pady", 4))
        button_h = self._button_height_px()
        label_h = int(self.config.get("font_size", 11)) + 10
        width = padding * 2 + self._button_width_px() * 5 + int(self.config.get("button_padx", 4)) * 4
        height = (
            padding * 2
            + user32.GetSystemMetrics(SM_CYCAPTION)
            + label_h
            + button_h
            + pady
            + 8
            + label_h
            + button_h
            + pady
            + 8
            + label_h
            + button_h * 2
            + pady
            + 12
            + button_h
        )
        return width, height

    def _button_width_px(self):
        width_units = int(self.config.get("button_width", 10))
        font_size = int(self.config.get("font_size", 11))
        return max(70, width_units * max(7, font_size // 2 + 2))

    def _button_height_px(self):
        height_units = int(self.config.get("button_height", 2))
        font_size = int(self.config.get("font_size", 11))
        return max(36, height_units * (font_size + 10))

    def _setup_tray(self):
        if pystray is None or Image is None or ImageDraw is None:
            return

        def create_image():
            image = Image.new("RGB", (64, 64), color=(30, 30, 30))
            draw = ImageDraw.Draw(image)
            draw.rounded_rectangle((8, 8, 56, 56), radius=10, fill=(70, 130, 180))
            draw.text((18, 20), "KB", fill=(255, 255, 255))
            return image

        def on_show(icon, item):
            self.ui_queue.put(self.show_window)
            user32.PostMessageW(self.hwnd, WM_APP_QUEUE, 0, 0)

        def on_exit(icon, item):
            self.ui_queue.put(self.quit_app)
            user32.PostMessageW(self.hwnd, WM_APP_QUEUE, 0, 0)

        menu = pystray.Menu(
            pystray.MenuItem("Show", on_show),
            pystray.MenuItem("Exit", on_exit),
        )
        self.tray_icon = pystray.Icon("touch_shortcuts", create_image(), "Touch Shortcuts", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def show_window(self):
        user32.ShowWindow(self.hwnd, SW_SHOWNOACTIVATE)
        if bool(self.config.get("topmost", True)):
            user32.SetWindowPos(self.hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002)

    def hide_to_tray(self):
        if self.ctrl_win_held:
            self._end_ctrl_win_hold()
        user32.ShowWindow(self.hwnd, SW_HIDE)

    def quit_app(self):
        if self.ctrl_win_held:
            self._end_ctrl_win_hold()
        if self.tray_icon:
            self.tray_icon.stop()
        user32.DestroyWindow(self.hwnd)

    def _remember_target_window(self):
        foreground = user32.GetForegroundWindow()
        if foreground and foreground != self.hwnd:
            self.last_target_hwnd = foreground

    def _restore_target_window(self):
        hwnd = self.last_target_hwnd
        if not hwnd or not user32.IsWindow(hwnd):
            return
        if user32.IsIconic(hwnd):
            user32.ShowWindow(hwnd, SW_RESTORE)
        user32.SetForegroundWindow(hwnd)

    def _send_to_target(self, action):
        self._restore_target_window()
        time.sleep(0.03)
        action()

    def _handle_button(self, button_id: int):
        if button_id == BUTTON_ID_CTRL_WIN:
            self.ctrl_win_held = bool(
                user32.SendMessageW(self.buttons[BUTTON_ID_CTRL_WIN], BM_GETCHECK, 0, 0) == BST_CHECKED
            )
            if self.ctrl_win_held:
                self._send_to_target(self._begin_ctrl_win_hold)
            else:
                self._end_ctrl_win_hold()
            return
        if button_id == BUTTON_ID_CTRL_SHIFT:
            self.ctrl_shift_checked = bool(
                user32.SendMessageW(self.buttons[BUTTON_ID_CTRL_SHIFT], BM_GETCHECK, 0, 0) == BST_CHECKED
            )
            return
        if button_id == BUTTON_ID_CTRL_Z:
            self._send_to_target(lambda: self._send_hotkey(VK_LCONTROL, VK_Z))
            return
        if button_id == BUTTON_ID_CTRL_X:
            self._send_to_target(lambda: self._send_hotkey(VK_LCONTROL, VK_X))
            return
        if button_id == BUTTON_ID_CTRL_C:
            self._send_to_target(lambda: self._send_hotkey(VK_LCONTROL, VK_C))
            return
        if button_id == BUTTON_ID_CTRL_V:
            self._send_to_target(lambda: self._send_hotkey(VK_LCONTROL, VK_V))
            return
        if button_id == BUTTON_ID_CTRL_Y:
            self._send_to_target(lambda: self._send_hotkey(VK_LCONTROL, VK_Y))
            return
        if button_id == BUTTON_ID_UP:
            self._send_arrow("up")
            return
        if button_id == BUTTON_ID_LEFT:
            self._send_arrow("left")
            return
        if button_id == BUTTON_ID_DOWN:
            self._send_arrow("down")
            return
        if button_id == BUTTON_ID_RIGHT:
            self._send_arrow("right")
            return
        if button_id == BUTTON_ID_ENTER:
            self._send_to_target(lambda: self._send_hotkey(VK_RETURN))
            return
        if button_id == BUTTON_ID_DELETE:
            self._send_to_target(lambda: self._send_hotkey(VK_DELETE))
            return
        if button_id == BUTTON_ID_HIDE:
            self.hide_to_tray()
            return
        if button_id == BUTTON_ID_QUIT:
            self.quit_app()

    def _send_ctrl_win(self):
        try:
            keyboard.send("ctrl+windows")
            return
        except Exception:
            pass
        self._send_hotkey(VK_LCONTROL, VK_LWIN)

    def _begin_ctrl_win_hold(self):
        self._send_key_event(VK_LCONTROL, key_up=False)
        time.sleep(0.01)
        self._send_key_event(VK_LWIN, key_up=False)

    def _end_ctrl_win_hold(self):
        self._send_key_event(VK_LWIN, key_up=True)
        time.sleep(0.01)
        self._send_key_event(VK_LCONTROL, key_up=True)
        self.ctrl_win_held = False
        user32.SendMessageW(self.buttons[BUTTON_ID_CTRL_WIN], BM_SETCHECK, BST_UNCHECKED, 0)

    def _send_arrow(self, direction: str):
        vk_map = {
            "up": VK_UP,
            "left": VK_LEFT,
            "down": VK_DOWN,
            "right": VK_RIGHT,
        }

        def action():
            if self.ctrl_shift_checked:
                self._send_hotkey(VK_LCONTROL, VK_LSHIFT, vk_map[direction])
            else:
                self._send_hotkey(vk_map[direction])

        self._send_to_target(action)

    def _send_hotkey(self, *virtual_keys: int):
        for virtual_key in virtual_keys:
            self._send_key_event(virtual_key, key_up=False)
            time.sleep(0.01)
        for virtual_key in reversed(virtual_keys):
            self._send_key_event(virtual_key, key_up=True)
            time.sleep(0.01)

    def _send_key_event(self, virtual_key: int, key_up: bool):
        scan_code = user32.MapVirtualKeyW(virtual_key, MAPVK_VK_TO_VSC)
        flags = 0
        if virtual_key in {VK_LWIN, VK_DELETE, VK_LEFT, VK_UP, VK_RIGHT, VK_DOWN}:
            flags |= KEYEVENTF_EXTENDEDKEY
        if key_up:
            flags |= KEYEVENTF_KEYUP
        user32.keybd_event(virtual_key, scan_code, flags, 0)

    def pump_ui_queue(self):
        try:
            while True:
                action = self.ui_queue.get_nowait()
                action()
        except queue.Empty:
            pass

    def _draw_button(self, draw_item):
        button_id = draw_item.CtlID
        button_rect = draw_item.rcItem
        is_checked = button_id in {BUTTON_ID_CTRL_WIN, BUTTON_ID_CTRL_SHIFT} and bool(
            user32.SendMessageW(self.buttons[button_id], BM_GETCHECK, 0, 0) == BST_CHECKED
        )
        is_pressed = bool(draw_item.itemState & ODS_SELECTED)

        brush = self.button_active_brush if is_checked else self.button_brush
        if is_pressed:
            brush = self.button_pressed_brush

        user32.FillRect(draw_item.hDC, ctypes.byref(button_rect), brush)
        user32.FillRect(draw_item.hDC, ctypes.byref(RECT(button_rect.left, button_rect.top, button_rect.right, button_rect.top + 1)), self.border_brush)
        user32.FillRect(draw_item.hDC, ctypes.byref(RECT(button_rect.left, button_rect.bottom - 1, button_rect.right, button_rect.bottom)), self.border_brush)
        user32.FillRect(draw_item.hDC, ctypes.byref(RECT(button_rect.left, button_rect.top, button_rect.left + 1, button_rect.bottom)), self.border_brush)
        user32.FillRect(draw_item.hDC, ctypes.byref(RECT(button_rect.right - 1, button_rect.top, button_rect.right, button_rect.bottom)), self.border_brush)

        gdi32.SetBkMode(draw_item.hDC, TRANSPARENT)
        gdi32.SetTextColor(draw_item.hDC, 0xFFFFFF)
        text_rect = RECT(
            button_rect.left + 4,
            button_rect.top + 2,
            button_rect.right - 4,
            button_rect.bottom - 2,
        )
        user32.DrawTextW(
            draw_item.hDC,
            self.button_labels.get(button_id, ""),
            -1,
            ctypes.byref(text_rect),
            DT_CENTER | DT_VCENTER | DT_SINGLELINE,
        )

    def _wndproc(self, hwnd, msg, wparam, lparam):
        if msg == WM_MOUSEACTIVATE:
            return MA_NOACTIVATE
        if msg == WM_APP_QUEUE:
            self.pump_ui_queue()
            return 0
        if msg == WM_DRAWITEM:
            self._draw_button(ctypes.cast(lparam, ctypes.POINTER(DRAWITEMSTRUCT)).contents)
            return 1
        if msg == WM_COMMAND:
            if hiword(wparam) == BN_CLICKED:
                try:
                    self._handle_button(loword(wparam))
                except Exception as exc:
                    print(f"Button handler failed: {exc}", file=sys.stderr)
                return 0
        if msg == WM_CLOSE:
            self.hide_to_tray()
            return 0
        if msg == WM_DESTROY:
            user32.PostQuitMessage(0)
            return 0
        if msg == WM_CTLCOLORSTATIC:
            gdi32.SetTextColor(wparam, 0xFFFFFF)
            gdi32.SetBkMode(wparam, TRANSPARENT)
            return self.window_brush
        if msg in (WM_CTLCOLORBTN, WM_CTLCOLOREDIT):
            return self.window_brush
        return user32.DefWindowProcW(hwnd, msg, wparam, lparam)

    def run(self):
        msg = MSG()
        while True:
            self.pump_ui_queue()
            self._remember_target_window()
            result = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if result == 0:
                break
            if result == -1:
                raise ctypes.WinError()
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        if self.font:
            gdi32.DeleteObject(self.font)
        for brush in (
            self.window_brush,
            self.button_brush,
            self.button_active_brush,
            self.button_pressed_brush,
            self.border_brush,
        ):
            if brush:
                gdi32.DeleteObject(brush)


def main():
    if os.name != "nt":
        raise SystemExit("This app currently supports Windows only.")
    panel = ShortcutPanel(load_config())
    panel.run()


if __name__ == "__main__":
    main()
