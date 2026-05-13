# Treatment Frontend-Backend Integration

This document describes how the FitPro Ultima Laser Treatment panel talks to the HairKiller backend and how to start both applications during development.

## Repositories

Frontend repository:

```bash
~/Projects/fitpro-ultima-laser
```

Backend repository:

```bash
~/Projects/hairkiller
```

Backend API reference:

```bash
~/Projects/hairkiller/docs/hk_backend_app_api.md
```

Mock backend implementation:

```bash
~/Projects/hairkiller/app/hk_full_app_mock.py
```

## Runtime Ports

Default frontend:

```text
http://localhost:3000
```

Default HairKiller API:

```text
http://localhost:8000
```

The frontend uses `http://localhost:8000` by default. To point it at another backend URL, set:

```bash
VITE_HK_API_BASE_URL=http://<backend-host>:<port>
```

Example:

```bash
VITE_HK_API_BASE_URL=http://192.168.1.50:8000 npm run dev
```

## Starting The Backend

### Mock Backend

Use this for frontend development without real hardware.

```bash
cd /home/mike/Projects/hairkiller
python3 -m pip install -r requirements.txt
python3 -m uvicorn app.hk_full_app_mock:app --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

Expected response contains:

```json
{"ok": true, "mock": true}
```

### Real Backend

Use this when the real HairKiller app and hardware controllers are available.

```bash
cd /home/mike/Projects/hairkiller
python3 -m pip install -r requirements.txt
python3 -m uvicorn app.hk_full_app:app --host 0.0.0.0 --port 8000
```

The real backend uses camera, detector, galvo, target controller, laser controller, and serial hardware. If one of these is unavailable, related endpoints may return JSON errors such as `Laser unavailable`, `Target controller unavailable`, or `No points`.

## Starting The Frontend

Install dependencies once:

```bash
cd /home/mike/Projects/fitpro-ultima-laser
npm install
```

Run the Vite dev server:

```bash
npm run dev
```

Open:

```text
http://localhost:3000
```

Production build check:

```bash
npm run build
```

## Frontend Code Entry Points

Treatment screen:

```bash
src/features/laser-treatment/LaserTreatmentScreen.tsx
```

Treatment styles:

```bash
src/features/laser-treatment/LaserTreatmentScreen.scss
```

HairKiller API client:

```bash
src/services/hairKillerApi.ts
```

Vite env typing:

```bash
src/vite-env.d.ts
```

## Backend Endpoints Used By Treatment

Connection and status:

```text
GET  /health
GET  /stats
GET  /laser/settings
GET  /laser/temp
GET  /detection/status
GET  /sse/detection
GET  /frame/current
```

Detection and target preparation:

```text
POST /detection/toggle?enabled=true|false
POST /detection/conf?conf=<0.01..1.0>
POST /detection/capture
POST /points/clear
POST /seq/update_targets
POST /seq/clear_targets
POST /seq/show_targets?enabled=true|false
```

Laser and sequence control:

```text
POST /laser/settings
POST /laser/red_dot?enabled=true|false
POST /seq/mode?mode=manual|auto
POST /seq/start
POST /seq/step
POST /seq/stop
```

Vacuum control currently uses the raw command endpoint because the full app API does not expose dedicated typed REST endpoints for vacuum:

```text
POST /app/raw_command
```

Payloads:

```json
{"command": "APP_SET_VACUUM_EN 1"}
{"command": "APP_SET_VACUUM_EN 0"}
{"command": "APP_SET_CHECK_VACUUM 1"}
{"command": "APP_SET_CHECK_VACUUM 0"}
```

## Treatment Logic

The Treatment panel supports three operating modes.

### Auto

User intent:

```text
Vacuum closes, hairs are detected, and the frontend automatically fires the target sequence.
```

Frontend flow:

1. Enable detection.
2. Enable backend vacuum safety check.
3. Set target sequence mode to `auto`.
4. When `VACUUM LOCK` is turned on:
   - call `/detection/capture`
   - call `/seq/update_targets`
   - call `/seq/show_targets?enabled=true`
   - call `/seq/start`

### Semi Auto

User intent:

```text
Targets are detected and loaded automatically, but firing waits for the FIRE button or physical trigger.
```

Frontend flow:

1. Enable detection.
2. Ignore vacuum and do not check vacuum lock.
3. Stop any previous target sequence.
4. Clear any previous errors.
5. Set target sequence mode to `auto`.
6. Call `/detection/capture`.
7. Call `/seq/update_targets`.
8. Call `/seq/show_targets?enabled=true`.
9. When `FIRE` is pressed:
   - ensure laser settings are synced and armed
   - call `/seq/start`

### Manual

User intent:

```text
Vacuum is not required. After detection, every hair shot needs FIRE or physical trigger.
```

Frontend flow:

1. Enable detection.
2. Disable backend vacuum safety check.
3. Set target sequence mode to `manual`.
4. When `FIRE` is pressed:
   - if no targets are loaded, call `/detection/capture` and `/seq/update_targets`
   - call `/seq/step`

## Controls And Backend Mapping

Arm/disarm:

```text
POST /laser/settings
```

The frontend sends current power, pulse width, and `armed`.

808 / 980 / 1064 sliders:

```text
POST /laser/settings
```

The sliders map to backend logical channel power values:

```json
{"p808": 0-100, "p980": 0-100, "p1064": 0-100}
```

Pulse width:

```text
POST /laser/settings
```

The frontend sends:

```json
{"pulse_ms": 10-1000}
```

Red dot:

```text
POST /laser/red_dot?enabled=true|false
```

Vacuum on/off:

```text
POST /app/raw_command
APP_SET_VACUUM_EN 1|0
```

Sensitivity:

```text
POST /detection/conf?conf=<0.01..1.0>
```

There is no separate vacuum sensitivity endpoint in `hk_full_app_api.md` or the mock backend. The Treatment panel therefore maps the sensitivity slider to detection confidence, which is the available treatment-side sensitivity control.

Camera:

```text
GET /frame/current
```

The frontend renders the MJPEG stream directly in an image tag. When detection and target overlay are enabled, the backend draws overlays into the stream.

Target count:

The frontend combines:

```text
/stats detection_count
/stats detected_points
/laser/settings targets_count
/sse/detection count
```

`targets_count` is the count that matters for firing an already loaded target sequence.

## Error Handling

Failed backend calls are surfaced through the existing global `ErrorModal` using `systemSlice.showError`.

Common backend errors:

```text
Laser unavailable
Target controller unavailable
Galvo unavailable
No points
Homography unavailable
```

`No points` usually means `/seq/update_targets`, `/seq/start`, or `/seq/step` was called before a successful `/detection/capture`.

## Development Smoke Test

With backend running:

```bash
curl http://localhost:8000/health
curl -X POST "http://localhost:8000/detection/toggle?enabled=true"
curl -X POST "http://localhost:8000/detection/capture"
curl -X POST "http://localhost:8000/seq/update_targets"
curl -X POST "http://localhost:8000/seq/start"
```

With frontend running:

```bash
curl -I http://localhost:3000/
```

Build verification:

```bash
npm run build
```

## Notes

- Calibration is intentionally out of scope for this integration pass.
- The backend owns detection, coordinate conversion, target ordering/loading, and sequence execution.
- The frontend owns user mode selection, UI state, parameter editing, and sequencing calls based on Treatment mode.
- Keep HairKiller API changes mirrored in `src/services/hairKillerApi.ts` so the screen code stays readable.
