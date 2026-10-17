"""Historial de cambios de última hora (todas las órdenes)."""

import streamlit as st

import ui_datos
from ui_components import banner, mostrar, tabla, titulo

COLUMNAS_CSV = ["folio", "sku_original", "sku_nuevo", "responsable", "fecha_hora", "motivo"]


def render(app):
    mostrar(titulo("Historial", "Cambios de última hora registrados. El SKU original nunca se borra."))

    log = app.obtener_log_cambios()
    if log.empty:
        mostrar(banner("info", "Aún no hay cambios registrados", "Aparecerán aquí cuando reemplaces un SKU."))
        return

    log = log.sort_values("id", ascending=False)
    filas = [
        [ui_datos.fecha_hora_corta(f.fecha_hora), f.folio, f.sku_original, f.sku_nuevo, f.responsable, f.motivo or "—"]
        for f in log.itertuples()
    ]
    mostrar(
        tabla(
            [
                ("Fecha y hora", ""),
                ("Orden", ""),
                ("SKU original", "bp-sku"),
                ("SKU nuevo", "bp-sku"),
                ("Responsable", ""),
                ("Motivo", ""),
            ],
            filas,
        )
    )
    st.download_button(
        "Descargar historial (CSV)",
        data=ui_datos.neutralizar_csv(log[COLUMNAS_CSV]).to_csv(index=False).encode("utf-8"),
        file_name="log_cambios.csv",
        mime="text/csv",
        key="historial_csv",
    )
