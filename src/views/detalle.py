"""Pantalla 2: Detalle de la orden."""

import streamlit as st

import db
import ui_datos
from ui_components import banner, ficha_orden, mostrar, pill, subtitulo, tabla, titulo
from ui_nav import avisar, boton_volver, ir, mostrar_aviso


def _validar(repo, folio):
    """Callback: pide la validacion a la base (queda guardada) y abre el resultado."""
    try:
        repo.validar(folio)
    except (db.ReglaDeNegocio, db.ErrorDeBase) as e:
        avisar("error", getattr(e, "mensaje", str(e)))
        return
    ir("validacion", folio)


def render(repo):
    ss = st.session_state
    folio = ss.folio
    boton_volver("← Volver a órdenes", "ordenes", "volver_ordenes")
    mostrar(titulo("Detalle de la orden", "Revisa los equipos y valida su información."))
    mostrar_aviso()

    orden = repo.orden(folio) if folio else None
    if orden is None:
        mostrar(banner("info", "No hay una orden seleccionada", "Elige una desde Órdenes."))
        return

    etiqueta, tono = ui_datos.estado_visible(orden["estado"])
    et_modalidad = "Modalidad" if orden["tipo_movimiento"] == "Despacho" else "Motivo del retiro"
    mostrar(
        ficha_orden(
            folio,
            pill(etiqueta, tono),
            [
                ("Tipo de movimiento", orden["tipo_movimiento"]),
                (et_modalidad, orden["modalidad"]),
                ("Cliente", orden["cliente"] or "-"),
                ("Fecha", ui_datos.fecha_corta(orden["fecha_carga"])),
            ],
        )
    )

    lineas = repo.lineas(folio)
    mostrar(subtitulo(f"Equipos en la orden ({len(lineas)})"))

    filas = []
    for i, f in enumerate(lineas.itertuples(), start=1):
        et, tn, _ = ui_datos.describir_resultado_base(f.resultado, f.estado_equipo)
        filas.append(
            [
                i,
                f.sku,
                f.descripcion if isinstance(f.descripcion, str) else "—",
                pill(et, tn),
                ui_datos.texto_o_guion(f.ultima_modificacion, ui_datos.fecha_hora_corta),
            ]
        )
    mostrar(
        tabla(
            [("#", "bp-oculto-movil"), ("SKU", "bp-sku"), ("Equipo", ""), ("Estado", ""), ("Última modificación", "")],
            filas,
        )
    )

    _, col_boton = st.columns([3, 1.4])
    if orden["estado"] == "emitida":
        col_boton.button("Ver guía →", key="ver_guia", type="primary", on_click=ir, args=("guia", folio), use_container_width=True)
    else:
        col_boton.button(
            "Validar SKUs →",
            key="validar_skus",
            type="primary",
            on_click=_validar,
            args=(repo, folio),
            use_container_width=True,
            disabled=lineas.empty,
        )
