# ROADMAP DE CONTINUACIÓN

## FASE 0 — Recuperar el proyecto real

PRIORIDAD MÁXIMA

1. Obtener el proyecto completo `AutoorigenInspect`.
2. Exportar todos los `.swift`.
3. Obtener `.xcodeproj` o `.xcworkspace`.
4. Obtener `Info.plist` y configuración relevante.
5. Registrar dependencias/SPM/CocoaPods si existen.
6. Confirmar estructura de carpetas.
7. Compilar sin modificar nada.
8. Ejecutar la app en iPhone.
9. Crear una inspección de prueba.
10. Comprobar dónde se almacena.

## FASE 1 — Persistencia

Resolver definitivamente:
- crear inspección
- guardar
- recuperar
- listar
- abrir
- eliminar/archivar
- asociar medios

Criterio de aceptación:
Después de cerrar y volver a abrir la app, la inspección de prueba debe seguir apareciendo.

## FASE 2 — Cámara

- foto
- video
- múltiples capturas
- asociación automática con Inspection
- miniaturas
- eliminación individual
- control de permisos

## FASE 3 — Finalizar

El botón debe:
1. detener captura
2. guardar cambios
3. cerrar sesión de inspección
4. volver a `Mis Inspecciones` o mostrar resumen
5. permitir abrir la inspección posteriormente

## FASE 4 — Checklist

Crear categorías:
- motor
- transmisión
- frenos
- suspensión
- dirección
- electricidad/electrónica
- carrocería
- pintura
- interiores
- neumáticos
- niveles/fluidos

Cada punto puede tener:
- estado
- observación
- foto
- video
- severidad

## FASE 5 — Evidencia inteligente

OCR de placa mediante Vision.
Reconocimiento/lectura asistida.
Notas de voz.
Transcripción.

## FASE 6 — Informe

Generar informe profesional:
- datos del vehículo
- cliente
- fecha
- técnico
- checklist
- hallazgos
- evidencia
- recomendaciones
- firma
- PDF

## FASE 7 — IA

La IA no debe inventar diagnósticos.

Debe ayudar a:
- organizar hallazgos
- resumir evidencia
- redactar observaciones
- sugerir preguntas
- estructurar informe

Toda recomendación técnica debe quedar distinguida de un diagnóstico confirmado.

## FASE 8 — Backend

Cuando el producto local esté estable:
- API
- usuarios
- autenticación
- base de datos
- sincronización
- almacenamiento multimedia
- panel web

## FASE 9 — Ecosistema Autoorigen

- órdenes de trabajo
- inventario
- clientes
- vehículos
- historial
- contenido
- vehículos en venta
- Autoorigen Academy
