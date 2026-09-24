# app-ios — AutoorigenInspect (AO)

Esta carpeta está reservada para el proyecto Xcode de la app iOS.

**Estado:** el código fuente todavía NO está aquí. Se debe exportar desde el MacBook Pro (Xcode 16.4).

## Cómo traerlo

1. En el Mac, copiar la carpeta completa `AutoorigenInspect/` (la que contiene `AutoorigenInspect.xcodeproj`) dentro de `app-ios/`.
2. Verificar que estén todos los `.swift`, `Assets.xcassets`, `Info.plist` y entitlements.
3. Hacer commit desde el Mac.

Estructura esperada:

```text
app-ios/
└── AutoorigenInspect/
    ├── AutoorigenInspect.xcodeproj
    └── AutoorigenInspect/
        ├── ContentView.swift
        ├── NewInspectionView.swift
        ├── CameraView.swift
        ├── CameraService.swift
        ├── Inspection.swift
        └── Assets.xcassets
```

El contexto, errores conocidos y roadmap de la app están en `docs/migracion-ia/`.

## Backend disponible (desde el rediseño V2 de la web)

La web (`autoorigen/routes/api.py`) ya expone una API REST pensada para que
`AutoorigenInspect` la consuma cuando su persistencia esté resuelta (Fase 8 del
roadmap). No hay que inventar nada del lado del servidor: solo llamarla.

**Autenticación:** header `Authorization: Bearer <token>`. El token se genera
desde `/admin/api-tokens` (solo un usuario `superadmin`) y se copia una sola vez.

**Base URL:** la misma de la web (`http://IP-DE-LA-TORRE:5000` en pruebas).

### `POST /api/vehiculos`
Crea o actualiza un vehículo por placa (upsert). Si el cliente no existe, se crea.

```json
{
  "placa": "ABC123",
  "cliente_nombre": "Nombre del dueño",
  "cliente_telefono": "+57...",
  "marca": "Mazda", "modelo": "3", "anio": "2018", "color": "Gris"
}
```
Respuesta: `{"ok": true, "vehiculo_id": 1}`

### `POST /api/ordenes`
Crea una nueva orden (inspección) para un vehículo. Arranca en la etapa `recibido`.

```json
{ "vehiculo_id": 1, "titulo": "Inspección AutoorigenInspect 2026-09-24" }
```
Respuesta: `{"ok": true, "orden_id": 7}`

### `POST /api/ordenes/<orden_id>/eventos`
Agrega un evento de texto a la línea de tiempo (se publica en vivo al cliente).

```json
{ "tipo": "hallazgo", "titulo": "Pastillas de freno desgastadas", "descripcion": "..." }
```
`tipo` puede ser `nota`, `hallazgo` o `informe`.

### `POST /api/ordenes/<orden_id>/medios`
Sube una foto o video (multipart/form-data, campo `archivo`), crea el medio y un
evento de timeline asociado. Formatos aceptados: jpg, jpeg, png, heic, webp (foto);
mp4, mov, m4v, webm (video). Campos opcionales de formulario: `titulo`, `descripcion`.

Todas las escrituras (`eventos`, `medios`) emiten un evento Socket.IO al cliente
que tenga abierta la hoja de vida de ese vehículo (`/historial/vehiculo/<placa>`),
así que la app móvil alimenta directamente la línea de tiempo en tiempo real.
