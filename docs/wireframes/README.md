# Wireframes

Grupo 6 · Automatizacion_bodega · Entrega 4

**Estado: Especificación en texto; los PNG de Figma están pendientes (Grupo B).**

Este documento describe en texto cuatro pantallas del MVP pensadas para celular, en formato vertical de 360 x 800. No hay imágenes todavía: cuando el Grupo B termine los wireframes en Figma (blanco y negro), se exportan como PNG y se suben a esta carpeta con estos nombres:

`W1_carga_masiva.png` · `W2_validador.png` · `W3_ajuste.png` · `W4_guia_emitida.png`

Son un diseño objetivo, no una descripción de la app actual. La app actual (Streamlit) tiene tres vistas y no separa la guía emitida en una pantalla propia.

Los requisitos de uso en celular de cada pantalla salen de un ensayo con personajes ficticios (guantes, sol, una mano, señal débil). Son **hipótesis por validar con la entrevista real**, que todavía no se ha hecho.

## Resumen

| Pantalla | Historias | Navegación |
|---|---|---|
| W1 Carga del listado | H01 | Cargar → W2 |
| W2 Validación | H02, H03, H07 | Emitir guía → W4 · Ajustar → W3 |
| W3 Ajuste de último minuto | H05, H06 | Confirmar → W2 |
| W4 Guía emitida | H04 | Nueva orden → W1 |

Las historias están en `docs/historias-usuario/historias_usuario.md`.

## Reglas comunes

- Solo blanco, negro y grises. Sin colores, sin imágenes decorativas.
- Cada pantalla lleva su título, su historia de origen y una flecha por acción con la pantalla destino.
- Si una historia no justifica una pantalla, la pantalla sobra.
- Requisitos de uso en celular, válidos para las cuatro pantallas (hipótesis):
  - **Botones grandes**, con la acción principal abajo, al alcance del pulgar.
  - **Alto contraste**, con texto grande; los estados se indican con texto y no solo con color.
  - **Pocos pasos:** una acción principal por pantalla y los campos justos.
  - **Señal débil:** si se pierde la señal, la pantalla avisa qué quedó guardado y qué no, y no pierde lo ingresado.

---

## W1 · Carga del listado

**Historia:** H01

**Objetivo.** Que el encargado de mantenimiento cargue el listado de SKU de una orden.

**Elementos** (de arriba hacia abajo)
1. Título "Carga del listado".
2. Campo "Folio".
3. Selector "Tipo de movimiento" (Despacho o Retiro).
4. Selector "Modalidad" (depende del tipo).
5. Área de texto "Listado de SKU" (uno por línea), con opción de pegar.
6. Botón grande "Cargar", abajo.

**Datos que muestra:** folio, tipo de movimiento, modalidad y listado de SKU.

**Navegación:** Cargar → W2.

**Anotaciones**
- Campos obligatorios: folio, tipo, modalidad y listado.
- Lo que ocurre pero no se ve: al cargar, la orden queda guardada con su fecha y hora.
- Camino alternativo: sin SKU, no se carga y avisa "Falta el listado de SKU".

**Uso en celular:** pegar el listado debe ser lo más corto posible; evitar escribir a mano. Al perder la señal, el listado ingresado no se borra y se avisa que no se pudo cargar.

---

## W2 · Validación

**Historias:** H02, H03, H07

**Objetivo.** Que el jefe de bodega vea el resultado de cada SKU y decida si emite la guía o ajusta.

**Elementos** (de arriba hacia abajo)
1. Título "Validación" y folio de la orden.
2. Estado de la orden (por ejemplo, "Sin diferencias" o "Bloqueada").
3. Lista de SKU, una tarjeta por SKU, con su resultado.
4. Bloque "Cambios de último minuto", con los SKU cambiados destacados.
5. Botón "Ajustar".
6. Botón grande "Emitir guía", abajo.

**Datos que muestra:** cada SKU con su resultado (OK o su motivo), los cambios de último minuto con fecha, hora y responsable, y el estado de la orden.

**Navegación:** Emitir guía → W4 · Ajustar → W3.

**Anotaciones**
- Lo que ocurre pero no se ve: la validación cruza el listado con el inventario.
- Orden de la lista: primero los SKU con problema, después los OK.
- Camino alternativo: si un SKU no existe, la orden queda bloqueada y "Emitir guía" queda deshabilitado, con el motivo a la vista.
- H07: quien cargó la orden ve aquí por qué quedó bloqueada.

**Uso en celular:** una tarjeta por SKU en vez de una tabla ancha; el resultado va en texto grande.

---

## W3 · Ajuste de último minuto

**Historias:** H05, H06

**Objetivo.** Reemplazar un equipo de la orden y ver el historial de cambios.

**Elementos** (de arriba hacia abajo)
1. Título "Ajuste de último minuto" y folio.
2. Selector "SKU anterior".
3. Selector o campo "SKU nuevo".
4. Campo "Responsable".
5. Campo "Motivo" (opcional).
6. Lista "Historial de cambios".
7. Botón grande "Confirmar", abajo.

**Datos que muestra:** SKU anterior, SKU nuevo, responsable y el historial de cambios de la orden.

**Navegación:** Confirmar → W2.

**Anotaciones**
- Campos obligatorios: SKU anterior, SKU nuevo y responsable. El motivo es opcional (así está en la app y en `docs/datos/estructura_datos.md`).
- Lo que ocurre pero no se ve: el cambio queda registrado con fecha, hora y responsable, y el equipo anterior no se borra.
- Orden de la lista: el historial, por fecha.
- Camino alternativo: si el SKU nuevo no existe, se rechaza el cambio y se mantiene el equipo original. Si no hay cambios, el historial dice "Sin cambios registrados".

**Uso en celular:** elegir el SKU de una lista en vez de escribirlo; el responsable debe poder completarse sin pedir clave en cada paso (hipótesis).

---

## W4 · Guía emitida

**Historia:** H04

**Objetivo.** Mostrar la guía emitida y dejarla disponible para descargar.

**Elementos** (de arriba hacia abajo)
1. Título "Guía emitida".
2. Número de guía.
3. Datos de la guía: tipo, cantidad de SKU, fecha de emisión y usuario que emite.
4. Botón "Descargar guía".
5. Botón grande "Nueva orden", abajo.

**Datos que muestra:** número de guía, tipo, cantidad de SKU, fecha de emisión y usuario que emite.

**Navegación:** Nueva orden → W1.

**Anotaciones**
- Lo que ocurre pero no se ve: la guía queda guardada asociada a la orden.
- Camino alternativo: si la orden está bloqueada, la guía no se genera y no se llega a esta pantalla.

**Uso en celular:** si se pierde la señal al emitir, la pantalla avisa si la guía quedó guardada o no, y no deja emitir dos veces sin avisar.
