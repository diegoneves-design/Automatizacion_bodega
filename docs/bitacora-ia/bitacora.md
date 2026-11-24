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

---

## Encargo 10. Pauta de la conversación con el usuario

Encargos 10 a 13 hechos por Oscar Ynchaustegui el 2026-10-10, con Claude, a partir de las instrucciones oficiales del Avance 4.

**Objetivo.** Preparar una pauta corta para la conversación con una persona que hoy realiza la tarea del flujo principal, como pide el Avance 4.

**Instrucción entregada.**
- Contexto: las instrucciones oficiales del Avance 4 (una conversación de unos 15 minutos con una sola persona) y el caso del Avance 2. El entrevistado es Oscar, subjefe de bodega en la empresa del caso y a cargo de la bodega durante 4 meses en total.
- Intención: un documento Word con preguntas y espacio para responder, centrado en el flujo principal (recibir el listado, validar, emitir la guía y los cambios de último minuto).
- Restricciones: preguntas por casos concretos, no por opiniones generales; nada inventado; las dudas abiertas del proyecto (modalidad, máximo de SKU, prefijos) en una sección aparte.

**Respuesta obtenida.** Una pauta de 15 preguntas en cinco bloques, cinco dudas del proyecto y una pregunta de cierre por los 2 o 3 problemas principales.

**Qué se aceptó y qué se corrigió.**
- Aceptado: los bloques y las preguntas por casos concretos ("cuéntame la última vez que…").
- Corregido: el agente sugirió primero conversar con otra persona de la bodega; como Oscar realiza la tarea (subjefe y a cargo de la bodega 4 meses en total), se decidió que él fuera el entrevistado y que en `historias.md` se declare que es integrante del equipo.
- Descartado: la entrevista simulada del Encargo 7 no se usó como fuente; solo su lista "Qué confirmar con una persona real" sirvió para elegir preguntas.

**Cómo se verificó.** Se comparó la pauta con lo que pide el Avance 4: cargo (no nombre), fecha y 2 o 3 problemas con palabras del usuario. Se revisó que cada pregunta apunte al flujo principal.

---

## Encargo 11. Corrección de redacción de las respuestas

**Objetivo.** Corregir la ortografía y la redacción de las respuestas de Oscar sin cambiar su contenido.

**Instrucción entregada.**
- Contexto: el Word de la pauta respondido por Oscar, escrito rápido y con errores de tipeo.
- Intención: dejar las respuestas legibles para usarlas en las historias.
- Restricciones: mantener la forma de hablar de Oscar en las frases que sirven como cita; no agregar información; marcar las dudas en vez de inventar.

**Respuesta obtenida.** El Word con las respuestas corregidas y divididas en párrafos, y la conversación en Markdown (`docs/entrevistas/entrevista_subjefe_bodega.md`).

**Qué se aceptó y qué se corrigió.**
- Aceptado: la ortografía, los tildes, la puntuación y la división en párrafos.
- Aceptado: se mantuvieron expresiones como "harta pega", "pistolear" y "buscar como locos".
- Revisado con Oscar: en la pregunta 8 el agente agregó que la guía se emite en el ERP y se sube al SII, dato tomado de las respuestas 1 y D5; en la pregunta 13 interpretó "no lo notifico" como "no lo informo", y Oscar lo corrigió: los cambios no dejan ninguna huella, porque el ERP no registra quién corrigió la guía.

**Cómo se verificó.** Oscar revisa cada respuesta corregida contra su original, antes de subirla, para confirmar que dice lo mismo.

---

## Encargo 12. Historias de usuario a partir de la conversación

**Objetivo.** Escribir `docs/historias.md` según la plantilla del Avance 4: conversación, flujo principal, 3 a 5 historias y los criterios de la historia principal.

**Instrucción entregada.**
- Contexto: las respuestas de Oscar, el borrador de historias H01 a H07 del Encargo 8 y el caso de uso del Avance 2.
- Intención: ajustar el borrador del grupo con evidencia real, en lugar de partir de cero.
- Restricciones: entre 3 y 5 historias numeradas HU-01…; cargo concreto, acción de la persona y beneficio; un escenario principal y uno alternativo solo para la historia principal, con un "entonces" que describa lo que se ve en pantalla.

**Respuesta obtenida.** Cinco historias: HU-01 validar el pedido (principal), HU-02 cargar el listado del PV, HU-03 registrar un cambio de último minuto, HU-04 ver los cambios destacados y HU-05 dejar lista la guía.

**Qué se aceptó y qué se corrigió.**
- Corregido: el agente propuso primero que la historia principal fuera registrar los cambios de último minuto (el dolor número uno de la conversación). Se mantuvo validar el pedido, porque la profesora define el flujo principal como el escenario principal del caso de uso del Avance 2, y los cambios son una extensión.
- Corregido respecto del Encargo 8: el listado lo envía comercial (no mantenimiento); los cambios los hacen tres áreas; el máximo es de 60 productos; la guía oficial sale del ERP.
- Descartado: H06, H07 y las candidatas H08 a H15, para quedar en 5 historias del flujo principal.
- Pendiente: los accesorios genéricos, que la conversación sí respalda, quedan para una historia futura.

**Cómo se verificó.** Se revisó cada historia contra los errores frecuentes del Avance 4 (rol genérico, beneficio circular, tarea técnica, "entonces" interno) y cada cita contra las respuestas de Oscar.

---

## Encargo 13. Wireframes del flujo principal

**Objetivo.** Dibujar los wireframes del flujo principal con las cuatro notas por pantalla y dejarlos en `docs/wireframes/`.

**Instrucción entregada.**
- Contexto: `docs/historias.md` y `docs/datos/estructura_datos.md`.
- Intención: entre 3 y 5 pantallas en baja fidelidad, cada una con de qué historia viene, qué datos muestra, qué parte del criterio se ve y a dónde lleva cada botón.
- Restricciones: solo pantallas que alguna historia pida; nombres de datos iguales a los de la estructura de datos; los dos escenarios de la HU-01 dibujados.

**Respuesta obtenida.** Seis imágenes PNG: el flujo completo y las pantallas P1 Cargar pedido, P2a Validación (todo correcto), P2b Validación (con error), P3 Registrar cambio y P4 Guía lista, con un `README.md` que las muestra.

**Qué se aceptó y qué se corrigió.**
- Aceptado: las cinco pantallas y la navegación P1 → P2 → P4, con P3 como desvío desde P2.
- Corregido: en una primera versión, la misma extensión (`SD-63A20-0314`) aparecía en dos órdenes distintas, justo el error que contó Oscar; se cambiaron los SKU de la orden 3002.
- Corregido: los wireframes de texto del Encargo 9 (W1 a W4) quedan reemplazados por estas imágenes.

**Cómo se verificó.** Se revisó que cada pantalla tenga sus cuatro notas, que cada historia HU-01 a HU-05 aparezca en al menos una pantalla, que los nombres de los campos existan en `estructura_datos.md` y que lo que dice el "entonces" de los dos escenarios de la HU-01 esté dibujado en P2a y P2b.

---

## Encargo 14. Análisis ético del prototipo (Avance 5, Parte B)

Hecho por Oscar Ynchaustegui el 2026-11-01, con Claude.

**Objetivo.** Escribir `docs/etica.md` con las cuatro piezas de la Parte B del Avance 5 (mapa de exclusión, ficha de datos, accesibilidad y riesgos) y documentar la modificación del prototipo que motivó el análisis.

**Instrucción entregada.**
- Contexto: las instrucciones del Avance 5, el prototipo en `prototipo/` y `docs/prototipo.md`, la conversación con el subjefe de bodega (`docs/entrevistas/`), `docs/datos/estructura_datos.md` y el ejercicio de clase "¿quién queda fuera?".
- Intención: un análisis referido a este prototipo, con personas, campos y pantallas concretas, no afirmaciones genéricas.
- Restricciones: cada campo de la ficha debe existir en el formulario del prototipo y en la estructura de datos; los valores de contraste se toman de la medición ya hecha por el equipo; lo que no aplica (IA, ordenamiento) se declara con justificación; no inventar plazos legales.

**Respuesta obtenida.** `docs/etica.md` con la tabla de tres actores (el excluido es el bodeguero de terreno sin cuenta que anota en papel), una ficha de 11 filas, la revisión de accesibilidad de P1 a P4, tres prácticas de uso eficiente y cinco riesgos con tratamiento, responsable y fecha de revisión, más las capturas de antes y después del borde de las tarjetas.

**Qué se aceptó y qué se corrigió.**
- Aceptado: el actor excluido sale de la conversación (preguntas 3, 14 y 15), no de un supuesto.
- Aceptado: declarar "no aplica" para IA y ordenamiento, con su razón.
- Corregido: el agente revisó el código y encontró que el campo Cliente de solo lectura tiene fondo gris, así que su borde mide aún menos que 1,59:1; se dejó como riesgo pendiente con responsable.
- Corregido: el plazo de conservación queda como propuesta por confirmar con administración, en lugar de citar un plazo legal sin verificarlo.
- Pendiente: los responsables de los riesgos 3 a 5 son una propuesta; los integrantes deben confirmarlos al revisar el pull request.

**Cómo se verificó.** Cada campo de la ficha se buscó en `prototipo/js/app.js` (etiquetas de P1 y P3) y en `estructura_datos.md`. Los contrastes se compararon con la tabla de `docs/prototipo.md` y con las variables de `prototipo/css/estilos.css`. Las rutas de las capturas se comprobaron contra `docs/img/etica/`.

---

## Encargo 15. Corregir los ejemplos de la estructura de datos según la revisión del Avance 3

Preparado el 2026-11-01 con Claude a partir de la retroalimentación de la profesora; revisado y subido por Sebastián Carmona, con revisión de Oscar Ynchaustegui en el pull request.

**Objetivo.** Corregir en `docs/datos/estructura_datos.md` los cuatro problemas que señaló la revisión del Avance 3 (punto 6) y que la verificación del Encargo 2 no detectó, porque revisaba el modelo anterior de seis tablas.

**Instrucción entregada.**
- Contexto: la retroalimentación de la profesora, el modelo de siete tablas vigente y la conversación con el subjefe de bodega (`docs/entrevistas/`).
- Intención: que todas las tablas de ejemplo cuenten la misma historia y que las reglas sigan al negocio, no a los ejemplos.
- Restricciones: no cambiar las tablas ni las relaciones del diagrama salvo lo necesario; mantener los campos que ya usan el prototipo y los wireframes; cada clave externa debe apuntar a un registro que exista.

**Respuesta obtenida.** Ejemplos rehechos como una sola mañana de bodega (órdenes 3001, 3002 y 3003), `motivo` reemplazado por `motivo_alternativo` (obligatorio solo si la modalidad es alternativa), `motivo_cambio` obligatorio, estado y ubicación de los equipos actualizados después de cada guía, y el diagrama regenerado.

**Qué se aceptó y qué se corrigió.**
- Aceptado: la orden 3003 y los equipos 503, 504, 505 y 507 se agregan a sus tablas, en lugar de borrar las filas que los usaban.
- Aceptado: `modalidad` aplica a despacho y retiro, porque la conversación (pregunta D1) dice que "alternativo" es el cambio por mantención o falla en ambos.
- Corregido respecto del Avance 3: `motivo_cambio` deja de ser opcional. Antes se había dejado opcional para que un ejemplo vacío no incumpliera la regla; ahora el ejemplo se ajusta a la regla.
- Pendiente: el prototipo todavía ofrece "Sin motivo" en P3 (riesgo 3 de `docs/etica.md`) y `docs/prototipo.md` todavía menciona `ORDENES.motivo`.

**Cómo se verificó.** Un script recorrió las tablas de ejemplo y comprobó que cada `id_cliente`, `id_usuario`, `id_orden` e `id_equipo` usado como clave externa existe en su tabla, y que ningún cambio tiene el motivo vacío: cero errores. Se revisó a mano que cada cambio ocurra antes de la guía de su orden y que el estado final de cada equipo calce con las guías emitidas. El diagrama se regeneró desde el bloque Mermaid y se revisó la imagen.

---

## Encargo 16. Revisar el Avance 5 en main y dejar coherentes los documentos

Hecho por Diego Neves el 2026-11-01, con Claude, en la rama `feature/coherencia-avance5`, que sale de `main` actualizado.

**Objetivo.** Revisar `main` contra las instrucciones del Avance 5 sin modificar nada y, a partir de esa revisión, corregir las inconsistencias entre `docs/prototipo.md`, `docs/datos/estructura_datos.md`, el README y la aplicación.

**Instrucción entregada.**
- Contexto: `main` con los PR del Avance 5 (#14 a #18) y la corrección de la estructura de datos (#20); las instrucciones del Avance 5 (README, `docs/prototipo.md`, prototipo, `docs/etica.md`).
- Intención: primero un diagnóstico de solo lectura (qué cumple, qué falta, qué archivos sobran y qué PR aprobó cada integrante); después, corregir solo lo pedido, punto por punto.
- Restricciones: un commit por punto, con mensaje en español; mostrar el cambio y esperar aprobación antes de cada commit; confirmar que ninguna captura se enlaza antes de borrarla; no editar el Encargo 15; no corregir la app en este PR; no hacer push sin preguntar.

**Respuesta obtenida.**
- Diagnóstico: el Avance 5 cumple casi todo. Faltas: los PR #14 a #17 se fusionaron sin aprobación de otro integrante; `prototipo.md` quedó desactualizado después del PR #20; el README seguía en el Avance 4 y describía un flujo con `dev` que no se usa; había 4 capturas de ética que no enlaza ningún archivo.
- Cuatro commits:
  1. `docs/prototipo.md`: el equipo en mantención del modelo es `SD-63A20-0316`, no `SD-63A20-0315`, y el campo se llama `ORDENES.motivo_alternativo`. Esto resuelve la nota pendiente del Encargo 15 sobre `ORDENES.motivo`.
  2. README: estado al Avance 5, carpeta `prototipo/` en el árbol, y flujo de trabajo con ramas `feature/<tema>` desde `main` y pull request aprobado por otro integrante.
  3. Eliminación de `antes/despues-p2-3001-360.png` y `antes/despues-p2-3002-1280.png`, que aplica la práctica de sostenibilidad 2 de `etica.md`.
  4. README: "Qué vas a ver" y la prueba guiada pasan a la interfaz actual de cinco vistas (Órdenes, Carga masiva, Validador, Ajuste de última hora, Historial).
- Revisión de esta bitácora: la ética está registrada (Encargo 14); el prototipo de los PR #14 a #17 no tiene entrada.

**Qué se aceptó y qué se corrigió.**
- Aceptado: quitar de "Pendiente" el bloqueo de la guía cuando un SKU no valida, porque la app ya lo hace (`src/views/validacion.py`, botón *Emitir guía* desactivado).
- Aceptado: dejar como pendientes de la app el límite de 60 SKU (`MAX_SKUS` sigue en 50) y destacar los cambios en el validador (HU-04).
- Corregido: el agente intentó hacer el commit del punto 2 y preparar el borrado del punto 3 en un solo paso; se rechazó y se pidió un paso a la vez.
- Corregido: el mensaje del commit del punto 3 se cambió para citar la práctica de sostenibilidad que lo motiva.
- Corregido: se agregó a la prueba guiada la nota de borrar `bodega.db` antes de empezar, porque la app no rechaza un folio repetido.
- Pendiente (Bastián Vargas, app): al cargar un folio que ya existe, la app agrega los SKU nuevos a la orden antigua, y el mensaje dice "cargada con 5 SKU" aunque la orden quede con 10.
- Pendiente (Bastián Vargas, app): la carga acepta SKU con una coma al final (por ejemplo `EXC-001,`) y no reconoce el equipo.
- Pendiente (Bastián Vargas): registrar en esta bitácora el uso de IA en el prototipo (PR #14 a #17), si lo hubo.
- Revisado: el agente marcó que los riesgos de `etica.md` tienen hitos ("Semana 7", "Próximo avance") y no fechas. Se confirmó que los riesgos indican la oportunidad de revisión que pide la pauta; no requiere cambio.

**Cómo se verificó.**
- El diagnóstico se hizo leyendo los archivos de `main` y el código del prototipo (`prototipo/js/app.js` y `datos.js`). Los autores y las aprobaciones de los PR se consultaron en la API pública de GitHub.
- Antes de borrar las capturas se buscaron sus nombres en todo el repositorio: solo `docs/etica.md` enlaza capturas de ética, y no usa ninguna de las cuatro borradas.
- La prueba guiada nueva se escribió leyendo `src/views/` y `src/app.py` (nombres de menús, campos, botones, mensajes e inventario inicial).
- Diego ejecutó la app con la base limpia y siguió la prueba guiada paso a paso: los nombres de menús, campos y botones coinciden con la interfaz. Funcionaron la carga, la validación con `MON-050` sin stock, *Corregir SKU*, *Guardar cambio*, la emisión y descarga de la guía, y el Historial con fecha, responsable y motivo.
- Cada commit se revisó en el diff antes de aprobarlo. No se ejecutaron tests: no se cambió código.

---

## Encargo 17. Diseño de la prueba de usuarios y pauta de validación (Avance 6)

Lo hizo Oscar Ynchaustegui el 2026-11-05, con Claude. Lo revisa Sebastián Carmona en el pull request.

**Objetivo.** Armar `docs/prueba-usuarios.md` (objetivo e hipótesis, tareas con umbral, perfiles y plan de registro) y `docs/pauta-validacion.md` (el guion de cada sesión, en no más de dos planas y 20 minutos), siguiendo las instrucciones del Avance 6.

**Instrucción entregada.**
- Contexto. Las instrucciones del Avance 6, el prototipo y `docs/prototipo.md` con sus órdenes de ejemplo 3001 y 3002, `docs/historias.md`, el mapa de exclusión de `docs/etica.md` y la conversación con el subjefe de bodega.
- Intención. Que la prueba pueda demostrar que estamos equivocados, con una hipótesis que pueda fallar y umbrales con número fijados antes de ver a nadie.
- Restricciones. Para la prueba solo estamos disponibles dos integrantes. Ninguna tarea puede nombrar botones ni pantallas, las preguntas de contexto tienen que ser sobre cosas que ya pasaron, no puede quedar ningún nombre ni contacto de participantes en el repositorio y la sesión completa no puede pasar de 20 minutos.

**Respuesta obtenida.** Dos tareas (T1, un despacho sin problemas, y T2, un retiro con un código que no existe), cada una con su umbral, y un SUS esperado de 68 o más. Dos hipótesis, una sobre el flujo principal y otra sobre si de verdad dejamos fuera al bodeguero de terreno. Dos perfiles de usuarios, incluido el excluido del Avance 5, y cuatro de stakeholders. Un reparto de roles para dos personas, la planilla vacía, la regla de decisión y la pauta de 20 minutos con su versión imprimible.

**Qué se aceptó y qué se corrigió.**
- Aceptado. Dos tareas en vez de tres, porque con tres la sesión pasaba de los 20 minutos.
- Aceptado. Una segunda hipótesis que pone a prueba lo que dijimos en el Avance 5. Si el bodeguero de terreno logra la tarea solo, nos equivocamos sobre quién queda fuera.
- Corregido. Como Oscar está a cargo de la bodega del caso, no facilita ni asiste a las sesiones con sus compañeros de trabajo, para que no se sientan evaluados por su jefe. Esas sesiones las facilita Sebastián, y Oscar las registra después, desde la grabación.
- Corregido. Oscar tiene un conocido que ve la bodega igual que él. Puede participar, pero solo como 1 de los 5 de U1, queda anotado como conocido y lo facilita Sebastián. Así evitamos armar una muestra que solo confirme lo que ya creemos.
- Corregido. Oscar pidió reescribir los dos documentos con un tono más cercano, en primera persona y con razones sacadas de la bodega real, sin cambiar la estructura, los umbrales ni los perfiles. Las frases del cuestionario SUS no se tocaron, porque es un instrumento estándar.
- Corregido. Oscar pasó la pauta a limpio en Word, con el encabezado de la universidad y su propia redacción del consentimiento. Su primera versión ocupaba 3 planas. Con Claude se dejó en 2 y se corrigieron detalles como el enlace del prototipo, la numeración de las tareas (4.1 y 4.2), algunas comas y tildes, y la frase "la ayudamos con un ¿Qué está pensando ahora?", que se cambió por "se le pregunta", porque esa pregunta no cuenta como ayuda. El `.md` se ajustó para que diga lo mismo que el PDF. También pidió sacar los dos puntos y los punto y coma de los textos, porque no es como escribimos nosotros.
- Hecho. El 2026-11-06 ensayamos la pauta completa, con Sebastián leyéndola en voz alta y Oscar como participante. Lo que salió del ensayo está en el Encargo 18.

**Cómo comprobamos que no hubiera sesgo.**
- Buscamos en los escenarios y en las preguntas de contexto y de cierre las palabras de la interfaz ("botón", "pantalla", "Cargar pedido", "Validar", "Preparar guía", "Registrar cambio", "rojo", "verde", "bloqueado", "no existe") y no aparece ninguna.
- Buscamos preguntas de opinión o sobre el futuro ("¿le gustó?", "¿usaría…?", "¿le parece…?") y no hay ninguna fuera del cuestionario SUS. El único "¿Está de acuerdo…?" está en el consentimiento, donde se pide permiso para grabar.
- Revisamos en el prototipo que las dos tareas se pueden terminar solo con lo que dice el escenario, la orden 3001 y la orden 3002 con la extensión `SD-63A20-0315` disponible.
- Sumamos los tiempos de la pauta (2 + 3 + 1 + 9 + 3 + 2 = 20 minutos) y generamos la versión imprimible, que ocupa 2 planas tamaño carta.

---

## Encargo 18. Ajustes a la pauta después del ensayo (Avance 6)

El ensayo lo hicimos Sebastián Carmona y Oscar Ynchaustegui el 2026-11-06. Oscar le pidió los ajustes a Claude, Sebastián los sube y Oscar los revisa en el pull request.

**Objetivo.** Corregir la pauta con lo que notamos al ensayarla, antes de la primera sesión con participantes.

**Instrucción entregada.**
- Contexto. La pauta del Encargo 17 y lo que pasó en el ensayo, con Sebastián como facilitador, Oscar como participante y el prototipo abierto en bodega-prototipo.vercel.app.
- Intención. Que las frases del cuestionario se entiendan cuando las lee otra persona y que la sesión pueda mostrar si el papel sigue siendo necesario, sin sugerirle nada al participante.
- Restricciones. Mantener el sentido y el orden de las frases del SUS, no agregar preguntas que lleven a una respuesta y mantener la pauta en 20 minutos y 2 planas.

**Lo que notamos en el ensayo.**
- A Oscar le pareció que las frases del SUS no están bien redactadas para leerlas en voz alta. Están escritas como si las dijera el participante ("Pensé que el sistema era fácil de usar"), y cuando las lee quien facilita pueden sonar como su propia opinión.
- Al hacer las tareas, Oscar notó que el prototipo no elimina el papel. En la bodega se seguiría anotando a mano lo que sale y vuelve, para después traspasarlo al sistema, igual que hoy.
- Como Oscar es del equipo y ya conocía el prototipo, sus respuestas y su SUS no se cuentan como resultado de la prueba.

**Respuesta obtenida.** Claude propuso dejar las frases del SUS igual, porque si se cambian el puntaje ya no se puede comparar con la meta de 68, y cambiar solo la forma de presentarlas. También propuso no mencionarle el papel al participante, sino observar si lo nombra solo en la pregunta de cierre que ya existe.

**Qué se aceptó y qué se corrigió.**
- Corregido. Oscar encontró más engorroso que quien facilita tenga que explicar que las frases se leen "como si las dijera usted", y prefirió cambiar la redacción de la tabla. Las diez frases quedaron en tercera persona (por ejemplo, "El sistema le pareció fácil de usar"), con el mismo sentido, el mismo orden y el mismo cálculo. Claude advirtió que así el SUS deja de ser el estándar al pie de la letra, por lo que la meta de 68 queda como referencia. Lo dejamos anotado en `docs/prueba-usuarios.md`.
- Corregido. A Oscar la frase 2 ("le pareció innecesariamente complejo") le parecía igual a la 3 ("le pareció fácil de usar"). Las dos se mantienen, porque el SUS alterna frases a favor y en contra para notar si alguien responde sin pensar, y el cálculo necesita las diez. Lo que cambió es que la 2 ahora dice más claro a qué se refiere, "El sistema tiene más pasos o cosas de las que hacen falta".
- Aceptado. En el cierre, quien registra anota si la persona habla del papel o de traspasar datos a mano sin que se lo preguntemos. Lo mismo quedó en el plan de `docs/prueba-usuarios.md`.
- Corregido. Oscar propuso que Sebastián le comentara al participante, como mejora futura, el uso de lector de código de barras. Lo dejamos fuera de la sesión, porque si se lo sugerimos lo más probable es que diga que sí y eso no nos dice nada.
- Idea a futuro, todavía sin probar. Registrar las salidas y devoluciones con lector de código de barras, "pistoleando" cada producto como en un supermercado, para no anotar en papel. Calza con el bodeguero de terreno que anota en papel (`docs/etica.md`), pero primero queremos ver si los participantes también hablan del papel.

**Cómo se verificó.**
- Comparamos una por una las diez frases nuevas con las del Encargo 17. Cada una dice lo mismo, en el mismo orden, y las impares siguen siendo positivas y las pares negativas, así que el cálculo del puntaje no cambia.
- Revisamos que la nota nueva del cierre no le dice nada al participante, solo a quien registra.
- Los tiempos de cada parte no cambiaron (20 minutos) y la versión imprimible sigue en 2 planas tamaño carta.

---

## Encargo 19. Atender la retroalimentación de los Avances 3 a 5 y revisar el Avance 6

**Objetivo.** Corregir lo que la profesora pidió en los Avances 4 y 5 y revisar `docs/prueba-usuarios.md` y `docs/pauta-validacion.md` contra las instrucciones del Avance 6.

**Instrucción entregada.**
- Contexto: las instrucciones del Avance 6, la retroalimentación de los Avances 3, 4 y 5, y los archivos `docs/historias.md`, `docs/etica.md`, `docs/prototipo.md` y `docs/pauta-validacion.md`.
- Intención: dejar HU-05 con una acción de la persona, pasar a `historias.md` los criterios de HU-02 a HU-05 que estaban como borrador, y proponer un plazo de conservación con número.
- Restricciones: no cambiar la prueba de usuarios ni sus umbrales; no tocar la aplicación Streamlit; no inventar datos de participantes.
- Verificación: decir qué cambió en cada archivo y qué no se pudo comprobar.

**Respuesta obtenida.** HU-05 reescrita como "preparar la guía solo con los productos validados"; criterios de HU-02 a HU-05 movidos de `prototipo.md` a `historias.md`; plazo de 24 meses desde la emisión de la guía en la ficha de `etica.md`. Además, una comparación del sitio publicado con `prototipo/`: el CSS de Vercel no tiene el borde de tarjetas corregido.

**Qué se aceptó y qué se corrigió.**
- Aceptado: los criterios de HU-02 a HU-05 tal como estaban en el borrador, con redacción mínima ("el jefe de bodega" explícito).
- Pendiente: los criterios los propuso la IA; la profesora pidió que los escriba el equipo, así que **el equipo debe revisarlos y aprobarlos** antes del pull request.
- Pendiente: el plazo de 24 meses es una propuesta, a confirmar con administración.
- No resuelto: volver a publicar el prototipo en Vercel requiere acceso del equipo a ese servicio.
- Ajuste posterior: con la prueba de concepto el prototipo queda conectado a Supabase, así que `docs/prueba-usuarios.md` ya no dice que "no está conectado a nada" y deja escrito que las sesiones son de una persona a la vez, con Reiniciar demo entre una y otra; `docs/pauta-validacion.md` lo agrega a la preparación. El PDF `pauta-validacion.pdf` no se regeneró y queda desactualizado en esa frase.

**Cómo se verificó.** Se comparó con `curl` cada archivo del sitio publicado con el del repositorio: `index.html`, `js/app.js` y `js/datos.js` coinciden; `css/estilos.css` no. Se revisó con `grep` que no queden referencias a "borrador" de HU-02 a HU-05 ni al texto antiguo de HU-05. No se imprimió ni se contó las planas del PDF de la pauta.

## Encargo 20. Corregir la modalidad y el motivo en el modelo de datos y dejarlo ejecutable

**Objetivo.** Responder a la retroalimentación del Avance 3 sobre la modalidad y el motivo obligatorios en toda orden, y dejar el modelo como esquema SQL que se pueda probar.

**Instrucción entregada.**
- Contexto: `docs/datos/estructura_datos.md`, la retroalimentación de la profesora, `CLAUDE.md` (despacho convencional o alternativo, retiro preventivo o por falla) y la conversación con el subjefe de bodega (preguntas 3 y D1).
- Intención: que `modalidad` aplique solo al despacho y el motivo solo al retiro, sin valores de relleno; que las claves externas del ejemplo existan; que el motivo del cambio sea obligatorio.
- Restricciones: no tocar la aplicación Streamlit; los ejemplos se ajustan a la regla, no al revés.
- Verificación: pruebas que fallen si una clave externa apunta a un registro que no existe o si una regla se rompe.

**Respuesta obtenida.** `modalidad` solo en despacho y `motivo_retiro` (antes `motivo_alternativo`) solo en retiro; ejemplos ajustados (3002 retiro por falla, 3003 retiro por mantención preventiva); `supabase/schema.sql` con las reglas como restricciones y `supabase/seed_ejemplo.sql`; `tests/test_modelo_datos.py`; diagrama regenerado con Mermaid.

**Qué se aceptó y qué se corrigió.**
- Ya estaban corregidos desde el Encargo 15 las claves externas rotas, el equipo 501 y el motivo del cambio obligatorio; solo faltaba la modalidad. Se convirtieron en restricciones de la base.
- La interpretación de que el retiro tiene solo los motivos falla y mantención preventiva es de la IA a partir de `CLAUDE.md` y de la pregunta 3. **Queda por validar con el jefe de bodega**, igual que si existe un retiro normal sin motivo.

**Cómo se verificó.** `pytest tests`: pasan las pruebas, incluidas las de `test_modelo_datos.py` (en SQLite). El diagrama se revisó a ojo contra el Mermaid.

---

## Encargo 21. Prueba de concepto del prototipo con Supabase

**Objetivo.** Conectar el prototipo a Supabase en lo mínimo (leer órdenes, validar SKU, registrar cambio y preparar guía) aplicando la validación en tres capas de la clase 7.

**Instrucción entregada.**
- Contexto: el prototipo (`prototipo/`), `supabase/schema.sql`, los apuntes de la clase 7 (CRUD, validación en tres capas, mensajes de error, estados de pantalla, pruebas de rotura) y las opciones del proyecto de Supabase (sin exponer tablas automáticamente, con RLS automático).
- Intención: que la regla "la guía solo incluye productos validados" y "el motivo del cambio es obligatorio" las haga cumplir la base, no solo la pantalla.
- Restricciones: no tocar la app Streamlit ni otras ramas; sin sesión, así que políticas abiertas solo de lectura y escritura únicamente por funciones; ninguna clave en el repositorio; no pedir la contraseña de la base ni la clave `service_role`; no marcar nada como probado en Supabase hasta confirmarlo.
- Verificación: decir qué se probó y contra qué.

**Respuesta obtenida.** `supabase/acceso.sql` (RLS, permisos y políticas), `supabase/funciones.sql` (cinco funciones), `supabase/seed_poc.sql`; `prototipo/js/api.js`, `reglas.js` y `app.js` reescritos; `prototipo/generar-config.mjs` para generar la configuración desde variables de entorno; `docs/poc-supabase.md`; pruebas estáticas en `tests/test_supabase_scripts.py`.

**Qué se aceptó y qué se corrigió.**
- Corregido por la IA en el esquema: un cambio de un SKU que no existe no se podía registrar, porque el equipo que sale era una clave externa obligatoria. Se agregó `sku_sale` y `id_equipo_sale` quedó opcional.
- Corregido tras probar la pantalla: al reiniciar la demo, el aviso de confirmación se borraba por dibujar la pantalla dos veces.
- Decisión: las tablas solo se leen desde el navegador y toda escritura pasa por funciones que validan; es más estricto que "políticas abiertas" y evita saltarse las reglas escribiendo directo en las tablas.
- Pendiente de decisión del equipo: qué debe comprobar «Validar» en un retiro (hoy exige disponible, igual que el despacho).

**Cómo se verificó.**
- `pytest tests`: pasan, incluidas las pruebas estáticas de los scripts y de que no haya claves en el repositorio.
- Sintaxis de los scripts de PostgreSQL con un analizador (`pglast`), incluido el código de las funciones. Eso no detectó ninguno de los dos defectos de abajo: solo revisa la forma, no cómo se comporta en Supabase.
- La pantalla, en un navegador real, contra una réplica en memoria de Supabase escrita solo para probar (no es parte del proyecto): flujo completo de las tareas 1 y 2, campos vacíos, 61 productos, motivo vacío, tres envíos seguidos, corte de conexión y error del sistema. Es una prueba de la pantalla; no prueba las funciones SQL.
- Antes de que existieran las tablas se hizo una sola lectura contra el proyecto real: devolvió el error esperado `PGRST205` y la pantalla mostró el mensaje con «Reintentar». Con eso se comprobó que la clave publicable es válida.
- **Los cuatro scripts los ejecutó Bastián en el editor SQL de Supabase, sin error, con los conteos esperados.** Después se probó la base real con la clave publicable, llamando a cada función (`supabase/probar_en_supabase.py`): 73 de 80 comprobaciones pasaron en la primera ejecución.
- **Dos defectos que solo aparecieron al probar en Supabase y que la IA no había previsto:** (1) `reiniciar_demo` fallaba desde la API con `DELETE requires a WHERE clause`, porque Supabase rechaza un `DELETE` sin `WHERE` para las llamadas de la API; (2) una línea con solo una tabulación se aceptaba como SKU, porque `btrim` solo quita espacios normales. Se corrigieron en `funciones.sql` (`where true` y una función `_limpiar`) y se agregó una restricción de PostgreSQL para el motivo del cambio.
- La primera ejecución de la prueba ignoraba el error de `reiniciar_demo` y siguió con datos sucios; se corrigió el script para que verifique el reinicio. Esa ejecución dejó los datos de la demo modificados en Supabase.
- **Correcciones confirmadas.** Bastián volvió a ejecutar `funciones.sql` y `select public.reiniciar_demo();` en Supabase, sin error. La prueba contra la base real se repitió con 3 comprobaciones nuevas para los espacios: **82 de 82 correctas**.
- **La pantalla se probó contra la base real** en un navegador: el flujo completo de las tareas 1 y 2 (27 comprobaciones) y las pruebas de rotura (18), todas correctas. Incluye un caso en que se salta la validación del navegador y la base rechaza el dato, y que tres envíos seguidos dejan un solo cambio guardado. El corte de conexión y el fallo interno se simularon interceptando la red del navegador.
- **Sin probar:** celular, poca señal real, otros navegadores y uso simultáneo de dos personas.
- La demo quedó reiniciada: 2 órdenes con 4 líneas pendientes, sin guías ni cambios.

---

## Encargo 22. Kit para ejecutar la prueba con usuarios, línea base y chequeo del celular

**Objetivo.** Dejar listo lo que falta para ejecutar de verdad la prueba diseñada en el Avance 6 y para reforzar la prueba de concepto: protocolo de línea base, kit de la prueba y chequeo en pantallas chicas.

**Instrucción entregada.**
- Contexto: `docs/prueba-usuarios.md` y `docs/pauta-validacion.md` (en `main` y en `feature/mejora-avance6`), las instrucciones del Avance 6 con sus criterios de revisión, la ficha de datos con los 24 meses propuestos y el prototipo conectado a Supabase.
- Intención: complementar y enlazar lo que ya existe, sin duplicarlo; escribir cómo se mide la línea base, el consentimiento, la planilla, el ensayo, el plan de sesiones, la regla de decisión y el checklist del celular; revisar todo contra los criterios del Avance 6.
- Restricciones: no tocar `supabase/` ni las otras ramas; no ejecutar `supabase/probar_en_supabase.py`; ningún nombre, teléfono ni correo de personas reales; grabaciones y evidencia fuera del repositorio; corregir solo CSS o textos en un commit aparte y sin cambiar reglas de validación; si se agrega un script, agregarle pruebas.
- Verificación: decir qué se verificó y qué no.

**Respuesta obtenida.**
- `docs/linea-base.md`, `docs/plantillas/linea_base_registro.csv` y `herramientas/calcular_linea_base.py`, con 49 pruebas.
- `docs/kit-prueba/`: consentimiento, planilla, ensayo interno, plan de sesiones, regla de decisión, revisión contra el Avance 6 y un índice.
- `herramientas/md_a_pdf.py` (con 12 pruebas) y los PDF imprimibles de la pauta, el consentimiento y la regla.
- `docs/checklist-celular.md` y una corrección de CSS en un commit aparte.
- `tests/test_kit_prueba.py`: coherencia entre el kit, la pauta y `prueba-usuarios.md`, enlaces, ausencia de datos personales, de nombres del equipo y de emojis.

**Qué se aceptó y qué se corrigió.**
- Aceptado: la rama parte de `feature/poc-supabase` con `feature/mejora-avance6` unido por un merge local, para que el kit y el PDF salgan de los documentos en su estado final. Hubo un conflicto en esta bitácora, resuelto dejando los Encargos 19, 20 y 21 en orden.
- Corregido, borde del campo «Cliente»: la revisión de pantallas chicas encontró que el borde del campo de solo lectura medía 1,59:1 (mínimo 3:1). Se cambió solo el CSS y ahora mide 4,37:1. Es el mismo hallazgo pendiente de `docs/etica.md`.
- Corregido, convertidor de PDF: escapaba dos veces el `&` de los enlaces (`&amp;amp;`). Lo encontró una prueba.
- Corregido, línea base: la guarda de datos personales marcaba una fecha (`2026-11-16`) como si fuera un teléfono. Se limitó a las columnas de texto libre.
- Corregido, pruebas del kit: tres falsos positivos de mi propia revisión de datos personales (el nombre de una imagen, el RUT ficticio del modelo y los datos de prueba de la guarda); se afinaron las reglas sin aflojarlas, de modo que un RUT, correo o teléfono real siga haciendo fallar la prueba.
- Corregido, emojis: la revisión del kit (`revision-avance6.md`) usaba emojis para marcar el estado. Bastián pidió que no haya emojis en el repositorio; se reemplazaron por palabras y se agregó una prueba que los detecta. Se dejaron los símbolos «✓» y «✕» del prototipo, que acompañan siempre a un texto.
- Corregido, herramienta de escritura: dos secuencias de escape (` ` y `\b`) se convirtieron en caracteres invisibles dentro de archivos. Se detectó con las pruebas, se corrigió y se revisó que ningún archivo del repositorio tenga caracteres de control.
- **No se aplicó:** el cambio de redacción de tres preguntas de la pauta que rozan la regla de no sugerir la respuesta. Está propuesto en `revision-avance6.md` y lo decide el equipo, porque cambiar una pregunta cambia lo que se mide.

**Cómo se verificó.**
- `pytest tests`: 169 pruebas pasan (las 71 anteriores más las nuevas).
- **PDF de la pauta:** regenerado desde el texto actual, 2 planas contadas con `pypdf`, y las seis etapas suman exactamente 20 minutos (sin holgura). La hoja de la regla y el consentimiento ocupan una plana cada uno. Se revisaron visualmente.
- **Pantallas chicas:** el prototipo se cargó dentro de un marco de 360 × 640 y de 390 × 844 y se recorrieron 16 estados en cada tamaño, contra una réplica de la base escrita solo para probar la pantalla. Se revisó desplazamiento horizontal, texto cortado, controles de 44 px o más (87 revisados), contraste de texto con la fórmula de WCAG (324 textos, el más bajo 5,63:1), contraste de bordes, estados que dependen solo del color y tamaño de letra de los campos. Para comprobar que la revisión sirve se le inyectaron a propósito cinco problemas y los detectó todos. Mi primer intento de ese control falló porque la política de seguridad de la página bloquea los estilos en línea: eso era un defecto del control y no de la revisión.
- **No se ejecutó** `supabase/probar_en_supabase.py` ni se tocó Supabase: la demo quedó como estaba.
- **No se pudo verificar:** un celular real, señal real, otros navegadores, dos personas usando la demo a la vez y el sitio publicado en Vercel. Tampoco se hizo el ensayo de la pauta con una persona ni ninguna medición de línea base: todo eso está escrito, no ejecutado.


---

## Encargo 23. Aplicar las decisiones del equipo sobre el instrumento de la prueba con usuarios

**Objetivo.** Aplicar a `docs/prueba-usuarios.md`, `docs/pauta-validacion.md` y al kit las seis decisiones que tomó el equipo tras la revisión del Encargo 22.

**Instrucción entregada.**
- Contexto: `docs/kit-prueba/revision-avance6.md` (lo que la revisión encontró) y las seis decisiones de Bastián: usar roles en vez de nombres en `prueba-usuarios.md` y dejar la autoría en el README por ahora; reescribir la pregunta 3 de contexto y la 2 de cierre y dejar la frase 1 del SUS; umbral en tres tramos para 5 personas (4 o 5 se cumple, 3 entorpece, 2 o menos bloquea); quitar una pregunta de contexto para dejar 2 o 3 minutos de holgura y regenerar el PDF; en la tarea 2, «dilo en voz alta» en vez de «señala con el cursor o en voz alta»; aceptar la regla de fallas del sistema como propuesta.
- Restricciones: no subir nada; no tocar el README; no tocar `supabase/` ni las otras ramas; sin emojis; ningún nombre ni dato personal.
- Verificación: correr las pruebas, regenerar el PDF y contar planas y minutos.

**Respuesta obtenida.** Cambios en `prueba-usuarios.md` (roles con integrante A y B, tres tramos, éxito de la tarea 2 de oído, regla de fallas del sistema), en la pauta (una pregunta de contexto menos, dos preguntas reescritas) y en el kit (hoja de la regla, plan de sesiones, ensayo, índice y revisión). PDF de la pauta y de la hoja de la regla regenerados. Doce pruebas nuevas que fijan estas decisiones.

**Qué se aceptó y qué se corrigió.**
- Aceptado: las dos preguntas se reescribieron con la redacción que se había propuesto, sin cambios.
- **La holgura es de 1 minuto y no de 2 o 3.** Al quitar una pregunta de contexto, la etapa pasó de 3 a 2 minutos y el total de 20 a 19. Para llegar a 2 minutos habría que recortar otro minuto de otra etapa, y eso lo decide el equipo. La pauta decía «Dura 20 minutos en total» y quedó desactualizada: se corrigió a 19 y una prueba lo comprueba.
- **Qué pregunta se quitó:** la 1 de contexto («cuénteme paso a paso»), por ser la más larga y la más general. Las dos que quedan se relacionan con las tareas.
- **Tramos de la tarea 2.** Los tres tramos eran para la tarea 1. Se aplicaron también a «se dan cuenta solas del código malo». A «terminan sin ayuda en menos de 5 minutos», que ya tenía el umbral de 3 de 5, se le agregaron **por analogía** los tramos de 2 de 5 y de 1 o menos. Eso lo agregó la IA y no lo decidió el equipo: está marcado como tal en los documentos, por confirmar en el ensayo.
- **El umbral quedó más permisivo en un punto.** Antes se fallaba con «2 o más no lo logran» (3 o menos que lo logran); ahora solo bloquea con 2 o menos que lo cumplen y con 3 entorpece. Se cambia antes de la primera sesión, que es lo que permite el enunciado.
- **Una inconsistencia que se encontró y se resolvió sin que se pidiera.** El plan de sesiones le asignaba al integrante que trabaja en la bodega del caso registrar mirando la grabación de sus compañeros, mientras la hoja de consentimiento promete a los participantes que esa persona no ve las grabaciones. Al pasar a roles se resolvió protegiendo al participante: en esas sesiones registra quien facilitó, después. **Es un cambio de fondo al plan, hecho por la IA; si el equipo prefiere el original, hay que cambiar también el consentimiento.** Una prueba comprueba que el plan y el consentimiento no se contradigan.
- **Ajuste posterior, a pedido de Bastián, que además aceptó los tres puntos de arriba** (la fila de tramos por analogía de la tarea 2, el umbral en tres tramos y quién registra las grabaciones): la hipótesis dice ahora de forma explícita que solo 4 o 5 de 5 cuentan como «se cumple» y que con 3 de 5 no pasa (es «entorpece»). La misma aclaración está en la hoja de la regla de decisión, cuyo PDF se regeneró, y una prueba la fija en los dos documentos.
- Se arreglaron dos defectos de las propias pruebas nuevas: un helper fallaba con la última sección de un documento, y una comprobación de la duración dejó de coincidir con el texto nuevo de la pauta.
- No se aplicó: quitar los nombres del README, de la bitácora ni de `docs/etica.md` y `docs/entrevistas/`, que también los tienen. La decisión fue solo sobre `prueba-usuarios.md`; el kit y esos dos documentos no llevan nombres.

**Cómo se verificó.**
- `pytest tests`: 180 pruebas pasan.
- **PDF de la pauta:** regenerado con el texto nuevo, 2 planas contadas con `pypdf`, las seis etapas suman 19 minutos, y una prueba comprueba que el PDF trae las preguntas reescritas. La hoja de la regla sigue en una plana.
- Una prueba comprueba que `prueba-usuarios.md` y la pauta no nombran a ningún integrante, y otra que los números de la hoja de la regla coinciden con los de `prueba-usuarios.md`.
- **Comprobación de que las preguntas nuevas no introducen sesgo:** se releyeron contra la regla del enunciado (ninguna sugiere la respuesta, pide una opinión sobre el futuro ni promueve una idea). **Es una lectura, no una prueba con una persona.** El ensayo interno es donde se confirma que se entienden y que no empujan una respuesta.
- **No se verificó:** el ensayo con una persona, que la frase de la tarea 2 se pueda comprobar de oído en una grabación real, ni los tiempos por etapa, que siguen siendo los del documento.


---

## Encargo 24. Cerrar los pendientes del avance y preparar la fusión de las ramas

**Objetivo.** Ordenar en el README lo hecho, lo pendiente del avance, lo congelado y la siguiente etapa, según la retroalimentación de la profesora, y dejar las ramas listas para abrir sus pull requests una por una.

**Instrucción entregada.**
- Contexto: la retroalimentación del Avance 5 («no le dediquen más horas a la aplicación Streamlit mientras la prueba con usuarios no confirme el flujo»), el PR #24 ya fusionado en `main` y el estado de las ramas.
- Intención: pasar a «Hecho» lo que ya está hecho; marcar como «Congelado, no se hará por ahora», con su razón, lo de la aplicación Streamlit (límite de 60, cambios destacados en el validador, motivo obligatorio, borde del campo Cliente, cuentas y permisos); dejar como «Siguiente etapa» y no como pendiente del avance la línea base, el ensayo, la prueba en un celular real, la prueba con usuarios y las dos preguntas al jefe de bodega.
- Restricciones: traer los cambios de `origin/main` a cada rama antes de su pull request, resolver los conflictos, correr las pruebas y avisar, en el orden `mejora-avance6`, `poc-supabase`, `kit-validacion`; no subir ni abrir ningún pull request sin confirmación; una rama a la vez.

**Respuesta obtenida.** La sección «En qué estado está» del README en cuatro bloques (hecho, pendiente del avance, congelado, siguiente etapa) y la sincronización de `mejora-avance6` con `main`.

**Qué se aceptó y qué se corrigió.**
- **Se agregó un bloque que no se pidió, «Pendiente del avance»,** porque quedan tres cosas reales que no son de la siguiente etapa: que el equipo confirme los criterios de HU-02 a HU-05 (propuestos con ayuda de IA), confirmar con administración los 24 meses y configurar Vercel. Si el equipo prefiere otra clasificación, es un cambio de texto.
- **El borde del campo Cliente** estaba en la lista de lo congelado, pero la aplicación Streamlit no tiene ese campo (se comprobó buscando «cliente» en `src/`). El que existía era el del prototipo y ya está corregido. El README lo dice así.
- **Lo congelado no se perdió:** el trabajo de la aplicación está en dos ramas locales que no se suben ni se fusionan (`feature/avance5-pendientes-app` y `feature/login-etapa1`), y el README las nombra.
- La fecha del README («Al 5 de noviembre») estaba desactualizada y pasó al 15 de noviembre de 2026.
- **Sincronización de `mejora-avance6`:** se simularon las tres ramas contra `main` y ninguna tenía conflictos. Se hizo el merge de `origin/main` en `mejora-avance6`, sin conflictos (commit `4a4e2b5`), y sus 56 pruebas pasan. No se hizo todavía en `poc-supabase` ni en `kit-validacion`, porque cada una debe sincronizarse después de que la anterior se fusione. Se simuló `poc-supabase` contra `mejora-avance6` ya fusionada: habrá un conflicto en la bitácora, que se resuelve dejando los Encargos 19, 20 y 21 en orden.

**Cómo se verificó.**
- `pytest tests`: 181 pruebas pasan en `kit-validacion` y 56 en `mejora-avance6`.
- Se comprobó que no hay emojis ni caracteres de control ocultos, que no hay `config.js` ni `.env` versionados y que ningún commit lleva líneas de Claude.
- Se repitió, sin cambiar nada, el barrido de nombres de personas ajenas al equipo, teléfonos y correos: no hay teléfonos ni correos reales en los archivos. Los hallazgos están en la respuesta de la sesión.
- **No se verificó:** el contenido de las 27 imágenes, la carpeta anidada que git excluye ni `bodega.db`.


---

## Encargo 25. Abrir el PR de `mejora-avance6` y reemplazar los RUT de ejemplo

**Objetivo.** Subir `feature/mejora-avance6` y abrir su pull request como borrador, con un revisor, y reemplazar los RUT de las empresas de ejemplo por valores claramente falsos.

**Instrucción entregada.**
- Contexto: el barrido de datos personales del Encargo 24 (un RUT de ejemplo con dígito verificador válido) y la orden de fusión decidida: `mejora-avance6`, `poc-supabase` y `kit-validacion`.
- Intención: subir solo `mejora-avance6`; abrir el PR hacia `main` como borrador, asignar a `sebastiancarmonap-web` como revisor y no fusionarlo; reemplazar el RUT de ejemplo con dígito verificador válido (el de Minera Cordillera) por `11.111.111-1` y `22.222.222-2` en las semillas, los documentos y las pruebas, en un commit aparte.
- Restricciones: no subir nada más; detenerse después de abrir el PR hasta que Bastián avise que se fusionó; sin líneas de Claude; avisar antes de que se vuelva a ejecutar `seed_poc.sql` en Supabase.

**Respuesta obtenida.**
- Push de `feature/mejora-avance6` y PR #25 en borrador, con `sebastiancarmonap-web` como revisor solicitado. No se fusionó.
- Commit `871d0c8` en `feature/kit-validacion` con el reemplazo de los RUT.

**Qué se aceptó y qué se corrigió.**
- **Interpretación del reemplazo:** la instrucción nombraba un RUT y dos valores nuevos. Se entendió que los dos RUT de ejemplo cambian, en orden: el de Constructora Andes pasa a `11.111.111-1` y el de Minera Cordillera a `22.222.222-2`.
- **Los dos valores nuevos tienen dígito verificador válido** (el que corresponde a `11.111.111` es 1 y a `22.222.222` es 2) y están en el rango de las personas naturales, no en el de las empresas. Son placeholders muy usados, y se aplicaron porque así se decidió; lo que ya no existe es la coincidencia posible con una empresa real.
- **Dónde quedó el cambio.** Primero se hizo en `feature/kit-validacion` (commit `871d0c8`), porque ahí existen a la vez las semillas, los documentos y la prueba que lista los RUT permitidos. Después Bastián pidió una rama aparte: `feature/rut-ficticios`, que sale de `main` y cambia lo que existe allí (`seed_ejemplo.sql`, `docs/datos/estructura_datos.md`) con dos pruebas nuevas en `tests/test_modelo_datos.py`. **`seed_poc.sql` no existe en `main`** (llega con la prueba de concepto), así que su cambio se hace como commit propio en `feature/poc-supabase` al sincronizarla. Los cambios de esas ramas y el del kit son idénticos, así que al fusionarlas no chocan. La rama aparte no lleva entrada propia en la bitácora para no agregar otro conflicto al final del archivo; este Encargo la cubre.
- **No se cambió** el PDF `docs/unidad1/Avance_3_grupo_6.pdf` (plana 11 y 12), que es un documento entregado y todavía trae los RUT anteriores.
- **La base real de Supabase sigue con los RUT anteriores** hasta que Bastián vuelva a ejecutar `seed_poc.sql`; no se ejecutó nada ni se tocó Supabase.
- Una prueba nueva impide que los RUT anteriores vuelvan a las semillas y al modelo de datos. Al escribirla, mi primera versión contenía los RUT anteriores como texto y la revisión de datos personales del repositorio la marcó: se corrigió armándolos por partes.
- El primer intento de `push` no se ejecutó porque mi comando encadenaba un `grep -c` que devuelve error cuando cuenta cero; se repitió el push solo.

**Cómo se verificó.**
- `pytest tests`: 182 pruebas pasan en `kit-validacion`.
- Antes del push se comprobó que los tres commits de `mejora-avance6` no llevan trailers de Claude ni `config.js` ni `.env`.
- El borrador y el revisor se verificaron en la página del PR #25. Las 3 verificaciones automáticas de GitHub estaban pendientes cuando se cerró la pestaña.
- **No se verificó:** que la semilla con los RUT nuevos corra en Supabase; se ejecuta después de este aviso.


---

## Encargo 26. Cerrar el Avance 6 y la prueba de concepto: sincronizaciones, PR y fusiones

**Objetivo.** Dejar el Avance 6 y la prueba de concepto fusionados en `main` por pasos, cada uno revisado por alguien distinto de Bastián, y preparar el PR del kit de validación.

**Instrucción entregada.**
- Contexto: la retroalimentación de la profesora, el PR #24 ya fusionado y las ramas `mejora-avance6`, `rut-ficticios`, `poc-supabase`, `kit-validacion`, `criterios-historias` y `mantener-supabase`.
- Intención: sincronizar cada rama con `main` antes de su PR, corriendo las pruebas y revisando el diff; abrir cada PR con revisor y con descripción de cinco partes (qué cambia, cómo se probó, qué revisar, qué no se verificó, orden de fusión).
- Restricciones: la IA no fusiona sin la aprobación de un tercero y sin el mensaje «fusiona #N»; los criterios de `historias.md` no se suben hasta «aprobado historias»; no se toca Supabase ni `feature/avance5-pendientes-app` ni `feature/login-etapa1`; `git add` solo con nombres de archivo.

**Respuesta obtenida.**
- **PR #25** (`mejora-avance6`): ya estaba fusionado por `diegoneves-design` cuando se retomó, con la versión anterior de los criterios. Los criterios reescritos van en la rama `feature/criterios-historias`, con un commit local pendiente de «aprobado historias».
- **PR #26** (RUT de ejemplo) y **PR #27** (prueba de concepto): abiertos con revisores asignados por sus cargos del README. Ambos fueron fusionados por `diegoneves-design`. El #26 con dos aprobaciones (`oscarynchau-dev` y `diegoneves-design`) y el #27 con la de `oscarynchau-dev`; el revisor asignado al #27, `sebastiancarmonap-web`, no llegó a revisar. **Ninguna de las fusiones la hizo la IA.**
- **Rama `feature/mantener-supabase`:** el flujo que evita que Supabase se pause, con su sección 6 en `docs/poc-supabase.md` y 7 pruebas. Es local y su PR se abre al final.
- **PR del kit** (esta rama): sincronizada con `main` sin conflictos; los Encargos 1 a 25 quedaron en orden y sin repetir.

**Qué se aceptó y qué se corrigió.**
- Las pruebas del RUT se movieron a `tests/test_rut_ejemplo.py` antes de fusionar el #26, porque agregaban pruebas al final del mismo archivo que la prueba de concepto y habrían chocado.
- No se publicaron comentarios pidiendo revisión en el #26 y el #27, porque cuando se iba a hacer ya estaban fusionados.
- **Un incidente propio:** en la prueba de control del revisor del diff, git borró el `prototipo/js/config.js` local de Bastián al cambiar de rama (la prueba forzaba un archivo con ese nombre dentro de una rama desechable). Se regeneró desde `.env` con `generar-config.mjs`. No se versionó nada.
- En el README se agregó a «Pendiente del avance» que Bastián debe ejecutar `seed_poc.sql` con los RUT nuevos y reiniciar la demo, y se amplió la fila de los criterios a HU-01 a HU-05.

**Cómo se verificó.**
- `pytest tests`: 184 pruebas pasan en esta rama.
- Revisión de las líneas agregadas por cada rama antes de su PR, con un script que busca emojis, caracteres de control, claves, `config.js`, correos y teléfonos que no sean de ejemplo, RUT no permitidos y nombres ajenos al equipo. El script no se versiona. Se comprobó que detecta los siete tipos de defecto con una rama desechable.
- Se comprobó que `docs/prueba-usuarios.md` y la pauta no nombran a ningún integrante, que el README enlaza la prueba de usuarios, la pauta, el kit, la línea base y el checklist del celular, y que ningún enlace está roto.
- **No se verificó:** el contenido de las 27 imágenes; que el equipo haya verificado los criterios de `historias.md`; el flujo de Supabase, que no se ejecutó; ni nada que dependa de Vercel o del celular.

---

## Encargo 27. Diagrama de arquitectura y camino delgado (Avance 7)

Lo hizo Oscar Ynchaustegui el 2026-11-22, con Claude. Lo revisa Sebastián Carmona en el pull request.

**Objetivo.** Escribir `docs/arquitectura.md` con la plantilla del Avance 7. El diagrama de componentes con su tabla de piezas y el plan de falla, el camino delgado con una sola acción y la evidencia.

**Instrucción entregada.**
- Contexto. El enunciado del Avance 7, la prueba de concepto que ya estaba en `main` (`prototipo/`, `supabase/` y `docs/poc-supabase.md`) y el encargo con que se construyó, que es el Encargo 21 de esta bitácora, con sus cuatro partes (contexto, intención, restricciones y verificación).
- Intención. Que cada pieza diga qué hace en nuestra solución y no una definición de manual, y que el camino delgado sea una sola acción justificada como lo más frágil.
- Restricciones. No tocar el código, una sola acción aunque la PoC haga cuatro, declarar lo que queda fuera como decisión y no poner nada como probado si no se comprobó en el repositorio.
- Verificación. Que cada mensaje de error citado exista tal cual en el código y que los datos de la orden 3002 calcen con la semilla.

**Respuesta obtenida.** El archivo `docs/arquitectura.md` con un diagrama Mermaid de seis piezas y siete comunicaciones numeradas, la tabla de piezas, el plan de falla de Supabase, el camino delgado "Preparar la guía de una orden" con su recorrido en cuatro pasos, el caso de error de la orden 3002 y la lista de lo que queda fuera.

**Qué se aceptó y qué se corrigió.**
- Aceptado. "Preparar la guía" como camino delgado, porque es la acción que entrega una respuesta visible (el N.º interno de la guía) y la que bloquea un código que no existe, que es el problema que originó el proyecto.
- Corregido. El diagrama de `docs/poc-supabase.md` no mostraba la publicación ni el servicio externo, y su tabla decía qué hace cada pieza en general. Se agregaron GitHub, Vercel y Supabase como servicio externo con su plan de falla, y el ERP como pieza fuera de la PoC.
- Corregido. La PoC hace cuatro acciones (cargar, validar, registrar cambio y preparar guía) y el enunciado pide una sola. Las otras tres quedan declaradas como fuera del camino delgado, no como parte de él.
- Decisión. El enunciado pide el código en `src/`, pero la PoC está en `prototipo/` y `supabase/`, y `src/` tiene la aplicación Streamlit congelada. Se explica en el documento en vez de mover el código el día antes de la entrega, porque moverlo podía romper la publicación en Vercel.
- Decisión. El inventario real de la bodega no forma parte de la PoC. El enunciado pide que los datos guardados sean de ejemplo e inventados, y la base no tiene inicio de sesión.

**Cómo se verificó.**
- Cada mensaje citado se buscó en `supabase/funciones.sql` y `prototipo/js/app.js` ("Corrige 1 producto para continuar.", "Solo el jefe de bodega puede preparar la guía.", el de sin conexión y el de fallo del sistema) y está escrito igual.
- En `supabase/seed_poc.sql`, la orden 3002 trae `SD-63A20-9999`, que no está en el inventario, y sus otros tres productos están disponibles, así que el error es por un solo producto.
- Que `preparar_guia` rechaza sin pasar por la pantalla está en la tabla de pruebas de rotura de `docs/poc-supabase.md` (sección 3), contra el Supabase real.
- **Pendiente.** Abrir la dirección pública en una ventana de incógnito, grabar el video y agregar su enlace en la sección de evidencia.

---

## Encargo 28. Cargar el inventario real a Supabase (primera parte: carga)

**Objetivo.** Pasar el Excel de inventario de la bodega a la base de datos de la prueba de concepto, sin subir datos reales al repositorio, como base de un tablero que se hará en una segunda parte.

**Instrucción entregada.**
- Contexto: el Excel de la bodega (tres hojas: equipos, extensiones eléctricas y catálogo de familias), `supabase/` y la prueba de concepto ya fusionada.
- Intención: cargar 1.617 equipos y 319 extensiones; que `reiniciar_demo` no borre el inventario real; que `seed_poc.sql` no pueda borrarlo por accidente.
- Restricciones: el Excel y lo generado viven solo en `datos_locales/` (ignorado por Git); el reporte solo trae totales; la IA no ejecuta nada en Supabase, lo hace Bastián; detenerse antes de que Bastián corra la carga.
- Numeración: se usa el Encargo 28 porque el 22 al 26 están en el PR del kit (#28) y el 27 está reservado para el flujo que mantiene activo a Supabase.

**Respuesta obtenida.** `herramientas/importar_inventario.py`, `supabase/inventario.sql`, cambios en `reiniciar_demo` (`supabase/funciones.sql`) y en `supabase/seed_poc.sql`, `docs/analisis-inventario.md` y `tests/test_importar_inventario.py`. El importador generó en `datos_locales/` seis archivos de carga y el de extensiones.

**Qué se aceptó y qué se corrigió.**
- Supuesto de la columna Ubicación (valor numérico o nombre = arrendado): lo definió Bastián y queda escrito como supuesto a confirmar con Oscar en `docs/analisis-inventario.md`.
- Dos cifras preliminares de Bastián diferían del cálculo: EC, AP y AC suman 1.324 equipos, el 81,9 % (no 83 %), y Bastián lo corrigió a 82 %; y el «modelo más repetido» dependía de cómo se defina modelo, que se resolvió en el Encargo 29.
- Corregido por la IA durante la prueba: un patrón de capacidad (TR) fallaba por un grupo faltante; se vio en las pruebas.
- El importador usa `openpyxl`, que no está en `requirements.txt` (la app no lo usa); queda indicado en el propio script.

**Cómo se verificó.**
- `pytest tests`: 132 pruebas pasan (60 nuevas, con filas ficticias): mapeo de ubicación, extracción de capacidad, largos, trozos de máximo 300 filas, escape de comillas, que el reporte no traiga SKU ni descripciones ni ubicaciones, y revisiones estáticas de los SQL.
- Los archivos generados se ejecutaron en una base SQLite en memoria con el esquema real: 1.617 equipos con id desde 1000, 319 extensiones, y una segunda ejecución no duplica. Las restricciones de estado y lugar pasan.
- **No se verificó:** nada contra PostgreSQL ni Supabase (`inventario.sql`, la nueva `reiniciar_demo` y el guard de `seed_poc.sql` solo tienen revisión estática); el contenido real de los datos más allá de los totales; ni el tablero, que no existe todavía.

---

## Encargo 29. Dashboard interactivo de inventario

**Objetivo.** Agregar al prototipo un Dashboard para todos los roles, con 12 gráficos que se filtran entre sí, sobre el inventario real ya cargado en Supabase.

**Instrucción entregada.**
- Contexto: el inventario cargado y verificado (1.617 equipos, 319 extensiones, 7 de demo; `reiniciar_demo` lo deja intacto), el prototipo y sus reglas de estilo.
- Intención: una función de datos de solo lectura; 12 gráficos con etiquetas, filtro cruzado, tabla de casos con CSV y panel de detalle, vistas por rol, filtros en la dirección y lectura de datos que se recalcula.
- Ajustes pedidos por Bastián: 82 % en lugar de 83 %; el Pareto agrupa por modelo y lo documenta; capacidad sin mezclar BTU/H y TR; nota con el criterio de las 7 familias; `openpyxl` en un archivo aparte.
- Restricciones: sin CDN (ECharts copiado), sin datos reales ni claves en el repositorio, no tocar Supabase, no abrir el PR hasta que Bastián lo confirme.

**Respuesta obtenida.** `supabase/dashboard.sql` (`inventario_dashboard()`), `prototipo/dashboard.html`, `css/dashboard.css`, `js/filtros.js` (lógica sin navegador), `js/graficos.js`, `js/dashboard.js`, `js/vendor/` (ECharts 5.5.1 con un build propio de 640 KB), `prototipo/pruebas/filtros.test.js`, `tests/test_dashboard.py` y `requirements-herramientas.txt`; un enlace desde `index.html`; la sección 9 de `docs/analisis-inventario.md`.

**Qué se aceptó y qué se corrigió.**
- Modelo: primera palabra tras «MODELO» en la descripción; da 362 equipos (22,4 %) para el mayor, como indicó Bastián.
- Capacidad: se pasó TR a BTU/H (1 TR = 12.000 BTU/H) y la nota del gráfico lo declara; cada vista usa una sola unidad.
- Dejado fuera por decisión de la IA, anotado como mejora futura: indicar en el panel si el equipo aparece en una orden del prototipo.
- Corregido tras verlo en el navegador: leyenda del gráfico 4 con colores equivocados; etiquetas del Pareto y de las medianas encima de las barras; texto blanco ilegible sobre celdas medias del mapa de calor; treemap con colores oscuros; etiquetas de la dona cortadas a 375 px; mensaje de extensiones que decía «con el filtro de corriente» sin que hubiera uno.
- Bastián pidió llamar a la vista «Dashboard» en toda la interfaz (antes se llamaba de otra forma) y que fuera una vista más del programa: se renombraron `dashboard.html`, `dashboard.css` y `dashboard.js`, y se agregó un menú principal compartido (Pedidos y Dashboard, con estado activo) en `index.html` y `dashboard.html`. Las menciones anteriores a ese nombre en el Encargo 28 se dejaron como estaban.
- Un intento de la IA de cerrar un servidor de prueba terminando todos los procesos `node` fue bloqueado y no se repitió: se usó otro puerto.

**Cómo se verificó.**
- `node --test`: 30 pruebas de la lógica de filtros con datos ficticios. `pytest tests`: 146 pasan, incluida la revisión de que la función devuelve solo las 9 columnas permitidas, que la página no tiene estilos ni scripts en línea y que ECharts pesa menos de 1 MB.
- Las cifras del Dashboard se recalcularon con la misma lógica sobre los datos reales (solo totales): estados, tasas por familia, Pareto, capacidad y extensiones coinciden con `docs/analisis-inventario.md`. El JSON real pesa 236 KB.
- El Dashboard se probó en Chrome contra una página local con datos ficticios, no contra Supabase: clic en la dona y filtro, enlace con filtros (`#estado=fuera_servicio&familia=AC`), panel de detalle con Escape y foco, y 375 px (sin desborde horizontal, tabla desplazable, panel a pantalla completa).
- **No se verificó:** la función `inventario_dashboard()` en Supabase (solo revisión estática); la página publicada en Vercel; la descarga del CSV en el navegador (solo la función que lo arma, con pruebas); la navegación solo con teclado más allá de los botones y el panel; el celular real ni otros navegadores que no sean Chrome.


---

## Encargo 30. Migrar el MVP (Streamlit) a Supabase

**Objetivo.** Pasar el MVP de `src/` de una base SQLite con datos de ejemplo a la base real de Supabase, sin exponer ninguna clave y sin tocar el prototipo. El orden fue: auditoría y plan primero (sin cambiar nada), y recién después de que Bastián aprobó el plan, la implementación.

**Instrucción entregada.**
- Contexto: el MVP son las pantallas de `src/` y sus datos en SQLite; el prototipo de `prototipo/` ya está probado y no se rehace; Supabase ya tiene la base real (1.617 equipos desde el id 1000, 319 extensiones, demo 501 a 507) y las funciones del flujo. Streamlit no corre en Vercel.
- Intención: que el MVP lea y escriba en Supabase llamando a las funciones SQL (fuente única de verdad), con una capa `db.py` de dos implementaciones (SQLite para pruebas y PostgreSQL con psycopg, sin ORM, para producción, elegida por `DATABASE_URL`).
- Restricciones (no negociables): ninguna contraseña, cadena de conexión ni clave en el repositorio, en registros ni en el chat; la aplicación no se conecta como `postgres` sino con un rol limitado sin contraseña escrita en el SQL; pooler de Supabase en modo sesión; la IA no ejecuta nada en Supabase; rama `feature/mvp-supabase` desde `feature/dashboard-inventario`; no fusionar nada sin aprobación de otra persona y la orden «fusiona #N».
- Verificación pedida: pruebas verdes sin conexión a internet, y detenerse antes de levantar el MVP contra Supabase hasta el «listo» de Bastián.
- Decisiones de Bastián tras la auditoría: columna `ordenes.folio` (único, opcional, formato `GUIA-2026-001`, exigido por `crear_pedido`); `psycopg[binary]` con versión fija, importado solo si hay `DATABASE_URL`; el responsable del cambio sale de la tabla `usuarios` y la falta de inicio de sesión se documenta; `reiniciar_demo` solo restaura las órdenes 3001 y 3002 y no se le da al rol del MVP; evaluar un servicio de PostgreSQL en el CI.

**Respuesta obtenida.**
- Auditoría y plan: tabla de equivalencias entre el MVP y la base (folio contra `id_orden`, «stock» contra estado del equipo, 50 contra 60 SKU, modalidad y motivo de retiro separados, estados derivados contra guardados) y la lista de lo que Supabase no tenía (crear órdenes, listado, detalle, historial). Decisión recomendada y aprobada: llamar a las funciones SQL.
- SQL nuevo: `supabase/mvp_folio.sql`, `mvp_funciones.sql` (`crear_pedido`), `mvp_vistas.sql` (tres vistas de lectura), `mvp_rol.sql` (rol `app_mvp`), `verificar_mvp.sql`; cambios en `schema.sql`, `funciones.sql` (ayuda `_skus_limpios` y `reiniciar_demo` acotado a la demo) y `probar_en_supabase.py`.
- Python: `src/db.py` (interfaz, `RepoPostgres`, `RepoSqlite`, lector de `.env`), las siete pantallas de `src/views/` y `ui_router`, `ui_datos` y `app.py` adaptados; `requirements.txt` con `psycopg[binary]==3.3.9`.
- Pruebas: `tests/test_contrato_repo.py` (las mismas pruebas contra las dos implementaciones, y las exclusivas de PostgreSQL), `tests/test_mvp_ui.py` (recorridos de pantalla), `tests/conftest.py`, y revisiones estáticas nuevas en `tests/test_supabase_scripts.py`. CI con un servicio de PostgreSQL 16.
- Documentación: `docs/mvp-supabase.md` (orden de ejecución, contraseña, de dónde copiar la cadena del pooler, permisos, límites) y el README.

**Qué se aceptó y qué se corrigió.**
- La IA cambió `cargar_pedido` (una función ya probada con 82 comprobaciones) para que use la ayuda `_skus_limpios` compartida con `crear_pedido`, en lugar de duplicar la limpieza. No era pedido textual; se hizo para que las dos limpien igual, y se compensó con las pruebas de contrato. Bastián debe volver a correr las comprobaciones por la API pública tras ejecutar el SQL.
- `crear_pedido` y las vistas no se dan a la API pública (decisión de la IA, no pedida): el sitio publicado no necesita crear órdenes y Supabase da permisos por omisión a lo que se crea después.
- La IA mantuvo `main_clasico` y las funciones de SQLite de `app.py`, que ya no usa `main()`, porque el repositorio pide no eliminar código funcional sin confirmación. Queda la pregunta de si se borran.
- Corregido durante el trabajo: (1) un error de la IA en su propia prueba (usaba una columna que no existía en `clientes`), visto en el primer intento contra PostgreSQL; (2) la IA notó que Streamlit no lee `.env`, así que agregó un lector que no pisa variables ya definidas, y blindó las pruebas para que nunca lo lean ni usen `DATABASE_URL`; (3) la revisión estática de credenciales encontró una contraseña falsa escrita literal en una prueba de la propia IA, y se pasó a armarla al ejecutar; (4) `probar_en_supabase.py` asumía exactamente 7 equipos y 2 órdenes, lo que ya no es cierto con el inventario real y las órdenes del MVP, así que se acotó a la demo; (5) los números de línea de `reiniciar_demo` eran fijos (9001 a 9008) y podían chocar con los de otras órdenes, así que ahora siguen al mayor existente.
- Agregado después, al aprobar el plan de la vista Dashboard del MVP: `mvp_rol.sql` también le da al rol `app_mvp` el permiso de ejecutar `inventario_dashboard()` (solo lectura), con su fila en `verificar_mvp.sql` y sus pruebas.
- Hallazgo al ejecutar en Supabase (2026-11-23): la comprobación nueva de `probar_en_supabase.py` mostró que la clave publicable podía leer el RUT y la dirección de los clientes, porque `acceso.sql` daba lectura de la tabla completa (un defecto anterior al MVP que ninguna prueba cubría). Bastián lo cerró a mano en Supabase y la IA lo replicó en `acceso.sql`, `verificar_mvp.sql`, el script de comprobación y sus pruebas, y corrigió `docs/poc-supabase.md` (que además decía que «Reiniciar demo» borra todas las órdenes). El prototipo no usa esas dos columnas (solo `id_cliente` y `razon_social`).
- Limitación documentada, por decisión de Bastián: el MVP no tiene inicio de sesión; cualquiera con acceso opera como el usuario que elija (README y `docs/mvp-supabase.md`).
- Contexto que consta: la profesora pidió en el Avance 5 no dedicar más horas a la app Streamlit hasta que la prueba con usuarios confirme el flujo; esta migración la decidió Bastián (2026-11-20).
- Nombres de personas en el repositorio: solo los de los usuarios ficticios de siempre (Pedro Soto y Camila Rojas).

**Cómo se verificó.**
- `py -m pytest tests`: 221 pasan y 70 se omiten (las que necesitan PostgreSQL o `psycopg`). Con un PostgreSQL 16 local y desechable (`DATABASE_URL_TEST`): 285 pasan y 6 se omiten.
- Las reglas de las cuatro funciones y sus mensajes exactos dan lo mismo en SQLite y en PostgreSQL; el rol `app_mvp` rechaza escribir directo en las ocho tablas, leer correo, teléfono, RUT y dirección, y ejecutar `reiniciar_demo`; `anon` no puede usar `crear_pedido` ni las vistas; `reiniciar_demo` como `anon` no borra las órdenes del MVP ni los equipos reales.
- Los archivos SQL se aplicaron en el orden documentado sobre una base nueva y sobre una que simula la actual (estado anterior más inventario ficticio y una orden sin folio), dos veces cada una; `verificar_mvp.sql` solo falló en los conteos del inventario real, porque la base local no los tiene.
- `node --test prototipo/pruebas/filtros.test.js`: 30 pruebas pasan; el prototipo no se modificó.
- **No se verificó:** nada en Supabase (no se ejecutó ningún SQL ahí); las comprobaciones por la API pública de `probar_en_supabase.py`, que necesitan la API de Supabase; el pooler con el usuario `app_mvp.<referencia>`; el MVP en un navegador contra Supabase; el flujo del CI en GitHub (solo se validó su sintaxis). Tampoco se probó la aplicación a mano en un navegador: los recorridos usan Streamlit AppTest.

---

## Encargo 31. Dashboard del inventario dentro del MVP

**Objetivo.** Llevar el análisis del inventario real (12 gráficos, filtro cruzado, indicadores, tabla de casos, CSV, vistas por rol y «Lectura de los datos») a una vista «Dashboard» del MVP, reutilizando el código del prototipo sin duplicarlo, con los datos entregados por el servidor y con una distribución pensada para pantallas anchas.

**Instrucción entregada.**
- Contexto: el MVP (Streamlit) ya usa `db.py` y el rol `app_mvp`; el prototipo ya fue evaluado y queda como archivo histórico (no se rehace, no se rompe) (más tarde, el 2026-11-23, Bastián decidió además mantenerlo publicado en su propio proyecto de Vercel para el video del README y la prueba con usuarios; ver Encargo 32). Rama `feature/mvp-dashboard`, desde `feature/mvp-supabase`.
- Intención: enfoque a evaluar y confirmar antes de implementar (componente HTML incrustado con datos del servidor, un «modo incrustado» y una sola fuente de scripts); rediseño ancho (indicadores en una fila, 3 columnas en pantallas grandes y 2 en medianas, gráficos densos con más ancho, tabla a todo el ancho, panel lateral que no tape los gráficos); revisar CSV, panel y filtros en la dirección dentro de Streamlit.
- Restricciones: ninguna clave, contraseña ni cadena de conexión en el repositorio; el navegador no usa la clave pública en esta vista; la vista solo aparece con `DASHBOARD_INVENTARIO=1`; no cambiar el flujo de pedidos del prototipo ni nada de su dashboard salvo lo necesario para compartir el código; fijar `streamlit==1.65.0`; probar los tamaños 1366×768, 1920×1080, 2560×1440 y 375 px de uno en uno y cerrar cada proceso por su número.
- Decisiones de Bastián tras el plan: `st.iframe`, código compartido con marcadores, CSS ancho solo para el MVP, solución del panel y de los filtros en la URL, la bandera, y fijar la versión de Streamlit.

**Respuesta obtenida.**
- Plan evaluado: `st.components.v1.html` está obsoleto en la 1.65, y `st.iframe` mide el contenido. Alternativas descartadas con razones: reescribir en Plotly (cada clic sería un viaje al servidor, habría que reescribir `filtros.js` y sumar una dependencia) y `st.html` o componentes v2 (el código correría dentro de la página de Streamlit y chocaría con sus estilos).
- Código compartido: dos pares de marcadores en `prototipo/dashboard.html` (solo comentarios) y un «entorno» opcional en `prototipo/js/dashboard.js` (por omisión se comporta como antes).
- MVP: `src/ui_dashboard.py` (arma la página, escapa los datos y fija la política de seguridad por hash), `src/dashboard_incrustado/` (entorno, datos y CSS ancho), `src/views/dashboard.py`, el método `dashboard()` de `db.py` en SQLite y PostgreSQL, el menú y `?vista=dashboard`, el permiso del rol (en `mvp_rol.sql`, del Encargo 30), `requirements.txt` y `Dockerfile` (copia los archivos uno a uno, nunca `config.js`).
- Pruebas: `tests/test_ui_dashboard.py`, `tests/js/incrustado.test.js` y el contrato de `dashboard()` en `tests/test_contrato_repo.py`.

**Qué se aceptó y qué se corrigió.**
- El panel lateral del prototipo es fijo: en un iframe del alto total del contenido habría quedado anclado al final de la página. Se resolvió como se había propuesto: el iframe ocupa el alto de la ventana, con el contenido desplazándose dentro, y en pantallas anchas el panel se acopla a un lado.
- Corregido durante el trabajo: (1) mi primera captura «completa» salió del tamaño de la ventana, no del contenido, porque Streamlit desplaza su propio contenedor; se rehízo ampliando la ventana; (2) el iframe quedaba a 286 px del borde de la ventana: se compactó la fila del título con el botón «Actualizar datos» (224 px); (3) el selector «Operar como» del menú, de la etapa anterior, tenía texto blanco sobre fondo claro (ilegible); el primer arreglo de CSS no funcionó porque Streamlit 1.65 ya no usa `data-baseweb`, y se corrigió mirando el HTML real en el navegador; (4) una prueba mía comparaba objetos de un contexto aislado de Node con `deepEqual` estricto y fallaba por el prototipo; se comparan por contenido.
- Dejado fuera: nada de lo pedido. Queda como decisión de Bastián si, en pantallas medianas, el treemap debe seguir a ancho completo.
- Quedó apagado en público por decisión de Bastián, a la espera de la respuesta de Oscar (pregunta 4 de `docs/analisis-inventario.md`).

**Cómo se verificó.**
- `py -m pytest tests`: 248 pasan y 71 se omiten (las que necesitan un PostgreSQL de prueba). Con un PostgreSQL 16 local y desechable: 313 pasan y 6 se omiten. `node --test`: 38 pasan (30 del prototipo y 8 nuevas).
- Contra Supabase real (rol `app_mvp`, solo lectura): `inventario_dashboard()` devuelve 1.617 equipos y 319 extensiones con las 9 columnas permitidas.
- En Chrome sin ventana, con la aplicación local conectada a Supabase, un tamaño a la vez: 1366×768 (2 columnas), 1920×1080 y 2560×1440 (3 columnas) y 375 px (1 columna). En los cuatro: sin desplazamiento horizontal de la página ni del iframe, los 12 gráficos dibujados, ninguno aplastado (mínimo 300 px de alto), indicadores en una fila desde 720 px de ancho, y ningún error de consola (la política de seguridad no bloquea nada).
- En el navegador, a 1920 y a 375: el filtro de un indicador queda en la dirección de la página de Streamlit; abrir con `#estado=arrendado` restaura el filtro (243 equipos); el CSV descargado trae 244 líneas (243 más el encabezado), también con la política estricta; el panel se acopla sin tapar los gráficos a 1920 y es modal a 375; Escape lo cierra.
- Las otras vistas conservan su ancho (1120 px en Órdenes y Carga masiva) y el Dashboard usa el ancho completo. El prototipo, probado en el mismo navegador, da las mismas cifras (1.617, 899, 243, 195 y 280), 12 gráficos, su ancho de 1280 px y sus filtros en su propia dirección.
- Las capturas están en la carpeta temporal de la sesión, no en el repositorio (muestran el inventario real).
- **No se verificó:** otros navegadores distintos de Chrome ni un celular real; el MVP publicado en un hosting; una persona usándolo con el teclado o un lector de pantalla; la lectura de las etiquetas más pequeñas de los gráficos en todos los tamaños más allá de las capturas revisadas; la carga con muchas sesiones a la vez.

---

## Encargo 32. Portal para Vercel (entrada pública del proyecto)

**Objetivo.** Dejar Vercel como entrada pública del proyecto: Streamlit no corre en Vercel, así que Vercel publica una página estática mínima con un único botón hacia el MVP, en un proyecto de Vercel aparte. El prototipo sigue publicado en el suyo.

**Instrucción entregada.**
- Contexto: el MVP (Streamlit) se publicará en un hosting aparte, todavía por elegir; el prototipo ya fue evaluado; Vercel sigue sin estar conectado al repositorio correcto y no se da por resuelto.
- Intención: una carpeta `portal/` con título del proyecto, una frase de qué hace y un único botón «Abrir la aplicación» cuya dirección vive en una sola constante en un solo lugar; mientras esté vacía, el botón aparece desactivado con el texto «Aplicación en despliegue», para poder publicar el portal antes de que el MVP exista; mismo estilo del proyecto, responsive y en español; documentar en README y bitácora qué es el portal y dónde está la dirección del MVP; dar los pasos de Vercel.
- **Decisión posterior de Bastián (2026-11-23):** NO cambiar el proyecto `bodega-prototipo` (Root Directory = `prototipo`, Build Command = `node generar-config.mjs`): el prototipo debe seguir publicado para el video del README y para la prueba con usuarios. El portal va en un **segundo proyecto** de Vercel (`bodega-portal`), conectado al mismo repositorio, con Root Directory = `portal`, *Framework Preset* «Other», sin Build Command y sin variables de entorno. La primera versión de este encargo suponía cambiar el proyecto existente; se reescribieron los pasos en `portal/LEEME.md` y en el README, y se quitó el aviso de que el prototipo dejaría de mostrarse.
- Restricciones: no enlazar al prototipo ni a su dashboard; sin dependencias externas, sin claves y sin Supabase; no tocar nada en Vercel; commit aparte y sin abrir ningún pull request todavía.

**Respuesta obtenida.** `portal/` con `index.html`, `estilos.css`, `portal.js`, `config.js` (la constante `URL_APLICACION`), `icono.svg`, `vercel.json` (encabezados de seguridad, sin comandos de construcción) y `LEEME.md`; las pruebas `tests/test_portal.py` y `tests/js/portal.test.js`; las secciones del README («Portal público en Vercel», la estructura, el estado y el aviso sobre el prototipo); los pasos de Vercel con su forma de comprobarlos.

**Qué se aceptó y qué se corrigió.**
- Solo se aceptan direcciones `https` sin usuario ni contraseña en `config.js`; `javascript:`, `data:`, `http:`, direcciones relativas y direcciones con credenciales se ignoran y el botón queda desactivado. Es una decisión de la IA, no pedida, para que una dirección mal escrita no deje un botón que lleve a un lugar inesperado.
- Un solo botón visible en cada estado: el desactivado y el enlace son dos elementos del HTML, y `portal.js` deja visible solo uno. Sin JavaScript queda el desactivado y un aviso.
- La IA no editó los documentos de los avances ya evaluados que mencionan `bodega-prototipo.vercel.app` (`docs/prototipo.md`, `docs/pauta-validacion.md`, `docs/prueba-usuarios.md`, `docs/etica.md`): cambiarlos alteraría entregas evaluadas. Con la decisión de mantener el prototipo en su dirección, la IA revisó si siguen siendo correctos, **comprobando el sitio publicado** (solo lectura, con `curl` y comparando con el historial de git). Hallazgo: lo publicado hoy es exactamente el prototipo del 25 de octubre (los archivos coinciden con los commits `feef798`, `a3a330c` y `8b86288`): no tiene `api.js` ni `reglas.js` (sin conexión a Supabase), `/js/config.js` da 404 y `/dashboard.html` da 404. Por eso `docs/prototipo.md` y `docs/etica.md` (Avance 5) describen correctamente lo publicado, pero `docs/pauta-validacion.md`, `docs/prueba-usuarios.md` y el kit de la prueba (Avance 6) suponen la versión conectada (órdenes 3001 y 3002, «Reiniciar demo», base compartida) que todavía **no** está publicada: se publicará cuando `bodega-prototipo` se vuelva a conectar a `main` con sus dos variables. Quedó anotado en el README como pendiente aparte.
- Dos pruebas de la IA estaban mal planteadas (una exigía que `portal.js` nombrara la constante una sola vez, aunque la nombra también en un comentario) y se corrigieron para exigir lo que importa: que solo `config.js` la defina.
- El `vercel.json` no define `buildCommand`: el proyecto nuevo se crea sin Build Command, así que no hay nada que anular. No se pudo comprobar en Vercel qué hace un valor vacío frente al de la configuración del proyecto, y por eso no se usa.

**Cómo se verificó.**
- `tests/test_portal.py` (9 pruebas: una sola constante, sin enlace al prototipo, sin claves ni dependencias externas, sin código en línea, política de seguridad, un solo botón, `vercel.json`) y `tests/js/portal.test.js` (4 pruebas: dirección vacía o inválida desactiva el botón, una `https` válida lo convierte en enlace).
- En Chrome sin ventana, con el portal servido en el computador, en 375 px y 1366 px y con la dirección vacía y con una dirección de prueba (en una copia fuera del repositorio): siempre un único botón visible con el texto pedido, sin desplazamiento horizontal, sin errores de consola y sin más recursos que los cinco archivos del portal; el único enlace de la página es el de la constante. Los servidores y el navegador se cerraron por su número de proceso.
- **No se verificó:** nada en Vercel (ni la creación del proyecto nuevo, ni la conexión al repositorio, ni Root Directory, ni la publicación, ni que los encabezados de `vercel.json` se apliquen); la configuración interna de `bodega-prototipo` (solo se vio lo que publica, no su panel); otros navegadores ni un celular real; la dirección real del MVP, que no existe todavía.

