# Surface Touch Shortcuts Panel

This package contains a small always-on-top Windows utility panel designed for touch use on a Microsoft Surface.

## Features

- Always-on-top mini panel
- Hides to the notification area / system tray when closed
- Tray menu with **Show** and **Exit**
- Buttons for:
  - Ctrl+Win
  - Ctrl+Shift toggle
  - Ctrl+Z
  - Ctrl+X
  - Ctrl+C
  - Ctrl+V
  - Ctrl+Y
  - Arrow keys
- Config file loaded from the same folder as the script or built EXE

## Files in this package

- `surface_shortcuts_panel.py` – main app
- `touch_shortcuts_config.json` – sample config
- `build_exe.bat` – Windows build script for PyInstaller
- `requirements.txt` – Python packages used
- `README.md` – this file

## Quick start: run from Python

Open Command Prompt or PowerShell in this folder and run:

```bat
py -m pip install -r requirements.txt
py surface_shortcuts_panel.py
```

## Build a standalone EXE

Run:

```bat
build_exe.bat
```

That will produce:

```text
dist\surface_touch_shortcuts.exe
```

Keep `touch_shortcuts_config.json` in the same folder as the EXE.

## Config file

The app looks for:

```text
touch_shortcuts_config.json
```

in the same folder as the script or executable.

Example:

```json
{
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

- `button_width`: default button width in Tkinter text units
- `button_height`: button height in Tkinter text units
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

- `button_width` and `button_height` are not exact pixel sizes.
- `font_size`, `button_padx`, and `button_pady` usually make the biggest difference for touch friendliness.
- The app uses the `keyboard` package to send key combinations.
- On Windows, key simulation may work best when the app is run at the same privilege level as the target app.
- If a target app is elevated, you may need to run this panel as administrator too.

## Suggested next improvements

Possible future enhancements:

- Drag-anywhere window movement
- Save current position automatically when moved
- Adjustable opacity
- Separate Ctrl and Shift toggles
- Additional custom shortcut buttons
- More native Windows version in C# / WinForms


## Architecture-aware builds

The included `build_exe.bat` script detects the Windows architecture it is running on and names the output accordingly:

- Intel / AMD 64-bit Windows build machine → `surface_touch_shortcuts_x64.exe`
- ARM64 Windows build machine → `surface_touch_shortcuts_arm64.exe`

This makes it easy to keep both versions side by side.

Recommended approach if you use both kinds of tablets:

- Build once on your x64 machine for `..._x64.exe`
- Build once on your ARM64 machine for `..._arm64.exe`

Then keep the same `touch_shortcuts_config.json` next to each EXE.
