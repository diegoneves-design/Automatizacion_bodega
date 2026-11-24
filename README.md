# Automatizacion_bodega

MVP del Grupo 6 para el electivo *Ingeniería Digital en Acción: Datos, IA, MVP* (USACH, Departamento de Ingeniería Industrial).

## Qué es la solución

Una aplicación web que **genera automáticamente la guía de despacho o retiro** de equipos de arriendo. Hoy el jefe de bodega digita cada guía a mano, y la rehace cuando mantenimiento cambia un equipo a último minuto. El MVP reemplaza esa digitación por un flujo con tres pasos:

1. **Carga masiva** de SKU (pegados o desde archivo), eligiendo el tipo de movimiento: Despacho (Convencional o Alternativo) o Retiro (Preventivo o Por falla). Elimina duplicados y bloquea la carga si se exceden los 60 SKU por guía.
2. **Validación automática** de cada SKU contra el inventario. Cada fila queda como `OK`, `No disponible` (el equipo existe pero está arrendado, en mantención o fuera de servicio) o `No existe`, con exportación a CSV.
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
- Prueba de concepto con Supabase (reglas, mensajes de error y pruebas de rotura): [docs/poc-supabase.md](docs/poc-supabase.md)
- Inventario real de la bodega: método, supuestos y orden de carga a Supabase: [docs/analisis-inventario.md](docs/analisis-inventario.md)
- Dashboard (en el menú del prototipo, junto a Pedidos; archivo `prototipo/dashboard.html`): gráficos con filtros que se combinan; sus reglas están en `docs/analisis-inventario.md`
- MVP (Streamlit) conectado a Supabase: orden de ejecución del SQL, rol limitado, cómo conectarlo y límites: [docs/mvp-supabase.md](docs/mvp-supabase.md)
- Diseño de la prueba de usuarios (Avance 6): [docs/prueba-usuarios.md](docs/prueba-usuarios.md)
- Guion para cada sesión de la prueba (Avance 6): [docs/pauta-validacion.md](docs/pauta-validacion.md)

### Estructura del repositorio

```
src/                  código de la solución (app.py y las pantallas; db.py es la capa de datos: Supabase o SQLite)
tests/                pruebas automáticas
docs/unidad1/         Avances 2 y 3 de la Unidad 1 (PDF)
docs/bitacora-ia/     registro de encargos a un agente de IA
docs/datos/           diseño de la base de datos y su diagrama
supabase/             esquema SQL y datos de ejemplo de la base (se prueba en SQLite y en Supabase)
docs/historias.md     historias de usuario y criterios de aceptación (Avance 4)
docs/wireframes/      wireframes del flujo principal, con sus notas (Avance 4)
docs/entrevistas/     conversación con el usuario y su guion (Avance 4)
docs/recorrido-usuario/ borrador del mapa de recorrido (ensayo, sin validar)
prototipo/            prototipo del flujo principal (Avance 5), en HTML, CSS y JS sin build; conectado a Supabase en la prueba de concepto
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
- Sin configurar nada, la aplicación usa una **base local de pruebas** (`bodega_mvp.db`, que se crea sola) con 7 equipos y 2 órdenes de ejemplo; el menú lo dice: «Base local de pruebas (SQLite)». Para trabajar con la base real en Supabase hay que definir `DATABASE_URL` (ver `docs/mvp-supabase.md`); entonces el menú dice «Base: Supabase (PostgreSQL)».

### Paso 6. Cerrar el programa

Haz clic en la ventana de PowerShell y presiona `Ctrl + C`. Después ya puedes cerrar el navegador y la ventana. Para volver a usarlo otro día, repite los pasos 3 y 5.

### Qué vas a ver

La aplicación abre en **Órdenes**. A la izquierda hay un menú con cinco opciones. *Validador* y *Ajuste de última hora* trabajan sobre la orden que tengas elegida; si no hay ninguna, te devuelven a *Órdenes*.

| Vista | Para qué sirve |
|---|---|
| **Órdenes** | Ver las órdenes del día, buscarlas por número, cambiar la fecha y filtrar por Despacho o Retiro. *Ver detalle* abre la orden con sus equipos, el estado de cada uno y su última modificación |
| **Carga masiva** | Cargar el listado de SKU de una orden (pegados o desde un archivo `.txt` o `.csv`), eligiendo el tipo de movimiento: Despacho (Convencional o Alternativo) o Retiro (Preventivo o Por falla). Pide el folio (con la forma `GUIA-2026-003`) y el cliente, elimina duplicados y no deja cargar más de 60 SKU por guía. Al cargar, abre el detalle de la orden nueva |
| **Validador** | Revisar cada SKU de la orden contra el inventario. El resultado queda guardado en la base. Cada fila queda como `OK`, `No disponible` o `No existe`, y se puede descargar en CSV. Si algún SKU tiene problemas, *Emitir guía* queda bloqueado y *Corregir SKU* lleva al ajuste. Con todo `OK`, emite la guía (solo el jefe de bodega puede) con su número y la deja para descargar en `.txt`. Una orden con guía ya no admite cambios |
| **Ajuste de última hora** | Reemplazar un SKU por otro del inventario (se busca por parte del SKU o de la descripción), con motivo y responsable (se elige de la lista de usuarios). El original no se borra y el cambio queda en el historial de la orden; después hay que volver a validar |
| **Historial** | Ver todos los cambios de última hora (fecha y hora, orden, SKU original y nuevo, responsable y motivo) y descargarlos en CSV |
| **Dashboard** (opcional, apagado por omisión) | Análisis del inventario real: 5 indicadores, 12 gráficos que se filtran entre sí, tabla de equipos con descarga en CSV, vistas rápidas por rol y «Lectura de los datos». Solo aparece con `DASHBOARD_INVENTARIO=1` |

### Dashboard del inventario (opcional)

Es el análisis del inventario real de la bodega (1.617 equipos y 319 extensiones), dentro del mismo menú del MVP. **Viene apagado**: el inventario real no se muestra en público sin permiso de la bodega (pregunta 4 de `docs/analisis-inventario.md`, todavía abierta).

- **En tu computador:** en `.env`, `DASHBOARD_INVENTARIO=1`, y que `DATABASE_URL` apunte a Supabase (con la base local de pruebas la vista sale vacía). Aparece «Dashboard» en el menú, y también se abre directo con `http://localhost:8501/?vista=dashboard`.
- **En un hosting público:** déjalo **sin definir**. Para encenderlo, agrega la variable de entorno `DASHBOARD_INVENTARIO` con el valor `1` en el servicio y reinícialo; para apagarlo, quítala. Cómo y por qué: `docs/analisis-inventario.md` (sección 11).
- **Cómo funciona:** los gráficos son los mismos del prototipo (se arma la página con los mismos archivos, sin copiarlos). Los datos los lee el servidor con el rol limitado `app_mvp` y viajan dentro de la página: el navegador no usa la clave publicable ni llama a Supabase. Los filtros quedan en la dirección (`?vista=dashboard#estado=arrendado`) y se pueden compartir.
- **Streamlit está fijo en la versión 1.65.0** (`requirements.txt`): el Dashboard usa `st.iframe`, que no existe en versiones antiguas.

### Prueba guiada (5 minutos)

Sirve para comprobar que todo funciona. Sigue los pasos en orden. Usa las dos órdenes de ejemplo (`GUIA-2026-001` y `GUIA-2026-002`), que ya vienen cargadas.

> Si ya probaste la app antes con la base local, borra `bodega_mvp.db` para volver a partir con los datos de ejemplo. Con la base de Supabase, quien administra el prototipo puede reiniciar la demo (`select public.reiniciar_demo();`, que solo restaura esas dos órdenes).

1. En **Órdenes** elige `GUIA-2026-002` (un retiro por falla) y presiona **Ver detalle**. Aparecen sus cuatro equipos como `Sin validar`.
2. Presiona **Validar SKUs →**. En *Resultado de validación* aparece `Validación con diferencias` (3 de 4 SKU válidos): `SD-63A20-9999` sale como `No existe`. Es a propósito. *Emitir guía* queda bloqueado.
3. Presiona **Corregir SKU**. Se abre *Ajuste de última hora* con `SD-63A20-9999` ya elegido en *SKU a reemplazar*. En el formulario:
   - *Buscar el equipo que entra*: escribe `0315` y en *Nuevo SKU* elige `SD-63A20-0315`.
   - *Motivo del cambio*: `Otro`. *Responsable*: el nombre de la lista (por ejemplo, `Camila Rojas`).
   - Presiona **Guardar cambio**. Vuelves a la validación, que dice que la orden aún no se valida y avisa `Cambio registrado: SD-63A20-9999 → SD-63A20-0315. Vuelve a validar la orden.`
4. Presiona **Validar ahora**: aparece `Validación completada` (4 de 4) y todo sale `OK`. Presiona **Emitir guía →** (el menú de la izquierda dice quién opera: debe ser el jefe de bodega, `Pedro Soto`; con otro usuario la base responde `Solo el jefe de bodega puede preparar la guía.`). Se abre *Guía generada* con su número y el botón **Descargar guía (.txt)**. La primera guía lleva el número 15230.
5. En el menú elige **Historial**: el cambio queda anotado con fecha, hora, orden, responsable y motivo.
6. En **Carga masiva** crea una orden nueva: folio `GUIA-2026-003`, un cliente, `Despacho` y `Convencional`, y pega `ST-0042` y `MP-0107`. Se abre su detalle. Si repites el folio, la base responde `Ya existe una orden con ese folio. Usa otro.`

### Si algo falla

| Qué ves | Por qué pasa | Qué hacer |
|---|---|---|
| `py` no se reconoce como comando, o dice que no se encontró Python | Python no está instalado o no se marcó "Add python.exe to PATH" | Repite el paso 1 y reinicia PowerShell |
| `No module named streamlit` | No se hizo el paso 4, o se hizo con otro Python | Repite el paso 4 y luego el 5, siempre usando `py -m` |
| `can't open file ... src/app.py` | Estás en la carpeta equivocada | Vuelve al paso 3 y haz la comprobación con `dir` |
| El navegador no abre nada | A veces Streamlit no abre el navegador solo | Abre tú `http://localhost:8501` |
| `Port 8501 is already in use` | Ya hay otra copia del programa abierta | Ciérrala con `Ctrl + C`, o usa otro puerto: `py -m streamlit run src/app.py --server.port 8502` y abre `http://localhost:8502` |
| Quiero empezar de cero, sin las órdenes que cargué | Con la base local, los datos quedan en `bodega_mvp.db` | Cierra el programa (`Ctrl + C`), borra el archivo `bodega_mvp.db` y vuelve a ejecutar; se crea de nuevo con los datos de ejemplo |
| Dice «El folio debe tener la forma GUIA-2026-001.» | El folio tiene otra forma | Escribe `GUIA`, el año de cuatro cifras y un número, por ejemplo `GUIA-2026-003` |
| Dice «No se pudo conectar con la base de datos.» | `DATABASE_URL` está mal escrita, la contraseña no es la del rol o no hay internet | Revisa `DATABASE_URL` en `.env` (ver `docs/mvp-supabase.md`), sin compartirla, y presiona **Reintentar** |

Sobre Mac o Linux: es lo mismo, pero se escribe `python3` en lugar de `py` (por ejemplo, `python3 -m streamlit run src/app.py`).

### Opciones para quien ya tiene experiencia

**Variables de entorno (opcionales).** `DATABASE_URL` es la conexión a PostgreSQL (Supabase) con el rol limitado `app_mvp`; si no se define, se usa una base SQLite local (`BODEGA_MVP_DB` indica dónde; por omisión, `bodega_mvp.db`). La aplicación lee un archivo `.env` en la raíz del repositorio, **sin pisar** las variables que ya estén definidas en el sistema (en un hosting mandan sus secretos). La contraseña y la cadena de conexión nunca se suben al repositorio: `.env` está en `.gitignore` y `.env.example` solo muestra los nombres. Cómo armar `DATABASE_URL`: `docs/mvp-supabase.md`.

**Con Docker:**

```bash
docker build -t automatizacion-bodega .
docker run -p 8501:8501 automatizacion-bodega
```

Para conectarla a Supabase, pasa la variable sin escribirla en ningún archivo: `docker run -p 8501:8501 -e DATABASE_URL automatizacion-bodega` (toma el valor de tu sistema).

**Pruebas automáticas.** Corren sin conexión a internet. Requieren instalar `pytest`, que no viene con el paso 4:

```powershell
py -m pip install -r requirements-dev.txt
py -m pytest tests
```

Las pruebas contra PostgreSQL de verdad (capa de datos, rol limitado y recorridos de pantalla) son **opcionales**: corren solo si defines `DATABASE_URL_TEST` con una base vacía de prueba cuyo nombre termine en `_test`. En el CI de GitHub corren siempre, contra un PostgreSQL temporal. Detalle en `docs/mvp-supabase.md`.

## En qué estado está

Al 5 de noviembre de 2026 el proyecto está en **etapa inicial**, en el **Avance 6**. Ya está diseñado cómo vamos a probar el prototipo con personas de fuera del equipo, pero la prueba todavía no se hace. A partir de la conversación con un subjefe de bodega que hoy hace la tarea (integrante del equipo), de las historias de usuario y de los wireframes del Avance 4, se construyó un prototipo navegable del flujo principal, publicado en [bodega-prototipo.vercel.app](https://bodega-prototipo.vercel.app) e independiente de la app, y se hizo su análisis ético. Ni el prototipo ni la app están probados con usuarios reales, y varias decisiones pueden cambiar.

| Hecho | Pendiente |
|---|---|
| Problema, caso de uso y maqueta de tres pantallas | Medir cuánto demoran hoy las guías y cuántas se rehacen |
| Conversación con el usuario (`docs/entrevistas`) | Ejecutar la prueba de usuarios diseñada en el Avance 6 (`docs/prueba-usuarios.md`) |
| Historias HU-01 a HU-05 con criterios principal y alternativo (`docs/historias.md`) | Que el equipo confirme los criterios de HU-02 a HU-05, propuestos con ayuda de IA |
| Wireframes del flujo principal con sus notas (`docs/wireframes`) | Subir el límite de 50 a 60 productos por guía en la app (máximo real del ERP; el prototipo ya usa 60; el MVP conectado a Supabase, en la rama `feature/mvp-supabase`, ya usa 60) |
| Prototipo navegable P1 a P4 con sistema mínimo, mapa de navegación y registro de decisiones (`prototipo/`, `docs/prototipo.md`) | Destacar los cambios de último minuto en el validador de la app (HU-04) |
| Análisis ético: exclusión, datos personales, accesibilidad, sostenibilidad y riesgos (`docs/etica.md`) | Hacer obligatorio el motivo del cambio y corregir el borde del campo Cliente (riesgos 3 y 5 de `docs/etica.md`) |
| Carga masiva, validador de SKU y ajuste de última hora con registro de cambios; la app bloquea la emisión de la guía si algún SKU no valida | Cuentas y permisos (la app Streamlit queda congelada hasta validar el flujo con usuarios) |
| Diseño de la base de datos con el esquema SQL y datos de ejemplo consistentes (`docs/datos`, `supabase/`) | Validar con el jefe de bodega que el retiro tenga solo los motivos falla y mantención preventiva, y si existe un retiro normal sin motivo |
| Base SQLite con inventario simulado, tests y CI en GitHub Actions. Los cuatro scripts de `supabase/` corrieron en Supabase y las 82 comprobaciones con la clave publicable pasan (`supabase/probar_en_supabase.py`) | Cerrar el acceso con inicio de sesión antes de usar datos reales: hoy las políticas son abiertas |
| | Integración con el ERP (etapa posterior, fuera del alcance del MVP) |
| Diseño de la prueba con usuarios y guion de cada sesión (`docs/prueba-usuarios.md`, `docs/pauta-validacion.md`) | |
| Prueba de concepto escrita: el prototipo lee órdenes, valida SKU, registra cambios (con motivo obligatorio) y prepara la guía en Supabase, con validación en tres capas (`prototipo/`, `supabase/`, `docs/poc-supabase.md`), probada en Supabase: las reglas de la base y la pantalla en un navegador contra la base real | Probarla en un celular, con poca señal y con personas ajenas al equipo (prueba de usuarios, `docs/prueba-usuarios.md`) |
| MVP (Streamlit) sobre Supabase, en la rama `feature/mvp-supabase`: capa de datos `src/db.py` (Supabase o SQLite) que llama a las funciones SQL, folio de la orden, `crear_pedido`, vistas de lectura y un rol de base limitado `app_mvp` (`docs/mvp-supabase.md`). Probado contra un PostgreSQL local y en SQLite | Ejecutar en Supabase los archivos `mvp_*.sql` y `funciones.sql`, definir la contraseña del rol `app_mvp`, correr `supabase/verificar_mvp.sql` y `probar_en_supabase.py`, y decidir dónde se publica el MVP (Streamlit no corre en Vercel) |
| Inventario real cargado en Supabase (1.617 equipos y 319 extensiones eléctricas) y Dashboard interactivo con 12 gráficos, filtros cruzados, tabla de casos y vistas por rol (`prototipo/dashboard.html`, `supabase/dashboard.sql`, `docs/analisis-inventario.md`) | Ejecutar `supabase/dashboard.sql` en Supabase, revisar el Dashboard en la página publicada y confirmar con Oscar o el jefe de bodega los supuestos del análisis (valores numéricos = arrendado, significado de POR HABILITAR y de BAJA, y si el inventario real puede mostrarse en una demo pública) |

### Prueba de concepto con Supabase: qué hay que configurar

El proyecto de Supabase del Grupo 6 ya existe (plan gratis). Se creó sin exponer automáticamente las tablas y con RLS automático, así que cada permiso está escrito en los scripts.

**1. La base (una sola vez).** En Supabase, **SQL Editor**, pega y ejecuta estos archivos de `supabase/` **en este orden**, cada uno en una consulta nueva:

| Orden | Archivo | Qué hace |
|---|---|---|
| 1 | `schema.sql` | Crea las siete tablas con sus restricciones |
| 2 | `acceso.sql` | Activa RLS, da permiso de lectura y crea las políticas |
| 3 | `funciones.sql` | Crea las cinco funciones que validan y guardan |
| 4 | `seed_poc.sql` | Carga los datos de la demo (órdenes 3001 y 3002). Se puede volver a ejecutar |

Para comprobar que quedó bien, desde la raíz del repositorio y con `.env` completo: `py supabase/probar_en_supabase.py --si`. Llama a cada función con la clave publicable y muestra las fallas; **modifica y reinicia los datos de la demo**, así que no lo ejecutes durante una sesión de prueba de usuarios.

`seed_ejemplo.sql` es aparte: son los datos del documento `docs/datos/estructura_datos.md`, para comprobar el modelo. No se ejecuta junto con `seed_poc.sql`; si se ejecutó, `seed_poc.sql` lo reemplaza. Si se vuelve a ejecutar `acceso.sql`, hay que ejecutar `funciones.sql` otra vez.

**2. El prototipo.** Necesita la dirección del proyecto y la clave **publicable** (empieza con `sb_publishable_`). Nunca uses la clave secreta ni `service_role`: no se necesitan.

- **En el computador:** copia `.env.example` a `.env`, completa `SUPABASE_URL` y `SUPABASE_PUBLISHABLE_KEY`, y ejecuta `node prototipo/generar-config.mjs`. Eso crea `prototipo/js/config.js`. Luego, desde la carpeta `prototipo`, abre el sitio con un servidor local, por ejemplo `py -m http.server 8000`, y entra a `http://127.0.0.1:8000`.
- **En Vercel:** en el proyecto, agrega las variables de entorno `SUPABASE_URL` y `SUPABASE_PUBLISHABLE_KEY`, y como **Build Command** `node generar-config.mjs` (si la carpeta raíz del proyecto es `prototipo`) o `node prototipo/generar-config.mjs` (si es la raíz del repositorio). Sin eso el sitio muestra «Falta la configuración de la base de datos».

`.env` y `prototipo/js/config.js` no se suben a git (están en `.gitignore`).

### Seguridad de la base en esta etapa

El prototipo **no tiene inicio de sesión**: cualquier persona con el enlace lo usa. Por eso, en esta etapa de prueba de concepto las políticas de acceso (RLS) son **abiertas**: quien abra el prototipo puede **leer** todas las tablas (de la tabla de usuarios solo el nombre, el cargo y si está activo, y de la de clientes solo el identificador y la razón social; el correo, el teléfono, el RUT y la dirección no salen por la API) y puede llamar a las funciones. Es aceptable solo porque **los datos son de ejemplo y ficticios**: no cargues datos reales.

Lo que sí se protege desde ya: las tablas **no aceptan escribir directo** desde el navegador; todo cambio pasa por funciones de la base que vuelven a validar antes de guardar, y las restricciones de las tablas son la última barrera. Como no hay sesión, quién prepara la guía o registra un cambio lo elige la persona en la pantalla: sirve para la demo, no es seguridad. Cualquiera puede además presionar «Reiniciar demo» y borrar lo hecho por otra persona.

**El MVP (Streamlit) se conecta distinto.** No usa la clave publicable ni el usuario `postgres`: se conecta desde el servidor con un rol limitado, `app_mvp`, por la variable `DATABASE_URL`. Ese rol solo lee las columnas que las pantallas usan (sin correo ni teléfono de usuarios, ni RUT ni dirección de clientes), no puede insertar, actualizar ni borrar directo en ninguna tabla, no puede llamar a `reiniciar_demo` y tiene límite de conexiones y de tiempo por consulta. Todo cambio pasa por las funciones de la base. `crear_pedido` no está abierta a la API pública.

**Limitación conocida del MVP: no hay inicio de sesión.** Quien opera se elige en el menú («Operar como»), y la base solo comprueba el rol para emitir la guía. Es decir, **cualquiera con acceso a la aplicación opera como el usuario que elija**: sirve para la demo y la prueba con datos ficticios, no es seguridad. El inicio de sesión real es la siguiente etapa. Por eso, el MVP publicado no debe tener datos personales reales y su dirección no debe difundirse más allá de quienes participen en la prueba.

Antes de usar datos reales hay que agregar inicio de sesión y cerrar las políticas por rol.

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
