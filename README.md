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
- **Arquitectura y camino delgado de la prueba de concepto (Avance 7): [docs/arquitectura.md](docs/arquitectura.md)**
- Prueba de concepto con Supabase (reglas, mensajes de error y pruebas de rotura): [docs/poc-supabase.md](docs/poc-supabase.md)
- Inventario real de la bodega: método, supuestos y orden de carga a Supabase: [docs/analisis-inventario.md](docs/analisis-inventario.md)
- Dashboard (en el menú del prototipo, junto a Pedidos; archivo `prototipo/dashboard.html`): gráficos con filtros que se combinan; sus reglas están en `docs/analisis-inventario.md`
- MVP (Streamlit) conectado a Supabase: orden de ejecución del SQL, rol limitado, cómo conectarlo y límites: [docs/mvp-supabase.md](docs/mvp-supabase.md)
- Diseño de la prueba de usuarios (Avance 6): [docs/prueba-usuarios.md](docs/prueba-usuarios.md)
- Guion para cada sesión de la prueba (Avance 6): [docs/pauta-validacion.md](docs/pauta-validacion.md) · [versión para imprimir](docs/pauta-validacion.pdf)
- Kit para ejecutar la prueba (consentimiento, planilla, ensayo, plan de sesiones y regla de decisión): [docs/kit-prueba/](docs/kit-prueba/)
- Línea base: cómo medir hoy una guía a mano y el indicador de éxito: [docs/linea-base.md](docs/linea-base.md)
- Chequeo del prototipo en un celular real: [docs/checklist-celular.md](docs/checklist-celular.md)

### Estructura del repositorio

```
src/                  código de la solución (app.py y las pantallas; db.py es la capa de datos: Supabase o SQLite)
tests/                pruebas automáticas
docs/unidad1/         Avances 2 y 3 de la Unidad 1 (PDF)
docs/bitacora-ia/     registro de encargos a un agente de IA
docs/datos/           diseño de la base de datos y su diagrama
supabase/             esquema SQL y datos de ejemplo de la base (se prueba en SQLite y en Supabase)
docs/historias.md     historias de usuario y criterios de aceptación (Avance 4)
docs/kit-prueba/      kit para ejecutar la prueba con usuarios (Avance 6)
docs/plantillas/      plantillas vacías en CSV (línea base)
herramientas/         scripts de apoyo: cálculo de la línea base y PDF imprimible, con pruebas
docs/wireframes/      wireframes del flujo principal, con sus notas (Avance 4)
docs/entrevistas/     conversación con el usuario y su guion (Avance 4)
docs/recorrido-usuario/ borrador del mapa de recorrido (ensayo, sin validar)
prototipo/            prototipo del flujo principal (Avance 5), en HTML, CSS y JS sin build; conectado a Supabase en la prueba de concepto
README.md             portada del proyecto
.gitignore            archivos locales que no se suben (base de datos, .env)
.env.example          nombres de variables de entorno, sin valores
```

Sin emojis en el código; lo vigila `tests/test_sin_emojis.py`.

## Para quién es

- **Usuario principal:** el jefe de bodega, que hoy digita cada guía a mano y la rehace cuando mantenimiento cambia un equipo a último minuto.
- **Usuarios secundarios:** comercial, que envía el pedido de venta (PV), y mantenimiento, comercial y operaciones, que piden los cambios de último minuto.

## Prueba de concepto (Avance 7)

**Qué hace.** Demuestra una sola acción de punta a punta con piezas reales, **preparar la guía de una orden**. La persona presiona *Preparar guía*, la base de datos vuelve a revisar cada producto contra el inventario, guarda la guía y la pantalla muestra su número interno. Si hay un código que no existe, la guía no se guarda y aparece el mensaje para corregirlo. El diagrama, las piezas y lo que queda fuera están en [docs/arquitectura.md](docs/arquitectura.md).

**Dirección pública.** [bodega-prototipo.vercel.app](https://bodega-prototipo.vercel.app). Se abre sin iniciar sesión.

**Video (1 a 2 minutos).** Se agrega el enlace cuando esté grabado.

**Qué flujo demuestra.**

| Caso | Cómo se prueba | Qué se ve |
|---|---|---|
| Exitoso | Orden 3001 → *Cargar pedido* → *Validar* → *Preparar guía* | La pantalla de guía lista con el **N.º interno** de la guía |
| Error | Orden 3002 → *Cargar pedido* → *Validar* | La guía queda bloqueada con el mensaje *"Corrige 1 producto para continuar"* por el código `SD-63A20-9999`, que no existe |
| Volver a empezar | Botón *Reiniciar demo* | Las órdenes 3001 y 3002 vuelven a estar como al inicio |

**Qué tecnología requiere.**
- Para usarla, solo un navegador.
- Para levantarla en tu computador, [Node.js](https://nodejs.org) 18 o superior, Python 3 (solo para abrir un servidor local) y Git o la descarga en ZIP del repositorio.
- Una base en [Supabase](https://supabase.com). Puede ser la del grupo, ya preparada, o una propia creada con los scripts de `supabase/`.

**Qué variables necesita.** Están en `.env.example`, sin valores. Se copian a un archivo `.env`, que no se sube al repositorio.

| Variable | Qué es | Dónde se obtiene |
|---|---|---|
| `SUPABASE_URL` | La dirección del proyecto, con la forma `https://xxxx.supabase.co` | Supabase → *Project Settings* → *Data API* |
| `SUPABASE_PUBLISHABLE_KEY` | La clave **publicable**, que empieza con `sb_publishable_` | Supabase → *Project Settings* → *API Keys*. Si usas la base del grupo, pídela al equipo por un canal privado. Nunca uses la clave secreta |

### Cómo levantarla desde cero

Los comandos son para PowerShell en Windows. En Mac o Linux, usa `cp` en vez de `copy` y `python3` en vez de `py`.

**Paso 1. Descargar el proyecto.**

```
git clone https://github.com/diegoneves-design/Automatizacion_bodega.git
cd Automatizacion_bodega
```

**Paso 2. Preparar la base.** Si usas la base del grupo, ya está lista y puedes pasar al paso 3. Si creas una propia, en Supabase entra a *SQL Editor* y ejecuta estos archivos de `supabase/` en este orden, cada uno en una consulta nueva: `schema.sql`, `acceso.sql`, `funciones.sql` y `seed_poc.sql`.

**Paso 3. Completar las variables.**

```
copy .env.example .env
```

Abre `.env` con el Bloc de notas y completa `SUPABASE_URL` y `SUPABASE_PUBLISHABLE_KEY`. Deja el resto como está.

**Paso 4. Generar la configuración del prototipo.**

```
node prototipo/generar-config.mjs
```

Tiene que decir `prototipo/js/config.js creado.` Si dice que falta una variable, revisa el paso 3.

**Paso 5. Abrir el prototipo.**

```
cd prototipo
py -m http.server 8000
```

Entra a `http://127.0.0.1:8000` en el navegador y prueba los casos de la tabla de arriba. Para cerrarlo, vuelve a PowerShell y presiona `Ctrl + C`.

**Si algo falla.**
- *"Falta la configuración de la base de datos"* en la pantalla. No se hizo el paso 4, o se abrió el archivo `index.html` con doble clic en vez de usar el servidor del paso 5.
- *"No hay conexión con la base de datos"*. Revisa tu internet y que `SUPABASE_URL` esté bien escrita.
- La orden 3001 ya tiene guía. Presiona *Reiniciar demo*.

**En Vercel** el sitio se publica solo desde `main`, con las variables `SUPABASE_URL` y `SUPABASE_PUBLISHABLE_KEY` configuradas en el proyecto y el comando de construcción que genera la configuración (detalle en «Prueba de concepto con Supabase: qué hay que configurar», más abajo).

## Aplicación Streamlit (MVP): cómo se instala y se ejecuta

Esta es la aplicación Streamlit de `src/`, el MVP. La profesora pidió (Avance 5) no invertirle más horas hasta confirmar el flujo con usuarios; por decisión de Bastián, desde el 20 de noviembre de 2026 se retomó el trabajo sobre ella: ahora se conecta a Supabase (`docs/mvp-supabase.md`). La prueba de concepto de arriba sigue siendo la del prototipo; en «Congelado» se explica qué parte del MVP sigue congelada y cuál no.


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

Al 15 de noviembre de 2026 el proyecto está en **etapa inicial**, en el **Avance 6**. A partir de la conversación con un subjefe de bodega que hoy hace la tarea (integrante del equipo), de las historias de usuario y de los wireframes del Avance 4, se construyó un prototipo navegable del flujo principal, independiente de la aplicación Streamlit, y se hizo su análisis ético. Después se conectó a una base real en Supabase como prueba de concepto. Ya está diseñado y preparado cómo se va a probar con personas de fuera del equipo, pero **esa prueba todavía no se hace**. Ni el prototipo ni la aplicación están probados con usuarios reales, y varias decisiones pueden cambiar.

La profesora indicó en la retroalimentación del Avance 5 que, mientras la prueba con usuarios no confirme el flujo, no se le dediquen más horas a la aplicación Streamlit. Por eso el estado se ordena en cuatro bloques.

### Hecho

| Qué | Dónde |
|---|---|
| Problema, caso de uso y maqueta de tres pantallas | `docs/unidad1` |
| Conversación con el usuario | `docs/entrevistas` |
| Historias HU-01 a HU-05 con criterios principal y alternativo, y HU-05 con una acción de la persona | `docs/historias.md` |
| Wireframes del flujo principal con sus notas | `docs/wireframes` |
| Prototipo navegable P1 a P4 con sistema mínimo, mapa de navegación y registro de decisiones; borde del campo Cliente corregido (contraste 3:1) | `prototipo/`, `docs/prototipo.md` |
| Análisis ético: exclusión, datos personales, accesibilidad, sostenibilidad y riesgos; plazo de conservación propuesto de 24 meses | `docs/etica.md` |
| Aplicación Streamlit: carga masiva, validador de SKU, ajuste de última hora con registro de cambios y bloqueo de la guía si algún SKU no valida; base SQLite con inventario simulado, pruebas y CI en GitHub Actions | `src/`, `tests/` |
| Diseño de la base de datos con el esquema SQL y datos de ejemplo consistentes (modalidad solo en el despacho y motivo solo en el retiro) | `docs/datos`, `supabase/` |
| Prueba de concepto en Supabase: el prototipo lee órdenes, valida SKU, registra cambios con motivo obligatorio y prepara la guía, con validación en tres capas. Los cuatro scripts corrieron en Supabase, las 82 comprobaciones con la clave publicable pasan y la pantalla se probó en un navegador contra la base real | `prototipo/`, `supabase/`, `docs/poc-supabase.md` |
| Diseño de la prueba con usuarios y guion de cada sesión, con pauta imprimible de 2 planas | `docs/prueba-usuarios.md`, `docs/pauta-validacion.md` |
| Kit para ejecutar la prueba (consentimiento, planilla, ensayo, plan de sesiones, regla de decisión), protocolo de la línea base con su herramienta de cálculo y checklist del celular. El prototipo se revisó en pantallas de 360 y 390 px de ancho | `docs/kit-prueba/`, `docs/linea-base.md`, `docs/checklist-celular.md` |
| Inventario real cargado en Supabase (1.617 equipos y 319 extensiones eléctricas) y Dashboard interactivo con 12 gráficos, filtros cruzados, tabla de casos y vistas por rol | `prototipo/dashboard.html`, `supabase/dashboard.sql`, `docs/analisis-inventario.md` |
| MVP (Streamlit) sobre Supabase, en la rama `feature/mvp-supabase`: capa de datos `src/db.py` (Supabase o SQLite) que llama a las funciones SQL de la base, folio de la orden, `crear_pedido`, vistas de lectura, un rol de base limitado `app_mvp` y el cierre de la lectura del RUT y la dirección de los clientes con la clave publicable. Ejecutado en Supabase el 23 de noviembre de 2026 (resultados informados por Bastián): `verificar_mvp.sql` con sus 46 filas OK y `probar_en_supabase.py` con 89 OK y 0 FALLAS; además probado contra un PostgreSQL local y en SQLite | `src/`, `supabase/mvp_*.sql`, `docs/mvp-supabase.md` |

### Pendiente del avance

| Qué | Por qué falta |
|---|---|
| Que el equipo verifique y apruebe los criterios de HU-01 a HU-05 de `docs/historias.md` | Se propusieron con ayuda de IA contra el código y la profesora pidió que los escriba el equipo |
| Confirmar con administración el plazo de conservación de 24 meses | Es una propuesta del equipo (`docs/etica.md`, ficha B2) |
| Ejecutar `supabase/seed_poc.sql` en Supabase con los RUT de ejemplo nuevos (`11.111.111-1` y `22.222.222-2`) y luego `select public.reiniciar_demo();` | La base real sigue con los RUT anteriores hasta que se vuelva a ejecutar la semilla |
| Configurar Vercel (variables `SUPABASE_URL` y `SUPABASE_PUBLISHABLE_KEY` y comando de construcción) y volver a publicar desde `main` | Hasta entonces el sitio publicado no es la versión conectada a Supabase |
| Revisar el Dashboard en la página publicada y confirmar con Oscar o el jefe de bodega los supuestos del análisis (valores numéricos = arrendado, significado de POR HABILITAR y de BAJA) y **si el inventario real puede mostrarse en una demo pública** (pregunta 4 de `docs/analisis-inventario.md`, todavía abierta) | `supabase/dashboard.sql` ya se ejecutó en Supabase (la función devuelve 1.617 equipos y 319 extensiones). Falta la respuesta de la bodega y publicar el prototipo desde `main` |
| Elegir dónde se publica el MVP (Streamlit no corre en Vercel), guardar su `DATABASE_URL` como secreto del servicio y, más adelante, agregar inicio de sesión real y políticas por rol | Hoy el MVP corre solo en el computador y no tiene inicio de sesión: cualquiera con acceso opera como el usuario que elija (limitación documentada en «Seguridad de la base en esta etapa») |
| Volver a ejecutar en Supabase `supabase/probar_en_supabase.py` y probar a mano el flujo de órdenes del MVP contra Supabase | El último resultado informado de `probar_en_supabase.py` (89 OK y 0 FALLAS) es anterior a dos comprobaciones nuevas sobre los clientes (dirección y razón social); `verificar_mvp.sql` ya se ejecutó completo (46 filas OK). El flujo de órdenes todavía no se probó en un navegador contra Supabase |

### Congelado, no se hará por ahora

Hasta el 20 de noviembre todo esto era de la **aplicación Streamlit**: la profesora pidió (retroalimentación del Avance 5) no invertirle más horas mientras la prueba con usuarios no confirme el flujo. **Por decisión de Bastián, desde el 20 de noviembre de 2026 el MVP (Streamlit, `src/`) retoma ese trabajo**: se migró a Supabase y se le agregan vistas (`docs/mvp-supabase.md`). Por eso la tabla se separa en lo que ya no está congelado y lo que sigue congelado.

**Retomado en el MVP (ya no está congelado):**

| Qué | Estado |
|---|---|
| Subir el límite de 50 a 60 productos por guía en la aplicación | **Hecho en el MVP** (rama `feature/mvp-supabase`): el límite lo define la base (60), igual que el prototipo. El MVP lo cubre sin usar la rama local `feature/avance5-pendientes-app`, que sigue sin subir ni fusionar |
| Hacer obligatorio el motivo del cambio en la aplicación | **Hecho en el MVP**: la base lo exige (`registrar_cambio`) y la pantalla pide el motivo. El prototipo y la base ya lo exigían |

**Sigue congelado:**

| Qué | Estado |
|---|---|
| Destacar los cambios de último minuto en el validador de la aplicación (HU-04) | Sigue congelado. El detalle de la orden del MVP muestra una columna «Última modificación», pero no hay destaque visual como el que pide HU-04. El prototipo sí los destaca |
| Corregir el borde del campo Cliente en la aplicación | Sigue pendiente, y ya no es cierto que la aplicación no tenga ese campo: el MVP tiene un selector de Cliente en Carga masiva (de Streamlit), cuyo contraste no se ha revisado. El del prototipo ya se corrigió |
| Cuentas y permisos en la aplicación | Sigue congelado: el MVP no tiene inicio de sesión (se elige quién opera en el menú; limitación documentada en «Seguridad de la base en esta etapa»). Hay un inicio de sesión por jerarquía en la rama local `feature/login-etapa1`, sin subir ni fusionar |

### Siguiente etapa (no es pendiente del avance)

| Qué | Dónde |
|---|---|
| Línea base: medir cuánto demoran hoy las guías y cuántas se rehacen | `docs/linea-base.md` (protocolo y herramienta escritos, sin medir) |
| Ensayo interno de la pauta, con alguien que no diseñó las tareas | `docs/kit-prueba/ensayo-interno.md` |
| Prueba del prototipo en un celular real, con datos móviles | `docs/checklist-celular.md` |
| Prueba con usuarios de fuera del equipo | `docs/prueba-usuarios.md` y el kit de `docs/kit-prueba/` |
| Dos preguntas al jefe de bodega: qué motivos tiene un retiro y si existe un retiro normal sin motivo; y qué debe comprobar «Validar» en un retiro | `docs/poc-supabase.md` (sección 4) y `docs/datos/estructura_datos.md` (sección 5) |

Quedan fuera del alcance del MVP la integración con el ERP, y antes de usar datos reales hay que cerrar el acceso con inicio de sesión (ver «Seguridad de la base en esta etapa»).

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
