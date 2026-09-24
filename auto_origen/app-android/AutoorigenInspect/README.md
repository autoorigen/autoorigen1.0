# AutoorigenInspect — app Android (mecánicos)

App nativa para que los mecánicos del taller registren inspecciones: login,
"Nueva inspección" (registro del carro por placa → fotos/video → observaciones)
y "Revisión de inspecciones anteriores" (solo lectura).

Kotlin + Jetpack Compose (Material 3) + CameraX + Retrofit. Sin base de datos
local: cada paso llama directo al backend de Autoorigen (ver "Cómo funciona"
más abajo). Si el taller se queda sin conexión a mitad de una inspección, ese
paso falla y hay que reintentarlo — no hay guardado/sincronización offline en
esta versión.

## Cómo abrir el proyecto

1. Abre Android Studio → **Open** → selecciona esta carpeta
   (`app-android/AutoorigenInspect/`), **no** la carpeta `auto_origen` completa.
2. Si Android Studio pregunta por el *Gradle Wrapper* (falta el `.jar` porque
   este repo no lo trae binario), acepta que lo genere — Android Studio lo hace
   solo la primera vez.
3. Espera el *Gradle Sync*. Compila con **minSdk 26** (Android 8.0+), así que
   sirve cualquier emulador o teléfono razonablemente moderno.
4. **Run ▶** con un emulador o un teléfono por USB (depuración USB activada).

## Backend: cómo conectarla

La app necesita la web de Autoorigen corriendo (`python app.py` en la raíz del
repo — ver el `README.md` principal). En la pantalla de login hay un campo
**"URL del servidor"**:

- **Emulador de Android Studio:** deja el valor por defecto
  `http://10.0.2.2:5000/` — `10.0.2.2` es cómo el emulador ve el `localhost`
  de tu PC.
- **Teléfono físico:** cámbialo por la IP de tu PC en la red local (la misma
  que muestra `probar.sh` al arrancar, ej. `http://192.168.1.10:5000/`). El
  teléfono y el PC deben estar en la misma red WiFi.

### Crear el primer mecánico

Desde la raíz del repo, con el venv activado:

```bash
flask --app app crear-tecnico juan ClaveSegura123 "Juan Pérez"
```

O desde `/admin/mecanicos` en la web (necesitas iniciar sesión como un admin
`superadmin`).

## Contrato de API que usa la app

Ver `autoorigen/routes/api.py`, sección "Login de mecánico + endpoints de la
app Android". Autenticación: `POST /api/tecnicos/login` con
`{"usuario","password"}` devuelve un token firmado (12 h de validez) que se
manda como `Authorization: Bearer <token>` en todo lo demás:

| Endpoint | Uso en la app |
|---|---|
| `POST /api/inspecciones` | Pantalla "Nueva inspección": crea el registro del carro (placa, cliente, marca/modelo, combustible, kilometraje, kilometraje del aceite) y abre la orden. |
| `POST /api/inspecciones/<id>/medios` | Pantalla de captura: sube cada foto/video (multipart), incluida la foto de la placa. |
| `POST /api/inspecciones/<id>/eventos` | Pantalla de observaciones: `tipo` = `observacion_mecanico` o `comentario_cliente`. |
| `GET /api/inspecciones` | "Revisión de inspecciones anteriores": lista de solo lectura. |
| `GET /api/inspecciones/<id>` | Detalle de solo lectura de una inspección (incluye su línea de tiempo). |
| `GET /api/inspecciones/medios/<ruta>` | Sirve las fotos para mostrarlas en el detalle (requiere el mismo token). |

Cada evento/foto/video que sube la app aparece también **en vivo** en la
página web `/historial/vehiculo/<placa>` que ve el cliente (vía WebSocket) y
en el panel admin — es el mismo modelo de datos, no hay nada separado que
sincronizar.

## Estructura del proyecto

```text
app/src/main/java/com/autoorigen/autoorigeninspect/
├── AutoorigenApp.kt          Application: crea SessionManager + Repository una sola vez
├── MainActivity.kt / AutoorigenNavHost.kt   Navegación entre pantallas
├── data/
│   ├── network/               ApiService (Retrofit), ApiClient, DTOs
│   ├── SessionManager.kt      DataStore: URL del servidor, token, nombre del técnico
│   └── InspeccionRepository.kt  Une la UI con la red y traduce errores
└── ui/
    ├── login/ home/ nueva/ captura/ observaciones/ historial/ detalle/
    │   Una pantalla + un ViewModel por carpeta, siguiendo el flujo:
    │   Login → Home → Nueva inspección → Captura (fotos/video) → Observaciones → Home
    │                └→ Revisión de inspecciones anteriores → Detalle
    ├── components/  Campos y botones reutilizables
    └── theme/       Mismos colores que static/css/style.css en la web
```

## Limitaciones conocidas (a propósito, para mantener el alcance simple)

- Sin modo offline: cada acción necesita conexión al servidor en el momento.
- El detalle de una inspección anterior muestra las fotos, pero los videos se
  marcan como "disponibles en el servidor" sin reproductor embebido (se
  puede agregar más adelante con Media3/ExoPlayer si hace falta).
- No hay edición de inspecciones pasadas — es intencionalmente de solo
  lectura, como se pidió.
