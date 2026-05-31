# FitPro Ultima Laser rendszerarchitektura

Ez a dokumentum a FitPro Ultima Laser aktualis szoftveres es hardverkozeli architekturajat foglalja ossze. A kezelo felulet nativ PySide6/QML kiosk alkalmazas a `qt_app/` mappaban.

## 1. Rendszerattekintes

A rendszer egy erintokepernyos, nativ Qt kiosk alkalmazasbol, egy lokalis Python/FastAPI backendbol es egy soros porton elerheto mikrokontrolleres vezerlobol all.

```text
Erintokepernyo / PySide6 QML kiosk app
        |
        | HTTP JSON, MJPEG frame URL
        v
Python FastAPI / Uvicorn :8000
        |
        | USB Virtual COM, 115200 8N1
        v
STM32 / mikrokontroller
        |
        +--> lezer modulok: 808 / 980 / 1064 nm, red dot
        +--> galvo / target pozicionalas
        +--> vakuum allapot es safety check
        +--> szenzorok: homerseklet, aram, feedback, allapotok
```

A Qt app kozvetlenul a backend API-t hivja, kulon webes kiszolgalasi reteg nelkul.

## 2. Fobb komponensek

### Nativ Qt frontend

A frontend ebben a repoban talalhato: `qt_app/`.

Technologiak:

- Python 3
- PySide6 / Qt Quick / QML
- QML kepernyok es komponensek
- Python controller reteg Qt propertykkel, signalokkal es slotokkal
- egyszeru HTTP kliens a FastAPI backendhez

Fo feladatai:

- erintokepernyos kiosk UI
- kepernyonavigacio: start, login placeholder, settings placeholder, system info, laser treatment
- lezer parameter UI: 808 / 980 / 1064 teljesitmeny, pulse width, arm/disarm
- red dot, vakuum, capture/load targets, fire es stop kontrollok
- kamera frame megjelenitese a backend `/frame/current` endpointjan keresztul
- backend allapot, hiba es foglaltsagi allapot megjelenitese

Fontos Qt frontend fajlok:

- `qt_app/main.py`: PySide6 entrypoint, QML engine inicializalas
- `qt_app/app_controller.py`: nativ alkalmazasallapot, QML propertyk, slotok es async API worker logika
- `qt_app/api_client.py`: FastAPI backend kliens
- `qt_app/qml/Main.qml`: fo ablak, fullscreen/windowed mod, screen loader, globalis error dialog
- `qt_app/qml/screens/`: QML kepernyok
- `qt_app/qml/components/`: ujrahasznalt QML komponensek
- `qt_app/run-kiosk.sh`: fullscreen kiosk indito script
- `qt_app/systemd/fitpro-ultima-kiosk.service`: systemd minta service

Alapertelmezett backend URL:

```text
http://127.0.0.1:8000
```

Felulirhato:

```bash
FITPRO_API_BASE_URL=http://127.0.0.1:8000 python main.py --windowed
python main.py --api-base-url http://127.0.0.1:8000 --windowed
```

### Python backend

A backend a kapcsolodo `hairkiller` projektben talalhato FastAPI alkalmazas. Fejlesztesben es productionben Uvicorn futtatja, alapertelmezett portja `8000`.

Feladatai:

- REST API biztositasa a Qt frontend szamara
- kamera kepfolyam kezelese
- hajszal/follicle detektalas YOLO modellel
- detektalt pontok tarolasa es celpontokka alakitasa
- kepkoordinatak galvo koordinatakka konvertalasa homografia alapjan
- mikrokontroller parancsok osszeallitasa es soros porton kuldese
- hardvervalaszok ertelmezese es JSON API valaszokka alakitasa

Fontos backend modulok a `hairkiller` projektben:

- `app/hk_full_app.py`: real FastAPI alkalmazas
- `app/hk_mock_app.py`: hardver nelkuli mock backend
- `code/serial_devices_handler.py`: soros kommunikacio
- `code/serial_commands.py`: firmware parancsok es metadata
- `code/laser_handler.py`: lezer vezerles magasabb szintu wrapperben
- `code/target_handler.py`: target lista es szekvencia vezerles
- `code/galvo_handler.py`: galvo mozgatasi logika
- `code/detection_handler.py`: detektalas es pontkezeles
- `code/camera_handler.py`: kamera kezeles

Backend inditas fejleszteshez:

```bash
cd /home/jetson/Projects/hairkiller
python3 -m uvicorn app.hk_full_app:app --host 0.0.0.0 --port 8000
```

Backend service production peldaja:

```text
systemd service: hairkiller-backend
working directory: /home/jetson/Projects/hairkiller
exec: uvicorn backend.hk_backend_app:app --host 127.0.0.1 --port 8000
```

### Mikrokontroller reteg

A mikrokontroller USB Virtual COM porton keresztul erheto el. A dokumentalt fizikai kommunikacio:

- port: altalaban `/dev/ttyACM0`
- baud: `115200`
- parity: none
- stop bit: `1`
- data bit: `8`

Feladatai:

- lezer arm/disarm, lezer teljesitmeny es impulzushossz vezerlese
- 808 / 980 / 1064 nm csatornak es 660 nm red-dot kezelese
- galvo/target pozicio beallitasa `0..4095` koordinata tartomanyban
- target szekvencia inditasa, megallitasa, folytatasa
- vakuum es egyeb safety feltetelek ellenorzese
- szenzoradatok szolgaltatasa: lezerhomerseklet, aramok, tapfeszultseg, galvo feedback, hibaallapotok

Tipikus firmware parancsok:

```text
LASER_SET_ARM_EN 1
LASER_SET_ARM_EN 0
LASER_SET_CHANNEL_PWR 20,25,50
LASER_SET_RED_DOT_EN 1
LASER_FIRE 20
TARGET_SET_POS 1500,2000
TARGET_SET_NEW_TARGET x0,y0,x1,y1,p808,p980,p1064,duration_ms
TARGET_START
TARGET_STOP
APP_SET_VACUUM_EN 1
APP_SET_CHECK_VACUUM 1
SENSORS_GET_VALUES
```

A mikrokontroller valaszai szoveges protokollt kovetnek:

```text
[LASER_SET_ARM_EN][1]->[OK][12523]
[TARGET_START]->[NOK][reason][12523]
```

## 3. Kommunikacios kapcsolatok

### Qt frontend -> Backend

A `qt_app/api_client.py` szinkron HTTP hivasokat vegez `urllib.request` alapon. Az `AppController` ezeket `QThreadPool` workerben futtatja, hogy a QML UI ne blokkoljon.

Hasznalt endpointok:

```text
GET  /health
GET  /stats
GET  /detection/status
GET  /frame/current
GET  /laser/settings
GET  /sensors/values
GET  /seq/status

POST /detection/toggle?enabled=true|false
POST /detection/conf?conf=<0.01..1.0>
POST /detection/capture
POST /points/clear
POST /seq/update_targets
POST /seq/clear_targets
POST /seq/show_targets?enabled=true|false
POST /seq/mode?mode=manual|auto
POST /seq/start
POST /seq/step
POST /seq/stop
POST /laser/settings
POST /laser/arm
POST /laser/disarm
POST /laser/red_dot?enabled=true|false
POST /laser/fire?duration_ms=<ms>
POST /app/raw_command
POST /app/clear_error
```

A kamera megjelenites nem SSE-alapu. A QML kepforras a `/frame/current` URL-t kapja meg, cache-busting query parameterrel frissitve.

### Backend -> Mikrokontroller

A backend magasabb szintu API hivasaibol firmware parancsokat general. Pelda:

```text
Qt frontend:
POST /laser/settings

Backend:
LASER_SET_CHANNEL_PWR <p808>,<p980>,<p1064>
SET_LAS_PULSE / target pulse metadata

Mikrokontroller:
[...]->[OK][timestamp] vagy [...]->[NOK][reason][timestamp]
```

Target szekvencia eseten:

```text
Qt frontend:
POST /detection/capture
POST /seq/update_targets
POST /seq/start

Backend:
1. YOLO detektalas a legfrissebb kamerakepen
2. kepkoordinatak -> galvo koordinatak
3. TARGET_CLEAR_TARGETS
4. TARGET_SET_NEW_TARGET minden celpontra
5. TARGET_SET_MODE manual/auto
6. TARGET_START vagy TARGET_STEP
```

## 4. Futasmodok

### Fejlesztoi mod

```text
PySide6/QML app --windowed
        |
        v
Python backend :8000
        |
        v
mock backend vagy real mikrokontroller
```

Inditas:

```bash
# Qt frontend
cd /home/jetson/Projects/fitpro-ultima-laser/qt_app
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python main.py --windowed

# backend
cd /home/jetson/Projects/hairkiller
python3 -m uvicorn app.hk_full_app:app --host 0.0.0.0 --port 8000
```

Hardver nelkuli fejleszteshez a backend mock app hasznalhato.

### Production / kioszk mod

```text
system boot
   |
   +--> systemd: hairkiller-backend.service -> Uvicorn :8000
   |
   +--> systemd: fitpro-ultima-kiosk.service -> PySide6/QML fullscreen kiosk
```

Qt kiosk inditas:

```bash
cd /opt/fitpro-ultima-laser/qt_app
./run-kiosk.sh
```

A `run-kiosk.sh` X11 alatt kikapcsolja a kepernyovedot es DPMS blankinget, beallitja a `QT_QPA_PLATFORM=xcb` es `FITPRO_API_BASE_URL` kornyezeti valtozokat, majd fullscreen modban inditja a PySide6 appot.

Systemd minta:

```text
WorkingDirectory=/opt/fitpro-ultima-laser/qt_app
Environment=DISPLAY=:0
Environment=QT_QPA_PLATFORM=xcb
Environment=FITPRO_API_BASE_URL=http://127.0.0.1:8000
ExecStart=/opt/fitpro-ultima-laser/qt_app/run-kiosk.sh
Restart=always
```

## 5. Fo kezelesi folyamat

### Indulas

1. Backend elindul es inicializalja a kamerat, detektort, homografiat es soros hardver interfeszeket.
2. Qt kiosk service elinditja a PySide6/QML alkalmazast.
3. `main.py` letrehozza az `ApiClient` es `AppController` peldanyokat, majd betolti a `Main.qml` fajlt.
4. A QML screen loader a controller `screen` propertyje alapjan rendereli az aktualis kepernyot.
5. A laser treatment kepernyore lepve a controller lekeri az alap backend allapotot:
   - `/health`
   - `/laser/settings`
   - `/detection/status`
   - `/stats`

### Target capture es betoltes

1. A Qt app torli a korabbi targeteket es pontokat.
2. Kikapcsolja a target overlayt.
3. Meghivja a `/detection/capture` endpointot.
4. Ha van detektalt pont, meghivja a `/seq/update_targets` endpointot.
5. Bekapcsolja a target megjelenitest `/seq/show_targets?enabled=true` hivassal.

### Fire / Stop

1. FIRE hatasara a Qt app beallitja a szekvencia modot.
2. Manual modban `/seq/step` fut.
3. Auto es semi-auto modban `/seq/start` fut.
4. STOP hatasara `/seq/stop` fut, majd a controller megprobalja torolni a backend hiballapotot `/app/clear_error` hivassal.

## 6. Adat- es koordinatarendszerek

A backend tobb koordinatarendszert kezel:

- stream koordinata: `960x960`, UI/kepfolyam meret
- native cropped kamera koordinata: `1920x1920`
- galvo koordinata: `0..4095`

A detektalas native kepkoordinatakat ad. Ezeket a backend homografia segitsegevel galvo koordinatakka konvertalja. A target handler minden galvo koordinatat `0..4095` koze clampel, mielott mikrokontroller parancs lesz belole.

## 7. Allapotkezeles

Qt frontend oldalon:

- `AppController` tarolja a nativ UI allapotot Python propertykben.
- QML kepernyok property bindingokon keresztul olvassak az allapotot.
- QML gombok es kontrollok Qt slotokat hivnak.
- API hivasok `QThreadPool` workerben futnak.
- Hibak a globalis `ErrorDialog` komponensben jelennek meg.

Backend oldalon:

- A kamera folyamatosan friss frame-et szolgaltat.
- A detektalas csak bekapcsolt allapotban fut.
- A detektalt pontok es betoltott targetek backend memoriaban elnek.
- A mikrokontroller a vegso autoritativ allapot a lezer, target, vakuum es szenzorok tekinteteben.

## 8. Biztonsagi es uzemeltetesi megfontolasok

Fontos biztonsagi hatarok:

- A Qt frontend nem kozvetlenul vezerel hardvert, csak backend API-t hiv.
- A backend validalja a kerest, majd a hardver handler reteg clampeli a kritikus tartomanyokat.
- A mikrokontroller tovabbi safety felteteleket ervenyesit: arm allapot, vakuum, aktiv folyamat, homerseklet, hibak.
- Disarm/stop parancsoknak barmikor vegrehajthatonak kell maradniuk.

Uzemeltetes:

- A backend systemd service-kent fusson, naplozasa `journalctl -u hairkiller-backend -f`.
- A Qt kiosk kulon systemd service-kent fusson, naplozasa `journalctl -u fitpro-ultima-kiosk -f`.
- A Qt app dedikalt kiosk userrel es minimalis desktop kornyezettel fusson.
- A soros port jogosultsagokat a `setup_serial.sh` allitsa be.
- A backend API alapertelmezetten csak lokalis interface-en legyen elerheto productionben.

## 9. Deployment artefaktumok

Ebben a repoban:

- `qt_app/`: aktualis nativ Qt frontend
- `qt_app/requirements.txt`: PySide6 dependency
- `qt_app/run-kiosk.sh`: kiosk indito script
- `qt_app/systemd/fitpro-ultima-kiosk.service`: Qt kiosk systemd service minta
- `deploy/hairkiller-backend.service`: backend systemd service minta

Kapcsolodo backend repoban:

- `docs/hk_full_app_api.md`: backend API referencia
- `docs/README_serial.md`: soros/mikrokontroller kommunikacio
- `docs/stm_command_reference_from_code.xlsx`: STM parancsreferencia
- `setup_scripts/setup_serial.sh`: soros port jogosultsag beallitas

## 10. Nyitott architekturalis pontok

A jelenlegi repo es dokumentacio alapjan ezek a pontok tovabbi dontest vagy pontositast igenyelhetnek:

- A backend service fajlban szereplo `backend.hk_backend_app:app` es a fejlesztoi doksiban szereplo `app.hk_full_app:app` kozotti production entrypoint egyeztetese.
- A production telepitesi utvonal veglegesitese: repo checkout vagy `/opt/fitpro-ultima-laser`.
- Touchscreen kalibracio es X11/Wayland platform valasztas veglegesitese Jetsonon.
- Automatikus Qt smoke tesztek es backend integration smoke tesztek bevezetese.
