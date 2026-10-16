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

A la izquierda hay un menú con tres vistas:

| Vista | Para qué sirve |
|---|---|
| **1. Carga masiva** | Cargar el listado de SKU de una orden (pegados o desde un archivo `.txt` o `.csv`), eligiendo el tipo de movimiento: Despacho (Convencional o Alternativo) o Retiro (Preventivo o Por falla). Elimina duplicados y no deja cargar más de 50 SKU por guía |
| **2. Validador** | Revisar cada SKU contra el inventario. Cada fila queda como `OK`, `SIN STOCK DISPONIBLE` o `SKU NO EXISTE EN INVENTARIO`, y se puede exportar a CSV |
| **3. Ajuste de última hora** | Reemplazar un SKU por otro. El original no se borra y el cambio queda en un registro con fecha, hora, responsable y motivo |

### Prueba guiada (5 minutos)

Sirve para comprobar que todo funciona. Sigue los pasos en orden.

1. En el menú de la izquierda elige **1. Carga masiva**.
   - En *Folio de guia / orden* escribe `GUIA-2026-001`.
   - *Tipo de movimiento*: `Despacho`. *Modalidad*: `Convencional`.
   - En el cuadro grande pega estas cinco líneas (una por línea):

     ```
     EXC-001
     EXC-002
     RET-010
     GRU-020
     MON-050
     ```

   - Presiona **Cargar orden**. Debe aparecer un mensaje verde: `Orden 'GUIA-2026-001' cargada con 5 SKUs`.
2. Elige **2. Validador** y, en *Selecciona un folio*, `GUIA-2026-001`. `MON-050` aparece en rojo como `SIN STOCK DISPONIBLE`: es a propósito, porque en el inventario simulado tiene stock 0.
3. Elige **3. Ajuste de ultima hora**. En el formulario:
   - *SKU original a reemplazar*: la opción que termina en `MON-050`.
   - *SKU de reemplazo*: `PLA-060`.
   - *Responsable del cambio*: tu nombre.
   - *Motivo*: por ejemplo `Sin stock`.
   - Presiona **Registrar reemplazo**. Abajo, en *Log de cambios*, queda anotado el cambio.
4. Vuelve a **2. Validador**: ahora `PLA-060` aparece como `OK` y todo sale en verde.

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

Al 10 de octubre de 2026 el proyecto está en **etapa inicial**, en el **Avance 4**. Ya hubo una conversación real con un subjefe de bodega que hoy hace la tarea (integrante del equipo), y de ella salen las historias de usuario y los wireframes del flujo principal. La app no está probada con usuarios reales y varias decisiones pueden cambiar.

| Hecho | Pendiente |
|---|---|
| Problema, caso de uso y maqueta de tres pantallas | Medir cuánto demoran hoy las guías y cuántas se rehacen |
| Conversación con el usuario (`docs/entrevistas`) | Probar el flujo con usuarios (Semana 7) |
| Historias HU-01 a HU-05 y criterios de la historia principal (`docs/historias.md`) | Bloquear la guía cuando algún SKU no valida, como pide el criterio de la HU-01 |
| Wireframes del flujo principal con sus notas (`docs/wireframes`) | Subir el límite de 50 a 60 productos por guía (máximo real del ERP) |
| Carga masiva, validador de SKU y ajuste de última hora con registro de cambios | Destacar los cambios de último minuto en el validador (HU-04) |
| Diseño preliminar de la base de datos (`docs/datos`) | Cuentas y permisos; pasar la base a Supabase |
| Base SQLite con inventario simulado, tests y CI en GitHub Actions | Integración con el ERP (etapa posterior, fuera del alcance del MVP) |

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
