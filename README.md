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
- Historias de usuario y criterios de aceptación (Avance 4): [docs/historias.md](docs/historias.md)
- Wireframes del flujo principal (Avance 4): [docs/wireframes/](docs/wireframes/)
- Conversación con el usuario (Avance 4): [docs/entrevistas/entrevista_subjefe_bodega.md](docs/entrevistas/entrevista_subjefe_bodega.md)
- Prototipo navegable (Avance 5): [docs/prototipo.md](docs/prototipo.md) · [abrir el prototipo](https://bodega-prototipo.vercel.app)
- Análisis ético del prototipo (Avance 5): [docs/etica.md](docs/etica.md)

### Estructura del repositorio

```
src/                  código de la solución (app.py)
tests/                pruebas automáticas
docs/unidad1/         Avances 2 y 3 de la Unidad 1 (PDF)
docs/bitacora-ia/     registro de encargos a un agente de IA
docs/datos/           diseño de la base de datos y su diagrama
docs/historias.md     historias de usuario y criterios de aceptación (Avance 4)
docs/wireframes/      wireframes del flujo principal, con sus notas (Avance 4)
docs/entrevistas/     conversación con el usuario y su guion (Avance 4)
docs/recorrido-usuario/ borrador del mapa de recorrido (ensayo, sin validar)
prototipo/            prototipo navegable del flujo principal (Avance 5), en HTML, CSS y JS sin build
README.md             portada del proyecto
.gitignore            archivos locales que no se suben (base de datos, .env)
.env.example          nombres de variables de entorno, sin valores
```

## Para quién es

- **Usuario principal:** el jefe de bodega, que hoy digita cada guía a mano y la rehace cuando mantenimiento cambia un equipo a último minuto.
- **Usuarios secundarios:** comercial, que envía el pedido de venta (PV), y mantenimiento, comercial y operaciones, que piden los cambios de último minuto.

## Cómo se instala y se ejecuta

Guía paso a paso para Windows, pensada para quien nunca ha usado una terminal. Se hace una sola vez; las veces siguientes basta con los pasos 3 y 5. Toma entre 10 y 15 minutos.

**Qué necesitas:** un computador con Windows 10 u 11, conexión a internet y Python 3.10 o superior.

> **Cómo abrir PowerShell** (la ventana negra o azul donde se escriben los comandos): presiona la tecla Windows, escribe `PowerShell` y presiona Enter. Para pegar un comando basta con hacer clic derecho en la ventana; después presiona Enter para ejecutarlo.

### Paso 1. Revisar que Python esté instalado

En PowerShell escribe:

```powershell
py --version
```

- Si responde `Python 3.10` o un número mayor (por ejemplo `Python 3.12.4`): sigue con el paso 2.
- Si dice que no se encontró Python, o que es una versión menor a 3.10: descarga el instalador desde [python.org/downloads](https://www.python.org/downloads/) y ábrelo. **En la primera pantalla marca la casilla "Add python.exe to PATH"** (abajo) y luego presiona "Install Now". Al terminar, **cierra PowerShell y ábrelo de nuevo**, y repite `py --version`.

### Paso 2. Descargar el proyecto

Elige una de las dos opciones.

**Opción A, con Git** (si ya lo tienes instalado):

```powershell
git clone https://github.com/diegoneves-design/Automatizacion_bodega.git
```

**Opción B, sin Git:**

1. Entra a [github.com/diegoneves-design/Automatizacion_bodega](https://github.com/diegoneves-design/Automatizacion_bodega).
2. Presiona el botón verde **Code** y luego **Download ZIP**.
3. En la carpeta Descargas, haz clic derecho sobre el ZIP y elige **Extraer todo**.

### Paso 3. Entrar a la carpeta del proyecto

En PowerShell, escribe `cd`, un espacio, y la ruta de la carpeta del proyecto. Por ejemplo, si la dejaste en el Escritorio:

```powershell
cd $HOME\Desktop\Automatizacion_bodega
```

Si la carpeta está en otro lugar, hay un truco: abre la carpeta en el Explorador de archivos, haz clic derecho en un espacio vacío y elige **Abrir en Terminal**. Ya quedas dentro, sin escribir la ruta.

**Comprobación:** escribe `dir`. Debes ver, entre otros, `src`, `tests` y `requirements.txt`. Si no aparecen, estás en la carpeta equivocada (a veces el ZIP deja una carpeta dentro de otra con el mismo nombre; entra a la de adentro con `cd Automatizacion_bodega`).

### Paso 4. Instalar lo que necesita el programa

```powershell
py -m pip install -r requirements.txt
```

Puede tardar unos minutos y mostrar mucho texto: es normal. Termina bien si la última línea empieza con `Successfully installed` (o dice `Requirement already satisfied` si ya lo tenías). Esto se hace **una sola vez**.

### Paso 5. Ejecutar el programa

```powershell
py -m streamlit run src/app.py
```

- La primera vez, Streamlit puede pedir un correo electrónico: **déjalo vacío y presiona Enter**.
- Se abre solo el navegador con la aplicación. Si no se abre, escribe en la barra de direcciones: `http://localhost:8501`.
- **No cierres la ventana de PowerShell mientras uses la aplicación**: ahí es donde está corriendo.
- La primera vez se crea sola la base de datos `bodega.db`, con un inventario simulado de 10 equipos. No hay que configurar nada más.

### Paso 6. Cerrar el programa

Haz clic en la ventana de PowerShell y presiona `Ctrl + C`. Después ya puedes cerrar el navegador y la ventana. Para volver a usarlo otro día, repite los pasos 3 y 5.

### Qué vas a ver

La aplicación abre en **Órdenes**. A la izquierda hay un menú con cinco opciones. *Validador* y *Ajuste de última hora* trabajan sobre la orden que tengas elegida; si no hay ninguna, te devuelven a *Órdenes*.

| Vista | Para qué sirve |
|---|---|
| **Órdenes** | Ver las órdenes del día, buscarlas por número, cambiar la fecha y filtrar por Despacho o Retiro. *Ver detalle* abre la orden con sus equipos, el estado de cada uno y su última modificación |
| **Carga masiva** | Cargar el listado de SKU de una orden (pegados o desde un archivo `.txt` o `.csv`), eligiendo el tipo de movimiento: Despacho (Convencional o Alternativo) o Retiro (Preventivo o Por falla). Elimina duplicados y no deja cargar más de 50 SKU por guía. Al cargar, abre el detalle de la orden nueva |
| **Validador** | Revisar cada SKU de la orden contra el inventario. Cada fila queda como `OK`, `Sin stock` o `No existe`, y se puede descargar en CSV. Si algún SKU tiene problemas, *Emitir guía* queda bloqueado y *Corregir SKU* lleva al ajuste. Con todo `OK`, emite la guía y la deja para descargar en `.txt` |
| **Ajuste de última hora** | Reemplazar un SKU por otro del inventario, con motivo y responsable. El original no se borra y el cambio queda en el historial de la orden |
| **Historial** | Ver todos los cambios de última hora (fecha y hora, orden, SKU original y nuevo, responsable y motivo) y descargarlos en CSV |

### Prueba guiada (5 minutos)

Sirve para comprobar que todo funciona. Sigue los pasos en orden.

> Si ya probaste la app antes, borra `bodega.db` para partir con los datos de ejemplo: la app no rechaza un folio repetido y mezclaría las órdenes.

1. En el menú de la izquierda elige **Carga masiva**.
   - En *Folio de guía u orden* escribe `GUIA-2026-001`.
   - *Tipo de movimiento*: `Despacho`. *Modalidad*: `Convencional`.
   - En el cuadro grande pega estas cinco líneas (una por línea):

     ```
     EXC-001
     EXC-002
     RET-010
     GRU-020
     MON-050
     ```

   - Presiona **Cargar orden**. Se abre *Detalle de la orden* con el mensaje `Orden GUIA-2026-001 cargada con 5 SKU. Revisa los equipos y valídala.` Los cinco equipos aparecen como `Sin validar`.
2. Presiona **Validar SKUs →**. En *Resultado de validación* aparece `Validación con diferencias` (4 de 5 SKU válidos): `MON-050` sale como `Sin stock`. Es a propósito, porque en el inventario simulado tiene stock 0. *Emitir guía* queda bloqueado.
3. Presiona **Corregir SKU**. Se abre *Ajuste de última hora* con `MON-050` ya elegido en *SKU a reemplazar*. En el formulario:
   - *Nuevo SKU*: `PLA-060`.
   - *Motivo del cambio*: `Sin stock`.
   - *Responsable*: tu nombre (es obligatorio).
   - Presiona **Guardar cambio**. Vuelves a la validación con el mensaje `Cambio registrado: MON-050 → PLA-060.`
4. Ahora aparece `Validación completada` (5 de 5) y todo sale `OK`. Presiona **Emitir guía →**: se abre *Guía generada* con el botón **Descargar guía (.txt)**. La guía emitida se recuerda solo mientras la página esté abierta.
5. En el menú elige **Historial**: el cambio queda anotado con fecha, hora, orden, responsable y motivo.

### Si algo falla

| Qué ves | Por qué pasa | Qué hacer |
|---|---|---|
| `py` no se reconoce como comando, o dice que no se encontró Python | Python no está instalado o no se marcó "Add python.exe to PATH" | Repite el paso 1 y reinicia PowerShell |
| `No module named streamlit` | No se hizo el paso 4, o se hizo con otro Python | Repite el paso 4 y luego el 5, siempre usando `py -m` |
| `can't open file ... src/app.py` | Estás en la carpeta equivocada | Vuelve al paso 3 y haz la comprobación con `dir` |
| El navegador no abre nada | A veces Streamlit no abre el navegador solo | Abre tú `http://localhost:8501` |
| `Port 8501 is already in use` | Ya hay otra copia del programa abierta | Ciérrala con `Ctrl + C`, o usa otro puerto: `py -m streamlit run src/app.py --server.port 8502` y abre `http://localhost:8502` |
| Quiero empezar de cero, sin las órdenes que cargué | Los datos quedan guardados en `bodega.db` | Cierra el programa (`Ctrl + C`), borra el archivo `bodega.db` y vuelve a ejecutar; se crea de nuevo con el inventario original |
| Dice "Debes ingresar un folio antes de cargar la orden" | Falta escribir el folio | Escribe un folio, por ejemplo `GUIA-2026-001`, y presiona de nuevo **Cargar orden** |

Sobre Mac o Linux: es lo mismo, pero se escribe `python3` en lugar de `py` (por ejemplo, `python3 -m streamlit run src/app.py`).

### Opciones para quien ya tiene experiencia

**Variable de entorno (opcional).** `BODEGA_DB_PATH` indica dónde se guarda la base SQLite; si no se define, se usa `bodega.db` en la carpeta desde donde se ejecuta. La aplicación **no lee el archivo `.env`**: la variable hay que definirla en el sistema (por ejemplo, `$env:BODEGA_DB_PATH = "C:\ruta\bodega.db"` en PowerShell, antes del paso 5). Las claves reales nunca se suben al repositorio; `.env.example` solo muestra los nombres.

**Con Docker:**

```bash
docker build -t automatizacion-bodega .
docker run -p 8501:8501 automatizacion-bodega
```

**Pruebas automáticas** (18 casos sobre la capa de datos y la lógica de negocio). Requieren instalar `pytest`, que no viene con el paso 4:

```powershell
py -m pip install -r requirements-dev.txt
py -m pytest -v
```

## En qué estado está

Al 1 de noviembre de 2026 el proyecto está en **etapa inicial**, en el **Avance 5**. A partir de la conversación con un subjefe de bodega que hoy hace la tarea (integrante del equipo), de las historias de usuario y de los wireframes del Avance 4, se construyó un prototipo navegable del flujo principal, publicado en [bodega-prototipo.vercel.app](https://bodega-prototipo.vercel.app) e independiente de la app, y se hizo su análisis ético. Ni el prototipo ni la app están probados con usuarios reales, y varias decisiones pueden cambiar.

| Hecho | Pendiente |
|---|---|
| Problema, caso de uso y maqueta de tres pantallas | Medir cuánto demoran hoy las guías y cuántas se rehacen |
| Conversación con el usuario (`docs/entrevistas`) | Probar el flujo con usuarios (Semana 7) |
| Historias HU-01 a HU-05 y criterios de la historia principal (`docs/historias.md`) | Revisar y aprobar los criterios en borrador de HU-02 a HU-05 (`docs/prototipo.md`) |
| Wireframes del flujo principal con sus notas (`docs/wireframes`) | Subir el límite de 50 a 60 productos por guía en la app (máximo real del ERP; el prototipo ya usa 60) |
| Prototipo navegable P1 a P4 con sistema mínimo, mapa de navegación y registro de decisiones (`prototipo/`, `docs/prototipo.md`) | Destacar los cambios de último minuto en el validador de la app (HU-04) |
| Análisis ético: exclusión, datos personales, accesibilidad, sostenibilidad y riesgos (`docs/etica.md`) | Hacer obligatorio el motivo del cambio y corregir el borde del campo Cliente (riesgos 3 y 5 de `docs/etica.md`) |
| Carga masiva, validador de SKU y ajuste de última hora con registro de cambios; la app bloquea la emisión de la guía si algún SKU no valida | Cuentas y permisos; pasar la base a Supabase |
| Diseño preliminar de la base de datos (`docs/datos`) | Integración con el ERP (etapa posterior, fuera del alcance del MVP) |
| Base SQLite con inventario simulado, tests y CI en GitHub Actions | |

## Quiénes la desarrollan

Grupo 6, Universidad de Santiago de Chile. Profesora: Andrea Arredondo.

- **Bastián Vargas Fernández:** aplicación y repositorio.
- **Diego Neves Preau:** modelo de datos.
- **Sebastián Carmona Ponce:** validador y pruebas.
- **Oscar Ynchaustegui Narro:** documentación.

### Flujo de trabajo

- `main` guarda la versión estable, que es la que se entrega.
- Cada cambio se hace en una rama `feature/<tema>` que sale de `main` actualizado (por ejemplo, `feature/avance5-prototipo`).
- Terminado el cambio, se abre un pull request de esa rama hacia `main`. Otro integrante, distinto de quien hizo el cambio, lo revisa y lo aprueba antes de fusionarlo.
- Ningún integrante sube cambios directamente a `main`.
- La rama `dev` se usó en las primeras entregas y hoy no forma parte del flujo.
