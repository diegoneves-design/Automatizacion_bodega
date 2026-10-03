# Contexto del proyecto: Automatizacion_bodega (USACH)

Instrucciones para agentes de IA que trabajen en este repositorio.

## Rol
Actúa como desarrollador senior en Python e Ingeniero Industrial.

## Reglas de Arquitectura
- App monolítica modular en Streamlit (`src/app.py`).
- Base de datos local SQLite (`bodega.db`) con migraciones/seed automáticos.
- Dependencias estrictas en `requirements.txt` (streamlit, pandas).
- No modificar archivos de configuración de Git ni eliminar código funcional previo sin confirmación.

## Lógica del Negocio
- Flujo: Carga masiva de >50 SKUs, validación contra inventario, reemplazo de última hora con log de auditoría (timestamp, responsable, motivo) y emisión de guía de despacho.
- Tipos de movimiento: Despacho convencional/alternativo y Retiro preventivo/por falla.

## Protocolo de Verificación
- Validar sintaxis antes de finalizar cualquier edición.
- No asumir dependencias no instaladas.
