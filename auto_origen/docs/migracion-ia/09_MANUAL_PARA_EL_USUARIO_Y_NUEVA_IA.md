# MANUAL DE CONTINUIDAD

## Si entrego este paquete a otra IA

Primero debe leer:
1. `00_LEEME_PRIMERO.md`
2. `02_ESTADO_TECNICO_ACTUAL.md`
3. `03_ARQUITECTURA_Y_MODELO_DATOS.md`
4. `05_PROMPT_MAESTRO_PARA_OTRA_IA.md`

Después debe pedir/revisar el código real del proyecto.

## Primera sesión recomendada

Mensaje:

“Lee todo el paquete de migración de Autoorigen. No hagas cambios todavía. Primero dime qué entiendes del proyecto, qué partes están confirmadas, cuáles son hipótesis y qué archivos del proyecto necesitas para continuar.”

Después entregar el proyecto Xcode.

## Segunda sesión

Solicitar:
“Analiza el árbol completo y encuentra la implementación de Inspection, CameraView, CameraService, Finalizar y Mis Inspecciones. No modifiques nada. Haz un diagnóstico.”

## Tercera sesión

Resolver solamente persistencia y recuperación.

## Cuarta sesión

Resolver cámara y asociación de medios.

## Quinta sesión

Resolver informe.

## Importante

No mezclar simultáneamente:
- cámara
- IA
- backend
- OCR
- informes
- autenticación

Primero debe quedar estable el núcleo de inspección.
