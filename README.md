# Surface Touch Shortcuts Panel

This package contains a small always-on-top Windows utility panel designed for touch use on a Microsoft Surface.

## Features

- Native Windows panel that does not take typing focus when tapped
- Always-on-top mini panel
- Dark theme with white text
- Hides to the notification area / system tray when closed
- In-app **Help** button that opens local HTML documentation
- Tray menu with **Show** and **Exit**
- Buttons for:
  - Wispr Hold toggle
  - Ctrl+Shift toggle
  - Undo
  - Redo
  - Cut
  - Copy
  - Paste
  - Enter
  - Delete
  - Help
  - Arrow keys
- Config file loaded from the same folder as the script or built EXE

## Files in this package

- `surface_shortcuts_panel.py` – main app
- `touch_shortcuts_config.json` – sample config
- `surface_touch_shortcuts_help.html` – local help/documentation page
- `build_exe.bat` – Windows build script for PyInstaller
- `install_program_files.bat` – installs the packaged app into Program Files
- `uninstall_surface_touch_shortcuts.bat` – uninstall script copied into the install folder
- `requirements.txt` – Python packages used
- `README.md` – this file

## Quick start: run from Python

Open Command Prompt or PowerShell in this folder and run:

```bat
pip install -r requirements.txt
python surface_shortcuts_panel.py
```

or

```bat
new-pixi keyboard_311 "python=3.11" keyboard pystray pillow pyinstaller 
```

## Build a standalone EXE

Run:

```bat
build_exe.bat
```

That will produce:

```text
dist\surface_touch_shortcuts_x64.exe
dist\surface_touch_shortcuts_arm64.exe
```

The build script also creates a package folder in `dist\surface_touch_shortcuts_<arch>_package` containing:

- the EXE
- `touch_shortcuts_config.json`
- `surface_touch_shortcuts_help.html`
- `install_program_files.bat`
- `uninstall_surface_touch_shortcuts.bat`

Run `install_program_files.bat` from that package folder to copy everything into:

```text
C:\Program Files\Surface Touch Shortcuts
```

The installer script is architecture-neutral. If the package contains:

- `surface_touch_shortcuts_x64.exe`, it installs that build
- `surface_touch_shortcuts_arm64.exe`, it installs that build

No installer changes are needed between x64 and ARM64 packages.

The installer also creates:

- a Start Menu folder with app, help, and uninstall shortcuts
- an Installed Apps / Add or Remove Programs entry with uninstall support

This app can still be packaged as a standalone executable with PyInstaller. The UI is implemented with native Win32 calls via `ctypes`, so there is no extra GUI dependency beyond standard Python plus the packages in `requirements.txt`.

## Config file

The app looks for:

```text
touch_shortcuts_config.json
```

in the same folder as the script or executable.

Example:

```json
{
  "ui_scale": 1.0,
  "button_width": 12,
  "button_height": 3,
  "font_family": "Segoe UI",
  "font_size": 14,
  "window_padding": 10,
  "button_padx": 6,
  "button_pady": 6,
  "topmost": true,
  "start_hidden": false,
  "window_x": 1200,
  "window_y": 120
}
```

## Config settings

- `button_width`: approximate button width scaling
- `button_height`: approximate button height scaling
- `ui_scale`: proportional scale for the entire panel layout
  Practical range in the current app is roughly `0.4` to `3.0`.
- `font_family`: button font family
- `font_size`: button font size
- `window_padding`: outer padding around the panel
- `button_padx`: horizontal spacing around buttons
- `button_pady`: vertical spacing around buttons
- `topmost`: keep panel always on top
- `start_hidden`: launch directly into the tray
- `window_x`: window left position in pixels
- `window_y`: window top position in pixels

## Notes

- `Wispr Hold` is a latch: tap once to hold `Ctrl+Win`, tap again to release it.
- `Ctrl+Shift` is a latch for modified arrow navigation.
- `Enter` has the same focus-preserving behavior as the other non-Wispr keys.
- Drag-resizing scales the whole panel proportionally instead of stretching it.
- When you finish resizing, the current `ui_scale` is saved back to `touch_shortcuts_config.json`.
- At very small scales, a few long button labels switch to compact forms so the layout stays usable.
- At the smallest scales, several labels abbreviate further so the panel can shrink without text collisions.
- `button_width` and `button_height` are not exact pixel sizes.
- `font_size`, `button_padx`, and `button_pady` usually make the biggest difference for touch friendliness.
- Most shortcuts are sent with native Win32 key events. The `keyboard` package is still used as a fallback for the Wispr shortcut.
- The `Help` button opens `surface_touch_shortcuts_help.html` from the same folder as the EXE.
- On Windows, key simulation may work best when the app is run at the same privilege level as the target app.
- If a target app is elevated, you may need to run this panel as administrator too.

## Architecture-aware builds

The included `build_exe.bat` script detects the Windows architecture it is running on and names the output accordingly:

- Intel / AMD 64-bit Windows build machine → `surface_touch_shortcuts_x64.exe`
- ARM64 Windows build machine → `surface_touch_shortcuts_arm64.exe`

This makes it easy to keep both versions side by side.

Recommended approach if you use both kinds of tablets:

- Build once on your x64 machine for `..._x64.exe`
- Build once on your ARM64 machine for `..._arm64.exe`

Then keep the same `touch_shortcuts_config.json` next to each EXE.
