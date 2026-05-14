# Chromium Kiosk Autostart Configuration

This document describes the Chromium kiosk mode autostart configuration for the FitPro Ultima Laser application.

## Overview

The application is configured to automatically launch Chromium in kiosk mode on system startup, displaying the web interface at `http://localhost` in fullscreen without browser UI elements.

## Configuration File

**Location:** `~/.config/autostart/chromium-kiosk.desktop`

**Backup:** A copy is available in `deploy/chromium-kiosk.desktop`

## Configuration Details

```desktop
[Desktop Entry]
Type=Application
Name=Chromium Kiosk
Exec=chromium --kiosk --no-first-run --simulate-outdated-no-new-window --start-fullscreen --noerrdialogs --disable-infobars --disable-features=Translate,BubbleKeycaseTrigger,SidePanel --disable-session-crashed-bubble "http://localhost"
X-GNOME-Autostart-enabled=true
Terminal=false
```

## Chromium Flags Explained

- `--kiosk` - Launches Chromium in kiosk mode (fullscreen, no browser UI)
- `--no-first-run` - Skips first-run wizards and setup dialogs
- `--simulate-outdated-no-new-window` - Prevents "outdated browser" warnings from opening new windows
- `--start-fullscreen` - Ensures fullscreen mode on startup
- `--noerrdialogs` - Disables error dialogs
- `--disable-infobars` - Removes information bars (e.g., "Chromium is being controlled by automated software")
- `--disable-features=Translate,BubbleKeycaseTrigger,SidePanel` - Disables translation prompts, bubble notifications, and side panel
- `--disable-session-crashed-bubble` - Prevents "restore session" dialogs after crashes

## Installation

To set up autostart on a new system:

1. Create the autostart directory if it doesn't exist:
   ```bash
   mkdir -p ~/.config/autostart
   ```

2. Copy the configuration file:
   ```bash
   cp deploy/chromium-kiosk.desktop ~/.config/autostart/
   ```

3. Ensure the file has proper permissions:
   ```bash
   chmod +x ~/.config/autostart/chromium-kiosk.desktop
   ```

4. Reboot or log out and back in to test autostart

## Disabling Autostart

To temporarily disable autostart without deleting the file:

```bash
# Disable
sed -i 's/X-GNOME-Autostart-enabled=true/X-GNOME-Autostart-enabled=false/' ~/.config/autostart/chromium-kiosk.desktop

# Re-enable
sed -i 's/X-GNOME-Autostart-enabled=false/X-GNOME-Autostart-enabled=true/' ~/.config/autostart/chromium-kiosk.desktop
```

Or simply remove the file:
```bash
rm ~/.config/autostart/chromium-kiosk.desktop
```

## Troubleshooting

### Chromium doesn't start automatically
- Verify the file exists: `ls -la ~/.config/autostart/chromium-kiosk.desktop`
- Check if autostart is enabled in the file
- Ensure Chromium is installed: `which chromium`
- Check system logs: `journalctl --user -b | grep chromium`

### Application not loading
- Verify the web server is running and accessible at `http://localhost`
- Check if the application starts automatically before Chromium launches
- Consider adding a startup delay if needed

### Exiting kiosk mode
- Press `Alt+F4` to close Chromium
- Press `Ctrl+Alt+F1` to switch to a terminal (then `Ctrl+Alt+F7` to return to GUI)
