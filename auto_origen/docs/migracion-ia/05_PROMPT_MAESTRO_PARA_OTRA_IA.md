# PROMPT MAESTRO — CONTINUAR AUTOORIGEN

Quiero que continúes conmigo el desarrollo de mi proyecto Autoorigen.

## CONTEXTO

Soy el responsable de Autoorigen, un proyecto/taller automotriz. Estoy desarrollando una aplicación nativa llamada `AutoorigenInspect`, cuyo nombre visible es `AO`.

La aplicación tiene como objetivo documentar inspecciones vehiculares mediante sesiones persistentes, fotos, videos, notas, hallazgos y posteriormente informes.

## TECNOLOGÍA ACTUAL

- Swift
- SwiftUI
- Xcode 16.4
- macOS 15.7.7
- MacBook Pro 13" 2020 Intel
- Bundle: `com.autoorigen.AutoorigenInspect`

También quiero poder desarrollar parte del código desde Linux y posteriormente compilar/exportar iOS en Xcode.

## FLUJO PRINCIPAL

AO
→ Nueva inspección
→ placa/vehículo
→ crear sesión
→ cámara
→ fotos/videos/notas
→ finalizar
→ Mis inspecciones
→ detalle
→ informe

## ESTADO

Ya existe un proyecto nativo y se trabajó con:
- ContentView.swift
- NewInspectionView.swift
- CameraService.swift
- CameraView
- permisos de cámara y micrófono

Hubo problemas recientes:
- error al pasar `inspection` a CameraView
- botón Finalizar sin acción visible
- Mis Inspecciones sin mostrar registros
- incertidumbre sobre dónde se guardan los documentos

NO inventes cómo están implementadas esas partes. Primero pide/revisa los archivos reales.

## REGLAS DE TRABAJO CONMIGO

1. Explícame primero el concepto.
2. Después muéstrame el código.
3. No me des código sin explicar qué hace.
4. Si hay un error, analiza la causa antes de proponer cambios.
5. No reescribas archivos completos innecesariamente.
6. Indica exactamente qué archivo modificar.
7. Indica exactamente qué bloque reemplazar.
8. Después de cada cambio dime cómo probarlo.
9. Avanza paso a paso.
10. No asumas conocimientos que todavía no tengo.
11. Si detectas una confusión conceptual, detente y explícala.
12. Diferencia siempre:
   concepto → herramienta → tecnología → implementación.
13. Usa diagramas ASCII cuando ayuden.
14. Relaciona los conceptos con Autoorigen.
15. Si hay varias soluciones técnicas, compáralas antes de elegir.
16. Conserva las funciones que ya funcionan.
17. Antes de crear una nueva arquitectura, inspecciona la existente.
18. No afirmes que algo está guardado si no se puede demostrar mediante código/prueba.

## PRIMERA TAREA

Antes de modificar código:
1. analiza el árbol del proyecto;
2. identifica todos los archivos Swift;
3. identifica el modelo `Inspection`;
4. identifica cómo se crea una inspección;
5. identifica cómo se guarda;
6. identifica cómo se recupera;
7. identifica cómo `CameraView` recibe la inspección;
8. identifica qué hace `Finalizar`;
9. identifica qué usa `Mis Inspecciones`;
10. compila y reporta los errores.

Después de ese diagnóstico, propón el siguiente cambio mínimo.

## OBJETIVO INMEDIATO

Conseguir este comportamiento:

Nueva inspección
→ crear inspección
→ cámara
→ tomar foto/video
→ finalizar
→ persistir
→ Mis Inspecciones muestra la inspección
→ abrir inspección y ver evidencia.

No avances a IA, OCR, backend o funciones complejas hasta que este flujo sea sólido.

## PRINCIPIO DEL PROYECTO

Autoorigen debe convertir el proceso real del taller:

Entender → Diagnosticar → Explicar → Reparar → Verificar → Documentar

en información estructurada y evidencia digital.
