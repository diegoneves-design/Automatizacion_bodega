"""
Estado de navegacion de la interfaz (st.session_state). Lo usan el enrutador y las pantallas.

  vista      pantalla actual (ordenes, detalle, validacion, ajuste, guia, historial, carga)
  folio      orden seleccionada
  id_usuario quien opera (se elige en el menu lateral; la app no tiene inicio de sesion)
  validadas, guias  solo los usa la interfaz clasica; el MVP con base real lee ese estado de la base
  aviso      mensaje de una sola vez: (tipo, texto), tipo = ok / info / aviso / error
"""

import streamlit as st

import ui_dashboard
from ui_components import banner, mostrar


def _vista_inicial():
    """La pantalla con la que abre la sesion. ?vista=dashboard abre el Dashboard, pero solo si esta encendido."""
    try:
        pedida = st.query_params.get("vista")
    except Exception:  # noqa: BLE001 - sin parametros de direccion, se abre en Ordenes
        pedida = None
    return "dashboard" if pedida == "dashboard" and ui_dashboard.activo() else "ordenes"


def iniciar_estado():
    ss = st.session_state
    ss.setdefault("vista", _vista_inicial())
    ss.setdefault("folio", None)
    ss.setdefault("id_usuario", None)
    ss.setdefault("validadas", set())
    ss.setdefault("guias", {})
    ss.setdefault("sku_corregir", None)
    ss.setdefault("aviso", None)


def _limpiar_formulario_ajuste():
    """Los campos del ajuste (claves aj_*) arrancan de cero cada vez que se entra a la pantalla."""
    for clave in [k for k in st.session_state if str(k).startswith("aj_")]:
        del st.session_state[clave]


def ir(vista, folio=None, sku=None):
    """Callback de navegacion (usar en on_click: corre antes de redibujar la pagina)."""
    ss = st.session_state
    if vista == "ajuste":
        _limpiar_formulario_ajuste()
    ss.vista = vista
    if folio is not None:
        ss.folio = folio
    ss.sku_corregir = sku


def boton_volver(texto, vista, clave):
    """Enlace de vuelta (boton discreto) hacia otra pantalla."""
    st.button(texto, key=clave, on_click=ir, args=(vista,))


def ir_menu(destino):
    """Navegacion desde el menu: validar y ajustar necesitan una orden elegida."""
    ss = st.session_state
    if destino in ("validacion", "ajuste") and not ss.get("folio"):
        ss.aviso = ("info", "Primero elige una orden de la lista.")
        destino = "ordenes"
    ir(destino)


def avisar(tipo, texto):
    """Deja un mensaje para mostrarlo una vez en la proxima pantalla."""
    st.session_state.aviso = (tipo, texto)


def mostrar_aviso():
    """Muestra (y consume) el mensaje pendiente, si hay."""
    aviso = st.session_state.get("aviso")
    if aviso:
        tipo, texto = aviso
        mostrar(banner(tipo, texto))
        st.session_state.aviso = None
