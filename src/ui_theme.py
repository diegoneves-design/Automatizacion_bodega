"""
Tema visual de la aplicacion: constantes de marca y CSS.

- NOMBRE_APP y ESLOGAN_APP son provisorios: se cambian solo aqui.
- MENU_GREEN es el unico lugar donde se define el verde del menu lateral; el CSS lo
  expone como la variable --menu-green y todo lo demas la usa.
- El CSS depende de la estructura interna de Streamlit (data-testid y clases st-key-*).
  Se probo con streamlit 1.65.0; en otras versiones pueden hacer falta ajustes.
"""

import streamlit as st

from ui_components import TRAZOS

NOMBRE_APP = "BodegaPlus"
ESLOGAN_APP = "Guías más simples. Operaciones más seguras."
LEMA_APP = "Del pedido a la guía, sin errores."
FRASE_PIE = "Equipos en movimiento, negocios que avanzan."

MENU_GREEN = "#0B4F2E"

# Claves de los botones del menu lateral -> icono (ver ui_components.TRAZOS)
ICONOS_MENU = {
    "menu_ordenes": "ordenes",
    "menu_carga": "carga",
    "menu_validador": "validador",
    "menu_ajuste": "ajuste",
    "menu_historial": "historial",
}


def _mascara(trazo):
    """Icono como mascara CSS (data URI): toma el color del texto del boton."""
    svg = (
        "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' "
        "stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E"
        + trazo.replace('"', "'").replace("<", "%3C").replace(">", "%3E")
        + "%3C/svg%3E"
    )
    return f'url("data:image/svg+xml,{svg}")'


def _css_iconos_menu():
    reglas = []
    for clave, nombre in ICONOS_MENU.items():
        reglas.append(
            f'.stApp [data-testid="stSidebar"] .st-key-{clave} button p::before{{-webkit-mask-image:{_mascara(TRAZOS[nombre])};'
            f"mask-image:{_mascara(TRAZOS[nombre])};}}"
        )
    return "\n".join(reglas)


CSS = """
:root {
  --menu-green: __MENU_GREEN__;
  --menu-activo: #1f6fd0;
  --acento: #1a6ed8;
  --acento-oscuro: #1459b0;
  --texto: #0f2540;
  --suave: #5b6b80;
  --borde: #dfe6ef;
  --fondo: #f3f6fb;
  --tarjeta: #ffffff;
  --radio: 12px;
  --fuente: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* Tipografia del sistema (sin fuentes externas). Los iconos de Streamlit conservan su fuente. */
.stApp, .stApp :where(p, span, label, input, textarea, button, div, h1, h2, h3, h4, li, td, th, small):not([data-testid="stIconMaterial"]) {
  font-family: var(--fuente);
}
.stApp { background: var(--fondo); color: var(--texto); }
.block-container { max-width: 1120px; padding-top: 2rem; padding-bottom: 3rem; }
h1, h2, h3 { color: var(--texto); letter-spacing: -0.01em; }
header[data-testid="stHeader"] { background: transparent; }

/* ---------- Menu lateral (verde) ---------- */
[data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child { background: var(--menu-green); }
[data-testid="stSidebar"] * { color: #fff; }
[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] { padding-top: 1.2rem; }
.bp-marca { display: flex; align-items: center; gap: 10px; padding: 4px 6px 18px; font-size: 20px; font-weight: 700; letter-spacing: -0.2px; }
.bp-marca svg { width: 28px; height: 28px; }
.stApp [data-testid="stSidebar"] .stButton { margin-bottom: 2px; }
.stApp [data-testid="stSidebar"] .stButton button {
  width: 100%; justify-content: flex-start; min-height: 2.9rem;
  background: transparent; border: 0; border-radius: 9px; box-shadow: none; color: rgba(255,255,255,.92);
}
.stApp [data-testid="stSidebar"] .stButton button > div { width: 100%; justify-content: flex-start; text-align: left; }
.stApp [data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: .25rem; }
.stApp [data-testid="stSidebar"] .stButton button:hover { background: rgba(255,255,255,.1); }
.stApp [data-testid="stSidebar"] .stButton button p { font-size: 15px; display: flex; align-items: center; gap: 12px; margin: 0; }
.stApp [data-testid="stSidebar"] .stButton button p::before {
  content: ""; width: 20px; height: 20px; flex: none; background: currentColor;
  -webkit-mask-repeat: no-repeat; mask-repeat: no-repeat; -webkit-mask-position: center; mask-position: center;
  -webkit-mask-size: contain; mask-size: contain;
}
.stApp [data-testid="stSidebar"] .stButton button[kind="primary"],
.stApp [data-testid="stSidebar"] .stButton button[data-testid="stBaseButton-primary"] { background: var(--menu-activo); color: #fff; font-weight: 600; }
.stApp [data-testid="stSidebar"] .stButton button:disabled { opacity: .6; }
.stApp [data-testid="stSidebar"] .stButton button:disabled p::before { display: none; }
.bp-usuario { display: flex; align-items: center; gap: 10px; margin: 2rem 0 .8rem; padding: 14px 6px 0; border-top: 1px solid rgba(255,255,255,.18); }
.bp-usuario > div { line-height: 1.2; }
.bp-avatar { display: grid; place-items: center; width: 36px; height: 36px; border-radius: 50%; background: rgba(255,255,255,.95); font-size: 13px; font-weight: 700; flex: none; }
.bp-avatar, .bp-avatar * { color: var(--menu-green) !important; }
.bp-usuario strong { font-size: 14px; }
__ICONOS_MENU__

/* ---------- Botones del contenido ---------- */
.stApp .stButton button, .stApp .stDownloadButton button {
  min-height: 2.9rem; border-radius: 10px; font-weight: 600; border: 1px solid var(--borde); background: #fff; color: var(--acento);
}
.stApp .stButton button[kind="primary"], .stApp .stButton button[data-testid="stBaseButton-primary"],
.stApp .stDownloadButton button[kind="primary"], .stApp .stDownloadButton button[data-testid="stBaseButton-primary"] {
  background: var(--acento); border-color: var(--acento); color: #fff;
}
.stApp .stButton button[kind="primary"]:hover, .stApp .stButton button[data-testid="stBaseButton-primary"]:hover { background: var(--acento-oscuro); border-color: var(--acento-oscuro); }
.stApp .stButton button:disabled, .stApp .stDownloadButton button:disabled { opacity: .5; cursor: not-allowed; }
.stApp .stButton button[data-testid="stBaseButton-primary"]:disabled { background: #8db5ec; border-color: #8db5ec; color: #fff; }

/* ---------- Etiquetas de estado ---------- */
.bp-pill { display: inline-block; padding: 3px 10px; border-radius: 999px; border: 1px solid transparent; font-size: 12px; font-weight: 600; white-space: nowrap; }
.bp-pill-pendiente { background: #fff3d6; border-color: #f1d28a; color: #8a5a00; }
.bp-pill-revision { background: #e6f0ff; border-color: #b9d2fb; color: #1a5fc4; }
.bp-pill-completada, .bp-pill-ok { background: #e3f6e8; border-color: #aedfbb; color: #1b7a3a; }
.bp-pill-error { background: #fde8e8; border-color: #f3b9b9; color: #b42323; }
.bp-pill-aviso { background: #fff3d6; border-color: #f1d28a; color: #8a5a00; }
.bp-pill-prox, .bp-pill-neutro { background: #eef1f5; border-color: #dfe6ef; color: #5b6b80; }

/* ---------- Tablas ---------- */
.bp-tabla-wrap { overflow-x: auto; background: var(--tarjeta); border: 1px solid var(--borde); border-radius: var(--radio); margin: .5rem 0 1rem; }
.bp-tabla { width: 100%; border-collapse: collapse; font-size: 14px; }
.bp-tabla th { background: #f3f6fa; color: var(--texto); font-weight: 700; text-align: left; padding: 10px 14px; font-size: 13px; white-space: nowrap; }
.bp-tabla td { padding: 11px 14px; border-top: 1px solid var(--borde); vertical-align: middle; }
.bp-tabla .bp-sku { font-weight: 600; white-space: nowrap; }
.bp-vacio { text-align: center; color: var(--suave); padding: 18px; }
@media (max-width: 640px) {
  .bp-tabla th, .bp-tabla td { padding: 9px 8px; font-size: 13px; }
  .bp-oculto-movil { display: none; }
}

/* ---------- Avisos ---------- */
.bp-banner { display: flex; align-items: flex-start; gap: 12px; margin: .5rem 0 1rem; padding: 14px 16px; border-radius: var(--radio); border: 1px solid; }
.bp-banner strong { display: block; font-size: 15px; }
.bp-banner span:not(.bp-banner-icono) { display: block; font-size: 13px; color: var(--suave); margin-top: 2px; }
.bp-banner-icono svg { flex: none; }
.bp-banner-ok { background: #e9f7ee; border-color: #b9e3c6; }
.bp-banner-ok .bp-banner-icono { color: #1b9a46; }
.bp-banner-aviso { background: #fff4e5; border-color: #f6d7a3; }
.bp-banner-aviso .bp-banner-icono { color: #d98200; }
.bp-banner-error { background: #fdecec; border-color: #f3b9b9; }
.bp-banner-error .bp-banner-icono { color: #c62828; }
.bp-banner-info { background: #e9f1fe; border-color: #c5d9f8; }
.bp-banner-info .bp-banner-icono { color: var(--acento); }

/* ---------- Titulos ---------- */
.bp-titulo h1 { font-size: 30px; font-weight: 700; margin: 0; padding: 0; line-height: 1.2; }
.bp-titulo p { margin: 4px 0 18px; color: var(--suave); font-size: 15px; }

/* ---------- Campos (buscador y fecha) ---------- */
.stApp [data-testid="stTextInput"] input, .stApp [data-testid="stDateInput"] input, .stApp [data-testid="stSelectbox"] [data-baseweb="select"] > div,
.stApp [data-testid="stTextArea"] textarea {
  background: #fff; border: 1px solid var(--borde); border-radius: 10px; color: var(--texto);
}
.stApp [data-testid="stTextInput"] [data-baseweb="input"], .stApp [data-testid="stDateInput"] [data-baseweb="input"],
.stApp [data-testid="stTextArea"] [data-baseweb="textarea"] { background: transparent; border: 0; }

/* ---------- Pestanas de tipo (radio horizontal en forma de segmentos) ---------- */
.stApp [data-testid="stRadioGroup"] { gap: 0; background: #e6ebf2; border-radius: 10px; padding: 3px; width: fit-content; max-width: 100%; }
@media (max-width: 640px) { .stApp [data-testid="stRadioGroup"] { width: 100%; } }
.stApp [data-testid="stRadioGroup"] > div { flex: 1; }
.stApp [data-testid="stRadioOption"] { width: 100%; margin: 0; padding: 7px 10px; border-radius: 8px; cursor: pointer; justify-content: center; }
.stApp [data-testid="stRadioOption"] > div { width: 100%; justify-content: center; }
.stApp [data-testid="stRadioOption"] > div > div:first-child { display: none; }
.stApp [data-testid="stRadioOption"] p { font-size: 14px; font-weight: 600; color: var(--suave); text-align: center; margin: 0; white-space: nowrap; }
.stApp [data-testid="stRadioOption"][data-selected="true"] { background: #fff; box-shadow: 0 1px 2px rgba(15,37,64,.12); }
.stApp [data-testid="stRadioOption"][data-selected="true"] p { color: var(--acento); }

/* ---------- Lista de ordenes (filas con columnas de Streamlit) ---------- */
.bp-cabecera { font-size: 13px; font-weight: 700; color: var(--suave); padding: 4px 0; }
.bp-orden-grid { display: grid; grid-template-columns: 2.3fr 1.5fr 1.7fr 1.1fr 1.6fr; gap: 8px; align-items: center; }
.bp-folio { font-weight: 700; font-size: 15px; }
.bp-sub { font-size: 12px; color: var(--suave); }
.bp-celda { font-size: 14px; }
[data-testid="stHorizontalBlock"]:has(.bp-orden-grid:not(.bp-cabecera)) { align-items: center; border-top: 1px solid var(--borde); padding-top: .55rem; }
@media (max-width: 640px) {
  [data-testid="stHorizontalBlock"]:has(.bp-cabecera) { display: none; }
  .bp-orden-grid { grid-template-columns: 1fr 1fr; row-gap: 6px; }
  .bp-orden-folio { grid-column: 1 / -1; }
  .bp-celda::before { content: attr(data-et) ": "; color: var(--suave); }
}

/* ---------- Datos y tarjetas ---------- */
.bp-datos { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px 20px; margin: 0; }
.bp-datos dt { font-size: 12px; color: var(--suave); }
.bp-datos dd { margin: 2px 0 0; font-size: 15px; font-weight: 600; }
.stApp [data-testid="stVerticalBlockBorderWrapper"] { background: var(--tarjeta); border-radius: var(--radio); border-color: var(--borde); }
"""


def css():
    """CSS completo, con el verde del menu tomado de MENU_GREEN."""
    return CSS.replace("__MENU_GREEN__", MENU_GREEN).replace("__ICONOS_MENU__", _css_iconos_menu())


def inyectar():
    """Inserta el CSS en la pagina (un bloque <style>)."""
    st.markdown(f"<style>{css()}</style>", unsafe_allow_html=True)
