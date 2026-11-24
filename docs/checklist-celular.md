# Chequeo del prototipo en un celular real

El prototipo se usa en una bodega, con poca señal y con gente apurada. Esta lista es para ejecutarla **en un celular real con datos móviles** y anotar qué pasa. Lo que se puede revisar sin celular ya se revisó (sección 4); lo que no, queda aquí.

Se prueba el prototipo conectado a Supabase ([`docs/poc-supabase.md`](poc-supabase.md)), con datos de ejemplo. Es una revisión técnica y de uso, **no** la prueba con usuarios: la hace alguien del equipo, sin pauta ni consentimiento.

## 1. Antes de salir

- [ ] **El sitio publicado es la versión conectada.** Se abre el enlace del prototipo y la primera pantalla muestra las órdenes 3001 y 3002 y, al pie, «Datos de ejemplo, guardados en una base compartida». Si dice **«Falta la configuración de la base de datos»**, todavía no está configurado en Vercel (variables `SUPABASE_URL` y `SUPABASE_PUBLISHABLE_KEY` y el comando de construcción) y no se puede probar.
- [ ] **Datos móviles, sin Wi-Fi.** Se apaga el Wi-Fi del celular.
- [ ] **Nadie más usa la demo** mientras dura la revisión: los datos son compartidos.
- [ ] **Grabación de pantalla con micrófono activado** y, si el sistema lo permite, **«mostrar toques»** activado. Sin cámara. La grabación se guarda en la carpeta privada de Drive, no en el repositorio.
- [ ] **No molestar** activado, para que no aparezcan mensajes personales en la grabación.
- [ ] Cronómetro a mano.
- [ ] Se anota el **modelo del celular y el navegador con su versión** (por ejemplo, «Android 14, Chrome 130»). No se anota el número de teléfono ni ningún dato de la persona.

## 2. Recorrido

Se marca cada paso, se cronometra y se anota cualquier cosa rara. «Esperado» es lo que debería pasar.

### Camino normal

| Paso | Qué hacer | Esperado | Anotar |
|---|---|---|---|
| 1 | Presionar **Reiniciar demo** | Aviso «Demo reiniciada: las órdenes volvieron a su estado inicial» | Segundos que tarda |
| 2 | Abrir el enlace desde cero (cerrar la pestaña y volver) | Aparece «Cargando las órdenes…» y luego la pantalla con la orden 3001 y 4 productos | Segundos hasta ver las órdenes |
| 3 | **Cargar pedido** con la orden 3001 | Pasa a validar, con los 4 productos «Pendiente» y «Preparar guía» bloqueado | Segundos |
| 4 | **Validar** | «4 de 4 productos ok» y «Preparar guía» habilitado | Segundos |
| 5 | **Preparar guía** | Pantalla «Guía lista» con el número interno y «Lista para pasar al ERP» | Segundos |
| 6 | **Descargar para el ERP** | Se descarga el archivo y aparece «Archivo descargado» | Dónde queda el archivo y si se puede abrir |
| 7 | **Reiniciar demo**, elegir la orden **3002** y **Cargar pedido** | La orden 3002 es un **retiro**: pide «Motivo del retiro» y no «Modalidad» | |
| 8 | **Validar** | Un producto en rojo con «✕ no existe» y el texto «No está en el inventario…»; «Preparar guía» bloqueado | Si se entiende sin el color |
| 9 | **Registrar cambio**. El sistema sugiere un motivo según el problema del producto: **cambiarlo a mano a «Elige un motivo»** y guardar | Error junto al campo: «Elige el motivo del cambio.» No se guarda | Si el mensaje queda a la vista o hay que desplazarse |
| 10 | Elegir el equipo `SD-63A20-0315`, un motivo, y **Guardar cambio** | Vuelve a validar con la línea nueva destacada: «Cambiado por …, reemplaza a SD-63A20-9999» | Segundos |
| 11 | **Validar** y **Preparar guía** | «4 de 4 productos ok» y guía lista, sin el producto que no existía | |

### Robustez

| Paso | Qué hacer | Esperado | Anotar |
|---|---|---|---|
| R1 | **Corte de señal al guardar.** Con el cambio listo para guardar, activar el modo avión y tocar **Guardar cambio** | Aviso «No hay conexión con la base de datos. Lo que escribiste sigue aquí…». Lo elegido no se borra y el botón vuelve a quedar activo | Mensaje exacto y cuánto tarda en aparecer (debería ser de hasta 10 segundos) |
| R2 | **Reintento.** Apagar el modo avión y tocar de nuevo **Guardar cambio** | Se guarda **una sola vez**: en la validación aparece un único «Cambiado por …» | Cuántos cambios aparecen |
| R3 | **Doble toque** rápido en **Cargar pedido** y en **Guardar cambio** | Una sola acción; el botón se desactiva mientras trabaja | Si quedó algo duplicado |
| R4 | **Señal débil** (si se puede: un lugar con poca cobertura o el limitador de red del celular) | Los botones muestran que están trabajando; si pasan 10 segundos, el aviso de conexión | Qué se ve mientras espera |
| R5 | **Girar el celular** a horizontal en cada pantalla | Nada se corta ni se superpone | Qué pantalla falla |
| R6 | **Teclado.** Tocar el área de los productos | El campo sigue a la vista y se puede llegar al botón | Si el teclado tapa algo |
| R7 | **Letra grande.** Subir el tamaño de letra del sistema al máximo | Se puede leer y tocar todo, sin desplazamiento horizontal | Qué se rompe |
| R8 | **Brillo** al máximo y, si se puede, al aire libre | Se distingue el estado de cada producto | Si el verde y el rojo se confunden |
| R9 | **Pegar una lista de más de 60 productos** desde el portapapeles | Contador en rojo y mensaje «Hay N productos y el máximo es 60…» | |
| R10 | **Recargar la página** estando en la validación | Vuelve a «Cargar pedido» sin errores. Es una limitación conocida: la pantalla no recuerda dónde estaba, aunque los datos siguen en la base | Si asusta o confunde |
| R11 | Botón **Atrás** del celular desde la validación y desde registrar cambio | Vuelve a la pantalla anterior sin errores | |

Al terminar: **Reiniciar demo**, para dejar la demo como estaba.

## 3. Qué anotar

| Anotar | Cómo |
|---|---|
| **Tiempos** | La columna «Anotar» de cada paso, en segundos |
| **Errores** | El mensaje exacto, tal como se ve, y en qué paso apareció. Una captura de pantalla, guardada fuera del repositorio |
| **Qué se entendió mal** | Qué se creyó que iba a pasar y qué pasó. Se anota **lo que se creyó**, no lo que se debería haber creído |
| **Dedos** | Botones que se tocaron sin querer, texto demasiado chico, campos que cuesta tocar |
| **Condiciones** | Modelo, navegador, tipo de red (4G, 5G), cuánta señal y si fue en interior o al aire libre |

Resumen para el equipo: una tabla con los pasos que **fallaron**, el mensaje exacto y el modelo del celular. Va a la bitácora o a un documento del equipo, sin capturas que muestren datos personales.

## 4. Lo que ya se verificó sin celular

Revisado el **14 de noviembre de 2026** con el navegador de escritorio, **simulando pantallas de 360 × 640 y 390 × 844** (el prototipo se carga dentro de un marco de ese tamaño exacto, así que se aplican las reglas CSS de ese ancho), contra una réplica de la base escrita solo para probar la pantalla. Se recorrieron **16 estados** en cada tamaño: cargar pedido (inicial, con error de listado vacío y de 61 productos, retiro), validar (pendiente, todo ok, con un producto que no existe, con una línea cambiada), la guía, registrar cambio (formulario, con errores, con la conexión perdida), y las pantallas de «sin órdenes» y de «error al cargar».

| Revisión | Resultado en los dos tamaños |
|---|---|
| Sin desplazamiento horizontal ni elementos fuera del ancho | Cumple |
| Sin texto cortado | Cumple |
| Botones, enlaces y campos de **44 px de alto o más** (87 controles visibles revisados) | Cumple: el más bajo mide 44 px |
| **Contraste del texto** de 4,5:1 o más (324 textos revisados, con la fórmula de WCAG) | Cumple: el más bajo es 5,63:1 |
| **Contraste de los bordes** de campos y botones de 3:1 o más | Cumplía en todos menos uno: el borde del campo «Cliente» (solo lectura) medía 1,59:1. Se corrigió y ahora el más bajo es 4,37:1 |
| **Ningún estado depende solo del color**: el producto que no existe lleva «✕ no existe» y una explicación escrita; la línea cambiada dice «Cambiado por…»; los errores llevan «✕» y texto | Cumple |
| Letra de los campos de **16 px o más** (si no, el iPhone amplía la pantalla al enfocarlos) | Cumple |
| La página permite hacer zoom | Cumple |

**Corrección hecha:** solo CSS, en un commit aparte: el borde del campo de solo lectura pasó a ser discontinuo y con el color de borde normal. No se tocó la lógica ni ninguna regla de validación.

**Cómo se comprobó que la revisión sirve:** se inyectó a propósito un elemento más ancho que la pantalla, un botón de 30 px, un texto gris claro, una línea en rojo sin texto y una pastilla vacía. La revisión detectó los cinco problemas, y sin ellos solo marcó el borde del campo «Cliente».

**Una observación, no un defecto:** en la pantalla de validación el botón **Preparar guía** queda debajo de la primera pantalla de un celular de 640 px de alto, así que hay que desplazarse. Es esperable con cuatro productos y empeora con una lista larga; conviene mirarlo en el celular real (pasos 4 y 8).

## 5. Lo que no se pudo verificar

- **Un celular real.** No se probó el toque con el dedo, el teclado virtual, la barra del navegador que aparece y desaparece, ni las pantallas con muesca.
- **Señal real.** El corte de conexión y el fallo interno se simularon cortando la red del navegador, no con una cobertura mala de verdad. Tampoco se midió cuánto tarda la base en responder con 4G débil.
- **Otros navegadores.** Solo Chrome de escritorio. Falta Safari de iPhone, Chrome de Android, Firefox y Samsung Internet.
- **Dos personas a la vez.** Los datos son compartidos y no se probó qué pasa si dos personas usan la demo al mismo tiempo (una puede pisar lo de la otra).
- **El sitio publicado en Vercel.** Esta revisión usó una copia local. No se verificó que el enlace publicado tenga la configuración puesta.
- **Lector de pantalla, modo oscuro y rotación.** Solo se revisó que los mensajes estén en el texto de la página y que los campos tengan su etiqueta.
- **Lo que ve la persona real.** El contraste se calculó con los colores del CSS; no se midió sobre la pantalla de un celular con brillo bajo o al sol (paso R8).
