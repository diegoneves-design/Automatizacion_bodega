# MVP (Streamlit) conectado a Supabase

Estado: **escrito y probado contra un PostgreSQL local y en SQLite (2026-11-20); falta ejecutarlo en Supabase.** Ver la sección 9.

Este documento explica cómo el MVP (la aplicación Streamlit de `src/`) pasó de una base SQLite con datos de ejemplo a la base real de Supabase: qué se cambió, en qué orden se ejecuta el SQL, cómo conectarla sin exponer ninguna clave, qué permisos tiene la aplicación y qué falta. No contiene contraseñas, cadenas de conexión ni datos reales.

> **Contexto de la decisión.** En la retroalimentación del Avance 5 la profesora pidió no dedicar más horas a la app Streamlit hasta que la prueba con usuarios confirme el flujo. Esta migración se hizo por decisión de Bastián (2026-11-20), después de cargar el inventario real. La rama es `feature/mvp-supabase` y su pull request se fusiona **después** del PR del Dashboard, porque depende de sus archivos SQL.

## 1. Qué cambió

```
Pantallas (Streamlit)  ->  src/db.py  ->  RepoPostgres  ->  psycopg  ->  pooler de Supabase  ->  PostgreSQL
 (src/views/*.py)          una interfaz   (producción)      (sin ORM)    (modo sesión)          rol app_mvp + funciones SQL
                                      \->  RepoSqlite   (pruebas y desarrollo sin red)
```

- **Las reglas viven en la base.** Validar, reemplazar un equipo, bloquear la guía y preparar la guía son las funciones SQL que ya existían (`validar_pedido`, `registrar_cambio`, `preparar_guia`) más una nueva, `crear_pedido`. El MVP no vuelve a escribir esas reglas en Python: las llama. Así hay una sola fuente de verdad y el MVP y el prototipo no pueden contradecirse.
- **Una interfaz, dos implementaciones.** `src/db.py` define lo que necesitan las pantallas. `RepoPostgres` se usa si existe `DATABASE_URL`; `RepoSqlite` (mismo esquema, mismas reglas y mismos mensajes) se usa si no, para desarrollar y probar sin internet. `psycopg` se importa solo al conectar a PostgreSQL.
- **El MVP no se conecta como `postgres`.** Usa un rol propio con permisos mínimos (sección 5).
- **La interfaz clásica (`main_clasico` en `app.py`) y sus funciones de SQLite** (`bodega.db`) se conservan sin cambios, hasta confirmar su eliminación. `main()` ya no las usa.

### Equivalencias que se tuvieron que resolver

| Tema | MVP anterior (SQLite) | Ahora (Supabase) |
|---|---|---|
| Identificador de la orden | `folio` de texto; una fila por SKU | `ordenes.folio` (`GUIA-2026-001`, único, con esa forma) y las líneas en `detalle_orden` |
| Crear una orden | Se insertaban las filas | Función nueva `crear_pedido` (valida folio, cliente, usuario, SKU, tipo y modalidad) |
| Límite de SKU | 50 | 60 (el de la base y el del prototipo) |
| «Stock» | Un número por SKU | El **estado del equipo** (cada SKU es una unidad). `OK` solo si está `disponible`; si no, `No disponible` con su estado (arrendado, en mantención, fuera de servicio) |
| Estado de la orden | Se deducía en Python y la guía se perdía al cerrar la página | `pendiente`, `bloqueada`, `validada`, `emitida`, guardado en la base |
| Validación | Se calculaba al mirar la pantalla | `validar_pedido` la guarda; hay que validar de nuevo después de un cambio |
| Responsable del cambio | Texto libre | Se elige de la tabla `usuarios` |
| Guía | El N° era el folio y se perdía al cerrar | `numero_guia` consecutivo (desde 15230), guardado; solo el jefe de bodega puede prepararla; una orden con guía no admite cambios |
| Tipo y modalidad | Una columna `modalidad` con cuatro valores | `modalidad` solo en el despacho y `motivo_retiro` solo en el retiro |
| Reiniciar la demo | No existía | `reiniciar_demo()` restaura **solo** las órdenes 3001 y 3002 (con folio) y sus líneas, cambios y guías. No borra ninguna otra orden. El MVP no tiene botón de reinicio |

## 2. Archivos SQL nuevos y modificados

| Archivo | Qué hace |
|---|---|
| `supabase/schema.sql` | (modificado) `ordenes` trae la columna `folio` (opcional y única) en las bases nuevas |
| `supabase/mvp_folio.sql` | Agrega `folio` a una base que ya existe, con su unicidad y su forma (`GUIA-2026-001`), y pone el folio a las órdenes 3001 y 3002 |
| `supabase/funciones.sql` | (modificado) agrega la ayuda interna `_skus_limpios` (la usan `cargar_pedido` y `crear_pedido`) y reescribe `reiniciar_demo` para que solo toque la demo |
| `supabase/mvp_funciones.sql` | Crea `crear_pedido`. **No** se le da a `anon` ni a `authenticated` |
| `supabase/mvp_vistas.sql` | Tres vistas de solo lectura (`v_ordenes_resumen`, `v_detalle_orden`, `v_historial_cambios`) que consultan con los permisos de quien las lee |
| `supabase/mvp_rol.sql` | Crea el rol `app_mvp` (sin contraseña escrita en el archivo), sus límites, permisos y políticas |
| `supabase/verificar_mvp.sql` | Solo lee: una fila por comprobación, con lo esperado y lo real |
| `supabase/probar_en_supabase.py` | (modificado) las comprobaciones por la API pública ahora miran solo la demo (órdenes 3001 y 3002, equipos 501 a 507), porque la base tiene además el inventario real y las órdenes del MVP, y suman las de lo nuevo |

Todos los archivos nuevos se pueden volver a ejecutar sin error y no borran datos.

## 3. Orden de ejecución en Supabase

La ejecuta Bastián en el **SQL Editor**; la IA no toca Supabase. **Requisito:** `dashboard.sql` ya debe estar ejecutado (crea `inventario_dashboard()`, que `mvp_rol.sql` le da al rol). Cada archivo en una consulta nueva y en este orden:

1. `supabase/mvp_folio.sql`
2. `supabase/funciones.sql` (se vuelve a ejecutar: trae la ayuda nueva y el `reiniciar_demo` nuevo)
3. `supabase/mvp_funciones.sql`
4. `supabase/mvp_vistas.sql`
5. `supabase/mvp_rol.sql`
6. **La contraseña del rol** (la pones tú, una sola vez). En una consulta nueva, cambiando el texto de ejemplo por una contraseña larga, única, que no uses en ningún otro lugar y, para evitar problemas al armar la dirección, **solo con letras y números**:

   ```sql
   alter role app_mvp password 'REEMPLAZA-ESTE-TEXTO-POR-TU-CONTRASENA';
   ```

   No la pegues en el chat, en un commit ni en un archivo versionado. Si la olvidas, se cambia con la misma línea.
7. `supabase/verificar_mvp.sql`. Debe dar **`OK` en todas las filas**. Con el inventario real cargado, las filas de equipos reales (1617), extensiones (319) y equipos de demo (7) también deben dar `OK`.

Después, para confirmar que el prototipo no cambió su comportamiento (usa la clave publicable): `py supabase/probar_en_supabase.py --si`. **Modifica y reinicia los datos de la demo**: no lo ejecutes durante una sesión de prueba de usuarios.

> Si algún archivo falla, no sigas con el siguiente: copia el mensaje de error (sin contraseñas) y revísalo antes.

### Cómo deshacerlo

Los archivos no borran datos. Para quitar el acceso del MVP basta, en una consulta nueva: `drop owned by app_mvp; drop role app_mvp;`. La columna `folio` y las vistas pueden quedarse: el prototipo no las usa.

## 4. Conectar la aplicación (la cadena de conexión)

La aplicación necesita una **cadena de conexión** en la variable `DATABASE_URL`, con el pooler de Supabase en **modo sesión** (compatible con IPv4; la conexión directa es solo IPv6 y falla en muchos hostings y redes).

**De dónde copiarla** (la pantalla de Supabase puede haber cambiado de nombres; busca estas palabras):

1. En Supabase abre el proyecto del Grupo 6.
2. Arriba, en la barra del proyecto, presiona el botón **Connect**.
3. En el cuadro que se abre, en el tipo de conexión elige **Session pooler** (no «Direct connection» ni «Transaction pooler») y copia la cadena (**URI**). Usa el **puerto 5432**.
4. Tiene esta forma, con `postgres` como usuario y `[YOUR-PASSWORD]` como marcador:

   ```
   postgresql://postgres.<referencia-del-proyecto>:[YOUR-PASSWORD]@<servidor-del-pooler>:5432/postgres
   ```

5. **Cámbiala para que use el rol limitado.** Cambia solo la parte `postgres` del usuario por `app_mvp` y deja el punto y la referencia del proyecto:

   ```
   postgresql://app_mvp.<referencia-del-proyecto>:<la-contraseña-del-paso-6>@<servidor-del-pooler>:5432/postgres
   ```

   La referencia del proyecto (el código corto que va después del punto) también está en **Project Settings → General → Reference ID**. **El usuario es `app_mvp.<referencia>`, no `app_mvp` a secas**: el pooler usa esa parte para saber a qué proyecto entrar.
6. Si la contraseña tuviera símbolos (`@`, `:`, `/`, `#`, `%`), hay que escribirlos codificados (por ejemplo, `@` como `%40`); con solo letras y números no hace falta.

**Dónde guardarla:**

- **En tu computador:** copia `.env.example` a `.env` y pega la cadena como valor de `DATABASE_URL` (sin comillas). `.env` está en `.gitignore`. La aplicación lo lee sola, sin pisar variables que ya estén definidas en el sistema.
- **En el hosting:** como secreto o variable de entorno del servicio, con el nombre `DATABASE_URL`. No va en ningún archivo del repositorio.

Con la cadena puesta, ejecuta `py -m pip install -r requirements.txt` (instala `psycopg`, con versión fija) y `py -m streamlit run src/app.py`. El menú de la izquierda debe decir **«Base: Supabase (PostgreSQL)»**. Si dice «Base local de pruebas (SQLite)», la variable no se leyó.

Si la conexión falla, la pantalla muestra «No se pudo conectar con la base de datos» con un botón **Reintentar**; el mensaje no incluye la dirección ni la contraseña.

## 5. Qué puede y qué no puede hacer el rol `app_mvp`

| Puede | No puede |
|---|---|
| Leer las columnas que las pantallas usan: clientes (id, razón social), usuarios (id, nombre, rol, activo), equipos (id, SKU, descripción, estado, ubicación), órdenes, líneas, cambios, guías (sin el archivo PDF) y las tres vistas | Leer `usuarios.correo`, `usuarios.telefono`, `clientes.rut` ni `clientes.direccion` |
| Ejecutar `crear_pedido`, `cargar_pedido`, `validar_pedido`, `registrar_cambio` y `preparar_guia`, y leer el Dashboard con `inventario_dashboard()` (solo lectura: nueve columnas de equipos, extensiones y conteos, sin datos personales) | Insertar, actualizar ni borrar directo en ninguna tabla |
| Abrir hasta 5 conexiones, con consultas de máximo 10 segundos | Ejecutar `reiniciar_demo` ni las ayudas internas |
| | Crear objetos, ser superusuario, crear roles o bases, ni saltarse las políticas (RLS) |

`crear_pedido` y las vistas tampoco las puede usar la clave publicable del prototipo (`anon`, `authenticated`): `verificar_mvp.sql` y `probar_en_supabase.py` lo comprueban.

### Limitación conocida: no hay inicio de sesión

El MVP no tiene login. Quien opera se elige en el menú («Operar como») y la base solo comprueba, al preparar la guía, que ese usuario sea jefe de bodega. **Cualquiera con acceso a la aplicación opera como el usuario que elija.** Con datos ficticios y una dirección que no se difunde, es aceptable para la demo y la prueba de usuarios; con datos reales, no. El inicio de sesión real es la siguiente etapa. Hasta entonces no se cargan datos personales reales y la dirección de la aplicación se comparte solo con quienes participan en la prueba.

## 6. Pruebas

- **Siempre, sin red:** `py -m pytest tests`. Incluye las pruebas de contrato de `src/db.py` sobre SQLite, los recorridos de pantalla (Streamlit AppTest) y las revisiones estáticas de los SQL (que el rol no tenga contraseña ni escritura directa, que `crear_pedido` no se exponga, que no haya cadenas de conexión en el repositorio).
- **Opcionales, contra PostgreSQL de verdad:** las **mismas** pruebas de contrato y de pantalla corren contra PostgreSQL, conectando con el rol limitado, si defines `DATABASE_URL_TEST` con una base **vacía y de prueba cuyo nombre termine en `_test`** (la prueba borra y recrea el esquema `public`, y se niega a correr si el nombre no termina así). Nunca lee `DATABASE_URL`. Por ejemplo, con un PostgreSQL local: crea la base (`createdb bodega_test`) y define `DATABASE_URL_TEST` apuntando a ella.
- **En el CI de GitHub** el trabajo levanta un servicio de PostgreSQL 16 temporal (sin contraseña, solo accesible desde el propio trabajo), así que esas pruebas corren siempre. La decisión de usarlo: el esfuerzo fue pequeño (un bloque `services` en el flujo) y evita que las reglas de SQLite y las de PostgreSQL se separen sin que nadie lo note.

## 7. Qué se verificó y qué no

**Verificado** (2026-11-20), en una base PostgreSQL 16 local y desechable, no en Supabase:

- Los archivos SQL se aplican en el orden de la sección 3, sobre una base nueva **y** sobre una que simula la actual (estado anterior con inventario de ejemplo y una orden sin folio), y se pueden repetir.
- Las reglas de `crear_pedido`, `validar_pedido`, `registrar_cambio` y `preparar_guia`, con sus mensajes exactos, dan lo mismo en SQLite y en PostgreSQL (pruebas de contrato).
- El rol `app_mvp` no puede escribir directo en ninguna tabla, ni leer correo, teléfono, RUT ni dirección, ni ejecutar `reiniciar_demo`; `anon` y `authenticated` no pueden usar `crear_pedido` ni las vistas.
- `reiniciar_demo`, llamada como `anon` (como lo hace el prototipo), restaura solo 3001 y 3002 y no borra ni los equipos reales ni las órdenes y guías creadas por el MVP; dos reinicios seguidos no chocan con los números de línea de otras órdenes.
- Los recorridos de pantalla (cargar, validar, corregir, emitir la guía, historial y los mensajes de las reglas) en SQLite y contra PostgreSQL con el rol limitado.
- Las pruebas del prototipo (`node --test prototipo/pruebas/filtros.test.js`, 30) siguen pasando: el prototipo no se tocó.

**No verificado:**

- **Nada de esto se ejecutó en Supabase.** Falta la sección 3. Supabase agrega cosas que un PostgreSQL local no tiene (la API REST, `pg_safeupdate`, permisos por omisión sobre lo nuevo); por eso las vistas y las funciones nuevas quitan los permisos de forma explícita, y por eso hay que correr `verificar_mvp.sql` y `probar_en_supabase.py`.
- Las comprobaciones por la API pública de `probar_en_supabase.py` (modificadas en esta etapa) no se ejecutaron: necesitan la API de Supabase.
- La conexión por el **pooler** de Supabase con el usuario `app_mvp.<referencia>` (la forma exacta del usuario y que el pooler acepte un rol propio).
- El MVP en un navegador contra Supabase, y el servicio de PostgreSQL del CI de GitHub (el flujo no se ejecutó; se validó solo su sintaxis).

## 8. Efectos sobre el prototipo y los datos

- El prototipo no cambia: sigue usando `id_orden`, la clave publicable y las funciones de siempre. Las órdenes que se crean desde el MVP **también aparecen en la lista del prototipo**, porque son filas de la misma tabla.
- `reiniciar_demo` ya no vacía las órdenes: solo deja 3001 y 3002 como al comienzo. Lo que se cree desde el MVP no se pierde cuando alguien reinicia la demo del prototipo.
- Una orden **sin folio** (por ejemplo, una creada a mano) no aparece en la lista del MVP; las dos de la demo reciben su folio con `mvp_folio.sql`.
- Los folios `GUIA-2026-001` y `GUIA-2026-002` son de la demo: el MVP no los puede reutilizar.

## 9. Pendiente

1. Ejecutar la sección 3 en Supabase, definir la contraseña de `app_mvp` y correr `verificar_mvp.sql` y `probar_en_supabase.py`.
2. Levantar el MVP en el computador contra Supabase y probarlo a mano (Bastián).
3. **Elegir dónde se publica el MVP.** Streamlit necesita un servidor siempre encendido, así que no corre en Vercel; Vercel queda como entrada pública. Hay un `Dockerfile` listo. Queda decidir el servicio y cargar `DATABASE_URL` como secreto del servicio.
4. Inicio de sesión real y políticas por rol (siguiente etapa).
5. Que el equipo confirme los criterios de aceptación de HU-01 a HU-05 y el plazo de conservación de datos, que siguen pendientes de antes.
