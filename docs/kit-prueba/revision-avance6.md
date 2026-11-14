# Revisión del kit contra los criterios del Avance 6

Se revisó cada pieza del kit, y el instrumento que ya existía (`docs/prueba-usuarios.md` y `docs/pauta-validacion.md`), contra los **criterios de revisión**, los **errores frecuentes** y las **reglas de entrega** de las instrucciones del Avance 6. Es una revisión hecha leyendo y midiendo, no una nota: la evaluación la hace la profesora.

Estados: **Cumple**, **Observación** (cumple, pero hay algo que decidir o corregir) e **Incumple**.

## 1. Criterios de revisión (las cinco preguntas del enunciado)

| # | Criterio | Estado | Qué se vio |
|---|---|---|---|
| 1 | ¿La hipótesis puede resultar falsa y el umbral está fijado con un número antes de observar? | Observación | Hay hipótesis, números (4 de 5, 3 minutos, SUS 68) y una frase que dice que no se moverán. **Observación:** el umbral y el «nos equivocamos si» no son complementarios. Si 2 de 5 personas terminan la tarea 1 sin ayuda pero en más de 3 minutos, ni se cumple el umbral ni se cumple el fracaso. Conviene escribir una regla para esa zona intermedia (por ejemplo, «lo que no cumple el umbral no confirma la hipótesis») antes de la primera sesión |
| 2 | ¿Cada tarea plantea escenario y objetivo sin nombrar botones ni pantallas, con un criterio de éxito que otra persona podría verificar en la grabación? | Observación | Los escenarios no nombran botones ni pantallas, y los nombres de los botones están solo en la columna «No revelar». **Observación:** el éxito de la tarea 2 dice que la persona «señala, con el cursor o en voz alta, el código marcado "no existe"». En un **celular no hay cursor**, y la grabación de pantalla no siempre muestra los toques: ahí el criterio depende de la voz. Hay que activar «mostrar toques» en el celular o pedir expresamente que lo diga en voz alta |
| 3 | ¿Los perfiles distinguen usuarios de stakeholders, se justifican y consideran a quien queda excluido según el Avance 5? | Cumple | U1 y U2 (el bodeguero de terreno, el excluido) son usuarios; S1 a S4 son stakeholders. No se recluta entre compañeros de curso. Cada perfil tiene número, cómo se contacta y por qué. Los stakeholders son 1 por perfil, no 5; está justificado en el documento |
| 4 | ¿La pauta incluye consentimiento, preguntas sobre hechos pasados y ninguna pregunta que sugiera la respuesta? | Observación | Incluye consentimiento y preguntas sobre la última vez. **Tres preguntas rozan la regla**, detalladas en la sección 2 |
| 5 | ¿El plan asigna los tres papeles, contempla sesiones de no más de 20 minutos, protege la evidencia fuera del repositorio y termina en una regla de decisión explícita? | Cumple | Facilita, registra y guarda la evidencia; 20 minutos; carpeta de Drive con acceso restringido y fuera del repositorio; regla bloquea, entorpece y estético. El kit lo baja a pasos concretos (`plan-sesiones.md`) y a una hoja imprimible (`regla-decision.md`) |

## 2. Preguntas de la pauta que rozan la regla «ninguna pregunta sugiere, pide una opinión sobre el futuro ni promueve una idea»

| Dónde | Pregunta | Problema | Cambio propuesto (no aplicado) |
|---|---|---|---|
| Contexto, pregunta 3 | «Esa vez, ¿cómo revisó que los códigos de los equipos estuvieran bien escritos?» | **Sugiere**: da por hecho que la persona revisa los códigos y le pone el foco justo en lo que la tarea 2 va a medir | «Esa vez, antes de dejar lista la guía, ¿qué revisó?» |
| Cierre, pregunta 2 | «¿Qué hizo distinto de como lo hace hoy en su trabajo?» | **Da por hecho** que hizo algo distinto, y pide comparar con una herramienta que el equipo propone | «Cuando lo hace en su trabajo, ¿en qué se parece o en qué no se parece a lo que acaba de hacer?» o dejarla fuera |
| Cuestionario SUS, frase 1 | «Le gustaría usar este sistema con frecuencia» | Pide una **opinión sobre el futuro**. Es una frase del SUS, que el propio enunciado exige | Se deja: es parte de un instrumento estándar y el enunciado lo pide. Se puede dejar constancia en la bitácora de que se mantiene por eso |

No se modificó la pauta: son preguntas que el equipo diseñó y ensayó, y cambiar su redacción cambia lo que se mide. Se deja la decisión al equipo, idealmente en el ensayo interno.

## 3. Reglas de entrega y errores frecuentes

| Regla | Estado | Qué se vio |
|---|---|---|
| Pauta imprimible de no más de **2 planas** | Cumple | `docs/pauta-validacion.pdf` regenerado desde el texto actual: **2 planas** (tamaño carta), contadas con `pypdf` |
| **Duración** de cada etapa y suma ≤ 20 minutos | Observación | Las seis etapas suman **exactamente 20** (2 + 3 + 1 + 9 + 3 + 2). La regla del enunciado (consentimiento + contexto + tareas + SUS) da 17, así que se cumple, pero **sin holgura**: leer diez frases del SUS en 3 minutos es justo. Se mide en el ensayo interno |
| Ambos archivos enlazados desde el README | Cumple | `prueba-usuarios.md` y `pauta-validacion.md` están en la lista de documentación |
| Ningún archivo con **nombres, teléfonos ni correos de personas reales** | Incumple | **Nombres de integrantes del equipo** en el plan de sesiones de `prueba-usuarios.md` (sección 5) y en la lista de integrantes del README. Si se lee la regla en sentido literal («personas reales»), incumple. Los correos y teléfonos del repositorio son ficticios (`@ejemplo.cl`, `+56 9 1111 1111`) y se verificó con un barrido de todos los archivos. Pendiente de decisión del equipo; el kit no lleva ningún nombre |
| Planilla vacía con las seis columnas | Cumple | `planilla_registro.csv`: participante, tarea, minuto, observado, interpretado, severidad |
| Bitácora con las entradas del período, con objetivo, instrucción, respuesta, qué se aceptó y cómo se verificó; si se usó IA para redactar tareas o preguntas, cómo se comprobó que no introdujeran sesgo | Observación | Los Encargos 17 y 18 cubren el instrumento. **Falta dejar constancia** de cómo se comprobó que las preguntas de la pauta no sugieren la respuesta: la sección 2 de este documento es esa comprobación |
| Error frecuente: **demostración disfrazada de prueba** | Cumple | Los escenarios no dicen qué tocar y la pauta prohíbe explicar la pantalla |
| Error frecuente: **preguntas de opinión** | Observación | Ver sección 2 |
| Error frecuente: **umbral ausente o elástico** | Observación | Ver criterio 1 (zona intermedia sin regla) |
| Error frecuente: **perfiles genéricos / solo cercanos** | Cumple | Perfiles con número y contacto; máximo 1 conocido de 5 en U1 |
| Error frecuente: **sesiones extensas** | Observación | Ver duración |
| Error frecuente: **datos personales en el repositorio y grabaciones sin acceso restringido** | Observación | Las grabaciones van a Drive restringido y el `.gitignore` bloquea video, audio y las carpetas de evidencia. **Riesgo que sí existe:** las observaciones con código quedan en el repositorio, que ven los cuatro integrantes, y uno trabaja en la bodega del caso. Con una muestra tan chica, una observación detallada puede delatar a quién se refiere. El consentimiento lo avisa y la regla es escribir las notas sin datos que permitan reconocer a nadie |

## 4. Las piezas del kit

| Pieza | Estado | Observación |
|---|---|---|
| `consentimiento.md` (qué se registra, para qué, quién lo ve, cuánto se conserva) | Observación | Cubre los cuatro puntos que pide la pauta, no pide nombre y dice lo mismo que el texto oral. **Diferencia:** la hoja avisa que las notas con código quedan en el repositorio; el texto oral de la pauta no lo dice. Si se quiere que coincidan, hay que agregar una frase al texto oral, que ya ocupa 2 minutos |
| `planilla_registro.csv` | Cumple | Seis columnas exactas, vacía. No valida los valores de severidad (bloquea, entorpece, estético) ni calcula los umbrales: eso es a mano |
| `ensayo-interno.md` | Cumple | Reproduce la recomendación del enunciado (ensayar con alguien que no diseñó las tareas y descubrir las tareas ambiguas) y agrega comprobaciones medibles |
| `plan-sesiones.md` | Observación | Baja a pasos lo ya decidido sin contradecirlo. Introduce una **regla nueva** (una falla del sistema no cuenta a favor ni en contra de los umbrales) que está marcada como propuesta, porque los umbrales ya están fijados y cambiarlos después de ver resultados está prohibido |
| `regla-decision.md` | Cumple | Las tres categorías con la definición del enunciado, cómo clasificar en orden y los umbrales resumidos; una prueba comprueba que los números coinciden con los de `prueba-usuarios.md` |
| `linea-base.md` y la herramienta | Cumple | No son parte del Avance 6 (es un complemento): definen el indicador del Avance 2 y cómo medir su línea base |

## 5. Qué no se pudo verificar

- **El ensayo real.** Nadie leyó la pauta en voz alta con una persona: los tiempos por etapa son los del documento, no medidos.
- **Que otra persona pueda verificar el criterio de éxito mirando una grabación.** Hace falta tener una grabación.
- **La validez de la hoja de consentimiento** ante una organización que la exija: no la revisó nadie con competencia para ello. Si la piden en términos formales, corresponde el certificado del profesor y de la Universidad que menciona el enunciado.
- **Cómo la evalúa la profesora.** Esta revisión lee el enunciado; no lo interpreta por ella.
