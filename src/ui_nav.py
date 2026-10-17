"""
Estado de navegacion de la interfaz (st.session_state). Lo usan el enrutador y las pantallas.

  vista    pantalla actual (ordenes, detalle, validacion, ajuste, guia, historial, carga)
  folio    orden seleccionada
  validadas  folios cuya validacion se pidio en esta sesion
  guias    guias emitidas en esta sesion: folio -> {"numero", "fecha"}
"""

import streamlit as st


def iniciar_estado():
    ss = st.session_state
    ss.setdefault("vista", "ordenes")
    ss.setdefault("folio", None)
    ss.setdefault("validadas", set())
    ss.setdefault("guias", {})
    ss.setdefault("sku_corregir", None)
    ss.setdefault("aviso", None)


def ir(vista, folio=None, sku=None):
    """Callback de navegacion (usar en on_click: corre antes de redibujar la pagina)."""
    st.session_state.vista = vista
    if folio is not None:
        st.session_state.folio = folio
    st.session_state.sku_corregir = sku


def ir_menu(destino):
    """Navegacion desde el menu: validar y ajustar necesitan una orden elegida."""
    if destino in ("validacion", "ajuste") and not st.session_state.get("folio"):
        st.session_state.aviso = "Primero elige una orden de la lista."
        destino = "ordenes"
    st.session_state.vista = destino
    st.session_state.sku_corregir = None
