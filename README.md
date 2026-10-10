# Automatizacion_bodega

MVP del Grupo 6 para el electivo *Ingeniería Digital en Acción: Datos, IA, MVP* (USACH, Departamento de Ingeniería Industrial).

## Qué es la solución

Una aplicación web que **genera automáticamente la guía de despacho o retiro** de equipos de arriendo. Hoy el jefe de bodega digita cada guía a mano, y la rehace cuando mantenimiento cambia un equipo a último minuto. El MVP reemplaza esa digitación por un flujo con tres pasos:

1. **Carga masiva** de SKU (pegados o desde archivo), eligiendo el tipo de movimiento: Despacho (Convencional o Alternativo) o Retiro (Preventivo o Por falla). Elimina duplicados y bloquea la carga si se exceden los 50 SKU por guía.
2. **Validación automática** de cada SKU contra el inventario. Cada fila queda como `OK`, `SIN STOCK DISPONIBLE` o `SKU NO EXISTE EN INVENTARIO`, con exportación a CSV.
3. **Ajuste de última hora**: reemplaza un SKU ya cargado por otro. El original se archiva (no se borra) y el cambio queda en un registro con fecha, hora, responsable y motivo.

Indicador de éxito: porcentaje de guías emitidas sin errores y sin necesidad de rehacerlas.

Documentación del proyecto:

- Avances de la Unidad 1 (caso de uso, maqueta, repositorio): [docs/unidad1](docs/unidad1)
- Diseño de la base de datos, con diagrama: [docs/datos/estructura_datos.md](docs/datos/estructura_datos.md)
- Registro de los encargos hechos a un agente de IA: [docs/bitacora-ia/bitacora.md](docs/bitacora-ia/bitacora.md)

### Estructura del repositorio

```
src/                  código de la solución (app.py)
tests/                pruebas automáticas
docs/unidad1/         Avances 2 y 3 de la Unidad 1 (PDF)
docs/bitacora-ia/     registro de encargos a un agente de IA
docs/datos/           diseño de la base de datos y su diagrama
README.md             portada del proyecto
.gitignore            archivos locales que no se suben (base de datos, .env)
.env.example          nombres de variables de entorno, sin valores
```

## Para quién es

- **Usuario principal:** el jefe de bodega, que hoy digita cada guía a mano y la rehace cuando mantenimiento cambia un equipo a último minuto.
- **Usuario secundario:** el área de mantenimiento, que define qué SKU salen en cada orden y pide los cambios de último minuto.

## Cómo se instala y se ejecuta

Requisitos: Python 3.10 o superior.

En Windows, desde PowerShell (tecla Windows, escribir `PowerShell`, Enter):

```powershell
git clone https://github.com/diegoneves-design/Automatizacion_bodega.git
cd Automatizacion_bodega
py -m pip install -r requirements.txt
py -m streamlit run src/app.py
```

En Mac o Linux, reemplazar `py` por `python3`.

La primera vez, Streamlit pide un correo electrónico: se deja vacío y se presiona Enter. La app se abre sola en el navegador; si no, entrar a `http://localhost:8501`. Para detenerla, `Ctrl + C` en la terminal.

Al primer arranque se crea sola la base `bodega.db`, con un inventario simulado de 10 equipos. En la barra lateral aparecen tres vistas: **Carga masiva**, **Validador** y **Ajuste de última hora**.

Variables de entorno (opcionales): copiar `.env.example` a `.env`. Hoy solo existe `BODEGA_DB_PATH` (ruta de la base SQLite). Las claves reales nunca se suben al repositorio.

Con Docker:

```bash
docker build -t automatizacion-bodega .
docker run -p 8501:8501 automatizacion-bodega
```

Tests (18 casos sobre la capa de datos y la lógica de negocio):

```bash
py -m pip install -r requirements-dev.txt
py -m pytest -v
```

### Prueba guiada

1. En **Carga masiva**: folio `GUIA-2026-001`, tipo `Despacho`, modalidad `Convencional`, y pegar `EXC-001`, `EXC-002`, `RET-010`, `GRU-020`, `MON-050` (uno por línea).
2. En **Validador**: elegir `GUIA-2026-001`. `MON-050` aparece como `SIN STOCK DISPONIBLE` (a propósito, tiene stock 0).
3. En **Ajuste de última hora**: reemplazar `MON-050` por `PLA-060`, indicar responsable y motivo. El cambio queda en el registro y el Validador ahora muestra `PLA-060` como `OK`.

## En qué estado está

Al 4 de octubre de 2026 el proyecto está en **etapa inicial (tercer avance)**. Es un borrador de trabajo: no está probado con usuarios reales y varias decisiones pueden cambiar.

| Hecho | Pendiente |
|---|---|
| Problema, caso de uso y maqueta de tres pantallas | Validar el problema con un jefe de bodega real y medir cuánto demoran hoy las guías |
| Carga masiva, validador de SKU y ajuste de última hora con registro de cambios | Cuentas y permisos (mantenimiento carga; bodega valida y emite) |
| Guía de despacho/retiro descargable en texto plano | Guía en PDF y alertas de cambios de último minuto |
| Base SQLite con inventario simulado, tests y CI en GitHub Actions | Bloquear la emisión de la guía cuando algún SKU no valida (hoy se emite y marca el SKU) |
| Diseño preliminar de la base de datos (`docs/datos`) | Pasar la base a Supabase con el modelo de `docs/datos` |
| | Integración con el ERP (etapa posterior, fuera del alcance del MVP) |

## Quiénes la desarrollan

Grupo 6, Universidad de Santiago de Chile. Profesora: Andrea Arredondo.

- **Bastián Vargas Fernández:** aplicación y repositorio.
- **Diego Neves Preau:** modelo de datos.
- **Sebastián Carmona Ponce:** validador y pruebas.
- **Oscar Ynchaustegui Narro:** documentación.

### Flujo de trabajo

- `main` guarda la versión estable, que es la que se entrega.
- `dev` es donde el equipo trabaja día a día. Cada cambio se hace en `dev` o en una rama que sale de `dev`.
- Terminado el cambio, se abre un pull request de `dev` hacia `main`. Otro integrante, distinto de quien hizo el cambio, lo revisa y lo aprueba.
- Ningún integrante sube cambios directamente a `main`.
