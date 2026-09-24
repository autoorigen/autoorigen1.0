# ARQUITECTURA PROPUESTA

## Capas

### Presentación
SwiftUI:
- ContentView
- NewInspectionView
- CameraView
- Mis Inspecciones
- InspectionDetailView (prevista/por verificar)

### Dominio
Entidad principal:
`Inspection`

Conceptualmente:

```text
Inspection
├── id
├── fecha
├── placa
├── marca
├── modelo
├── año
├── kilometraje
├── estado
├── fotos
├── videos
├── audios/notas
├── hallazgos
└── informe
```

Los nombres exactos de propiedades deben tomarse del código real.

### Servicios

`CameraService`
- administra `AVCaptureSession`
- cámara
- captura de imágenes
- video

Servicios futuros:
- OCRService
- SpeechService
- StorageService
- ReportService
- AIService

## Persistencia

El requisito funcional es que una inspección sobreviva al cierre de las vistas y aparezca en `Mis Inspecciones`.

La implementación concreta de persistencia todavía debe verificarse:
- UserDefaults / Codable
- archivos JSON
- SwiftData
- Core Data
- otra solución

NO asumir cuál está implementada sin revisar el proyecto.

## Regla de diseño

Los archivos multimedia deben pertenecer a una inspección concreta, no solamente a una carpeta global.

Conceptualmente:

```text
Autoorigen/
└── Inspections/
    └── <inspection-id>/
        ├── inspection.json
        ├── photos/
        ├── videos/
        ├── audio/
        └── report/
```

Esta es una estructura conceptual, no una afirmación de que ya exista físicamente.

## Navegación

```text
AO
│
├── Nueva inspección
│   ├── datos vehículo
│   └── Iniciar
│
├── Cámara
│   ├── foto
│   ├── video
│   └── volver / finalizar
│
└── Mis inspecciones
    ├── lista
    └── detalle
        └── informe
```
