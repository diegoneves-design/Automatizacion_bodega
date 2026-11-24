"""
Vista Dashboard: el analisis del inventario real dentro del MVP.

Los graficos son los mismos del prototipo (ver ui_dashboard.py): la pagina se arma con los mismos archivos y se muestra en un
iframe. Los datos los lee ESTE servidor con el rol limitado (inventario_dashboard()) y viajan dentro de la pagina: el navegador
no usa la clave publica de Supabase. Solo aparece con DASHBOARD_INVENTARIO=1.
"""

import streamlit as st

import db
import ui_dashboard
from ui_components import banner, mostrar, titulo

ALTO_INICIAL = 900  # el iframe se ajusta solo al alto de la ventana (dashboard_incrustado/entorno.js)

# Esta vista usa todo el ancho (el resto de las pantallas conserva su ancho comodo de lectura).
ANCHO_COMPLETO = "<style>.block-container { max-width: none !important; }</style>"


@st.cache_data(ttl=300, show_spinner="Cargando el inventario…")
def _cargar(_repo):
    """(hay_equipos, pagina). Se guarda 5 minutos para todas las sesiones; un error no se guarda."""
    datos = _repo.dashboard()
    return ui_dashboard.hay_equipos(datos), ui_dashboard.pagina(datos)


def render(repo):
    st.markdown(ANCHO_COMPLETO, unsafe_allow_html=True)

    error = None
    hay_equipos = pagina = None
    try:
        hay_equipos, pagina = _cargar(repo)
    except (db.ErrorDeBase, ui_dashboard.ErrorDashboard) as e:
        error = str(e)

    # Titulo y boton en una sola fila: el Dashboard necesita todo el alto que se pueda
    izq, der = st.columns([5, 1.2], vertical_alignment="bottom")
    with izq:
        mostrar(titulo("Dashboard", "Inventario de la bodega. Haz clic en un gráfico para filtrar; todo lo demás se recalcula."))
    if error is None and hay_equipos:
        der.button("Actualizar datos", key="dash_actualizar", on_click=_cargar.clear, use_container_width=True,
                   help="Los datos se guardan 5 minutos; esto los vuelve a pedir a la base.")

    if error is not None:
        mostrar(banner("error", "No se pudo cargar el Dashboard", error))
        st.button("Reintentar", key="dash_reintentar", on_click=_cargar.clear)
        return

    if not hay_equipos:
        mostrar(
            banner(
                "info",
                "Todavía no hay inventario cargado",
                "Cuando el inventario real esté en la base de datos, aparecerá aquí. Con la base local de pruebas esta vista sale vacía.",
            )
        )
        return

    st.iframe(pagina, height=ALTO_INICIAL, alt="Dashboard del inventario de la bodega: indicadores, gráficos, tabla de equipos y lectura de los datos")
