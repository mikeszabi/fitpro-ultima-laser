# FitPro Ultima Laser rendszerarchitektura

Ez a dokumentum a FitPro Ultima Laser teljes szoftveres es hardverkozeli architekturajat foglalja ossze: mikrokontroller, Python backend, Vite/React frontend, Node.js fejlesztoi tooling es Nginx production kiszolgalas.

## 1. Rendszerattekintes

A rendszer egy erintokepernyos, kioszk jellegu kezelo feluletbol, egy lokalis Python backendbol es egy soros porton elerheto mikrokontrolleres vezerlobol all. A frontend bongeszoben fut, a backend FastAPI alkalmazaskent kezeli a kamerat, detektalast, celpont-generalast es a hardverparancsokat, a mikrokontroller pedig a lezer, galvo, vakuum es szenzor alacsony szintu vezerleset vegzi.

Production modban a kommunikacio jellemzoen egyetlen gepen belul tortenik:

```text
Erintokepernyo / Chromium kiosk
        |
        | HTTP, SSE, MJPEG
        v
Nginx :80  ---> statikus React build
        |
        | frontend API hivasok: http://localhost:8000
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

## 2. Fobb komponensek

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

A mikrokontroller valaszai szoveges protokollt kovetnek, peldaul:

```text
[LASER_SET_ARM_EN][1]->[OK][12523]
[TARGET_START]->[NOK][reason][12523]
```

### Python backend

A backend a `hairkiller` projektben talalhato FastAPI alkalmazas. Fejlesztesben es productionben Uvicorn futtatja, alapertelmezett portja `8000`.

Feladatai:

- REST API biztositasa a frontend szamara
- kamera kepfolyam kezelese
- hajszal/follicle detektalas YOLO modellel
- detektalt pontok tarolasa es celpontokka alakitasa
- kepkoordinatak galvo koordinatakka konvertalasa homografia alapjan
- mikrokontroller parancsok osszeallitasa es soros porton kuldese
- hardvervalaszok ertelmezese es JSON API valaszokka alakitasa
- SSE es MJPEG stream kiszolgalasa

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

Backend service production peldaja:

```text
systemd service: hairkiller-backend
working directory: /home/jetson/Projects/hairkiller
exec: uvicorn backend.hk_backend_app:app --host 127.0.0.1 --port 8000
```

A jelenlegi frontend dokumentacio fejleszteshez ezt hasznalja:

```bash
python3 -m uvicorn app.hk_full_app:app --host 0.0.0.0 --port 8000
```

### Frontend alkalmazas

A frontend ebben a repoban talalhato: `fitpro-ultima-laser`.

Technologiak:

- React 18
- TypeScript
- Redux Toolkit
- i18next / react-i18next
- SCSS
- Vite 5

Feladatai:

- erintokepernyos kezelo UI
- kezelesi modok: `auto`, `semi-auto`, `manual`
- lezer parameter UI: 808 / 980 / 1064 teljesitmeny, pulse width, arm/disarm
- red-dot, vakuum, vacuum lock, sensitivity es fire kontrollok
- kamera stream megjelenitese
- detektalt celpontok es backend allapot megjelenitese
- hibak globalis modalban torteno megjelenitese

Fontos frontend fajlok:

- `src/main.tsx`: React entry point
- `src/App.tsx`: screen valaszto es globalis modalok
- `src/features/laser-treatment/LaserTreatmentScreen.tsx`: kezelesi kepernyo es backend flow-k
- `src/services/hairKillerApi.ts`: HairKiller backend kliens
- `src/store/`: Redux store es slice-ok
- `src/i18n/`: magyar es angol forditasok

### Node.js es Vite

A Node.js itt nem production alkalmazasszerver, hanem fejlesztoi es build toolchain.

Feladatai:

- npm dependency management
- Vite dev server inditasa
- TypeScript ellenorzes
- production build generalasa
- opcionisan preview szerver futtatasa

Fontos scriptek:

```bash
npm run dev       # Vite dev server, alapertelmezett: http://localhost:3000
npm run build     # tsc + vite build, output: dist/
npm run preview   # local production preview
npm run deploy    # build + dist masolasa /var/www/frontend ala
```

Fejlesztesben a Vite dev server kozvetlenul szolgalja ki a frontendet `3000` porton. Productionben a Vite mar nem fut; csak a leforditott statikus `dist/` allomanyokat szolgalja ki az Nginx.

### Nginx

Az Nginx production modban statikus webszerverkent mukodik.

Aktualis production konfiguracio:

```nginx
server {
    listen 80;
    server_name _;

    root /var/www/frontend;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

Feladatai:

- React SPA statikus build kiszolgalasa `http://localhost` alatt
- deep link / kliens oldali routing tamogatasa `try_files ... /index.html` segitsegevel
- kioszk bongeszo szamara stabil lokalis URL biztositasa

Megjegyzes: a jelenlegi konfiguracio nem reverse proxyzza a backend API-t. A frontend kozvetlenul a `VITE_HK_API_BASE_URL` alapjan hivja a backendet, alapertelmezetten `http://localhost:8000`.

## 3. Kommunikacios kapcsolatok

### Frontend -> Backend

A frontend fetch API-val es EventSource-szal kommunikal:

- REST JSON API: `GET` / `POST`
- SSE: `/sse/detection`
- kamera stream: `/frame/current`, MJPEG kepfolyamkent

Alapertelmezett backend URL:

```text
http://localhost:8000
```

Felulirhato:

```bash
VITE_HK_API_BASE_URL=http://<backend-host>:<port>
```

Fontos API endpointok:

```text
GET  /health
GET  /stats
GET  /detection/status
GET  /sse/detection
GET  /frame/current
GET  /laser/settings
GET  /laser/temp
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
POST /app/raw_command
POST /app/clear_error
```

### Backend -> Mikrokontroller

A backend magasabb szintu API hivasaibol firmware parancsokat general. Pelda:

```text
Frontend:
POST /laser/settings

Backend:
LASER_SET_CHANNEL_PWR <p808>,<p980>,<p1064>
SET_LAS_PULSE / target pulse metadata

Mikrokontroller:
[...]->[OK][timestamp] vagy [...]->[NOK][reason][timestamp]
```

Target szekvencia eseten:

```text
Frontend:
POST /detection/capture
POST /seq/update_targets
POST /seq/start

Backend:
1. YOLO detektalas a legfrissebb kamerakepen
2. kepkoordinatak -> galvo koordinatak
3. TARGET_CLEAR_TARGETS
4. TARGET_SET_NEW_TARGET minden celpontra
5. TARGET_SET_MODE manual/auto
6. TARGET_START
```

## 4. Futasmodok

### Fejlesztoi mod

```text
Chromium / browser
        |
        v
Vite dev server :3000
        |
        v
Python backend :8000
        |
        v
mock backend vagy real mikrokontroller
```

Inditas:

```bash
# frontend
cd /home/mike/Projects/fitpro-ultima-laser
npm install
npm run dev

# backend
cd /home/mike/Projects/hairkiller
python3 -m uvicorn app.hk_full_app:app --host 0.0.0.0 --port 8000
```

Hardver nelkuli fejleszteshez a mock backend hasznalhato.

### Production / kioszk mod

```text
system boot
   |
   +--> systemd: hairkiller-backend.service -> Uvicorn :8000
   |
   +--> Nginx :80 -> /var/www/frontend
   |
   +--> desktop autostart -> Chromium --kiosk http://localhost
```

Production build:

```bash
npm run build
sudo cp -r dist/. /var/www/frontend
sudo systemctl reload nginx
```

Chromium kioszk konfiguracio:

```text
~/.config/autostart/chromium-kiosk.desktop
Exec=chromium --kiosk ... "http://localhost"
```

## 5. Fo kezelesi folyamat

### Indulas

1. Backend elindul es inicializalja a kamerat, detektort, homografiat es soros hardver interfeszeket.
2. Nginx kiszolgalja a frontend buildet.
3. Chromium kiosk megnyitja a `http://localhost` oldalt.
4. A React app betolt, majd a treatment screen a backendtol lekeri az alapallapotot:
   - `/health`
   - `/laser/settings`
   - `/detection/status`
   - `/stats`
5. A frontend elinditja az SSE detektalas figyelest es periodikus stat pollingt.

### Semi-auto kezeles

1. Frontend bekapcsolja a detektalast.
2. Vakuum safety check jelenleg semi-auto modban kikapcsolva.
3. Capture:
   - `/detection/capture`
   - `/seq/update_targets`
   - `/seq/show_targets?enabled=true`
4. A felhasznalo FIRE gombbal inditja a celpont szekvenciat.
5. A frontend pollolja a `/seq/status` endpointot, majd befejezes utan takarit:
   - `/seq/stop`
   - `/app/clear_error`

### Auto kezeles

1. Detection bekapcsol.
2. Vakuum safety check bekapcsol.
3. Vacuum lock eseten capture es target update tortenik.
4. Ha van celpont, a frontend automatikusan inditja a szekvenciat.
5. A backend/mikrokontroller safety feltetelek mellett vegrehajtja a target listat.

### Manual kezeles

1. Detection es celpont betoltes tortenhet.
2. FIRE hatasara a frontend manual modba allitja a szekvenciat.
3. A backend egy lepeses/manual target folyamatot indit.

## 6. Adat- es koordinatarendszerek

A backend tobb koordinatarendszert kezel:

- stream koordinata: `960x960`, UI/kepfolyam meret
- native cropped kamera koordinata: `1920x1920`
- galvo koordinata: `0..4095`

A detektalas native kepkoordinatakat ad. Ezeket a backend homografia segitsegevel galvo koordinatakka konvertalja. A target handler minden galvo koordinatat `0..4095` koze clampel, mielott mikrokontroller parancs lesz belole.

## 7. Allapotkezeles

Frontend oldalon:

- Redux tarolja a globalis UI, auth, settings, laser es system allapotokat.
- A treatment screen jelenleg sok realtime hardver allapotot lokalis React state-ben tart, mert ezek kozvetlen backend poll/SSE adatokbol frissulnek.
- A backend hibak `systemSlice.showError` akcion keresztul globalis error modalban jelennek meg.

Backend oldalon:

- A kamera folyamatosan friss frame-et szolgaltat.
- A detektalas csak bekapcsolt allapotban fut.
- A detektalt pontok es betoltott targetek backend memoriaban elnek.
- A mikrokontroller a vegso autoritativ allapot a lezer, target, vakuum es szenzorok tekinteteben.

## 8. Biztonsagi es uzemeltetesi megfontolasok

Fontos biztonsagi hatarok:

- A frontend nem kozvetlenul vezerel hardvert, csak backend API-t hiv.
- A backend validalja a kerest, majd a hardver handler reteg clampeli a kritikus tartomanyokat.
- A mikrokontroller tovabbi safety felteteleket ervenyesit: arm allapot, vakuum, aktiv folyamat, homerseklet, hibak.
- Disarm/stop parancsoknak barmikor vegrehajthatonak kell maradniuk.

Uzemeltetes:

- A backend systemd service-kent fusson, naplozasa `journalctl -u hairkiller-backend -f`.
- A frontend statikus buildje Nginx alatt legyen.
- A Chromium dedikalt kioszk userrel es minimalis desktop kornyezettel fusson.
- A soros port jogosultsagokat a `setup_serial.sh` allitsa be.

Javasolt webes hardening Nginx alatt:

```text
Content-Security-Policy: default-src 'self'; img-src 'self' data: http://localhost:8000; connect-src 'self' http://localhost:8000; style-src 'self' 'unsafe-inline'; script-src 'self'
X-Content-Type-Options: nosniff
Referrer-Policy: no-referrer
X-Frame-Options: DENY
Permissions-Policy: camera=(), microphone=(), geolocation=(), usb=()
```

Ezt a tenyleges API originhez kell igazitani, ha a backend nem `localhost:8000`.

## 9. Deployment artefaktumok

Ebben a repoban:

- `deploy/frontend.nginx`: production frontend Nginx config
- `deploy/test-frontend.nginx`: test frontend Nginx config
- `deploy/hairkiller-backend.service`: backend systemd service minta
- `deploy/chromium-kiosk.desktop`: Chromium kiosk autostart minta
- `dist/`: Vite production build output

Kapcsolodo backend repoban:

- `docs/hk_full_app_api.md`: backend API referencia
- `docs/README_serial.md`: soros/mikrokontroller kommunikacio
- `docs/stm_command_reference_from_code.xlsx`: STM parancsreferencia
- `setup_scripts/setup_serial.sh`: soros port jogosultsag beallitas

## 10. Nyitott architekturalis pontok

A jelenlegi repo es dokumentacio alapjan ezek a pontok tovabbi dontest vagy pontositast igenyelhetnek:

- A backend service fajlban szereplo `backend.hk_backend_app:app` es a fejlesztoi doksiban szereplo `app.hk_full_app:app` kozotti production entrypoint egyeztetese.
- A mock backend fajlnevek dokumentacios frissitese: a frontend doksi `hk_full_app_mock.py`-t emlit, a backend repoban jelenleg `hk_mock_app.py` lathato.
- Nginx reverse proxy dontes: maradjon-e kozvetlen `localhost:8000` API hivas, vagy legyen `/api` proxy ugyanazon origin alatt.
- CORS production szigoritasa, ha nem azonos originre kerul az API.
- Automatikus frontend tesztek es backend integration smoke tesztek bevezetese.
