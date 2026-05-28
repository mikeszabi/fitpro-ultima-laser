# FitPro Ultima Laser Qt Kiosk

Natív PySide6/QML kiosk alkalmazás a Jetson célhardverhez. Ez az app nem böngészőben fut; a meglévő FastAPI backendhez csatlakozik HTTP-n keresztül.

## Fejlesztői indítás

```bash
cd qt_app
python3 -m venv qt_venv
source qt_venv/bin/activate
pip install -r requirements.txt
python main.py --windowed
```

Alapértelmezett backend:

```text
http://127.0.0.1:8000
```

Felülírható:

```bash
FITPRO_API_BASE_URL=http://127.0.0.1:8000 python main.py --windowed
```

## Kiosk indítás

```bash
./run-kiosk.sh
```

A `run-kiosk.sh` kikapcsolja az X11 képernyővédőt és a DPMS blankinget, majd fullscreen módban indítja az appot. Fejlesztéshez használd a `python main.py --windowed` parancsot.

## Touchscreen ellenőrzés Jetsonon

```bash
cat /proc/bus/input/devices
sudo evtest
xinput list
```

Ha az érintés látszik input eventként, de a pozíció elcsúszik, X11 alatt `xinput_calibrator` vagy `xinput set-prop ... "Coordinate Transformation Matrix" ...` szükséges.

Touch UX állapot:

- Qt mouse/touch esemény szintézis engedélyezve.
- A teljesítményállítók slider mellett nagy `-` / `+` gombokat is használnak.
- A FIRE gomb nyomva tartás után indít.
- A STOP nagy, közvetlen gombként elérhető.

## Szerkezet

```text
qt_app/
  main.py                 # PySide6 entrypoint
  app_controller.py       # natív app state + QML slotok
  api_client.py           # FastAPI backend kliens
  qml/
    Main.qml              # fő ablak és képernyőváltás
    components/           # újrahasznált QML elemek
    screens/              # natív képernyők
  systemd/
    fitpro-ultima-kiosk.service
```

## Design and language

The QML interface is intentionally aligned with the existing React frontend: Ultima wave background, portrait 1080x1920 composition, white rounded treatment panels, vertical output bars, circular treatment mode controls, and the circular camera/status section. The native UI text is English.

## Jelenlegi állapot

Az első natív verzió a fő kezelési flow-t tartalmazza:

- start képernyő
- login placeholder
- beállítások placeholder
- rendszerinformáció
- laser treatment képernyő
- backend health / stats / laser settings szinkron
- kamera frame frissítés `/frame/current` alapján
- laser arm/disarm, red dot, vacuum, capture/load targets, fire, stop parancsok

Ez még nem teljes feature-paritás a React alkalmazással, hanem a Jetsonon futtatható natív alap.
