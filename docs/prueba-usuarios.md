# Diseño de prueba de usuarios · Automatizacion_bodega

Grupo 6 · Avance 6

Hasta ahora, todo lo que sabemos del [prototipo](https://bodega-prototipo.vercel.app) lo hemos juzgado nosotros mismos. Uno de nosotros trabaja en la bodega del caso, y eso nos ayuda a entender el problema, pero también nos puede hacer creer que algo se entiende solo porque a nosotros nos parece obvio. Por eso queremos ver qué pasa cuando lo usa alguien que nunca lo ha visto.

Esta prueba todavía no se hace. Aquí dejamos escrito qué vamos a observar, con quién y qué resultado consideraríamos un fracaso, antes de ver a ningún participante. El guion que se lee en cada sesión está en [docs/pauta-validacion.md](pauta-validacion.md).

## 1. Objetivo, hipótesis y alcance

**Pregunta.** ¿Una persona que arma guías en una bodega puede validar un pedido, corregir un equipo que no corresponde y dejar la guía lista para el ERP, sin que nadie le explique cómo?

**Hipótesis.** Creemos que un jefe o subjefe de bodega, sin ninguna explicación previa, puede revisar un pedido, darse cuenta de que un código no existe y corregirlo antes de dejar la guía lista. Lo sabremos cuando observemos que al menos 4 de 5 personas del perfil U1 terminan la tarea 1 sin ayuda en menos de 3 minutos, y que al menos 4 de 5 se dan cuenta solas del código que no existe en la tarea 2.

**Nos equivocamos si** 2 o más de esas 5 personas no logran la tarea 1 sin ayuda, o si 2 o más no ven el código malo y se quedan intentando avanzar sin entender por qué la guía no se deja preparar.

**Una segunda hipótesis, sobre a quién dejamos fuera.** En el Avance 5 dijimos que el bodeguero de terreno queda excluido, porque no arma guías y casi no usa computador en su trabajo ([docs/etica.md](etica.md), B1). Creemos que, si le damos la tarea 2, va a necesitar ayuda. Lo sabremos cuando 3 o más de 5 personas del perfil U2 pidan ayuda o dejen la tarea a medias. Si 3 o más la terminan solas, nos equivocamos sobre quién queda fuera, y hay que revisar el riesgo 1 de `docs/etica.md`.

**Lo que esta prueba no puede responder.**
- El prototipo funciona con datos de ejemplo y no está conectado a nada. No sirve para saber si el sistema funciona técnicamente, si el inventario está al día ni si la guía la acepta el ERP o el SII.
- No compara el prototipo con la forma en que se trabaja hoy, en papel, ni mide cuánto se demora una guía real.
- No prueba lo que el prototipo todavía no tiene, como cargar un archivo, iniciar sesión o los permisos de cada área.

## 2. Tareas, métricas y umbral

Elegimos dos tareas y no tres, porque con tres la sesión pasaba de los 20 minutos y no es justo pedirle más tiempo a alguien que está en plena jornada. Las dos salen del flujo principal. La primera es un día normal y la segunda es el problema que más se repite en la bodega, un pedido que viene con un código malo.

| Tarea | HU | Escenario (se lee tal cual, sin nombrar la pantalla) | Objetivo | Éxito (se puede comprobar en la grabación) | No revelar | Umbral |
|---|---|---|---|---|---|---|
| **T1 · Un despacho sin problemas** | HU-02, HU-01 (escenario principal), HU-05 | "Le llegó por correo el pedido de despacho de la Constructora Andes, orden 3001. Antes de armar la guía, revise que todo lo pedido se pueda despachar y déjela lista para pasarla al ERP." | Cargar el pedido 3001, comprobar que los 4 productos se pueden despachar y llegar a la guía lista | En la pantalla aparece la guía de la orden 3001 con 4 productos y el mensaje "Lista para pasar al ERP" | Que primero hay que cargar el pedido y después validarlo, el nombre de los botones ("Cargar pedido", "Validar", "Preparar guía") y cuántas pantallas tiene | 4 de 5 personas de U1 la terminan sin ayuda, en menos de 3 minutos y equivocándose de camino 1 vez como máximo |
| **T2 · Un retiro con un código que no corresponde** | HU-01 (escenario alternativo), HU-03, HU-04 | "Ahora le toca el retiro de la Minera Cordillera, orden 3002. Mantenimiento le confirmó que la extensión que corresponde retirar es la de 63 amperes y 20 metros número 0315. Deje la guía de ese retiro lista para el ERP." | Darse cuenta de que `SD-63A20-9999` no existe, cambiarlo por la extensión 0315 dejando el motivo, volver a validar y llegar a la guía lista | La persona señala, con el cursor o en voz alta, el código marcado "no existe". El cambio queda registrado con su motivo, y aparece la guía de la orden 3002 con "Lista para pasar al ERP" | Que hay un código mal escrito y cuál es, que la guía queda bloqueada, el botón "Registrar cambio" y dónde se elige el equipo que entra | 4 de 5 personas de U1 se dan cuenta solas del código malo. 3 de 5 terminan la tarea sin ayuda, en menos de 5 minutos y equivocándose de camino 2 veces como máximo |

### Qué vamos a medir en cada tarea

| Métrica | Qué miramos | Cómo lo anotamos |
|---|---|---|
| **Eficacia** | Si la termina sola, si la termina con ayuda o si no la termina | Al final de cada tarea, en la planilla de la sección 5 |
| **Tiempo** | Los minutos que pasan desde que terminamos de leer el escenario hasta que se cumple el criterio de éxito | Con el reloj de la grabación |
| **Ayudas** | Cuántas veces pide ayuda o quien facilita tiene que intervenir | Una fila por cada ayuda |
| **Desvíos** | Cuántas veces entra a una pantalla o toca algo que no la acerca a lo que tiene que hacer | Una fila por cada desvío |
| **Satisfacción** | El puntaje SUS, de 0 a 100, una sola vez al final de la sesión | Con el cuestionario de la pauta. **Esperamos un promedio de 68 o más en U1** |

Contamos como **ayuda** cualquier cosa que le diga a la persona qué hacer, como señalarle algo, nombrarle un botón o decirle "va bien". Si nos pide que le repitamos el escenario, eso no cuenta como ayuda.

**Estos números los fijamos ahora, antes de cualquier sesión, y no los vamos a mover después de ver los resultados.** Los resultados de U2 los informamos aparte, porque responden a la segunda hipótesis y no cuentan para el umbral de U1.

## 3. Perfiles y reclutamiento

No vamos a invitar a compañeros del curso ni a nadie del equipo. En el repositorio nunca aparecerá el nombre ni el contacto de un participante. Cada uno es un código (P01, P02…).

| Perfil | Usuario o stakeholder | N.º | Cómo se contacta | Por qué representa a quien usará la solución |
|---|---|---|---|---|
| **U1 · Jefe, subjefe o encargado de bodega que arma guías de despacho** | Usuario (hace las tareas) | 5 | Hasta 2 en la bodega del caso, si la jefatura lo autoriza (si piden algo formal, usamos el certificado que ofrece la profesora). Al menos 3 en otras empresas de arriendo de equipos o de bodegaje, a través de contactos de trabajo de uno de nosotros, como proveedores, transportistas y excompañeros. Si invitamos a un conocido, lo dejamos anotado en la planilla y no puede ser más de 1 de los 5 | Son quienes hoy digitan las guías en el ERP y quienes reciben los cambios de último minuto. En el mapa de impacto del Avance 5 son quienes ejecutan la tarea |
| **U2 · Bodeguero de terreno, cercano a la tercera edad, que anota en papel lo que sale y vuelve** | Usuario (hace las tareas) | 5 | Hasta 3 en la bodega del caso, con la misma autorización. Al menos 2 en otras bodegas del rubro, por los mismos contactos | Es **quien queda fuera** según el Avance 5. No tiene cuenta, le cuesta la tecnología y lo que anota en papel no llega al sistema. Si no lo probamos con él, nunca vamos a saber si de verdad lo dejamos fuera |
| **S1 · Gerente de administración** | Stakeholder (se le consulta) | 1 | Por correo, con autorización de la jefatura | Es quien autoriza los procedimientos y recibe el reporte cuando una guía se anula. Sin su visto bueno, la herramienta no se usa |
| **S2 · Supervisor de mantenimiento** | Stakeholder (se le consulta) | 1 | En persona, en la empresa del caso | De su área sale la mayoría de los cambios de último minuto (HU-03) |
| **S3 · Supervisor de operaciones o coordinador logístico** | Stakeholder (se le consulta) | 1 | En persona, en la empresa del caso | Organiza a la gente que sale a terreno y es quien espera la guía, y cuando la guía se rehace, a su equipo le toca salir tarde |
| **S4 · Ejecutivo comercial** | Stakeholder (se le consulta) | 1 | En persona o por videollamada | Manda el pedido de venta y también pide cambios. Sin él, el listado ni siquiera llega a bodega |

**Por qué un solo stakeholder por área y no cinco.** Cada uno trae una restricción distinta (autorizar, cambiar, salir a terreno y vender), y en la empresa del caso hay una sola persona en cada uno de esos cargos. Si se puede, sumamos a alguien del mismo cargo en otra empresa del rubro.

**A los stakeholders no les pedimos hacer las tareas.** Les hacemos tres preguntas, en no más de 10 minutos, siempre sobre cosas que ya pasaron.
1. "La última vez que una guía tuvo que anularse o rehacerse, ¿qué pasó después y quién tuvo que intervenir?"
2. "La última vez que se empezó a usar una herramienta o una planilla nueva en la bodega, ¿qué tuvo que cumplir para que se aprobara?"
3. "La última vez que un cambio de último minuto llegó a su área, ¿cómo quedó registrado?"

## 5. Plan de levantamiento de feedback

Vamos a hacer **10 sesiones con usuarios** (5 de U1 y 5 de U2) y **4 consultas a stakeholders**. Cada sesión con usuarios dura 20 minutos como máximo, repartidos como indica la pauta, y cada consulta a stakeholders, 10 minutos como máximo.

Para la prueba vamos a estar dos integrantes. Hay algo que nos importa cuidar. Uno de nosotros está a cargo de la bodega del caso, y si él les hace las preguntas a sus propios compañeros, lo más probable es que se sientan evaluados por su jefe y no se atrevan a equivocarse. Por eso **él no facilita ni está presente en las sesiones con su gente**, ni en la del conocido, si lo incluimos.

| Sesión | Facilita (la única persona que habla con el participante) | Registra | Guarda la evidencia |
|---|---|---|---|
| Participantes de la bodega del caso, y el conocido del equipo | Sebastián Carmona | Oscar Ynchaustegui, **después de la sesión**, mirando la grabación | Sebastián Carmona |
| Participantes de otras empresas | Oscar Ynchaustegui | Sebastián Carmona, en vivo | Sebastián Carmona |
| Consultas a stakeholders | Oscar Ynchaustegui | Sebastián Carmona, en vivo | Sebastián Carmona |

**Cómo grabamos.** Solo la pantalla y la voz del computador o celular en que se usa el prototipo, **nunca la cara**. Empezamos a grabar después de leer el consentimiento y solo si la persona dice que sí. El sí queda grabado en voz, sin decir su nombre.

**Dónde guardamos todo.** En una carpeta de Drive del curso a la que solo entramos los dos integrantes que hacemos la prueba y la profesora. **Nada de esto se sube al repositorio ni se enlaza desde él.** Las grabaciones se borran al terminar el semestre. En el repositorio solo quedan las observaciones, con el código de cada participante.

**Planilla de registro** (vacía, con una fila por cada cosa que observemos)

| Participante | Tarea | Minuto | Observado | Interpretado | Severidad |
|---|---|---|---|---|---|
| | | | | | |
| | | | | | |
| | | | | | |

- **Observado.** Lo que la persona hizo o dijo, tal cual. Por ejemplo, "vuelve dos veces a la pantalla donde se carga el pedido".
- **Interpretado.** Lo que nosotros creemos que significa, siempre en otra columna. Por ejemplo, "no encuentra dónde se valida".
- **Severidad.** Bloquea, entorpece o estético, según la regla que sigue.

**Cómo vamos a decidir qué corregir**
- **Bloquea** (no la termina sin ayuda). Se corrige en el prototipo **antes de construir** esa parte de la aplicación.
- **Entorpece** (la termina, pero con dudas o errores). Se ordena según **cuántas personas lo vivieron**, y lo que le pasó a 2 o más de 5 va primero.
- **Estético** (la termina y solo le molesta algo). Se anota y **espera**. No lo corregimos en esta etapa.
