"""
Piezas de interfaz reutilizables (HTML escapado, iconos, tablas, avisos).

Todo texto que viene de la base de datos o del usuario (SKU, responsable, motivo,
folio) pasa por esc() antes de llegar a HTML. Solo las cadenas marcadas como Html
(construidas en este modulo) se insertan sin escapar.
"""

import html as _html

import streamlit as st


class Html(str):
    """Texto HTML ya construido por este modulo: no se vuelve a escapar."""


def esc(valor):
    """Escapa un valor para insertarlo como texto dentro de HTML."""
    return _html.escape("" if valor is None else str(valor), quote=True)


def _celda(valor):
    return valor if isinstance(valor, Html) else Html(esc(valor))


def _svg(trazo, tam=20):
    return Html(
        f'<svg viewBox="0 0 24 24" width="{tam}" height="{tam}" fill="none" stroke="currentColor" '
        f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{trazo}</svg>'
    )


# Trazos de los iconos (propios, formas genericas). El menu los reutiliza como mascara CSS.
TRAZOS = {
    "logo": '<path d="M12 2l9 5v10l-9 5-9-5V7z"/><path d="M12 12l9-5M12 12L3 7M12 12v10"/>',
    "ordenes": '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4h6v3H9z"/><path d="M8 11h8M8 15h5"/>',
    "carga": '<path d="M12 3l9 5-9 5-9-5 9-5z"/><path d="M3 13l9 5 9-5"/>',
    "validador": '<rect x="4" y="4" width="16" height="16" rx="3"/><path d="M8.5 12.5l2.5 2.5 4.5-5"/>',
    "ajuste": '<path d="M4 8h14l-3-3M20 16H6l3 3"/>',
    "historial": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "ok": '<circle cx="12" cy="12" r="10"/><path d="M7.5 12.5l3 3 6-7"/>',
    "alerta": '<path d="M12 3l10 18H2L12 3z"/><path d="M12 10v5M12 18v.5"/>',
    "error": '<circle cx="12" cy="12" r="10"/><path d="M9 9l6 6M15 9l-6 6"/>',
    "info": '<circle cx="12" cy="12" r="10"/><path d="M12 11v6M12 7.5v.5"/>',
    "doc": '<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5M10 13h6M10 17h6"/>',
    "trazabilidad": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    "eficiencia": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "conectada": '<circle cx="9" cy="9" r="3"/><circle cx="17" cy="10" r="2.5"/><path d="M3.5 19c.5-3 2.7-5 5.5-5s5 2 5.5 5M15 15c2.5-.4 4.7 1 5.5 4"/>',
}


def icono(nombre, tam=20):
    return _svg(TRAZOS[nombre], tam)


def pill(texto, tono):
    """Etiqueta de estado. tono: pendiente, revision, completada, ok, error, aviso, prox, neutro."""
    return Html(f'<span class="bp-pill bp-pill-{esc(tono)}">{esc(texto)}</span>')


def tabla(columnas, filas, clase=""):
    """
    Tabla HTML de solo lectura.
    columnas: lista de (titulo, clase_css). filas: lista de listas de celdas (texto o Html).
    """
    cabecera = "".join(f'<th class="{esc(c)}">{esc(t)}</th>' for t, c in columnas)
    cuerpo = "".join(
        "<tr>" + "".join(f'<td class="{esc(columnas[i][1])}">{_celda(v)}</td>' for i, v in enumerate(fila)) + "</tr>"
        for fila in filas
    )
    if not filas:
        cuerpo = f'<tr><td class="bp-vacio" colspan="{len(columnas)}">Sin datos para mostrar.</td></tr>'
    return Html(
        f'<div class="bp-tabla-wrap {esc(clase)}"><table class="bp-tabla"><thead><tr>{cabecera}</tr></thead>'
        f"<tbody>{cuerpo}</tbody></table></div>"
    )


def banner(tipo, titulo, texto=""):
    """Aviso destacado. tipo: ok, aviso, error, info."""
    icono_nombre = {"ok": "ok", "aviso": "alerta", "error": "error", "info": "info"}[tipo]
    detalle = f"<span>{esc(texto)}</span>" if texto else ""
    return Html(
        f'<div class="bp-banner bp-banner-{esc(tipo)}" role="status">'
        f'<span class="bp-banner-icono">{icono(icono_nombre, 30)}</span>'
        f"<div><strong>{esc(titulo)}</strong>{detalle}</div></div>"
    )


def datos(items):
    """Cuadricula de pares etiqueta / valor. items: lista de (etiqueta, valor)."""
    celdas = "".join(f"<div><dt>{esc(e)}</dt><dd>{_celda(v)}</dd></div>" for e, v in items)
    return Html(f'<dl class="bp-datos">{celdas}</dl>')


def mostrar(contenido):
    """Dibuja HTML construido por este modulo. Va siempre envuelto en un bloque <div> (no se interpreta como markdown)."""
    st.markdown(str(contenido), unsafe_allow_html=True)
