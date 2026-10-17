"""Pantalla 5: Guía generada."""

import streamlit as st

import ui_datos
from ui_components import banner, ficha_guia, mostrar, titulo
from ui_nav import boton_volver, ir

PROXIMAMENTE = "Próximamente"


def render(app):
    ss = st.session_state
    folio = ss.folio
    mostrar(titulo("Guía generada", "La guía está lista para descargar."))

    guia = ss.guias.get(folio) if folio else None
    if not guia:
        mostrar(banner("info", "Esta orden aún no tiene guía emitida", "Valida la orden y emite la guía desde el resultado de la validación."))
        boton_volver("← Volver a la validación", "validacion", "volver_validacion")
        return

    resumen = app.obtener_resumen_ordenes()
    fila = resumen[resumen["folio"] == folio].iloc[0]
    orden = app.obtener_orden(folio)
    inventario = app.obtener_inventario()
    descripciones = dict(zip(inventario["sku"], inventario["descripcion"]))

    mostrar(
        banner(
            "ok",
            "Guía generada correctamente",
            "La guía de despacho o retiro quedó emitida y se puede descargar en esta sesión.",
        )
    )

    col_ficha, col_acciones = st.columns([1.6, 1])
    with col_ficha:
        mostrar(
            ficha_guia(
                [
                    ("N° de guía", guia["numero"]),
                    ("Fecha de emisión", ui_datos.fecha_emision(guia["fecha"])),
                    ("Tipo de movimiento", f"{fila['tipo_movimiento']} ({fila['modalidad']})"),
                    ("Total de equipos", len(orden)),
                ]
            )
        )
    with col_acciones:
        texto = app.generar_guia_despacho(
            folio, fila["tipo_movimiento"], fila["modalidad"], list(orden["sku"]), descripciones
        )
        st.download_button(
            "Descargar guía (.txt)",
            data=texto.encode("utf-8"),
            file_name=f"guia_{folio}.txt",
            mime="text/plain",
            type="primary",
            key="guia_descargar",
            use_container_width=True,
        )
        st.button(f"Descargar PDF · {PROXIMAMENTE}", key="guia_pdf", disabled=True, use_container_width=True, help=PROXIMAMENTE)
        st.button(f"Enviar por correo · {PROXIMAMENTE}", key="guia_correo", disabled=True, use_container_width=True, help=PROXIMAMENTE)
        st.button("Ver historial", key="guia_historial", on_click=ir, args=("historial",), use_container_width=True)
        st.button("Volver a órdenes", key="guia_ordenes", on_click=ir, args=("ordenes",), use_container_width=True)
