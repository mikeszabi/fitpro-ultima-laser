# FitPro Ultima Laser - fejlesztoi dokumentacio

Ez a dokumentum a projekt aktualis fejlesztoi attekinteset es a napi fejleszteshez szukseges lepeseket tartalmazza. A projekt fo frontendje mar a `qt_app/` alatti nativ PySide6/QML kiosk alkalmazas. A regi React/Vite frontend tovabbra is a repoban van, de jelenleg legacy/design referencia.

## Attekintes

A FitPro Ultima Laser UI egy nativ Qt kiosk alkalmazas Jetson celhardverre, 1080x1920-as portrait erintokepernyore optimalizalva. A Qt app HTTP-n keresztul kapcsolodik a lokalis FastAPI backendhez, amely a kamerat, detektalast, target-generalast es a mikrokontrolleres hardvervezerlest kezeli.

## Technologiai stack

- Python 3
- PySide6 / Qt Quick / QML
- FastAPI backend kliens `urllib.request` alapon
- QThreadPool worker alapu async API hivasok
- QML komponensek es kepernyok
- Hurme fontok es a meglovo visual assetek a `public/` mappabol

Legacy/reference stack:

- React 18 + TypeScript
- Vite 5
- Redux Toolkit
- i18next / react-i18next
- SCSS

## Kovetelmenyek

- Python 3.10+ ajanlott
- `python3-venv`
- PySide6 (`qt_app/requirements.txt`)
- Futasanak celkornyezete: Jetson + X11, `QT_QPA_PLATFORM=xcb`
- Backend: lokalis FastAPI service a `8000` porton

## Gyors inditas

Qt frontend:

```bash
cd qt_app
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python main.py --windowed
```

Alapertelmezett backend:

```text
http://127.0.0.1:8000
```

Feluliras:

```bash
FITPRO_API_BASE_URL=http://127.0.0.1:8000 python main.py --windowed
python main.py --api-base-url http://127.0.0.1:8000 --windowed
```

Backend inditas a kapcsolodo `hairkiller` projektbol:

```bash
cd /home/jetson/Projects/hairkiller
python3 -m uvicorn app.hk_full_app:app --host 0.0.0.0 --port 8000
```

## Kiosk inditas

```bash
cd qt_app
./run-kiosk.sh
```

A `run-kiosk.sh`:

- kikapcsolja az X11 screensavert
- kikapcsolja a DPMS blankinget
- beallitja a `QT_QPA_PLATFORM=xcb` valtozot
- beallitja a `FITPRO_API_BASE_URL` valtozot, ha nincs megadva
- fullscreen modban inditja a PySide6 alkalmazast

Fejleszteshez tovabbra is a windowed mod javasolt:

```bash
python main.py --windowed
```

## Projekt struktura

```text
qt_app/
  main.py                 # PySide6 entrypoint, QML engine inicializalas
  app_controller.py       # nativ app state + QML propertyk/signalok/slotok
  api_client.py           # FastAPI backend kliens
  requirements.txt        # PySide6 dependency
  run-kiosk.sh            # fullscreen kiosk indito script
  qml/
    Main.qml              # fo ablak, screen loader, globalis error dialog
    components/           # ujrahasznalt QML elemek
    screens/              # nativ kepernyok
  systemd/
    fitpro-ultima-kiosk.service

public/
  assets/                 # logo, hatterek, ikonok, design assetek
  fonts/                  # Hurme fontok

src/                      # regi React/Vite frontend, legacy/reference
deploy/                   # backend service es regi web deployment mintak
```

## Alkalmazas folyamata

`qt_app/main.py`:

1. feldolgozza a `--windowed` es `--api-base-url` argumentumokat
2. engedelyezi a Qt mouse/touch event szintezist
3. letrehozza a `QGuiApplication` peldanyt
4. letrehozza az `ApiClient` es `AppController` peldanyokat
5. `appController` neven kiteszi a controllert QML context propertykent
6. betolti a `qt_app/qml/Main.qml` fajlt

`Main.qml` a `appController.screen` property alapjan valt kepernyot. A globalis hibak az `ErrorDialog` komponensben jelennek meg.

## Allapotkezeles

A Qt appban nincs Redux vagy webes global state. Az allapotot az `AppController` tarolja:

- screen navigacio
- backend kapcsolat/statusz
- busy allapot
- laser armed allapot
- 808 / 980 / 1064 teljesitmeny
- pulse width
- red dot
- vacuum enabled / lock
- target allapot es target darabszam
- confidence
- treatment mode
- kamera frame URL
- globalis hibacim es hibauzenet

A QML UI property bindingokkal olvassa ezeket. A felhasznaloi interakciok QML-bol Qt slotokat hivnak, peldaul:

- `navigate(screen)`
- `syncBackend()`
- `setLaserReady(enabled)`
- `setPower(channel, value)`
- `setPulseWidth(value)`
- `setRedDot(enabled)`
- `setVacuumEnabled(enabled)`
- `setTreatmentMode(mode)`
- `setConfidence(confidence)`
- `captureAndLoadTargets()`
- `fire()`
- `stop()`

## Backend integracio

A backend kliens a `qt_app/api_client.py` fajlban van. Az alap URL:

```text
http://127.0.0.1:8000
```

Fontos backend hivasok:

```text
GET  /health
GET  /stats
GET  /detection/status
GET  /frame/current
GET  /laser/settings
GET  /sensors/values
GET  /seq/status

POST /detection/conf
POST /detection/capture
POST /points/clear
POST /seq/update_targets
POST /seq/clear_targets
POST /seq/show_targets
POST /seq/mode
POST /seq/start
POST /seq/step
POST /seq/stop
POST /laser/settings
POST /laser/arm
POST /laser/disarm
POST /laser/red_dot
POST /laser/fire
POST /app/raw_command
POST /app/clear_error
```

Az API hivasokat az `AppController._run()` workerbe csomagolja, igy a QML UI nem fagy be lassu backend vagy hardvervalasz eseten.

## UI fejlesztes QML-ben

Kepernyok:

- `qt_app/qml/screens/StartScreen.qml`
- `qt_app/qml/screens/LoginScreen.qml`
- `qt_app/qml/screens/SettingsScreen.qml`
- `qt_app/qml/screens/LaserTreatmentScreen.qml`
- `qt_app/qml/screens/SystemInfoScreen.qml`

Kozos komponensek:

- `AppButton.qml`
- `BackButton.qml`
- `ErrorDialog.qml`
- `HoldFireButton.qml`
- `ModeButton.qml`
- `PowerControl.qml`
- `StatusPill.qml`

Uj kepernyo hozzaadasa:

1. Hozz letre uj QML fajlt `qt_app/qml/screens/` alatt.
2. Importald vagy hasznald a screen komponenst `Main.qml`-ben.
3. Adj hozza uj screen azonosito erteket az `AppController.navigate()` hasznalati helyein.
4. Bovitd a `Main.qml` loader switch logikajat.

Uj backend muvelet hozzaadasa:

1. Adj uj methodust az `ApiClient` osztalyhoz.
2. Adj QML-bol hivhato `@Slot` methodust az `AppController` osztalyhoz.
3. A hosszu vagy blokkolhato hivasokat az `_run()` helperen keresztul futtasd.
4. Siker eseten frissitsd a controller propertyket es emiteld a megfelelo signalokat.

## Design es assetek

A QML UI szandekosan kozel tartja magat a korabbi React frontend latvanyahoz:

- Ultima wave hatter
- 1080x1920 portrait kompozicio
- feher kezelesi panelek
- vertikalis output barok
- kor alaku treatment mode kontrollok
- kor alaku kamera/statusz szekcio

Fontok es assetek:

- `public/fonts/`
- `public/assets/`

## Touchscreen es Jetson tippek

Touchscreen ellenorzes:

```bash
cat /proc/bus/input/devices
sudo evtest
xinput list
```

Ha az erintes latszik input eventkent, de a pozicio elcsuszik, X11 alatt `xinput_calibrator` vagy `xinput set-prop ... "Coordinate Transformation Matrix" ...` szukseges.

A Qt appban engedelyezve van:

- `Qt.AA_SynthesizeMouseForUnhandledTouchEvents`
- `Qt.AA_SynthesizeTouchForUnhandledMouseEvents`

## Systemd

Qt kiosk service minta:

```bash
sudo cp qt_app/systemd/fitpro-ultima-kiosk.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable fitpro-ultima-kiosk
sudo systemctl start fitpro-ultima-kiosk
```

Statusz es log:

```bash
sudo systemctl status fitpro-ultima-kiosk
sudo journalctl -u fitpro-ultima-kiosk -f
```

A service alapertelmezett telepitesi utvonala:

```text
/opt/fitpro-ultima-laser/qt_app
```

Ha fejlesztoi checkoutbol futtatod, modositani kell a `WorkingDirectory` es `ExecStart` ertekeket.

## Backend es serial setup

A backend systemd minta a `deploy/hairkiller-backend.service` fajlban van.

Serial jogosultsag a `hairkiller` projektbol:

```bash
cd /home/jetson/Projects/hairkiller/setup_scripts
./setup_serial.sh
```

A setup tipikusan:

- jogosultsagot ad a `/dev/ttyACM0` STM32 Virtual COM eszkozre
- hozzaadja a usert a `dialout` csoporthoz
- beallitja a megfelelo file permissiont

Kilepes/bejelentkezes szukseges lehet a csoporttagsag ervenyesulesehez.

## Teszteles

Jelenleg nincs automatizalt Qt tesztkeszlet. Javasolt minimalis manual smoke:

1. Inditsd el a backend mock vagy real appot.
2. Inditsd a Qt appot `python main.py --windowed` paranccsal.
3. Lepj a laser treatment kepernyore.
4. Ellenorizd, hogy a backend statusz OK-ra valt.
5. Ellenorizd, hogy a kamera frame frissul.
6. Probald ki a laser arm/disarm, red dot, vacuum, capture/load targets, fire es stop kontrollokat mock backenddel vagy biztonsagos hardveres korulmenyek kozott.

## Legacy React/Vite frontend

A regi web frontend tovabbra is elerheto:

```bash
npm install
npm run dev
npm run build
```

Ez mar nem az aktualis production kiosk utvonal. A kovetkezo elemek legacy/reference statuszuak:

- `src/`
- `package.json`
- `vite.config.ts`
- `deploy/frontend.nginx`
- `deploy/test-frontend.nginx`
- `deploy/chromium-kiosk.desktop`
- `CHROMIUM_AUTOSTART.md`

## Gyakori hibak / tippek

- Ha a Qt app nem eri el a backendet, ellenorizd a `FITPRO_API_BASE_URL` erteket es a backend `8000` portjat.
- Ha fullscreenben indul, de fejleszteni szeretnel, hasznald a `python main.py --windowed` parancsot.
- Ha a kiosk service nem indul, ellenorizd, hogy a service-ben szereplo `/opt/fitpro-ultima-laser/qt_app` utvonal letezik-e.
- Ha nincs kepfrissites, ellenorizd a backend `/frame/current` endpointjat.
- Ha az erintes pontatlan, ellenorizd az X11 touchscreen kalibraciot.
