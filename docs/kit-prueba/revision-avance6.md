# Revisión del kit contra los criterios del Avance 6

Se revisó cada pieza del kit, y el instrumento que ya existía (`docs/prueba-usuarios.md` y `docs/pauta-validacion.md`), contra los **criterios de revisión**, los **errores frecuentes** y las **reglas de entrega** de las instrucciones del Avance 6. Es una revisión hecha leyendo y midiendo, no una nota: la evaluación la hace la profesora.

Estados: **Cumple**, **Observación** (cumple, pero hay algo que decidir o vigilar) e **Incumple**.

La primera revisión (14 de noviembre de 2026, por la mañana) encontró varias observaciones. El equipo tomó seis decisiones ese mismo día y se aplicaron; la sección 6 las lista. Las tablas de abajo muestran el **estado actual**.

## 1. Criterios de revisión (las cinco preguntas del enunciado)

| # | Criterio | Estado | Qué se vio |
|---|---|---|---|
| 1 | ¿La hipótesis puede resultar falsa y el umbral está fijado con un número antes de observar? | Cumple | Hay hipótesis, números (4 o 5 de 5, 3 minutos, SUS 68) y una frase que dice que no se moverán. Ahora los resultados se leen en **tres tramos para 5 personas** (4 o 5 se cumple, 3 entorpece, 2 o menos bloquea), así que no queda ninguna zona sin regla |
| 2 | ¿Cada tarea plantea escenario y objetivo sin nombrar botones ni pantallas, con un criterio de éxito que otra persona podría verificar en la grabación? | Cumple | Los escenarios no nombran botones ni pantallas; los nombres están solo en la columna «No revelar». El éxito de la tarea 2 ahora dice «la persona dice en voz alta cuál es el código marcado "no existe"», que se verifica de oído y sirve igual en un celular, donde no hay cursor. Depende de que la persona hable, por eso la pauta pide pensar en voz alta |
| 3 | ¿Los perfiles distinguen usuarios de stakeholders, se justifican y consideran a quien queda excluido según el Avance 5? | Cumple | U1 y U2 (el bodeguero de terreno, el excluido) son usuarios; S1 a S4 son stakeholders. No se recluta entre compañeros de curso. Cada perfil tiene número, cómo se contacta y por qué. Los stakeholders son 1 por perfil, no 5; está justificado en el documento |
| 4 | ¿La pauta incluye consentimiento, preguntas sobre hechos pasados y ninguna pregunta que sugiera la respuesta? | Observación | Incluye consentimiento y dos preguntas de contexto sobre la última vez (el enunciado pide dos o tres). Las dos preguntas que sugerían se reescribieron. Queda la frase 1 del SUS, por decisión del equipo (sección 2) |
| 5 | ¿El plan asigna los tres papeles, contempla sesiones de no más de 20 minutos, protege la evidencia fuera del repositorio y termina en una regla de decisión explícita? | Cumple | Facilitador, registrador y resguardo de evidencia, con roles y sin nombres; 20 minutos; carpeta de Drive con acceso restringido y fuera del repositorio; regla bloquea, entorpece y estético. El kit lo baja a pasos concretos (`plan-sesiones.md`) y a una hoja imprimible (`regla-decision.md`) |

## 2. Preguntas de la pauta frente a la regla «ninguna pregunta sugiere, pide una opinión sobre el futuro ni promueve una idea»

| Dónde | Pregunta original | Problema | Estado |
|---|---|---|---|
| Contexto, pregunta 3 | «Esa vez, ¿cómo revisó que los códigos de los equipos estuvieran bien escritos?» | **Sugería**: daba por hecho que la persona revisa los códigos y le ponía el foco justo en lo que la tarea 2 mide | **Reescrita** y ahora es la pregunta 2 de contexto: «Esa vez, antes de dejar lista la guía, ¿qué revisó?» |
| Contexto, pregunta 1 | «¿Cuándo fue la última vez que preparó o revisó una guía…? ¿Me cuenta cómo lo hizo, paso a paso?» | No sugería nada, pero era la más larga | **Quitada** para dejar holgura de tiempo |
| Cierre, pregunta 2 | «¿Qué hizo distinto de como lo hace hoy en su trabajo?» | **Daba por hecho** que hizo algo distinto y pedía comparar con una herramienta que el equipo propone | **Reescrita**: «Cuando lo hace en su trabajo, ¿en qué se parece o en qué no se parece a lo que acaba de hacer?» |
| Cuestionario SUS, frase 1 | «Le gustaría usar este sistema con frecuencia» | Pide una **opinión sobre el futuro**. Es una frase del SUS, que el propio enunciado exige | **Se queda**, por decisión del equipo. Se deja constancia en la bitácora de que se mantiene por ser parte de un instrumento estándar |

**Cómo se comprobó que las preguntas nuevas no introducen sesgo.** Se releyeron contra la regla del enunciado: ambas preguntan por hechos o por una comparación abierta, ninguna da por hecho una respuesta ni nombra una función de la herramienta. **Eso es una lectura, no una prueba con una persona:** el ensayo interno es donde se confirma que se entienden y que no empujan una respuesta.

## 3. Reglas de entrega y errores frecuentes

| Regla | Estado | Qué se vio |
|---|---|---|
| Pauta imprimible de no más de **2 planas** | Cumple | `docs/pauta-validacion.pdf` regenerado con el texto nuevo: **2 planas** (tamaño carta), contadas con `pypdf` |
| **Duración** de cada etapa y suma de **20 minutos o menos** | Observación | Las seis etapas suman ahora **19 minutos** (2 + 2 + 1 + 9 + 3 + 2): **1 minuto de holgura**. Se pidieron 2 o 3; con una pregunta menos y su minuto recortado no alcanza. Para llegar a 2 minutos habría que quitar otro minuto, por ejemplo la segunda pregunta de cierre. Se mide en el ensayo interno |
| Ambos archivos enlazados desde el README | Cumple | `prueba-usuarios.md` y `pauta-validacion.md` están en la lista de documentación |
| Ningún archivo con **nombres, teléfonos ni correos de personas reales** | Observación | `prueba-usuarios.md` y la pauta ya **no llevan nombres**: usan roles (integrante A y B). La lista de integrantes del README conserva los nombres por decisión del equipo, por ahora. Los correos y teléfonos del repositorio son ficticios (`@ejemplo.cl`, `+56 9 1111 1111`) y una prueba lo verifica en todos los archivos |
| Planilla vacía con las seis columnas | Cumple | `planilla_registro.csv`: participante, tarea, minuto, observado, interpretado, severidad |
| Bitácora con las entradas del período, y si se usó IA para redactar tareas o preguntas, cómo se comprobó que no introdujeran sesgo | Cumple | Los Encargos 17 y 18 cubren el instrumento y los Encargos 22 y 23 el kit y los cambios de redacción. La comprobación del sesgo está en la sección 2 de este documento |
| Error frecuente: **demostración disfrazada de prueba** | Cumple | Los escenarios no dicen qué tocar y la pauta prohíbe explicar la pantalla |
| Error frecuente: **preguntas de opinión** | Observación | Solo queda la frase 1 del SUS (sección 2) |
| Error frecuente: **umbral ausente o elástico** | Cumple | Tres tramos con números para 5 personas |
| Error frecuente: **perfiles genéricos o solo cercanos** | Cumple | Perfiles con número y contacto; máximo 1 conocido de 5 en U1 |
| Error frecuente: **sesiones extensas** | Observación | 19 minutos de 20. Se mide en el ensayo |
| Error frecuente: **datos personales en el repositorio y grabaciones sin acceso restringido** | Observación | Las grabaciones van a Drive restringido y el `.gitignore` bloquea video, audio y las carpetas de evidencia. **Riesgo que sí existe:** las observaciones con código quedan en el repositorio, que ven los cuatro integrantes, y uno trabaja en la bodega del caso. Con una muestra tan chica, una observación detallada puede delatar a quién se refiere. El consentimiento lo avisa y la regla es escribir las notas sin datos que permitan reconocer a nadie |

## 4. Las piezas del kit

| Pieza | Estado | Observación |
|---|---|---|
| `consentimiento.md` (qué se registra, para qué, quién lo ve, cuánto se conserva) | Observación | Cubre los cuatro puntos que pide la pauta, no pide nombre y dice lo mismo que el texto oral. **Diferencia:** la hoja avisa que las notas con código quedan en el repositorio; el texto oral de la pauta no lo dice. Si se quiere que coincidan, hay que agregar una frase al texto oral, que ya ocupa 2 minutos |
| `planilla_registro.csv` | Cumple | Seis columnas exactas, vacía. No valida los valores de severidad ni calcula los umbrales: eso es a mano |
| `ensayo-interno.md` | Cumple | Reproduce la recomendación del enunciado y agrega comprobaciones medibles, entre ellas confirmar las dos preguntas reescritas y la verificación de oído de la tarea 2 |
| `plan-sesiones.md` | Observación | Baja a pasos lo ya decidido sin contradecirlo. Tiene una **regla nueva** (una falla del sistema no cuenta a favor ni en contra) aceptada como propuesta y por confirmar en el ensayo |
| `regla-decision.md` | Cumple | Las tres categorías con la definición del enunciado, cómo clasificar en orden y los umbrales en tres tramos; una prueba comprueba que los números coinciden con los de `prueba-usuarios.md` |
| `linea-base.md` y la herramienta | Cumple | No son parte del Avance 6 (es un complemento): definen el indicador del Avance 2 y cómo medir su línea base |

## 5. Qué no se pudo verificar

- **El ensayo real.** Nadie leyó la pauta en voz alta con una persona: los tiempos por etapa son los del documento, no medidos. Tampoco se probó con una persona el texto de las preguntas reescritas.
- **Que otra persona pueda verificar el criterio de éxito mirando una grabación.** Hace falta tener una grabación.
- **La validez de la hoja de consentimiento** ante una organización que la exija: no la revisó nadie con competencia para ello. Si la piden en términos formales, corresponde el certificado del profesor y de la Universidad que menciona el enunciado.
- **Cómo la evalúa la profesora.** Esta revisión lee el enunciado; no lo interpreta por ella.

## 6. Decisiones del equipo (14 de noviembre de 2026) y cambios aplicados

| # | Decisión | Qué se cambió |
|---|---|---|
| 1 | Quitar los nombres de `prueba-usuarios.md` y usar roles; en el README, dejar la autoría por ahora | La tabla de la sección 5 usa facilitador, registrador y resguardo de evidencia, con el integrante A y el integrante B. El README no se tocó |
| 2 | Reescribir la pregunta 3 de contexto y la 2 de cierre; el SUS 1 se queda | Las dos preguntas se reescribieron como estaban propuestas |
| 3 | Umbral en tres tramos para 5 personas: 4 o 5 se cumple, 3 entorpece, 2 o menos bloquea | En `prueba-usuarios.md` (hipótesis, tabla de tareas y una tabla de lectura) y en `regla-decision.md` |
| 4 | Quitar una pregunta de contexto para dejar 2 o 3 minutos de holgura, y regenerar el PDF | Se quitó la pregunta 1 de contexto. La suma bajó de 20 a 19 minutos (1 minuto de holgura, no 2 o 3). El PDF se regeneró: 2 planas |
| 5 | Tarea 2: cambiar «señala con el cursor o en voz alta» por «dilo en voz alta» | El criterio de éxito dice «la persona dice en voz alta cuál es el código marcado "no existe"» |
| 6 | Aceptar la regla de fallas del sistema como propuesta | Quedó escrita como propuesta aceptada, por confirmar en el ensayo, en `prueba-usuarios.md`, `plan-sesiones.md` y `regla-decision.md` |

**Qué se decidió al aplicarlas, y conviene confirmar**
- **Pregunta de contexto que se quitó.** Se quitó la 1 («cuénteme paso a paso»), porque es la más larga y la más general; las dos que quedan (cómo se enteró de un cambio y qué revisó) son las que se relacionan con las tareas. La pregunta 3 reescrita pasó a ser la 2.
- **Tramos de la tarea 2.** Los tres tramos se definieron para la tarea 1. Se aplicaron igual a «se dan cuenta solas del código malo». A «terminan sin ayuda en menos de 5 minutos», que ya tenía el umbral de 3 de 5, se le agregaron por analogía los tramos de 2 de 5 (entorpece) y de 1 o menos (bloquea). Esa fila es una extensión mía, marcada como tal en los dos documentos.
- **Cambio de umbral.** Antes se fallaba con «2 o más no lo logran», es decir, con 3 o menos que lo logran. Ahora solo bloquea con 2 o menos que lo cumplen, y con 3 entorpece. Es un umbral más permisivo en ese punto. Se cambia **antes de la primera sesión**, que es lo que permite el enunciado.
- **Una inconsistencia que se encontró y se resolvió.** El plan de sesiones decía que el integrante que trabaja en la bodega del caso no estaba presente en las sesiones con su gente, pero le asignaba registrar mirando la grabación; y la hoja de consentimiento le promete a los participantes que esa persona no ve las grabaciones. Se resolvió protegiendo al participante: en esas sesiones registra **quien facilitó, después**, y el integrante de la bodega no tiene ningún papel. Es un cambio al plan que ya estaba; si se prefiere el original, hay que cambiar también el consentimiento.
