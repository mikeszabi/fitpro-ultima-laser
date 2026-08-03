# FitPro Ultima Laser Qt Kiosk

Natív PySide6/QML kiosk alkalmazás a Jetson célhardverhez. Ez az app nem böngészőben fut; a meglévő FastAPI backendhez csatlakozik HTTP-n keresztül.

## User guide

The full operator guide is available in [USER_GUIDE.md](./USER_GUIDE.md). It documents the recommended workflow, every screen, and what each button does.

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

## Confidence konfiguráció

A Laser Treatment oldalon használt detection confidence tartománya,
alapértéke és érintőképernyős lépésköze a `config.json` fájlban állítható:

```json
{
  "confidence": {
    "minimum": 0.0,
    "maximum": 0.25,
    "default": 0.1,
    "step": 0.005
  }
}
```

Hibás konfiguráció esetén az alkalmazás naplózza a hibát és a beépített
alapértékeket használja. Az aktív tartomány és default a System Info oldalon
is látható.

## Kiosk indítás

```bash
./run-kiosk.sh
```

A `run-kiosk.sh` kikapcsolja az X11 képernyővédőt és a DPMS blankinget, majd fullscreen módban indítja az appot. Fejlesztéshez használd a `python main.py --windowed` parancsot.

Széles kijelzőn, ahol a teljes portré UI-nak látszania kell:

```bash
./run-wide.sh
```

A `run-wide.sh` ugyanúgy fullscreen módban indul, de a 1080x1920-as kezelőfelületet arányosan lekicsinyíti, hogy landscape monitoron se vágódjon le.

## Touchscreen ellenőrzés Jetsonon

```bash
cat /proc/bus/input/devices
sudo evtest
xinput list
```

Ha az érintés látszik input eventként, de a pozíció elcsúszik, X11 alatt `xinput_calibrator` vagy `xinput set-prop ... "Coordinate Transformation Matrix" ...` szükséges.

Ha egy érintés/gombnyomás csak a következő billentyűzet esemény után hajtódik
végre, maradjon bekapcsolva a `QT_XCB_NO_XI2=1` környezeti változó. A launcher
scriptek és service fájlok ezt alapból beállítják, hogy Qt X11 alatt a
stabilabb legacy mouse event útvonalat használja az XInput2 touch útvonal
helyett.
A Qt input event pump alapból ki van kapcsolva (`FITPRO_QT_INPUT_PUMP_MS=0`),
mert a beágyazott `processEvents()` hívások akadozást okozhatnak. Csak célzott
touchscreen hibakereséshez érdemes például `50` értékkel bekapcsolni.

Touch UX állapot:

- Qt mouse/touch esemény szintézis engedélyezve.
- A teljesítményállítók slider mellett nagy `-` / `+` gombokat is használnak.
- A FIRE gomb nyomva tartás után indít.
- A STOP nagy, közvetlen gombként elérhető.

## Szerkezet

```text
qt_app/
  main.py                 # PySide6 entrypoint
  config.json             # kezelőfelületi tartományok és alapértékek
  app_config.py           # konfiguráció betöltése és ellenőrzése
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

The QML interface is intentionally aligned with the Ultima visual design: wave background, portrait 1080x1920 composition, white rounded treatment panels, vertical output bars, circular treatment mode controls, and the circular camera/status section. The native UI text is English.

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

Ez a Jetsonon futtatható natív Qt alap.
