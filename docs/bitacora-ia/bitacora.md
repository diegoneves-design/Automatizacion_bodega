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

---

## Encargo 6. Corregir el nombre del Avance 2

**Objetivo.** Dejar en `docs/unidad1` el PDF con portada "AVANCE 2" con el nombre `Avance_2_grupo_6.pdf`, y dejar el repositorio ordenado (`dev` al día, README y carpetas de la Entrega 4) antes de empezar la Entrega 4.

**Instrucción entregada.**
- Contexto: el 2026-10-09 se pidió un diagnóstico de solo lectura. Este encontró que `Avance_1_grupo_6.pdf` tiene portada "AVANCE 2" y que el nombre venía del Encargo 4. El usuario aclaró que el documento es el Avance 2 y que se había llamado "1" por error.
- Intención: renombrar el archivo con `git mv`, corregir el README y crear las carpetas `docs/historias-usuario` y `docs/wireframes`, trabajando directo en `dev`, con un commit por tema y sin abrir ni fusionar el pull request.
- Restricciones: sin `force`, `reset` ni `rebase`; sin borrar ramas ni la etiqueta `v1.0`; sin tocar código, `bodega.db` ni `.env`; no editar los encargos anteriores; detenerse ante cualquier aviso inesperado de git.

**Respuesta obtenida.** El agente actualizó la vista del remoto (`git fetch --all --tags --prune`) y comprobó que `origin/main` ya tenía `src/` y `docs/`, que `origin/dev` estaba 8 commits atrás sin commits propios y que `feature/estructura-entrega` ya estaba contenida en `main`. Propuso un plan en pasos, el usuario lo aprobó con ajustes y el agente lo ejecutó: avance rápido de `dev` hasta `origin/main`, renombre del PDF, esta entrada, ajuste del README y creación de las dos carpetas.

**Qué se aceptó y qué se corrigió.**
- Corregido: el Encargo 4 renombró el archivo a Avance 1 por una indicación del usuario. Esta entrada lo revierte. El Encargo 4 se deja tal cual como parte del historial.
- Aceptado: dejar `docs/unidad1` con los Avances 2 y 3. No hay Avance 1 en el repositorio.
- Aceptado: no editar los Encargos 3 y 4, aunque hablen de "Avance 1", para no reescribir lo que pasó.
- Nota de proceso: los pull requests #3 y #4 se fusionaron de `feature/estructura-entrega` a `main` sin pasar por `dev` y sin revisor. Eso no cumple el flujo del README. El pull request `dev` → `main` de este encargo es el que se hará con revisión de otra persona.

**Cómo se verificó.** Se renombró con `git mv`, y `git status` mostró un renombre sin otros cambios en el archivo. El hash SHA-256 del PDF antes y después del renombre es el mismo (`79cec99b…b40a4`). Se listó `docs/unidad1`: queda con `Avance_2_grupo_6.pdf` y `Avance_3_grupo_6.pdf`. Antes de actualizar `dev` se comprobó que no tenía commits que no estuvieran en `main` (`git rev-list --left-right --count`: 8 atrás, 0 adelante) y el avance se hizo con `--ff-only`. No se ejecutaron tests: no se cambió código.

---

## Encargo 7. Simular una entrevista a un jefe de bodega para ensayar las preguntas

**Objetivo.** Ensayar la entrevista de la Entrega 4 con una persona simulada (jefe de bodega, y también mantenimiento y despachador), para afinar las preguntas y saber qué confirmar antes de hablar con una persona real.

**Instrucción entregada.**
- Contexto: el caso del Avance 2 (emisión automática de guía de despacho o retiro en una empresa de arriendo de equipos) y las cinco preguntas base de la pauta de entrevista.
- Intención: obtener un ensayo con preguntas, temas y condiciones de uso en celular. No una entrevista real.
- Herramienta: una skill de Claude que simula a un jefe de bodega y a su entorno (`entrevistado-bodega-guias`).
- Restricciones: dejar claro en cada nota que los personajes, las cifras y las anécdotas son inventados y que no se pueden citar como testimonio.

**Respuesta obtenida.** Dos notas de ensayo, guardadas fuera del repositorio: una "entrevista completa" (bloques de preguntas, mapa de áreas, guion de 15 minutos y hoja de notas) y una "entrevista profunda" (casos de sistemas anteriores, síntesis y riesgos). Ambas traen personajes ficticios, cifras y anécdotas inventadas.

**Qué se aceptó y qué se corrigió.**
- Aceptado: la estructura de preguntas (guion de 10 preguntas y reglas del entrevistador) y los temas por explorar (formato del listado, doble control, cambios de último minuto, uso en celular, accesorios sin código).
- Descartado: las cifras y las anécdotas inventadas (tiempos por guía, frecuencias, costos, casos de sistemas anteriores, nombres). No se usan como evidencia y no se copian al repositorio.
- Corregido: todo lo que se deriva del ensayo queda marcado como "hipótesis por validar con la entrevista real". La entrevista real todavía no se ha hecho.

**Cómo se verificó.** Se contrastó el ensayo con el documento del Avance 2 y con `src/app.py` (revisión hecha el 2026-10-10, al preparar la Entrega 4):
- Calza con el Avance 2: la digitación manual, el doble control físico, el reemplazo de equipos a último minuto y el bloqueo de la emisión cuando un SKU no coincide.
- No está en el Avance 2 ni en el código, y por eso queda como hipótesis: accesorios sin SKU, estados del equipo más allá de la disponibilidad, foto de la carga y el uso del celular en terreno.
- Falta aclarar un término: la app usa `Convencional`/`Alternativo` (despacho) y `Preventivo`/`Por falla` (retiro) como modalidades, mientras que el modelo de datos usa `normal`/`falla` como motivo. Se pregunta en la entrevista real.

---

## Encargo 8. Borrador de historias de usuario y criterios de aceptación

**Objetivo.** Dejar en `docs/historias-usuario/historias_usuario.md` las historias H01 a H07 con prioridad, criterios de aceptación y revisión INVEST, y las historias candidatas H08 a H15 aparte, sin validar. Además, dejar un borrador del mapa de recorrido en `docs/recorrido-usuario/mapa_recorrido.md`.

**Instrucción entregada.**
- Contexto: la nota de reparto de la Entrega 4 (borrador del grupo con H01 a H07, su prioridad sugerida y sus criterios) y las notas del ensayo del Encargo 7.
- Intención: pasar el borrador a Markdown, ordenarlo por prioridad y agregar la revisión INVEST.
- Restricciones: sin cifras ni anécdotas del ensayo; las candidatas H08 a H15 solo en formato Como / Quiero / Para; estado "Borrador"; no decir que la entrevista real se hizo.

**Respuesta obtenida.** El agente transcribió las siete historias en el orden de prioridad H01, H02, H04, H03, H05, H07, H06, con criterios principal y alternativo en formato Dado / Cuando / Entonces, una revisión INVEST por historia y una línea "En el MVP hoy" que compara cada una con `src/app.py`. Las candidatas H08 a H15 quedaron en una sección aparte. El mapa de recorrido se armó con las etapas del ensayo, con el aviso de que se reemplazará con la entrevista real.

**Qué se aceptó y qué se corrigió.**
- Aceptado: el formato Como / Quiero / Para, la priorización del borrador y los criterios principal y alternativo.
- Corregido: las candidatas H08 a H15 quedan sin prioridad y sin criterios hasta validarlas con la entrevista real.
- Corregido: la revisión INVEST muestra dependencias que el borrador no decía: H04 depende de H02, H06 depende de H05 y H07 depende de H02 y de las cuentas y permisos, que están pendientes.
- Pendiente: la nota de reparto dice que la profesora pidió que las historias las escriba el equipo y no la IA. Este documento es un borrador transcrito y redactado con ayuda de IA: el grupo debe revisarlo, corregirlo y adoptarlo antes de entregarlo.

**Cómo se verificó.** Se revisó cada historia con las seis letras de INVEST, indicando por qué cumple o no. Se contrastó cada historia con el caso de uso del Avance 2 (seleccionar la orden, destacar los cambios, validar, bloquear si un SKU no coincide, generar la guía) y con `src/app.py`: varias conductas que piden los criterios (bloqueo de la orden, número de guía, PDF, filtro del historial por orden, cuentas y permisos) no existen todavía y quedaron anotadas en "En el MVP hoy". No se ejecutaron tests: no se tocó código.

---

## Encargo 9. Especificación en texto de cuatro pantallas para celular

**Objetivo.** Dejar en `docs/wireframes/README.md` la especificación en texto de cuatro pantallas (W1 a W4) pensadas para celular, mientras el Grupo B termina los wireframes en Figma.

**Instrucción entregada.**
- Contexto: la tabla de pantallas de la nota de reparto (W1 Carga masiva, W2 Validador, W3 Ajuste de última hora, W4 Guía emitida) y las historias del Encargo 8.
- Intención: describir, por pantalla, objetivo, elementos, datos, navegación, anotaciones y requisitos de uso en celular (formato vertical de 360 x 800).
- Restricciones: no inventar imágenes; no agregar campos ni pantallas que no estén en la tabla; marcar como hipótesis los requisitos que salen del ensayo.

**Respuesta obtenida.** Una especificación en texto de W1 Carga del listado (H01), W2 Validación (H02, H03, H07), W3 Ajuste de último minuto (H05, H06) y W4 Guía emitida (H04), con la navegación entre ellas y los requisitos de uso en celular (botones grandes, alto contraste, pocos pasos y aviso de qué quedó guardado si se pierde la señal).

**Qué se aceptó y qué se corrigió.**
- Aceptado: la estructura por pantalla y la navegación W1 → W2 → W4, con W3 como desvío desde W2.
- Corregido: el campo "Motivo" de W3 no estaba en la tabla de la nota de reparto, pero sí está en la app y en el modelo de datos, como campo opcional; se dejó con esa aclaración.
- Corregido: los requisitos de uso en celular salen del ensayo y quedan marcados como hipótesis.
- Pendiente: los PNG de Figma (Grupo B) y la validación de las pantallas con la entrevista real.

**Cómo se verificó.** Se comprobó que cada pantalla enlaza con al menos una historia y que las siete historias H01 a H07 quedan cubiertas por alguna pantalla. Se comparó la navegación con la tabla de la nota de reparto y los datos de cada pantalla con `src/app.py` y con `docs/datos/estructura_datos.md`. No se generaron ni verificaron imágenes.
