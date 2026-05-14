# FitPro Ultima Laser - Frontend Mock

A frontend implementation for the Ultima Laser treatment system, built to match Adobe XD design specifications.

## Features

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **State Management**: Redux Toolkit
- **Styling**: SCSS with CSS variables (custom components, no UI frameworks)
- **Internationalization**: i18next (English & Hungarian)
- **Target Device**: Touchscreen (9:16 portrait, 1080x1920)
- **Path Aliases**: `@/` for cleaner imports

## Project Structure

```
src/
├── components/      # Reusable UI components
│   ├── common/      # Common components (Button, Container, WaveBackground, etc.)
│   └── modals/      # Modal components (GUIUpdateModal, ErrorModal)
├── features/        # Feature-based modules (screens)
│   ├── start/       # Start screen
│   ├── login/       # Login screen
│   ├── settings/    # Settings screen
│   ├── laser-treatment/  # Laser treatment screen
│   ├── system-info/ # System info screen
│   └── gui-update/  # GUI update loading screen
├── i18n/           # Translation files (en, hu)
├── services/       # Mock API services
│   ├── authService.ts      # Authentication mock
│   ├── configService.ts    # Configuration management
│   └── hardwareService.ts  # Hardware communication mock
├── store/          # Redux store and slices
│   ├── slices/     # Redux slices (ui, auth, settings, laser, system)
│   └── hooks.ts    # Typed Redux hooks
├── styles/         # Global SCSS styles
│   ├── variables.scss  # Design system variables
│   ├── fonts.scss      # Font definitions
│   └── global.scss     # Global styles
└── types/          # TypeScript type definitions
```

## Installation

```bash
npm install
```

## Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Build

```bash
npm run build
```

## Deploy

Builds the project and copies `dist/` to `/var/www/frontend`:

```bash
npm run deploy
```

> Note: `/var/www/frontend` must be writable by your user, or run with `sudo`.

### Nginx Configuration

| Config file | Target folder | Port |
|---|---|---|
| `deploy/frontend.nginx` | `/var/www/frontend` | 80 |
| `deploy/test-frontend.nginx` | `/var/www/test-frontend` | 8080 |

Install production frontend:

```bash
sudo cp deploy/frontend.nginx /etc/nginx/sites-available/frontend
sudo ln -s /etc/nginx/sites-available/frontend /etc/nginx/sites-enabled/frontend
sudo nginx -t
sudo systemctl reload nginx
```

## Backend (Hairkiller)

The backend is a FastAPI/uvicorn service managed by systemd. The service file is at `deploy/hairkiller-backend.service`.

```bash
# Install (first time)
sudo cp deploy/hairkiller-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable hairkiller-backend

# Start / Stop / Restart
sudo systemctl start hairkiller-backend
sudo systemctl stop hairkiller-backend
sudo systemctl restart hairkiller-backend

# Status & logs
sudo systemctl status hairkiller-backend
sudo journalctl -u hairkiller-backend -f
```

## Mock Services

All backend interactions are mocked:
- **Authentication**: Simulated Supabase auth
- **Hardware Control**: Simulated Python backend communication
- **Settings Persistence**: Local state only
- **Connection Monitoring**: Simulated heartbeat/ping

## Design Specifications

The UI matches the Adobe XD designs exactly:
- **Design Reference**: [Adobe XD Specs](https://xd.adobe.com/view/1e639d1c-9bff-4709-b89b-ca24d13d1c70-4b30/grid)
- **Resolution**: 1080x1920 (9:16 portrait)
- **Orientation**: Portrait (vertical touchscreen)
- **Design System**: Comprehensive SCSS variables for colors, typography, spacing, and components
- **Custom Components**: 
  - Wave backgrounds with animated gradients
  - Rounded containers with white borders (39px radius, 3px border)
  - Touch-optimized buttons with shadow effects
  - Circular mode buttons with active states
- **Typography**: Hurme Geometric Sans 3 custom font
- **Animations**: Smooth CSS transitions and transforms
- **Responsive**: Adjustable resolution while maintaining aspect ratio and spacing

## Screens

1. **Start Screen** - Logo and get started button
2. **Login Screen** - Email/password authentication
3. **Settings Screen** - Calibration, skin type, hair color/type selection
4. **Laser Treatment** - Output performance, treatment modes, camera view
5. **System Info** - User details, settings, hardware/software info
6. **GUI Update** - Version check modal and loading screen

## State Management

Redux Toolkit slices:
- **`uiSlice`** - Current screen navigation, modal states (GUI update, error), loading states
- **`authSlice`** - User authentication and session management (mocked)
- **`settingsSlice`** - Treatment settings (calibration, skin type, hair color/type, treatment mode)
- **`laserSlice`** - Laser parameters, output performance, treatment status
- **`systemSlice`** - System status, hardware connection state, heartbeat monitoring

## Components

### Common Components
- **Button** - Touch-optimized button with shadow effects and active states
- **BackButton** - Navigation back button with icon
- **InfoButton** - Circular info button for system information
- **Container** - Rounded container with white border styling
- **WaveBackground** - Animated gradient wave background

### Modals
- **GUIUpdateModal** - Software update notification and confirmation
- **ErrorModal** - Error message display with auto-dismiss

## Touchscreen Coordinate Setup

The touchscreen requires coordinate transformation to work correctly. Copy the `.xprofile` configuration to the user's home folder:

```bash
cp deploy/.xprofile ~/.xprofile
```

This script waits for the "Hi-Tech CoolTouch System" touchscreen device on startup and applies the coordinate transformation matrix to set proper touch coordinates.

## Hacks

```sh
gsettings set org.gnome.desktop.notifications show-banners false
```
^-> this one will hide desktop popups for "system throttled due to over-current" warning -> yolo model start drains too much power, should be sorted out

## License

Proprietary - All rights reserved
