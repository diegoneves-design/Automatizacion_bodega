"""
Estructura comun de la interfaz: menu lateral y despacho de pantallas.

La navegacion vive en st.session_state (ver ui_nav). Cada pantalla es una funcion
render(app) que recibe el modulo app.py, de modo que la capa de datos sigue en app.py
(y los tests pueden redirigir app.DB_PATH).
"""

import streamlit as st

import ui_nav
import ui_theme
from ui_components import Html, esc, icono, mostrar
from views import ajuste, carga, detalle, guia, historial, ordenes, validacion

# (clave del boton, etiqueta, pantalla de destino)
MENU = [
    ("menu_ordenes", "Órdenes", "ordenes"),
    ("menu_carga", "Carga masiva", "carga"),
    ("menu_validador", "Validador", "validacion"),
    ("menu_ajuste", "Ajuste de última hora", "ajuste"),
    ("menu_historial", "Historial", "historial"),
]

# Que opcion del menu queda resaltada en cada pantalla
MENU_ACTIVO = {
    "ordenes": "menu_ordenes",
    "detalle": "menu_ordenes",
    "guia": "menu_ordenes",
    "carga": "menu_carga",
    "validacion": "menu_validador",
    "ajuste": "menu_ajuste",
    "historial": "menu_historial",
}

# Paso del flujo (1 a 5) que corresponde a cada pantalla; las demas no resaltan ninguno
PASO_POR_VISTA = {"ordenes": 1, "detalle": 2, "validacion": 3, "ajuste": 4, "guia": 5}

# Usuario de ejemplo del menu: la app no tiene inicio de sesion (solo es una etiqueta).
USUARIO_ETIQUETA = "Jefe de Bodega"
USUARIO_INICIALES = "JB"


def _menu_lateral():
    with st.sidebar:
        mostrar(Html(f'<div class="bp-marca">{icono("logo", 28)}<span>{esc(ui_theme.NOMBRE_APP)}</span></div>'))
        activo = MENU_ACTIVO.get(st.session_state.vista)
        for clave, etiqueta, destino in MENU:
            st.button(
                etiqueta,
                key=clave,
                type="primary" if clave == activo else "secondary",
                on_click=ui_nav.ir_menu,
                args=(destino,),
                use_container_width=True,
            )
        mostrar(
            Html(
                f'<div class="bp-usuario"><span class="bp-avatar">{esc(USUARIO_INICIALES)}</span>'
                f"<div><strong>{esc(USUARIO_ETIQUETA)}</strong></div></div>"
            )
        )
        st.button("Cerrar sesión · Próximamente", key="menu_salir", disabled=True, use_container_width=True, help="Próximamente")


PANTALLAS = {
    "ordenes": ordenes.render,
    "detalle": detalle.render,
    "validacion": validacion.render,
    "ajuste": ajuste.render,
    "guia": guia.render,
    "historial": historial.render,
    "carga": carga.render,
}


def _encabezado():
    atributos = "".join(
        f'<div class="bp-atributo">{icono(icono_nombre, 18)}<span>{esc(etiqueta)}</span></div>'
        for etiqueta, icono_nombre in ui_theme.ATRIBUTOS
    )
    mostrar(
        Html(
            '<div class="bp-encabezado">'
            f'<div class="bp-encabezado-marca">{icono("logo", 34)}<div>'
            f'<div class="bp-encabezado-nombre">{esc(ui_theme.NOMBRE_APP)}</div>'
            f'<div class="bp-encabezado-eslogan">{esc(ui_theme.ESLOGAN_APP)}</div></div></div>'
            f'<div class="bp-encabezado-lado"><div class="bp-lema">{esc(ui_theme.LEMA_INICIO)} <b>{esc(ui_theme.LEMA_ENFASIS)}</b></div>'
            f'<div class="bp-atributos">{atributos}</div></div></div>'
        )
    )


def _flujo(vista):
    activo = PASO_POR_VISTA.get(vista)
    pasos = []
    for numero, texto in enumerate(ui_theme.PASOS, start=1):
        clase = " bp-paso-activo" if numero == activo else ""
        pasos.append(f'<div class="bp-paso{clase}"><span class="bp-paso-n">{numero}</span><span class="bp-paso-t">{esc(texto)}</span></div>')
    unidos = "".join(pasos)
    mostrar(Html(f'<div class="bp-flujo">{unidos}</div><div class="bp-frase">{esc(ui_theme.FRASE_PIE)}</div>'))


def run(app):
    """Punto de entrada de la interfaz: estado, tema, menu y pantalla actual."""
    ui_nav.iniciar_estado()
    ui_theme.inyectar()
    _menu_lateral()
    _encabezado()
    PANTALLAS[st.session_state.vista](app)
    _flujo(st.session_state.vista)
