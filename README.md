# Automatizacion_bodega

MVP del Grupo 6 para el electivo *Ingeniería Digital en Acción: Datos, IA, MVP* (USACH, Departamento de Ingeniería Industrial).

## Qué es la solución

Una aplicación web que **genera automáticamente la guía de despacho o retiro** de equipos de arriendo. Reemplaza la digitación manual de más de 50 SKU por guía por un flujo con tres pasos:

1. **Carga masiva** de SKU (pegados o desde archivo), eligiendo el tipo de movimiento: Despacho (Convencional o Alternativo) o Retiro (Preventivo o Por falla). Elimina duplicados y bloquea la carga si se excede el límite de 50.
2. **Validación automática** de cada SKU contra el inventario. Cada fila queda como `OK`, `SIN STOCK DISPONIBLE` o `SKU NO EXISTE EN INVENTARIO`, con exportación a CSV.
3. **Ajuste de última hora**: reemplaza un SKU ya cargado por otro. El original se archiva (no se borra) y el cambio queda en un registro con fecha, hora, responsable y motivo.

Detalle del caso, caso de uso y maqueta: [docs/unidad1](docs/unidad1). Diseño de la base de datos: [docs/datos/estructura_datos.md](docs/datos/estructura_datos.md).

## Para quién es

Para el **jefe de bodega** de una empresa de arriendo de equipos (usuario principal). El área de **mantenimiento** participa como usuario secundario: es quien define qué SKU salen en cada orden y quien pide los cambios de último minuto.

## Cómo se instala y se ejecuta

Requisitos: Python 3.10 o superior.

```bash
git clone https://github.com/diegoneves-design/Automatizacion_bodega.git
cd Automatizacion_bodega
pip install -r requirements.txt
streamlit run src/app.py
```

La app queda en `http://localhost:8501`. La base `bodega.db` se crea sola en el primer arranque, con un inventario simulado de 10 equipos.

Variables de entorno (opcionales): copiar `.env.example` a `.env`. Hoy solo existe `BODEGA_DB_PATH` (ruta de la base SQLite). Las claves reales nunca se suben al repositorio.

Con Docker:

```bash
docker build -t automatizacion-bodega .
docker run -p 8501:8501 automatizacion-bodega
```

Tests (18 casos sobre la capa de datos y la lógica de negocio):

```bash
pip install -r requirements-dev.txt
pytest -v
```

### Prueba guiada

1. En **Carga masiva**: folio `GUIA-2026-001`, tipo `Despacho`, modalidad `Convencional`, y pegar `EXC-001`, `EXC-002`, `RET-010`, `GRU-020`, `MON-050` (uno por línea).
2. En **Validador**: elegir `GUIA-2026-001`. `MON-050` aparece como `SIN STOCK DISPONIBLE` (a propósito, tiene stock 0).
3. En **Ajuste de última hora**: reemplazar `MON-050` por `PLA-060`, indicar responsable y motivo. El cambio queda en el registro y el Validador ahora muestra `PLA-060` como `OK`.

## En qué estado está

Estado al 2 de octubre de 2026: **MVP funcional en desarrollo, Unidad 1 en curso**.

| Hecho | Pendiente |
|---|---|
| Carga masiva, validador de SKU y ajuste de última hora con registro de cambios | Cuentas y permisos (mantenimiento carga; bodega valida y emite) |
| Guía de despacho/retiro descargable en texto plano | Guía en PDF y alertas de cambios de último minuto |
| Base SQLite con inventario simulado, tests y CI en GitHub Actions | Bloquear la emisión de la guía cuando algún SKU no valida (hoy se emite y marca el SKU) |
| Diseño preliminar de la estructura de datos (`docs/datos`) | Pasar la base a Supabase con el modelo de `docs/datos` |
| | Integración con el ERP (fuera del alcance del MVP) |

## Quiénes la desarrollan

Grupo 6, Universidad de Santiago de Chile:

- Sebastián Carmona Ponce
- Diego Neves Preau
- Bastián Vargas Fernández
- Oscar Ynchaustegui Narro

Profesora: Andrea Arredondo.

## Estructura del repositorio

```
src/        código de la solución (app.py)
tests/      pruebas automáticas
docs/       entregables: unidad1/, bitacora-ia/, datos/
.env.example  nombres de variables, sin valores
```

Flujo de trabajo: se trabaja en `dev` y se llega a `main` mediante un pull request revisado por otro integrante.
