"""Pantalla 1: Órdenes del día."""

from datetime import datetime

import streamlit as st

import ui_datos
from ui_components import banner, esc, mostrar, pill, titulo
from ui_nav import ir, mostrar_aviso

# Ancho de la cuadricula de datos frente al del boton "Ver detalle"
PROPORCION = [8.2, 1.5]
ENCABEZADOS = ["N° orden", "Tipo", "Modalidad", "Equipos", "Estado"]


def _fila_html(fila, estado):
    """Datos de una orden como cuadricula HTML (5 columnas en escritorio, 2 en celular)."""
    return (
        '<div class="bp-orden-grid">'
        f'<div class="bp-orden-folio"><div class="bp-folio">{esc(fila.folio)}</div>'
        f'<div class="bp-sub">{esc(ui_datos.fecha_corta(fila.fecha_carga))}</div></div>'
        f'<div class="bp-celda" data-et="Tipo">{esc(fila.tipo_movimiento)}</div>'
        f'<div class="bp-celda" data-et="Modalidad">{esc(fila.modalidad)}</div>'
        f'<div class="bp-celda" data-et="Equipos">{esc(int(fila.skus_vigentes))}</div>'
        f'<div class="bp-celda" data-et="Estado">{pill(estado, ui_datos.TONO_ESTADO[estado])}</div>'
        "</div>"
    )


def render(app):
    ss = st.session_state
    mostrar(titulo("Órdenes del día", "Selecciona la orden que deseas gestionar."))

    mostrar_aviso()

    resumen = app.obtener_resumen_ordenes()
    con_cambios = set(app.obtener_log_cambios()["folio"])
    emitidas = set(ss.guias)

    col_buscar, col_fecha = st.columns([3, 1.3])
    texto = col_buscar.text_input(
        "Buscar orden", key="buscar", placeholder="Buscar por número de orden…", label_visibility="collapsed"
    )
    fecha = col_fecha.date_input(
        "Fecha", value=datetime.now().date(), key="fecha_filtro", format="DD/MM/YYYY", label_visibility="collapsed"
    )

    del_dia = ui_datos.filtrar_ordenes(resumen, "todas", texto, fecha)
    total, despachos, retiros = ui_datos.contar_por_tipo(del_dia)
    etiquetas = {"todas": f"Todas ({total})", "Despacho": f"Despacho ({despachos})", "Retiro": f"Retiro ({retiros})"}
    tipo = st.radio(
        "Tipo de movimiento",
        options=list(etiquetas),
        format_func=etiquetas.get,
        key="filtro_tipo",
        horizontal=True,
        label_visibility="collapsed",
    )
    visibles = ui_datos.filtrar_ordenes(del_dia, tipo)

    if visibles.empty:
        if resumen.empty:
            mostrar(banner("info", "Aún no hay órdenes", "Carga una desde Carga masiva."))
        elif del_dia.empty:
            mostrar(
                banner(
                    "info",
                    "No hay órdenes para esta fecha",
                    f"Hay {len(resumen)} en otras fechas: cambia la fecha para verlas.",
                )
            )
        else:
            mostrar(banner("info", "Ninguna orden coincide con el filtro"))
        return

    with st.container(border=True):
        izq, der = st.columns(PROPORCION)
        izq.markdown(
            '<div class="bp-orden-grid bp-cabecera">' + "".join(f"<div>{esc(t)}</div>" for t in ENCABEZADOS) + "</div>",
            unsafe_allow_html=True,
        )
        der.markdown('<div class="bp-cabecera">Acciones</div>', unsafe_allow_html=True)

        for fila in visibles.itertuples():
            estado = ui_datos.estado_orden(fila.folio, con_cambios, emitidas)
            izq, der = st.columns(PROPORCION)
            izq.markdown(_fila_html(fila, estado), unsafe_allow_html=True)
            der.button(
                "Ver detalle",
                key=f"ver_{fila.folio}",
                type="primary",
                on_click=ir,
                args=("detalle", fila.folio),
                use_container_width=True,
            )
