"""Carga masiva de SKU: crea una orden de despacho o retiro (misma logica que la vista anterior)."""

import streamlit as st

import ui_datos
from ui_components import banner, mostrar, tabla, titulo
from ui_nav import avisar, ir

MAX_FOLIO = 40


def _skus(app):
    """SKU unicos y limpios: los pegados mas los del archivo (misma deduplicacion de siempre)."""
    ss = st.session_state
    archivo = ss.get("cm_archivo")
    contenido = archivo.getvalue() if archivo is not None else None
    return app.deduplicar_skus(ui_datos.unir_lineas(ss.get("cm_texto"), contenido))


def _cargar(app):
    """Callback: crea la orden y abre su detalle."""
    ss = st.session_state
    folio = (ss.get("cm_folio") or "").strip()
    skus = _skus(app)
    tipo = ss.get("cm_tipo")
    modalidad = ss.get(f"cm_modalidad_{tipo}")
    if not folio:
        ss.cm_error = "Debes ingresar un folio antes de cargar la orden."
        return
    if not skus or len(skus) > app.MAX_SKUS:
        ss.cm_error = f"La orden debe tener entre 1 y {app.MAX_SKUS} SKU."
        return
    app.insertar_ordenes(folio, skus, tipo, modalidad)
    for clave in [k for k in ss if str(k).startswith("cm_")]:
        del ss[clave]
    avisar("ok", f"Orden {folio} cargada con {len(skus)} SKU. Revisa los equipos y valídala.")
    ir("detalle", folio)


def render(app):
    ss = st.session_state
    mostrar(titulo("Carga masiva", f"Pega o carga hasta {app.MAX_SKUS} SKU para crear una orden de despacho o retiro."))

    with st.container(border=True):
        st.text_input("Folio de guía u orden", placeholder="Ej: GUIA-2026-001", max_chars=MAX_FOLIO, key="cm_folio")
        col_tipo, col_modalidad = st.columns(2)
        tipo = col_tipo.selectbox("Tipo de movimiento", list(app.MODALIDADES_POR_TIPO), key="cm_tipo")
        col_modalidad.selectbox("Modalidad", app.MODALIDADES_POR_TIPO[tipo], key=f"cm_modalidad_{tipo}")
        st.text_area("Pega los SKU (uno por línea)", height=180, placeholder="EXC-001\nEXC-002\nRET-010\n…", key="cm_texto")
        st.file_uploader("O carga un archivo .txt o .csv con un SKU por línea", type=["txt", "csv"], key="cm_archivo")

        skus = _skus(app)
        folio = (ss.get("cm_folio") or "").strip()
        if skus:
            if len(skus) > app.MAX_SKUS:
                mostrar(banner("error", f"Se detectaron {len(skus)} SKU", f"El límite permitido es {app.MAX_SKUS}."))
            else:
                mostrar(banner("info", f"SKU detectados: {len(skus)}"))
                mostrar(tabla([("#", "bp-oculto-movil"), ("SKU", "bp-sku")], [[i, s] for i, s in enumerate(skus, start=1)]))
        if folio and folio in app.obtener_folios():
            mostrar(
                banner("aviso", "Este folio ya existe", "Los SKU nuevos se agregarán a esa orden, sin reemplazar los anteriores.")
            )
        if ss.get("cm_error"):
            mostrar(banner("error", ss.cm_error))

        st.button(
            "Cargar orden",
            key="cm_cargar",
            type="primary",
            on_click=_cargar,
            args=(app,),
            disabled=not skus or len(skus) > app.MAX_SKUS,
        )
