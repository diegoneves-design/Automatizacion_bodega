"""Pantalla 3: Resultado de validación (criterio de la HU-01: sin guía mientras haya SKU con problemas)."""

from datetime import datetime

import streamlit as st

import ui_datos
from ui_components import banner, mostrar, pill, tabla, titulo
from ui_nav import boton_volver, ir, mostrar_aviso

COLUMNAS_CSV = ["sku", "descripcion", "stock_disponible", "tipo_movimiento", "modalidad", "resultado"]


def _emitir(app, folio):
    """Callback: emite la guia solo si no queda ningun SKU con problemas."""
    validos, total = ui_datos.contar_validos(app.validar_orden(folio))
    if total == 0 or validos != total:
        return
    st.session_state.guias.setdefault(folio, {"numero": folio, "fecha": datetime.now()})
    ir("guia", folio)


def render(app):
    ss = st.session_state
    folio = ss.folio
    boton_volver("← Volver al detalle", "detalle", "volver_detalle")
    mostrar(titulo("Resultado de validación", "Revisa el estado de cada SKU y corrige si es necesario."))
    mostrar_aviso()

    validada = app.validar_orden(folio) if folio else None
    if validada is None or validada.empty:
        mostrar(banner("info", "No hay equipos para validar", "Elige una orden con equipos desde Órdenes."))
        return

    ss.validadas.add(folio)
    validos, total = ui_datos.contar_validos(validada)
    con_problemas = validos != total

    if con_problemas:
        mostrar(banner("error", "Validación con diferencias", f"{validos} de {total} SKU son válidos."))
    else:
        mostrar(banner("ok", "Validación completada", f"{validos} de {total} SKU son válidos."))

    filas = []
    primer_problema = None
    for i, f in enumerate(validada.itertuples(), start=1):
        etiqueta, tono, detalle = ui_datos.describir_resultado(f.resultado, f.stock_disponible)
        if tono != "ok" and primer_problema is None:
            primer_problema = f.sku
        filas.append([i, f.sku, f.descripcion if isinstance(f.descripcion, str) else "—", pill(etiqueta, tono), detalle])
    mostrar(
        tabla(
            [("#", "bp-oculto-movil"), ("SKU", "bp-sku"), ("Equipo", ""), ("Estado", ""), ("Detalle", "")],
            filas,
        )
    )

    if con_problemas:
        mostrar(
            banner(
                "aviso",
                "No se puede emitir la guía",
                "Existen SKU con problemas. Corrige la información para continuar.",
            )
        )

    c_volver, c_corregir, c_emitir = st.columns(3)
    c_volver.button("← Volver", key="validacion_volver", on_click=ir, args=("detalle",), use_container_width=True)
    if con_problemas:
        c_corregir.button(
            "Corregir SKU",
            key="validacion_corregir",
            type="primary",
            on_click=ir,
            args=("ajuste", folio, primer_problema),
            use_container_width=True,
        )
    if folio in ss.guias:
        c_emitir.button(
            "Ver guía →", key="validacion_ver_guia", type="primary", on_click=ir, args=("guia", folio), use_container_width=True
        )
    else:
        c_emitir.button(
            "Emitir guía →",
            key="validacion_emitir",
            type="primary",
            on_click=_emitir,
            args=(app, folio),
            disabled=con_problemas,
            use_container_width=True,
        )

    columnas = [c for c in COLUMNAS_CSV if c in validada.columns]
    st.download_button(
        "Descargar validación (CSV)",
        data=ui_datos.neutralizar_csv(validada[columnas]).to_csv(index=False).encode("utf-8"),
        file_name=f"validacion_{folio}.csv",
        mime="text/csv",
        key="validacion_csv",
    )
