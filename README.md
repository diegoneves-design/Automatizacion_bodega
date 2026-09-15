# Automatizacion_bodega

MVP web para reducir errores de digitacion y perdida de trazabilidad en el despacho/retiro de maquinaria de arriendo. Reemplaza la carga manual de SKUs (50+ por guia) por un flujo de carga masiva, validacion automatica contra inventario y ajustes de ultima hora con trazabilidad completa.

### Grupo 6 - Integrantes:
- Bastian Vargas
- Diego Neves
- Oscar Ynchaustegui
- Sebastian Carmona

## Contexto del Proyecto: Automatizacion_bodega (USACH)

### Rol
Actúa como desarrollador senior en Python e Ingeniero Industrial.

### Reglas de Arquitectura
- App monolítica modular en Streamlit (`app.py`).
- Base de datos local SQLite (`bodega.db`) con migraciones/seed automáticos.
- Dependencias estrictas en `requirements.txt` (streamlit, pandas).
- No modificar archivos de configuración de Git ni eliminar código funcional previo sin confirmación.

### Lógica del Negocio
- Flujo: Carga masiva de >50 SKUs, validación contra inventario, reemplazo de última hora con log de auditoría (timestamp, responsable, motivo) y emisión de guía de despacho.
- Tipos de movimiento: Despacho convencional/alternativo y Retiro preventivo/por falla.

### Protocolo de Verificación
- Validar sintaxis antes de finalizar cualquier edición.
- No asumir dependencias no instaladas.

## Problema que resuelve

- El jefe de bodega digita a mano mas de 50 SKUs por guia -> alto riesgo de error humano.
- Mantenimiento cambia equipos a ultima hora sin dejar registro formal de quien autorizo el cambio ni cuando.
- No hay cruce automatico contra el inventario disponible, por lo que discrepancias (SKU inexistente, sin stock) se detectan tarde, en terreno.

## Funcionalidad (3 vistas)

1. **Carga masiva** — Pega o sube hasta 50 SKUs (uno por linea), elige tipo de movimiento (Despacho: Convencional/Alternativo — Retiro: Preventivo/Por falla). Deduplica automaticamente, bloquea la carga si se excede el limite y emite una guia de despacho descargable al confirmar.
2. **Validador** — Cruza los SKUs de una orden contra el inventario simulado en SQLite y marca cada fila como `OK`, `SIN STOCK DISPONIBLE` o `SKU NO EXISTE EN INVENTARIO`, con metricas y exportacion a CSV.
3. **Ajuste de ultima hora** — Reemplaza un SKU ya cargado por otro. El SKU original se archiva (no se borra) y el cambio queda registrado en un log con fecha, hora y responsable, tambien exportable a CSV.

## Arquitectura

Todo el MVP vive en [app.py](app.py) (Streamlit + SQLite, sin dependencias externas complejas):

- **Capa de datos**: funciones `insertar_ordenes`, `obtener_orden`, `reemplazar_sku`, etc. sobre 3 tablas SQLite (`inventario`, `ordenes`, `log_cambios`). `bodega.db` se crea solo en el primer arranque.
- **Logica de negocio pura** (testeable sin Streamlit): `deduplicar_skus`, `clasificar_fila`, `validar_orden`, `generar_guia_despacho`.
- **Vistas**: una funcion por pantalla (`vista_carga_masiva`, `vista_validador`, `vista_ajuste_ultima_hora`), navegables desde la barra lateral.

## Instalacion y ejecucion

```bash
pip install -r requirements.txt
streamlit run app.py
```

La app queda disponible en `http://localhost:8501`. `bodega.db` se genera automaticamente con un inventario simulado de 10 equipos.

### Con Docker

```bash
docker build -t automatizacion-bodega .
docker run -p 8501:8501 automatizacion-bodega
```

## Simulacion guiada: orden de 5 equipos con reemplazo de ultima hora

1. **Vista "Carga masiva"**: Folio `GUIA-2026-001`, tipo `Despacho`, modalidad `Convencional`. Pega:
   ```
   EXC-001
   EXC-002
   RET-010
   GRU-020
   MON-050
   ```
   Clic en **Cargar orden** (`MON-050` tiene stock 0 en el inventario demo, a proposito).

2. **Vista "Validador"**: selecciona `GUIA-2026-001`. Se veran 4 SKUs `OK` y `MON-050` marcado en rojo como `SIN STOCK DISPONIBLE` — el error que hoy comete el jefe de bodega al digitar a mano.

3. **Vista "Ajuste de ultima hora"**: selecciona el folio, elige `MON-050` como SKU original, reemplazalo por `PLA-060`, indica responsable y motivo. Al confirmar, el log de cambios registra el reemplazo con fecha/hora exacta, y al volver al Validador, `PLA-060` figura como `OK`.

## Tests

```bash
pip install -r requirements-dev.txt
pytest -v
```

Los tests cubren la capa de datos y la logica de negocio pura (deduplicacion, insercion, reemplazo, log de cambios y clasificacion de validacion) usando una base de datos SQLite temporal e independiente por test.

## CI

Cada push/PR a `main` o `dev` ejecuta automaticamente ([.github/workflows/ci.yml](.github/workflows/ci.yml)) una verificacion de sintaxis y la suite de tests en Python 3.10, 3.11 y 3.12.

## Roadmap (fuera de alcance del MVP)

- Autenticacion de usuarios y roles (bodega vs. mantenimiento).
- Conexion a un inventario real (ERP/API) en vez de la tabla `inventario` simulada.
- Notificaciones automaticas (email/Slack) cuando se registra un ajuste de ultima hora.
