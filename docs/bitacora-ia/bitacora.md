# Bitácora de uso de IA

Grupo 6 · Automatizacion_bodega

Cada entrada registra un encargo real a un agente de IA (Claude) y el criterio con que se revisó la respuesta. Lo que importa es cómo se revisó, no qué herramienta se usó.

Encargos de esta bitácora hechos por Bastián Vargas el 2026-10-02, a partir de la pauta de entrega de la Unidad 1. Ambos encargos se hicieron sobre la rama `feature/estructura-entrega`, que sale de `dev`.

---

## Encargo 1. Ordenar el repositorio según la pauta de entrega

**Objetivo.** Dejar el repositorio con la estructura mínima pedida: `src/`, `docs/` (con `unidad1`, `bitacora-ia`, `datos`), `.gitignore`, `.env.example` y un README con cinco títulos.

**Instrucción entregada.**
- Contexto: repositorio `Automatizacion_bodega`, MVP en Streamlit y SQLite, con `app.py` en la raíz, tests, Dockerfile y CI.
- Intención: cumplir la estructura de la pauta sin romper lo que ya funciona.
- Restricciones: no borrar código funcional, no agregar dependencias, no subir claves.
- Verificación: que los 18 tests sigan pasando y que Dockerfile y CI apunten a las rutas nuevas.

**Respuesta obtenida.** El agente propuso mover `app.py` a `src/`, actualizar Dockerfile, CI y tests, crear `.env.example`, reescribir el README con los cinco títulos, y copiar el Avance 2 a `docs/unidad1/`. También movió el bloque de "contexto para agentes" que estaba dentro del README a un `CLAUDE.md`, para que el README quede legible para alguien ajeno al equipo.

**Qué se aceptó y qué se corrigió.**
- Aceptado: mover el código a `src/` y ajustar las rutas en tests, Dockerfile y CI.
- Aceptado: `.env.example` solo con nombres de variables, sin valores, y `.env` en `.gitignore`.
- Corregido: el agente agregó la variable `BODEGA_DB_PATH` al código para que `.env.example` no listara variables inventadas; se revisó que el valor por defecto siga siendo `bodega.db`.
- Corregido: la sección "En qué estado está" del README se contrastó con el código real. Por ejemplo, la guía hoy sale en texto plano (no PDF) y se emite aunque un SKU no valide; el README lo dice así.

**Cómo se verificó.** Se ejecutó `pytest`: 18 tests pasan después del cambio. Se buscó `app.py` en todo el repositorio para confirmar que ninguna ruta quedó apuntando al archivo antiguo. Se revisó el diff completo antes de hacer el commit.

---

## Encargo 2. Primer borrador de la estructura de datos

**Objetivo.** Armar `docs/datos/estructura_datos.md`: diagrama de la base, campos con tipo, claves, cardinalidades, campos obligatorios y dos registros de ejemplo por tabla.

**Instrucción entregada.**
- Contexto: caso de uso del Avance 2 (emisión automática de guía) y las tres tablas SQLite que ya tiene el MVP.
- Intención: derivar las tablas desde los sustantivos del caso de uso, con claves primarias y externas y cardinalidad (1:N, N:1, 1:1).
- Restricciones: una columna guarda una sola variable; las claves externas van en el lado "muchos"; no crear la base en Supabase todavía.
- Verificación: que cada fila de ejemplo respete los tipos y los campos obligatorios, y que el diagrama sea Mermaid para que GitHub lo dibuje.

**Respuesta obtenida.** Un modelo de seis tablas: `USUARIO`, `EQUIPO`, `ORDEN`, `ORDEN_ITEM`, `GUIA` y `CAMBIO`, más el diagrama Mermaid y las tablas de ejemplo.

**Qué se aceptó y qué se corrigió.**
- Aceptado: separar `ordenes` del MVP en `ORDEN` y `ORDEN_ITEM`, porque hoy el folio, el tipo y la modalidad se repiten en cada SKU.
- Aceptado: agregar `USUARIO` y `GUIA`, que el Avance 2 menciona (cuentas y permisos, guía en PDF) y que el MVP aún no guarda.
- Corregido: en el MVP `ordenes.sku` no está declarada como clave externa hacia `inventario`; en el modelo nuevo sí lo es (`ORDEN_ITEM.sku` → `EQUIPO.sku`).
- Corregido: `CAMBIO` tiene dos claves externas hacia `EQUIPO` (`sku_original` y `sku_nuevo`); se dejó explícito en la tabla de cardinalidad.
- Corregido: `pdf_url` y `motivo` quedaron como opcionales y cada uno tiene un ejemplo con el campo vacío, para no declarar obligatorio algo que queda vacío.

**Cómo se verificó.** Se comparó cada campo con las columnas reales de `src/app.py`. Se revisó fila por fila que los ejemplos no dejen vacío ningún campo obligatorio ni mezclen tipos. Se comprobó que cada clave externa de los ejemplos apunta a un registro que existe (por ejemplo, `id_usuario` 2 existe en `USUARIO`).

---

## Encargo 3. Dejar los Avances 1 y 2 en docs/unidad1 y registrar el encargo

**Objetivo.** Dejar en `docs/unidad1` los PDF de los Avances 1 y 2 con nombres claros (`Avance_1_grupo_6.pdf`, `Avance_2_grupo_6.pdf`), reemplazando el Avance 2 si en la carpeta de entregables había una versión más nueva, y agregar esta misma entrada a la bitácora.

**Instrucción entregada.**
- Contexto: entregables en PDF ubicados en `C:\Users\basti\OneDrive\Documentos\Usach\Apuntes clases\IA\ENTREGABLES`; ya existía `docs/unidad1/Avance_2_grupo_6.pdf` y `docs/bitacora-ia/bitacora.md` con dos encargos previos.
- Intención: copiar ambos avances con nombre claro y, si el Avance 2 de ENTREGABLES era más nuevo, reemplazar el del repo.
- Restricciones: abrir cada PDF antes de copiarlo y confirmar en la portada que dice "AVANCE 1" o "AVANCE 2"; si un archivo no calza, no copiarlo y avisar; si falta un archivo, no inventarlo ni sustituirlo por otro; no modificar el contenido de los PDF; no tocar `main` ni `dev`, ni archivos fuera de `docs/` sin preguntar; un solo commit.
- Verificación pedida: mostrar `git status` y `git diff --stat` antes de comprometer, listar el contenido final de `docs/unidad1` y confirmar que ninguna carpeta de `docs` quedara vacía.

**Respuesta obtenida.** El agente revisó la carpeta ENTREGABLES y encontró un único archivo, `ENTREGA 1.pdf`. Al abrirlo, su portada decía "AVANCE 2 – PROYECTO GRUPAL" (no Avance 1, pese al nombre del archivo). Comparó su hash SHA-256 contra `docs/unidad1/Avance_2_grupo_6.pdf` y resultaron idénticos, así que no había una versión más nueva que copiar. No encontró ningún archivo con portada "AVANCE 1" en toda la carpeta ENTREGABLES.

**Qué se aceptó y qué se corrigió.**
- Aceptado: no copiar ni reemplazar nada en `docs/unidad1`, porque el único PDF disponible (pese a su nombre de archivo confuso) ya está presente en el repo de forma idéntica.
- Aceptado: no inventar ni sustituir el Avance 1 faltante; se avisó explícitamente que ese archivo no está en ENTREGABLES y queda pendiente de que el usuario lo agregue.
- Nota: el agente detectó una carpeta sin seguimiento (`Automatizacion_bodega/`) fuera de `docs/` y no la modificó, conforme a la restricción de no tocar archivos fuera de `docs/` sin preguntar.

**Cómo se verificó.** Se leyó el contenido de `ENTREGA 1.pdf` para confirmar el título real de la portada. Se calculó y comparó el hash SHA-256 de `ENTREGA 1.pdf` y `docs/unidad1/Avance_2_grupo_6.pdf`, que coincidieron exactamente. Se listó el contenido de `docs/unidad1` y `docs/bitacora-ia` antes y después del encargo para confirmar que no quedó ninguna carpeta vacía.

---

## Encargo 4. Corregir el nombre del Avance 1/2 tras aviso del usuario

**Objetivo.** Corregir el nombre de archivo en `docs/unidad1` después de que el usuario aclarara que el PDF entregado corresponde al Avance 1, no al Avance 2, pese a que la portada del documento dice "AVANCE 2".

**Instrucción entregada.** El usuario indicó que el archivo con portada "AVANCE 2" es en realidad la primera entrega (Avance 1): el grupo se equivocó al titular el documento, pero el nombre de archivo original en su carpeta ("ENTREGA 1") es el correcto.

**Respuesta obtenida.** El agente señaló la contradicción con la portada del PDF antes de actuar (ver Encargo 3) y pidió confirmación explícita, explicando la implicancia: el archivo ya commiteado como `Avance_2_grupo_6.pdf` pasaría a llamarse `Avance_1_grupo_6.pdf`, y `docs/unidad1` quedaría sin un Avance 2 real hasta que se entregue ese documento. El usuario confirmó la corrección.

**Qué se aceptó y qué se corrigió.**
- Aceptado: renombrar `docs/unidad1/Avance_2_grupo_6.pdf` a `docs/unidad1/Avance_1_grupo_6.pdf` con `git mv`, sin alterar el contenido del PDF, para preservar el historial del archivo.
- Pendiente: `docs/unidad1` queda sin el PDF del Avance 2 real; falta que el usuario lo entregue para agregarlo.

**Cómo se verificó.** Se usó `git mv` (no copia ni borrado manual) para que git registre el cambio como renombre y conserve el historial. Se revisó `git status` para confirmar que solo aparece el renombre y ningún otro cambio de contenido.

---

## Encargo 5. Incorporar el Avance 3 al repositorio y mejorar el README y el diagrama de datos

**Objetivo.** Subir el PDF del Avance 3 a `docs/unidad1`, reescribir el README con la sección "README inicial" del documento y con el trabajo real del repositorio, reemplazar el diagrama de la base de datos por el del Avance 3 y agregar su imagen al repositorio.

**Instrucción entregada.**
- Contexto: el entregable del Avance 3 está en la carpeta ENTREGABLES (PDF y Word, con la misma versión). El README actual dice que hay dos avances y tiene fecha del 2 de octubre; `docs/datos/estructura_datos.md` tiene un modelo de seis tablas que no coincide con el del documento.
- Intención: que el repositorio refleje lo que el grupo entregó en el Avance 3, sin cambiar el código.
- Restricciones: no cuestionar la numeración del entregable; revisar el análisis antes de subir; confirmar cuando todo esté en GitHub.

**Respuesta obtenida.** El agente extrajo las imágenes incrustadas en el Word: el escudo de la universidad y el diagrama de la base de datos. Propuso reemplazar el modelo de seis tablas por el de siete tablas del documento (CLIENTES, USUARIOS, ORDENES, EQUIPOS, DETALLE_ORDEN, GUIAS, REGISTRO_CAMBIOS), con sus relaciones, cardinalidad, decisiones de diseño y ejemplos. Reescribió el README con la solución, los usuarios, la instalación, el estado al 4 de octubre, los roles del equipo y el flujo de trabajo.

**Qué se aceptó y qué se corrigió.**
- Aceptado: usar el modelo de siete tablas del Avance 3 en lugar del de seis tablas del Encargo 2, porque es el que presentó el grupo.
- Aceptado: escribir los comandos de instalación con `py -m` (como en el documento) y no con `pip` ni `python` directos, porque en este equipo el comando `python` no resuelve a una instalación real (alias de la Microsoft Store).
- Corregido: no subir `image1.png` (el escudo de la universidad), porque no aporta al repositorio. Solo se sube el diagrama de la base de datos.
- Corregido: el README dice que la base tiene 10 equipos de ejemplo y que las vistas son Carga masiva, Validador y Ajuste de última hora; se comprobó contra `src/app.py` antes de dejarlo.
- Pendiente de revisar: el modelo del Avance 3 no coincide con las tablas que hoy crea el MVP en `src/app.py` (`inventario`, `ordenes`, `log_cambios`). El documento lo deja explícito como diseño objetivo, no como estado actual del código.

**Cómo se verificó.** Se comparó el PDF copiado con el original mediante hash SHA-256. Se confirmó en la portada que el PDF dice "AVANCE 3". Se revisó en `src/app.py` el nombre de las vistas, el seed de 10 equipos, la variable `BODEGA_DB_PATH` y el límite de 50 SKU. Se revisó el diff antes del commit. No se volvieron a ejecutar los tests en esta entrada: la cifra de 18 tests viene de la verificación del Encargo 1. El diagrama Mermaid se revisó a mano; no se renderizó localmente.
