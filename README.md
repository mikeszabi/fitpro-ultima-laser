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

## License

Proprietary - All rights reserved
