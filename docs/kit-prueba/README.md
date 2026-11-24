# Kit de la prueba con usuarios

Lo que hace falta para **ejecutar** la prueba diseñada en el Avance 6. El diseño (hipótesis, tareas, métricas, umbrales, perfiles) y el guion no se repiten aquí: están en [`docs/prueba-usuarios.md`](../prueba-usuarios.md) y [`docs/pauta-validacion.md`](../pauta-validacion.md), y si algo de este kit los contradice, mandan ellos. El kit solo agrega las piezas operativas.

La prueba **todavía no se ha hecho**. Todo lo de esta carpeta está escrito, no usado.

## Contenido

| Pieza | Para qué sirve | Se imprime |
|---|---|---|
| [`consentimiento.md`](consentimiento.md) | Hoja de información y consentimiento: qué se registra, para qué, quién lo ve y cuánto se conserva. Sin espacio para el nombre | Sí ([PDF](consentimiento.pdf)) |
| [`planilla_registro.csv`](planilla_registro.csv) | Planilla vacía de observaciones: participante, tarea, minuto, observado, interpretado, severidad | No |
| [`ensayo-interno.md`](ensayo-interno.md) | Checklist para ensayar la pauta completa dentro del equipo y descubrir qué tarea es ambigua | Opcional |
| [`plan-sesiones.md`](plan-sesiones.md) | Quién hace qué en cada sesión, cómo se graba, dónde se guarda, qué hacer si algo sale mal | Opcional |
| [`regla-decision.md`](regla-decision.md) | Hoja con la regla bloquea, entorpece y estético y los umbrales | Sí ([PDF](regla-decision.pdf)) |
| [`revision-avance6.md`](revision-avance6.md) | Revisión de todo contra los criterios del Avance 6: qué cumple y qué no | No |
| [Pauta imprimible](../pauta-validacion.pdf) | El guion de cada sesión, en 2 planas | Sí |

Fuera de esta carpeta, pero parte de lo mismo: [`docs/linea-base.md`](../linea-base.md) (cómo medir cuánto demora hoy una guía a mano) y [`docs/checklist-celular.md`](../checklist-celular.md) (la prueba en un celular real).

## En qué orden se usa

1. **Revisar lo decidido y lo pendiente** en [`revision-avance6.md`](revision-avance6.md): qué se cambió el 14 de noviembre de 2026 y qué sigue abierto.
2. **Pedir los permisos.** Si la persona trabaja en una organización que exige autorización, pedir al profesor el certificado (por correo, con la organización y la persona a quien se dirige) o invitar a alguien del mismo cargo en otra empresa.
3. **Ensayar** con [`ensayo-interno.md`](ensayo-interno.md) hasta que no quede ninguna tarea ambigua y la suma esté por debajo de los 20 minutos (la pauta suma 19).
4. **Preparar el material**: imprimir la pauta, el consentimiento y la regla de decisión, y revisar [`plan-sesiones.md`](plan-sesiones.md).
5. **Hacer las sesiones**, una persona a la vez y con **Reiniciar demo** entre una y otra.
6. **Analizar** con [`regla-decision.md`](regla-decision.md): primero lo que bloquea, después lo que entorpece según cuántas personas lo vivieron, y lo estético espera.

## Coherencia con la ficha de datos y con los 24 meses

La ficha de tratamiento de datos de [`docs/etica.md`](../etica.md) propone conservar **24 meses desde la emisión de la guía** los datos del **sistema** (órdenes, cambios y guías, con el nombre de quien los registra). Ese plazo **no se aplica a esta prueba**, que no guarda ningún dato de ninguna empresa: el prototipo usa datos de ejemplo.

| Qué | Cuánto se conserva | Dónde |
|---|---|---|
| Datos del sistema futuro (guías, cambios, quién los registra) | 24 meses desde la emisión de la guía (propuesta, a confirmar con administración) | `docs/etica.md`, ficha B2 |
| Grabaciones de la prueba (pantalla y voz) | Hasta el fin del semestre; después se borran | Drive privado, fuera del repositorio |
| Observaciones de la prueba (con código, sin datos personales) | Mientras dure el proyecto | Repositorio |
| Mediciones de la línea base (sin nombres) | El archivo, en Drive; solo el resumen va al repositorio | [`docs/linea-base.md`](../linea-base.md) |

El consentimiento le dice a cada participante lo que le corresponde a él (grabaciones y observaciones), no el plazo del sistema, que no lo toca. Si el equipo cambia el plazo de los 24 meses, esta tabla y la ficha se actualizan juntas.

## Qué hay que mantener fuera del repositorio

Grabaciones, archivos de mediciones reales, la lista que une códigos con personas y cualquier nombre, correo o teléfono. El `.gitignore` bloquea los archivos de video y audio y las carpetas `evidencia/` y `datos-medicion/`, pero no es una garantía: antes de cada commit se mira `git status`.
