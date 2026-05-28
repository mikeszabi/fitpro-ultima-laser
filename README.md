# FitPro Ultima Laser - Qt Kiosk Application

A native PySide6/QML kiosk application for the Ultima Laser treatment system, designed for Jetson hardware with touchscreen support.

## Features

- **Framework**: PySide6 with QML
- **Language**: Python 3
- **UI Design**: Native Qt/QML with portrait orientation (9:16, 1080x1920)
- **Target Device**: Touchscreen kiosk on Jetson hardware
- **Backend**: Connects to FastAPI backend via HTTP

## Project Structure

```
.
├── qt_app/                          # Qt/QML kiosk application
│   ├── main.py                      # PySide6 application entry point
│   ├── app_controller.py            # App state management and QML bindings
│   ├── api_client.py                # FastAPI backend client
│   ├── requirements.txt             # Python dependencies (PySide6)
│   ├── run-kiosk.sh                 # Kiosk startup script
│   ├── qml/
│   │   ├── Main.qml                 # Main window and screen switching
│   │   ├── components/              # Reusable QML components
│   │   └── screens/                 # Screen implementations
│   │       ├── StartScreen.qml
│   │       ├── LoginScreen.qml
│   │       ├── SettingsScreen.qml
│   │       ├── LaserTreatmentScreen.qml
│   │       └── SystemInfoScreen.qml
│   └── systemd/
│       └── fitpro-ultima-kiosk.service
├── src/                             # Legacy React frontend (archived)
└── public/                          # Static assets
```

## Architecture

Full system architecture documentation is available in [ARCHITECTURE.md](./ARCHITECTURE.md). It covers the microcontroller, Python backend, Qt frontend, and integration points.

## Quick Start

### Development Setup

```bash
cd qt_app
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run in Windowed Mode (Development)

```bash
cd qt_app
source .venv/bin/activate
python main.py --windowed
```

The application will connect to the backend at `http://127.0.0.1:8000` by default.

### Run in Full-Screen Kiosk Mode (Production)

```bash
cd qt_app
./run-kiosk.sh
```

This script:
- Disables X11 screensaver and power management (DPMS)
- Runs the application in fullscreen mode
- Uses the configured backend URL from environment variables

### Customize Backend URL

```bash
export FITPRO_API_BASE_URL="http://192.168.1.100:8000"
cd qt_app
source .venv/bin/activate
python main.py --windowed
```

Or with the kiosk script:

```bash
export FITPRO_API_BASE_URL="http://192.168.1.100:8000"
cd qt_app
./run-kiosk.sh
```

## Backend Setup

The application connects to a FastAPI/uvicorn backend service. The service file is at `deploy/hairkiller-backend.service`.

### Installation (First Time)

```bash
sudo cp deploy/hairkiller-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable hairkiller-backend
```

### Start / Stop / Restart Backend

```bash
sudo systemctl start hairkiller-backend
sudo systemctl stop hairkiller-backend
sudo systemctl restart hairkiller-backend
```

### Check Backend Status and Logs

```bash
sudo systemctl status hairkiller-backend
sudo journalctl -u hairkiller-backend -f
```

### Serial Port Setup

To access the laser device on `/dev/ttyACM0`, run the setup script from the hairkiller project:

```bash
cd /home/jetson/Projects/hairkiller/setup_scripts
./setup_serial.sh
```

This script:
- Changes ownership of the STM32 Virtual ComPort device to the current user
- Adds the user to the `dialout` group for serial port access
- Sets proper permissions (660) on `/dev/ttyACM0`

**Note:** You may need to log out and log back in for group changes to take effect.

## Systemd Service for Qt App (Optional)

For production deployment, you can run the Qt app as a systemd service:

```bash
sudo cp qt_app/systemd/fitpro-ultima-kiosk.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable fitpro-ultima-kiosk
sudo systemctl start fitpro-ultima-kiosk
```

View logs:

```bash
sudo journalctl -u fitpro-ultima-kiosk -f
```

## Touchscreen Setup

### Verify Touchscreen Detection on Jetson

```bash
cat /proc/bus/input/devices
sudo evtest
xinput list
```

### Touchscreen Coordinate Calibration

If touch input is detected but coordinates are offset, you may need to apply coordinate transformation. The deployment includes an `.xprofile` configuration:

```bash
cp deploy/.xprofile ~/.xprofile
```

This script applies the coordinate transformation matrix for the Hi-Tech CoolTouch System touchscreen on X11 startup.

## Screens

1. **Start Screen** - Logo and entry point
2. **Login Screen** - User authentication
3. **Settings Screen** - Treatment configuration (calibration, skin type, hair color/type)
4. **Laser Treatment Screen** - Main treatment interface with:
   - Performance output control
   - Treatment mode selection
   - Camera feed display
   - Fire, Stop, and red dot controls
5. **System Info Screen** - Device and software information

## UI Design

The Qt/QML interface reflects the Ultima Laser design system:
- **Resolution**: 1080x1920 (9:16 portrait)
- **Wave Background**: Animated gradient matching original design
- **Rounded Containers**: White-bordered treatment panels (39px radius, 3px border)
- **Touch Optimization**: Large buttons for touch-friendly interaction
- **Performance Sliders**: Accompanied by +/- buttons for precise control
- **Fire Button**: Hold-to-activate for safety
- **Stop Button**: Large, direct access button

## Backend Integration

The Qt application communicates with the FastAPI backend via HTTP:

- **Health Check**: `GET /health` - Monitor backend connectivity
- **Laser Control**: Arm/disarm, red dot, vacuum activation
- **Capture Management**: Load and save laser targets
- **Frame Streaming**: Real-time camera frames from `/frame/current`
- **Settings Sync**: Treatment parameters and device configuration

## Power Management (Kiosk Mode)

When running `./run-kiosk.sh`, the script automatically:
- Disables X11 screensaver
- Disables DPMS (monitor power management)
- Disables screen blanking
- Runs the application in fullscreen mode

To disable these behaviors during development, set environment variables:

```bash
export FITPRO_NO_XSET=1
python main.py --windowed
```

## Notes

- **Backend Requirement**: The Qt app requires a running FastAPI backend instance
- **Default Backend**: `http://127.0.0.1:8000`
- **Network Backend**: Set `FITPRO_API_BASE_URL` environment variable for remote backends
- **Development**: Use `--windowed` flag for easier debugging
- **Production**: Use `./run-kiosk.sh` or systemd service for headless operation

## License

Proprietary - All rights reserved
