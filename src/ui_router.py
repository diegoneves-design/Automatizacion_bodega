"""
Estructura comun de la interfaz: menu lateral y despacho de pantallas.

La navegacion vive en st.session_state (ver ui_nav). Cada pantalla es una funcion
render(repo) que recibe el repositorio de datos (src/db.py): PostgreSQL (Supabase) si hay
DATABASE_URL, o SQLite local si no.
"""

import streamlit as st

import db
import ui_datos
import ui_nav
import ui_theme
from ui_components import Html, banner, esc, icono, mostrar
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

# La app no tiene inicio de sesion: quien opera se elige en el menu (la base solo comprueba el rol).
# Limitacion conocida, documentada en el README: cualquiera con acceso a la app opera como el usuario que elija.
NOMBRE_BASE = {"postgres": "Base: Supabase (PostgreSQL)", "sqlite": "Base local de pruebas (SQLite)"}


def _iniciales(nombre):
    return "".join(p[0] for p in nombre.split()[:2]).upper() or "?"


def _usuario_actual(repo):
    """Elige quien opera (selectbox del menu) y devuelve su nombre. Por omision, el primer jefe de bodega."""
    ss = st.session_state
    usuarios = {u["id_usuario"]: u for u in repo.usuarios()}
    if not usuarios:
        ss.id_usuario = None
        return None
    if ss.id_usuario not in usuarios:
        ss.id_usuario = next((i for i, u in usuarios.items() if u["rol"] == "jefe_bodega"), next(iter(usuarios)))
    st.selectbox(
        "Operar como",
        list(usuarios),
        format_func=lambda i: f'{usuarios[i]["nombre"]} · {ui_datos.nombre_rol(usuarios[i]["rol"])}',
        key="id_usuario",
    )
    return usuarios[ss.id_usuario]["nombre"]


def _menu_lateral(repo):
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
        nombre = _usuario_actual(repo)
        if nombre:
            mostrar(
                Html(
                    f'<div class="bp-usuario"><span class="bp-avatar">{esc(_iniciales(nombre))}</span>'
                    f"<div><strong>{esc(nombre)}</strong></div></div>"
                )
            )
        st.caption(NOMBRE_BASE.get(repo.modo, ""))
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


def run(repo):
    """Punto de entrada de la interfaz: estado, tema, menu y pantalla actual."""
    ui_nav.iniciar_estado()
    ui_theme.inyectar()
    try:
        _menu_lateral(repo)
        _encabezado()
        PANTALLAS[st.session_state.vista](repo)
    except db.ErrorDeBase as e:
        # sin base no hay nada que mostrar: un solo mensaje claro (sin detalles de la conexion) y un boton para reintentar
        mostrar(banner("error", "No se pudo leer la base de datos", str(e)))
        st.button("Reintentar", key="reintentar")
        return
    _flujo(st.session_state.vista)
