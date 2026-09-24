# AUTOORIGEN — PAQUETE DE MIGRACIÓN A OTRA IA

Fecha de corte: 24 de septiembre de 2026
Proyecto principal: Autoorigen / AutoorigenInspect
Aplicación móvil: AO
Estado: desarrollo activo

## Objetivo de este paquete

Este paquete contiene el contexto técnico, funcional y de negocio necesario para entregar el desarrollo de Autoorigen a otra IA y continuar sin depender de este chat.

## Regla crítica

Este paquete documenta lo que se conoce del proyecto y separa:
- HECHO: confirmado en conversaciones/pruebas.
- PLANIFICADO: arquitectura o funcionalidad acordada.
- PENDIENTE: todavía debe implementarse o verificarse.
- NO DISPONIBLE: el archivo/código no está presente en el material recuperable.

## Estado actual resumido

Se está desarrollando una aplicación nativa para inspecciones vehiculares llamada `AutoorigenInspect`, cuyo nombre visible aceptado es `AO`.

Flujo base acordado:
Nueva inspección → placa/vehículo → crear sesión → cámara → fotos/videos/notas → finalizar → Mis inspecciones → informe.

La arquitectura propuesta usa SwiftUI y almacenamiento local por inspección. La cámara usa AVFoundation. Se contemplan posteriormente Vision/OCR, Speech/Audio e IA.

## Lo que NO debe hacer la nueva IA

1. No reiniciar el proyecto desde cero sin analizar primero este documento.
2. No cambiar de tecnología sin explicar ventajas/desventajas.
3. No inventar archivos, clases o código que no estén disponibles.
4. No eliminar funcionalidades existentes para resolver un error sin justificarlo.
5. No avanzar muchas etapas de una sola vez: el usuario quiere comprender el código.
6. No entregar código sin explicar qué hace.
