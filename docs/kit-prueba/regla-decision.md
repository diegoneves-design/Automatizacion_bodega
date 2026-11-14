# Regla de decisión

Hoja para tener a mano durante el análisis. A cada observación de la planilla se le asigna **una** severidad, según lo que la persona logró y no según lo que a nosotros nos parece.

| Severidad | Cómo se reconoce | Qué se hace | Cuándo |
|---|---|---|---|
| **Bloquea** | La persona **no completa la tarea sin ayuda**: pidió ayuda, se rindió o la tarea quedó a medias | Se corrige en el prototipo **antes de construir** esa parte de la aplicación | Primero |
| **Entorpece** | **Completa** la tarea, pero con dudas, desvíos o errores | Se ordena por **cuántas personas lo vivieron**: lo que le pasó a **2 o más de 5** va primero | Después de lo que bloquea |
| **Estético** | Completa y solo le **incomoda** algo (un color, un texto, el orden) | Se **anota y espera**. No se corrige en esta etapa | Más adelante |

## Cómo clasificar, en este orden

1. ¿Completó la tarea **sin ayuda**? Si **no**, es **bloquea**. Fin.
2. Si la completó, ¿dudó, se desvió, se equivocó o dijo algo que muestra que entendió mal? Si **sí**, es **entorpece**.
3. Si la completó sin tropiezos pero algo le molestó, es **estético**.
4. Si nada de eso pasó, no se anota como problema.

**Cuenta como ayuda** cualquier cosa que le diga a la persona qué hacer: señalarle algo, nombrarle un botón, decirle «va bien». Repetir el escenario **no** cuenta.

## Ejemplos

| Severidad | Ejemplo |
|---|---|
| Bloquea | No encuentra cómo cambiar el código que no existe y pide ayuda |
| Entorpece | Vuelve dos veces a la pantalla anterior antes de lograr validar; o lee «Registrar cambio» y duda si eso guarda algo |
| Estético | Comenta que un color le parece fuerte, pero termina la tarea sin problema |

## Los umbrales no se mueven

Están en la sección 2 de [`docs/prueba-usuarios.md`](../prueba-usuarios.md) y se fijaron **antes de ver a ningún participante**. No se cambian después de ver los resultados.

- **U1, tarea 1:** al menos **4 de 5** la terminan sin ayuda, en menos de **3 minutos** y con 1 desvío como máximo.
- **U1, tarea 2:** al menos **4 de 5** se dan cuenta solas del código malo, y **3 de 5** terminan sin ayuda en menos de **5 minutos** y con 2 desvíos como máximo.
- **Satisfacción:** puntaje SUS promedio de **68 o más** en U1.
- **Nos equivocamos si** 2 o más de 5 no logran la tarea 1 sin ayuda, o 2 o más no ven el código malo.
- **U2** (quien queda fuera) se informa **aparte** y no cuenta para el umbral de U1: si **3 o más de 5** piden ayuda o dejan la tarea a medias, se confirma que lo dejamos fuera; si 3 o más la terminan solas, nos equivocamos.

**Regla propuesta, a confirmar por el equipo antes de la primera sesión:** una falla del sistema (el prototipo se cae) no es una observación sobre la persona. Se anota aparte, no cuenta ni a favor ni en contra de los umbrales y la tarea se repite en otra sesión.
