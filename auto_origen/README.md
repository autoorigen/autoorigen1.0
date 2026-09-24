# AUTOORIGEN

Entender. Reparar. Restaurar. Evolucionar.

Repositorio central del proyecto Autoorigen: la página web con su backend en Flask
(citas, historia mecánica del vehículo con código de acceso propio de cada
vehículo, panel admin y API para las apps móviles), la app Android
**AutoorigenInspect** para mecánicos (`app-android/`) y su versión web/PWA
(`/mecanico/...`, instalable también en iPhone sin necesitar Mac), la
documentación del proyecto y el espacio reservado para la futura app iOS
nativa del mismo nombre (`app-ios/`).

## Estructura

```text
auto_origen/
├── app.py                  Punto de entrada: crea la app y arranca Flask + Socket.IO
├── autoorigen/              Paquete de la aplicación
│   ├── config.py             Lee .env (SECRET_KEY, rutas)
│   ├── db.py                 Esquema SQLite completo + conexión por request + migraciones ligeras
│   ├── models.py             Todas las operaciones de datos (clientes, vehículos y su código de
│   │                          acceso, citas, órdenes, línea de tiempo, medios, admins, mecánicos, tokens API)
│   ├── auth.py                 Usuario admin para Flask-Login
│   ├── sockets.py              Eventos Socket.IO de la línea de tiempo en vivo
│   └── routes/
│       ├── public.py            Home, "Agenda cita" (carro al taller / visita), contacto
│       ├── historial.py         "Historia mecánica del vehículo": placa + código de acceso del vehículo
│       ├── admin.py             Login admin + CRUD clientes/vehículos/citas/órdenes/usuarios/mecánicos
│       ├── mecanico.py           Páginas web (PWA) para mecánicos — misma API que la app Android
│       └── api.py               API REST: token de dispositivo (app iOS futura) + login de
│                                  mecánico (app Android y /mecanico/ web, "/api/tecnicos/..." y "/api/inspecciones/...")
├── requirements.txt        Dependencias de Python
├── probar.sh               Arranca la web para pruebas en red local
├── subir-github.sh         Sube el proyecto a GitHub
├── .env.example             Plantilla de variables de entorno (copiar a .env)
├── templates/
│   ├── layout.html           Banner + barra lateral de menú + estructura base de toda la web
│   ├── index.html            Secciones de la landing (nosotros, servicios, proceso, etc.)
│   ├── citas/                 Formularios "llevar el carro al taller" y "visita al taller"
│   ├── historial/              Placa + código de acceso del vehículo → hoja de vida en vivo
│   ├── admin/                  Panel admin (login, dashboard, CRUD, línea de tiempo)
│   └── mecanico/                Pantallas de AutoorigenInspect en la web (login, nueva inspección,
│                                  captura de fotos/video, observaciones, historial de solo lectura)
├── static/
│   ├── css/style.css        Diseño: colores, tipografía, sidebar, timeline, admin, responsive
│   ├── css/mecanico.css      Estilos de las pantallas /mecanico/* (sin el menú del sitio de clientes)
│   ├── manifest.webmanifest  PWA del sitio de clientes (instalable en iPhone/Android)
│   ├── manifest-mecanico.webmanifest  PWA de /mecanico/ (ícono e ingreso propios)
│   ├── sw.js                  Service worker de ambas PWA (solo cachea estáticos, nunca HTML/sesión)
│   ├── icons/                 Íconos de las PWA (generados con la misma marca del sitio)
│   └── js/
│       ├── main.js            Preloader, animaciones, formulario de contacto
│       ├── sidebar.js          Abre/cierra la barra lateral de menú
│       ├── pwa.js              Registra el service worker
│       ├── timeline.js         Cliente Socket.IO: línea de tiempo en vivo del vehículo
│       └── mecanico/            comun.js (sesión/token) + un archivo por pantalla de /mecanico/*
├── data/
│   ├── autoorigen.db         Se crea solo (NO se sube a GitHub)
│   └── uploads/                Fotos/video de vehículos (NO se sube a GitHub)
├── docs/
│   ├── migracion-ia/       Contexto del proyecto: negocio, app iOS, roadmap, prompt maestro
│   └── servidor/           Estado y guías del servidor Debian
├── app-android/AutoorigenInspect/   App Android real para mecánicos (Kotlin + Compose) — ver su README
└── app-ios/                Reservado para la futura app iOS + contrato de su API (token de dispositivo)
```

## Cómo funciona la web

```text
Navegador ──GET /────────────────────────▶ Flask ──▶ templates/index.html (banner + sidebar)
Navegador ──POST /citas/vehiculo─────────▶ Flask ──▶ crea cliente + vehículo + cita
Navegador ──POST /citas/visita───────────▶ Flask ──▶ crea cliente + cita de visita
Navegador ──POST /historial/verificar (placa + código)─▶ Flask ──▶ sesión con acceso a ese vehículo
Navegador ──GET /historial/vehiculo/<placa>──▶ Flask ──▶ hoja de vida + Socket.IO en vivo
Admin ──/admin (login)────────────────────▶ Flask ──▶ CRUD clientes/vehículos/citas/órdenes
Admin ── crea/regenera el código de un vehículo──▶ Flask ──▶ se lo entrega al cliente en persona/WhatsApp
Admin ── agrega evento a una orden ───────▶ Flask ──▶ guarda evento + emite Socket.IO al cliente
App/web de mecánicos ──POST /api/tecnicos/login──▶ Flask ──▶ token de sesión (12h)
App/web de mecánicos ──POST /api/inspecciones + medios/eventos──▶ Flask ──▶ mismo modelo de datos,
                                                                             visible en vivo en /historial y /admin
App iOS (futura) ──POST /api/...─────────▶ Flask ──▶ mismo modelo de datos (token de dispositivo)
```

Todo vive en `data/autoorigen.db` (SQLite): clientes, vehículos (por placa y su código de
acceso), citas, órdenes de trabajo, línea de tiempo, medios, usuarios admin, mecánicos
(app Android + web) y tokens de dispositivo para la futura app iOS.

## Configuración antes de correr

1. Copiar `.env.example` a `.env` y completar `SECRET_KEY` (cualquier cadena larga y
   aleatoria). Es el único valor que hace falta — "Historia mecánica del vehículo" ya
   no depende de ningún servicio externo (SMS/Twilio): cada vehículo tiene su propio
   código de acceso, generado automáticamente y visible/regenerable desde `/admin`.
2. Crear el primer usuario admin (con el venv activado):
   ```bash
   flask --app app crear-admin tu_usuario tu_password
   ```
   Para darle rol `superadmin` (puede crear otros admins y tokens de la app móvil),
   entra a `/admin/usuarios` con ese primer usuario y usa el selector de rol al crear
   el siguiente, o edítalo directamente en `data/autoorigen.db`.
3. Crear el primer mecánico para la app Android:
   ```bash
   flask --app app crear-tecnico usuario password "Nombre visible"
   ```
   Ver `app-android/AutoorigenInspect/README.md` para abrir y conectar la app.

## Uso rápido (en la torre Debian)

```bash
bash probar.sh          # crea el entorno, instala dependencias y arranca la web en el puerto 5000
bash subir-github.sh    # guarda los cambios y los sube a GitHub (pide usuario y token)
```

Luego abrir `http://IP-DE-LA-TORRE:5000` desde otro equipo de la red. `probar.sh` muestra la IP al arrancar.

### Instalar la web como app (PWA) en un iPhone

Sin Mac no se puede compilar una app nativa de iOS, pero la web se puede
"instalar" en la pantalla de inicio como si fuera una app: desde el iPhone,
abre la URL de arriba en **Safari** → botón compartir → **"Agregar a
pantalla de inicio"**. Queda con ícono propio y abre a pantalla completa
(`static/manifest.webmanifest`, `static/sw.js`, `static/icons/`). Funciona
igual en Android/Chrome con el botón de instalar del navegador.

Lo mismo aplica para los mecánicos: `http://IP-DE-LA-TORRE:5000/mecanico/login`
es la versión web de AutoorigenInspect (login, nueva inspección, cámara,
observaciones, historial) — se instala igual desde Safari y usa su propio
manifest (`static/manifest-mecanico.webmanifest`) para quedar como un ícono
separado del sitio de clientes. Necesita un mecánico creado con
`flask --app app crear-tecnico` (o desde `/admin/mecanicos`).

### Paso a paso manual (lo mismo que hace probar.sh)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Estado (24/09/2026)

| Parte | Estado |
|---|---|
| Web V2 — banner + sidebar, citas, historia del vehículo, admin, API móvil | Hecho — falta contenido real (fotos, video, redes, WhatsApp) |
| Formulario de contacto → base de datos | Hecho — conectado a `/api/contacto` |
| Citas (carro al taller / visita al taller) | Hecho — `/citas/vehiculo` y `/citas/visita` |
| Historia mecánica del vehículo (placa + código de acceso) | Hecho — sin dependencias externas, el código se genera solo por vehículo |
| Panel admin (CRUD + línea de tiempo en vivo) | Hecho — `/admin`, requiere crear el primer usuario con `flask --app app crear-admin` |
| App Android AutoorigenInspect (mecánicos) | Hecho — login, nueva inspección, fotos/video, observaciones, historial de solo lectura. Ver `app-android/AutoorigenInspect/README.md` |
| Versión web/PWA de AutoorigenInspect (`/mecanico/...`) | Hecho — mismas pantallas que la app Android, instalable en iPhone sin Mac |
| API con token de dispositivo (para la futura app iOS) | Hecho el contrato — ver `app-ios/README.md`. Pendiente que la app iOS la consuma |
| Servidor | En curso — Debian 13 nativo en torre ASUS; producción pendiente (Gunicorn, Nginx, dominio, SSL) |
| App iOS AO | En desarrollo en Xcode — código aún no está en este repositorio |

## Historial

- **V1.0 (05/09/2026):** web separada en templates/static, formulario conectado a Flask.
- **V1.1 (24/09/2026):** se incorporan el preloader y las animaciones de la versión V1 completa, con respaldo si JavaScript falla; se agregan documentación, carpeta de la app iOS y `.gitignore`.
- **V2.0 (24/09/2026):** rediseño completo — banner + barra lateral de menú, agenda de citas (carro al taller / visita al taller físico), "Historia mecánica del vehículo" con búsqueda por placa y verificación por SMS, panel admin con CRUD de clientes/vehículos/citas/órdenes/usuarios, línea de tiempo en vivo por WebSockets, y API REST lista para conectar la futura app iOS.
- **V2.1 (24/09/2026):** app Android **AutoorigenInspect** para mecánicos (`app-android/`) — login propio, registro del carro (placa, cliente, marca/modelo, combustible, kilometraje y kilometraje del aceite), captura de fotos/video con subida inmediata, foto de la placa, observación del mecánico y comentario del cliente, e historial de inspecciones anteriores de solo lectura. Nuevos endpoints `/api/tecnicos/login` e `/api/inspecciones/...`, tabla `mecanicos` y gestión desde `/admin/mecanicos`.
- **V2.2 (24/09/2026):** la web es instalable como PWA (pantalla de inicio de iPhone vía Safari, o Chrome/Android/escritorio) — pensada para poder "tener algo en el celular" sin necesitar una Mac para compilar la app iOS nativa.
- **V2.3 (24/09/2026):** `/mecanico/...` — versión web de AutoorigenInspect (login, nueva inspección, cámara del navegador, observaciones, historial de solo lectura) con su propio manifest/ícono de PWA, para poder usar la app de mecánicos en un iPhone sin Mac y sin Xcode.
- **V2.4 (24/09/2026):** "Historia mecánica del vehículo" deja de depender de SMS/Twilio — cada vehículo recibe un código de acceso propio al crearse (`vehiculos.codigo_acceso`), visible y regenerable desde `/admin/vehiculos/<id>`, que el taller entrega al cliente. Se quita `autoorigen/sms.py`, la tabla `otp_codigos` y la dependencia `twilio`.

## Notas

- La documentación de `docs/migracion-ia/` se conserva tal como se generó. Donde menciona Linux Mint, hoy el entorno Linux es Debian 13.
- Nunca subir `data/autoorigen.db` ni `data/uploads/`: contienen datos y medios de clientes (incluidos los códigos de acceso de los vehículos).
- Nunca subir `.env`: contiene la `SECRET_KEY`.
