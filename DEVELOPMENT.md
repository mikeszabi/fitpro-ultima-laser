# FitPro Ultima Laser - fejlesztoi dokumentacio

Ez a dokumentum a projekt fejlesztoi attekinteset, architekturajat, es a napi fejleszteshez szukseges lepeseket tartalmazza.

## Attekintes

A projekt egy React + TypeScript frontend mock a FitPro Ultima Laser kezelo feluletehez. A UI-t az Adobe XD specifikaciok alapjan, 1080x1920 (9:16, portrait) erintesre optimalizalt kijelzohoz terveztek. Minden backend es hardver kommunikacio mockolva van.

## Technologiai stack

- React 18 + TypeScript
- Vite 5 (build + dev server)
- Redux Toolkit (alkalmazasallapot)
- i18next + react-i18next (angol/magyar nyelv)
- SCSS (design system valtozokkal)

## Kovetelmenyek

- Node.js 18+ (Vite 5 ajanlott minimum)
- npm

## Node.js install
sudo apt update
sudo apt install -y curl
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

node -v
npm -v

## Gyors inditas

```bash
npm install
npm run dev
```

Alapertelmezett dev cim: `http://localhost:3000`

## Hasznos scriptek

```bash
npm run dev       # fejlesztoi szerver
npm run build     # TypeScript build + Vite build
npm run preview   # production build preview
npm run lint      # eslint
```

## Projekt struktura

```
src/
  App.tsx                 # ekran-valaszto logika + modalok
  main.tsx                # React entry point + Provider + i18n init
  components/
    common/               # gombok, kontenerek, hatterek
    modals/               # GUI update + hibauzenet modalok
  features/               # screen modulok
  i18n/                   # nyelvi fajlok + init
  services/               # mock service reteg
  store/                  # Redux store + slice-ok
  styles/                 # globalis stilus + valtozok + fontok
  types/                  # kozos TypeScript tipusok
```

## Alkalmazas folyamata

Az `App.tsx` a `ui.currentScreen` alapjan rendereli a megfelelo screen komponenst. A GUI update modal es a hiba modal globalisan a root szinten jelenik meg.

Screen valtas:
- `uiSlice` tarolja a `currentScreen` erteket.
- A screen komponensek akciokkal allitjak a navigaciot.

## Allapotkezeles (Redux Toolkit)

Fobb slice-ok:
- `authSlice`: bejelentkezes/fulfillment mock.
- `uiSlice`: screen navigacio, GUI update modal, hiba modal.
- `settingsSlice`: kalibracio, skin type, hair type/color, treatment mode.
- `laserSlice`: laser parameterek, output performance, run state.
- `systemSlice`: rendszer allapot, kapcsolat monitorozas, rendszer info.

Store init: `src/store/index.ts`
Typed hookok: `src/store/hooks.ts`

## Mock service reteg

`src/services/` alatt minden kulso kommunikacio mockolva van:
- `authService.ts`: bejelentkezes szimulacio
- `configService.ts`: konfiguracio mock (helyi allapot)
- `hardwareService.ts`: hardver parancsok + heartbeat szimulacio (random hibaval)

Fejleszteskor ezek helyere valos API/hardver integracio toltheto be.

## Internationalizacio (i18n)

Init: `src/i18n/index.ts`
Nyelvek:
- `src/i18n/locales/en.json`
- `src/i18n/locales/hu.json`

Uj kulcs hozzaadas:
1. Add a kulcsot mindket JSON fajlhoz.
2. Hasznald `useTranslation()`-nel a komponensben.

## Stilus es design system

Globalis SCSS:
- `src/styles/variables.scss`: szinek, spacing, tipografia meretek
- `src/styles/fonts.scss`: egyedi font definiciok
- `src/styles/global.scss`: globalis reset es alap stilusok

Komponens stilusok:
Minden komponensnek sajat `.scss` fajlja van, a markup kozeleben.

## UI komponensek

Kiemelt kozos elemek:
- `Button`, `BackButton`, `InfoButton`
- `Container` (feher border + rounded layout)
- `WaveBackground` (animalt hatter)

Modalok:
- `GUIUpdateModal` (update info)
- `ErrorModal` (globalis hiba)

## Uj screen hozzaadasa

1. Hozz letre uj mappat `src/features/<screen-name>/` alatt.
2. Implementald a komponenset es a SCSS-t.
3. Add hozza `ScreenType` unionhoz a `src/types/index.ts` fajlban.
4. Bovitd az `App.tsx` `renderScreen()` switch-et.
5. Szükség eseten add hozza a navigacios akciot a `uiSlice`-hoz.

## Uj slice hozzaadasa

1. Keszits uj slice-ot a `src/store/slices/` alatt.
2. Exportald a reducer-t.
3. Add hozza a root store-hoz `src/store/index.ts`.
4. Hasznald a typed hookokat (`useAppDispatch`, `useAppSelector`).

## Build es kiadas

Production build:
```bash
npm run build
```

Preview:
```bash
npm run preview
```

Vite build output a `dist/` mappaba kerul.

## Linting

```bash
npm run lint
```

Lint config: ESLint + TypeScript + React hooks.

## Teszteles

Jelenleg nincs automatikus tesztkeszlet. Javasolt irany:
- UI/komponens tesztek: React Testing Library
- State tesztek: Redux slice unit tesztek
- i18n snapshot/konzisztencia ellenorzes

## Kiberbiztonsag (Jetson Nano Orin 8GB + browser futtatas)

Az alkalmazas erintes-alapu kioszk jellegu UI. A cel, hogy a browserben futva se legyen trivialisan tamadhato. Az alabiak fejlesztesi es megvalositasi javaslatok.

### Kioszk es OS hardening

- Kioszk mod: dedikalt user, minimal UI, csak a megfelelo URL elerheto.
- Auto-start: rendszerinditas utan automatikus browser inditas, alkalmazas fokuszban tartasa.
- OS update fegyelme: rendszeres patchek, felesleges service-ek leallitasa.
- USB/Peripheral korlatozas: ha nem kell, tiltsd a hotplug es storage eszkozoket.

### Browser es futtatas biztonsag

- Offline mod: ahol lehet, ne legyen altalanos internet eleres (csak lokal).
- Korlatozott domain: a UI csak a sajat originrol toltson be eroforrasokat.
- Kioszk flag-ek: tiltsd a DevTools elerest es uj ablakok nyitasat.
- Session izolacio: ne legyen normal user profillal inditva a browser.

### Web biztonsagi header-ek

Ha van szerveroldal (pl. Nginx) a statikus build kiszolgalashoz, ajanlott header-ek:

```
Content-Security-Policy: default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'
X-Content-Type-Options: nosniff
Referrer-Policy: no-referrer
X-Frame-Options: DENY
Permissions-Policy: camera=(), microphone=(), geolocation=(), usb=()
```

Megjegyzes: a CSP-t a valos eroforrasokhoz kell igazitani. Ha inline script nincs, az `unsafe-inline` elhagyhato.

### UI szintu tamadasfeluletek minimalizalasa

- Ne jelenits meg felhasznaloi inputot HTML-kent (XSS).
- Soha ne hasznalj `dangerouslySetInnerHTML`-t.
- Minden user inputot kezeld szovegkent, escape-elve.
- Ne logolj erzekeny adatot a browser konzolra.

### Mock helyett valos API integracio (ha lesz)

- Kommunikacio csak HTTPS vagy belso IPC csatornan.
- Hitelesites: token alap (lejaro, rovid TTL), szerveroldali ellenorzes.
- Rate limit es request validation a backend oldalon.
- Strict CORS: csak a sajat origin.

### Build es deployment javaslatok

- Production build: `npm run build`
- A `dist/` statikus buildet lehet Nginx-zel kiszolgalni.
- Szigoruan kezeld a file jogosultsagokat (read-only a build outputra).
- Disable directory listing.

### Monitorozas es audit

- Minimal logolas (hiba es usage szint).
- Log rotacio es storage limit.
- Crash es restart: watchdog/systemd.

### Pentest-ellenorzes lista

- XSS: nincsenek inline script injection pontok.
- CSP: helyesen beallitva es enforced.
- CORS: csak sajat origin.
- Kioszk mod: DevTools es uj ablakok tiltva.
- Offline mod: nincs altalanos internet eleres.

## Gyakori hibak / tippek

- Ha a font nem toltodik be, ellenorizd a `src/styles/fonts.scss` fajlban a path-okat.
- Ha nem valt screen, ellenorizd a `uiSlice` akcioit es a `currentScreen` erteket.
- Random hardver hibak a `hardwareService.ts` mockbol jonnek (5%).

## Natív Qt/QML kiosk irány

A `qt` branchben elindult egy böngészőmotor nélküli Jetson kiosk alkalmazás a `qt_app/` mappában.

### Célarchitektúra

```text
PySide6/QML natív kiosk app
        |
        | HTTP / MJPEG frame frissítés
        v
FastAPI backend :8000
        |
        | USB serial
        v
STM32 / lézer vezérlő
```

### Fejlesztői indítás

```bash
cd qt_app
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python main.py --windowed
```

Backend URL felülírás:

```bash
FITPRO_API_BASE_URL=http://127.0.0.1:8000 python main.py --windowed
```

### Kiosk indítás

Paraméter nélkül fullscreenben indul:

```bash
python qt_app/main.py
```

Systemd példa:

```text
qt_app/systemd/fitpro-ultima-kiosk.service
```

Touchscreen/X11 kiosk indításnál a service a `qt_app/run-kiosk.sh` scriptet használja. Ez kikapcsolja a képernyővédőt és DPMS blankinget, majd `QT_QPA_PLATFORM=xcb` beállítással indítja a natív appot.

Érintés ellenőrzése Jetsonon:

```bash
cat /proc/bus/input/devices
sudo evtest
xinput list
```

Ha a panel érintésre küld eventeket, de a pozíció elcsúszik, X11 alatt `xinput_calibrator` vagy `xinput set-prop ... "Coordinate Transformation Matrix" ...` szükséges.

### Fontos fájlok

- `qt_app/main.py`: PySide6 entrypoint.
- `qt_app/app_controller.py`: QML-ből hívható app state és parancsok.
- `qt_app/api_client.py`: a meglévő FastAPI backend Python kliense.
- `qt_app/qml/screens/LaserTreatmentScreen.qml`: első natív kezelési képernyő.

### Jelenlegi státusz

Az első natív változat futtatható alapot ad, de még nem teljes feature-paritás a React UI-val. A fő kezelés flow már átkerült: backend sync, kamera frame frissítés, lézer ARM/DISARM, teljesítmény csúszkák, red dot, vákuum, célpont betöltés, FIRE és STOP.

Touch UX:

- A Qt app egér/touch esemény szintézist engedélyez a `main.py`-ban.
- A teljesítményállítók slider mellett nagy `-` / `+` gombokat is kaptak.
- A FIRE gomb nyomva tartás után indít, véletlen érintés ellen.
- A STOP nagy, közvetlen gombként marad elérhető.
