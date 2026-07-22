# FitPro Ultima Laser Qt App User Guide

This guide describes the Qt kiosk app screens, the purpose of each button, and the recommended order of operation.

Use this app only on the intended Ultima Laser system and only by trained operators. Always follow the device safety procedure, eye protection rules, treatment protocol, and local service instructions.

## Recommended Operating Order

1. Start the kiosk app.
2. Press `Get started`.
3. On the login screen, enter the user credentials and press `Login`.
4. On the settings screen, confirm the calibration status and patient/treatment selections.
5. If calibration is needed, press `Recalibration`, complete the calibration workflow, then return to settings.
6. Select `Skin Type`, `Hair color`, and `Hair Type`.
7. Press `Start treatment`.
8. On entering treatment mode, the app automatically switches off detection overlays, red dot, laser arm state, and vacuum before initializing treatment.
9. Set output power and pulse width.
10. Press `Apply settings`.
11. Select `Auto`, `Semi Auto`, or `Manual`.
12. Use `Detect` to find targets when using semi-auto or manual mode.
13. Confirm the target/app state indicators.
14. Arm the laser only when ready to treat.
15. Use `FIRE` in semi-auto mode or `Next` in manual mode according to the selected mode.
16. Use `DISARM`, `Emergency Stop`, or `Cleanup` whenever the session must be made safe or reset.

## Start Screen

The start screen is the first screen shown by the kiosk.

`Get started`

Opens the login screen.

## Login Screen

The login screen contains the account fields and navigation controls.

`Back`

Returns to the start screen.

`E-mail address`

Text field for the operator account e-mail.

`Password`

Text field for the operator password. The input is hidden.

`Login`

Continues to the laser treatment screen. In the current Qt app this is a UI flow action; the login fields are placeholders unless backend authentication is added.

`i`

Visual information icon. On this screen it is not wired to a separate action.

## Settings Screen

The settings screen is used before treatment to confirm calibration state and choose patient/treatment categories.

`Back`

Returns to the start screen.

`i`

Opens the system information screen.

`Recalibration`

Opens the calibration screen. Use this when the red-dot/galvo/camera alignment needs to be checked or recalculated.

`Skin Type I. - VI.`

Selects the Fitzpatrick skin type shown by the highlighted circle. This is currently a UI selection used by the screen state.

`Hair color`

Selects one of `Black`, `Dark Brown`, `Brown`, `Grey/White`, `Blonde`, or `Red`. The selected color is highlighted.

`Hair Type`

Selects `Thin`, `Medium`, or `Thick`. The selected type is highlighted.

`Start treatment`

Opens the laser treatment screen. When treatment mode is entered, the app immediately calls safety-off commands for detection, overlays, red dot, laser arm state, and vacuum.

## Laser Treatment Screen

This is the main operating screen for treatment.

### Automatic Entry Safety

Every time the treatment screen initializes, the app immediately requests:

- treatment detection off
- live overlay off
- mask overlay off
- calibration detection off
- red dot off
- laser disarm
- vacuum off

These commands are fired without waiting for backend responses. The UI state is also set to off/disarmed immediately.

### Navigation and Status

`Back`

Returns to the settings screen. Leaving treatment also stops the treatment camera stream.

`i`

Opens the system information screen.

`Show Logs` / `Hide Logs`

Shows or hides the treatment log panel. The panel displays recent app/backend actions, status changes, and errors.

`LASER MODULE TEMP`

Displays the latest known laser module temperature.

### Output Performance

`808 nm`

Sets the output power for the 808 nm laser channel. The displayed value is in watts.

`980 nm`

Sets the output power for the 980 nm laser channel. The displayed value is in watts.

`1064 nm`

Sets the output power for the 1064 nm laser channel. The displayed value is in watts.

`P.WIDTH`

Sets the pulse width in milliseconds.

`Apply settings`

Sends the selected power and pulse width settings to the backend. If settings were changed, the button shows `Apply settings`; after a successful apply it shows `Settings OK`.

Recommended order:

1. Adjust `808 nm`, `980 nm`, `1064 nm`, and `P.WIDTH`.
2. Press `Apply settings`.
3. Continue only after the app reports the settings were applied.

### Treatment Mode

`Auto`

Selects automatic treatment mode through the backend.

`Semi Auto`

Selects semi-automatic treatment mode. This is the default mode initialized by the app.

`Manual`

Selects manual treatment mode.

Recommended order:

1. Select the treatment mode.
2. Apply laser settings if they are dirty.
3. Detect or load targets.
4. Arm only after the desired target state is ready.

### Laser and Emergency Controls

`ARM`

Arms the laser. Use only after the treatment area, settings, and target state are confirmed.

`DISARM`

Disarms the laser.

`Emergency Stop`

Calls the treatment emergency stop endpoint and refreshes treatment state. Use this immediately if operation must stop.

### Camera and Target Controls

The circular image area shows the latest camera frame. If overlay or targets are enabled, the app requests the current processed frame; otherwise it requests a snapshot.

`Detect`

Available in semi-auto and manual modes. Applies pending laser settings if needed, then asks the backend to detect targets. The result updates `TARGET`, `APP`, `TARGETS`, and `TARGET STATE`.

`FIRE`

Available in semi-auto mode. Enabled only when `fireReady` is true. Applies pending settings if needed, then asks the backend to fire the selected/ready treatment target.

`Next`

Available in manual mode. Enabled when at least one target is loaded. Applies pending settings if needed, then asks the backend to move to the next target.

`VACUUM LOCK` switch

Toggles the vacuum on or off.

`CONFIDENCE` − / + controls

Sets the detection confidence threshold in precise, touchscreen-friendly steps. Higher values make detection stricter; lower values allow more detections. The allowed range, default, and step are configured in `config.json`.

`Detection On` / `Detection Off`

Toggles backend treatment detection.

`Overlay On` / `Overlay Off`

Toggles the live detection overlay.

`Check States`

Refreshes the treatment app status from the backend.

`Cleanup`

Calls backend startup cleanup and refreshes treatment status. Use this to clear/reset backend state before a new attempt.

`TARGET`

Shows whether the backend reports a ready target.

`APP`

Shows the backend treatment app state.

`TARGETS`

Shows the number of loaded targets.

`TARGET STATE`

Shows the backend target state.

### Semi-Auto Treatment Order

1. Enter treatment mode.
2. Set power and pulse width.
3. Press `Apply settings`.
4. Select `Semi Auto`.
5. Adjust `CONFIDENCE` if needed.
6. Press `Detect`.
7. Confirm `TARGET: OK` and target count/state.
8. Press `ARM`.
9. Press `FIRE` when it becomes enabled.
10. Press `DISARM` after firing or before changing setup.

### Manual Treatment Order

1. Enter treatment mode.
2. Set power and pulse width.
3. Press `Apply settings`.
4. Select `Manual`.
5. Adjust `CONFIDENCE` if needed.
6. Press `Detect`.
7. Confirm that `TARGETS` is greater than zero.
8. Press `ARM` only when ready.
9. Press `Next` to step through targets.
10. Press `DISARM` when finished or before changing setup.

### Auto Treatment Order

1. Enter treatment mode.
2. Set power and pulse width.
3. Press `Apply settings`.
4. Select `Auto`.
5. Confirm state indicators.
6. Use `Emergency Stop`, `DISARM`, or `Cleanup` if state is not correct.

The current Qt screen does not show a separate auto start button; auto behavior depends on the backend mode implementation.

## Calibration Screen

The calibration screen is used to align camera coordinates, red-dot detection, galvo movement, and saved homography.

Important: do not change HSV limits while red-dot detection is already working. If `Detection On` shows a stable crosshair on the laser red dot, leave the HSV settings untouched. Use `Detection On` / `Detection Off` to verify whether the app can detect the red dot reliably.

Recommended safe entry:

1. Open calibration from `Settings` -> `Recalibration`.
2. Keep the laser disarmed unless a procedure specifically requires arming.
3. Use red dot and detection controls only for alignment.
4. Press `DISABLE CALIBRATION MODE` before leaving calibration or before returning to treatment.

### Navigation and Live View

`Back`

Returns to the settings screen.

`i`

Opens the system information screen.

Camera image

Shows the live calibration frame. Clicking the image has two possible behaviors:

- HSV Inspect Off: clicking moves through image-to-galvo mapping if homography is available.
- HSV Inspect On: clicking samples HSV/RGB values at that image point.

With `HSV Inspect Off`, clicking anywhere on the image sends the red dot to that image position using the saved homography. If the red dot does not jump precisely to the clicked point, the HSV settings are not the first thing to adjust. Recalculate the homography.

### Red Dot Detection Panel

`Detection On` / `Detection Off`

Turns calibration red-dot detection on or off.

`Mask On` / `Mask Off`

Turns the detection mask overlay on or off.

`HSV Inspect Off` / `HSV Inspect On`

Toggles image click inspection mode. When on, image clicks sample and display HSV/RGB values instead of commanding a move.

`DISABLE CALIBRATION MODE`

Turns off HSV inspect mode in the UI and requests calibration-safe shutdown:

- mask off
- calibration detection off
- red dot off
- laser disarm

The shared UI state is also reset to detection off, overlay off, red dot off, laser disarmed, and vacuum off.

`Dot in image`

Displays the detected red-dot image coordinate.

`Click image`

Displays the last clicked image coordinate.

`Clicked HSV`

Displays HSV values sampled at the last inspected point.

`Clicked RGB`

Displays RGB values sampled at the last inspected point.

`Target galvo`

Displays the mapped galvo coordinate for the last image click.

`Move result`

Displays the result of the last image-based move.

`Galvo position`

Displays the latest galvo position read from the backend.

`Homography`

Displays whether homography is loaded/saved or reports the latest homography status.

### HSV Limits

Do not touch HSV limits if red-dot detection works and the crosshair is visible on the laser red dot. HSV tuning is only for cases where detection cannot find the red dot reliably, detects the wrong object, or the mask is unstable.

`Show` / `Hide`

Expands or collapses the HSV limits panel.

`Range 1: Low Hue Red`

Controls the lower and upper HSV bounds for the low-hue red range.

`Range 2: High Hue Red`

Controls the lower and upper HSV bounds for the high-hue red range.

`Lower H`, `Lower S`, `Lower V`, `Upper H`, `Upper S`, `Upper V`

Each slider updates one HSV channel in the backend. The slider sends the value when released.

Recommended HSV tuning order:

1. First turn `Detection On` and check whether the crosshair sits on the laser red dot.
2. If detection works, do not change HSV limits.
3. If detection does not work, turn `HSV Inspect On`.
4. Click the red dot in the camera image.
5. Read `Clicked HSV` and `Clicked RGB`.
6. Press `Show` in HSV Limits.
7. Adjust the lower/upper HSV limits until detection is stable.
8. Use `Mask On` to inspect the mask result.
9. Turn `HSV Inspect Off` when finished.

### Laser Control

`ARM`

Arms the laser from the calibration screen.

`DISARM`

Disarms the laser from the calibration screen.

`Red Dot ON`

Turns the red dot on.

`Red Dot OFF`

Turns the red dot off.

Recommended order:

1. Keep `DISARM` selected unless the calibration procedure requires arming.
2. Use `Red Dot ON` for visual/detection alignment.
3. Use `Red Dot OFF` when done.
4. Press `DISABLE CALIBRATION MODE` before treatment.

### Direct Galvo Control

`X` field

Sets the target galvo X coordinate.

`Y` field

Sets the target galvo Y coordinate.

`Move`

Moves the galvo to the X/Y target fields.

`Step` field

Sets the step size used by the directional buttons.

`Up`

Moves the galvo up by the configured step.

`Down`

Moves the galvo down by the configured step.

`Left`

Moves the galvo left by the configured step.

`Right`

Moves the galvo right by the configured step.

Recommended order:

1. Confirm the current `Galvo position`.
2. Enter X/Y or set `Step`.
3. Use `Move` for exact coordinates or direction buttons for small adjustments.
4. Watch `Galvo position` after each move.

### Calibration Collection

`Start`

Starts a new calibration point collection and resets the stored point count.

`Store Point`

Stores the current calibration point.

`Calculate & Save`

Calculates the homography from stored points and saves it.

`Reload`

Reloads the saved homography from the backend.

`Status`

Shows the latest calibration/homography status.

Recommended homography calibration order:

1. Press `Start`.
2. Move or click to align a known calibration point.
3. Press `Store Point`.
4. Store points across the whole field, not only near the center.
5. Useful pattern: store four points in each quadrant: `UPLEFT`, `DOWNLEFT`, `UPRIGHT`, and `DOWNRIGHT`.
6. Repeat until enough points are stored for a reliable homography.
7. Press `Calculate & Save`.
8. Confirm `Status` reports saved/loaded state.
9. Press `Reload` if the saved homography should be reloaded immediately.
10. Press `DISABLE CALIBRATION MODE`.
11. Return to settings or treatment.

Best calibration setup:

1. Use a green background.
2. Use a flat, homogeneous surface.
3. Place the surface perpendicular to the optical axis.
4. Make sure the surface is in focus.

If image clicks are not landing the red dot precisely at the clicked point, recalculate homography before changing HSV limits.

## System Info Screen

The system info screen shows user, hardware, software, and diagnostic entry points.

`Back`

Returns to the settings screen.

`Logout`

Displayed as a user action. In the current QML it does not trigger a controller action.

Language, Wifi network, Bluetooth gear icons

Displayed settings indicators. In the current QML they do not trigger controller actions.

`GUI version check`

Calls backend sync. Use it as a quick connectivity/status refresh.

`HW/SW test`

Opens the hardware/software test screen.

## HW/SW Test Screen

This screen is for service and diagnostics.

`Back`

Returns to system info.

`Sudo password`

Password field used by the backend restart action.

`Restart backend`

Restarts `hairkiller-backend.service` using the entered sudo password and displays the command output.

`Skip YOLO model load`

When checked, the full backend test skips model-loading checks.

`Run full test`

Runs the full backend check and displays:

- overall summary
- last run time
- per-check status table
- raw output

Recommended diagnostic order:

1. Open `System Info`.
2. Press `HW/SW test`.
3. Press `Run full test`.
4. Review failed or warning rows.
5. If the backend is stuck, enter the sudo password and press `Restart backend`.
6. Run the full test again.

## CLI and Journal Logs

When running under systemd, follow the Qt kiosk logs with:

```bash
sudo journalctl -u fitpro-ultima-kiosk -f
```

Backend logs:

```bash
sudo journalctl -u hairkiller-backend -f
```

The Qt app logs task start, success, slow calls, failures, camera refresh progress, treatment safety shutdown commands, and heartbeat messages.

## Quick Safety Reset Checklist

Before switching from calibration to treatment:

1. Press `DISABLE CALIBRATION MODE`.
2. Confirm red dot is off.
3. Confirm laser is disarmed.
4. Confirm detection/mask overlays are off.
5. Enter treatment mode.

Before leaving the device unattended:

1. Press `DISARM`.
2. Turn vacuum off.
3. Turn red dot off if visible.
4. Use `Emergency Stop` if anything is still running.
5. Check the CLI/journal logs if the UI becomes unresponsive.
