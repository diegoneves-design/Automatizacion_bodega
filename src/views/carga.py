"""Carga masiva de SKU: crea una orden de despacho o retiro con su folio."""

import streamlit as st

import db
import ui_datos
from ui_components import banner, mostrar, tabla, titulo
from ui_nav import avisar, ir

MAX_FOLIO = 20


def _lineas(ss):
    """Las lineas pegadas en el cuadro de texto mas las del archivo, sin limpiar: la base las limpia."""
    archivo = ss.get("cm_archivo")
    contenido = archivo.getvalue() if archivo is not None else None
    return ui_datos.unir_lineas(ss.get("cm_texto"), contenido)


def _cargar(repo):
    """Callback: crea la orden y abre su detalle. Si una regla la rechaza, deja el mensaje exacto en pantalla."""
    ss = st.session_state
    tipo = ss.get("cm_tipo")
    try:
        folio = repo.crear_pedido(
            ss.get("cm_folio"), ss.get("cm_cliente"), ss.get("id_usuario"), tipo, ss.get(f"cm_modalidad_{tipo}"), _lineas(ss)
        )
    except db.ReglaDeNegocio as e:
        ss.cm_error = e.mensaje
        return
    except db.ErrorDeBase as e:
        ss.cm_error = str(e)
        return
    cantidad = len(db.skus_limpios(_lineas(ss)))
    for clave in [k for k in ss if str(k).startswith("cm_")]:
        del ss[clave]
    avisar("ok", f"Orden {folio} cargada con {cantidad} SKU. Revisa los equipos y valídala.")
    ir("detalle", folio)


def render(repo):
    ss = st.session_state
    mostrar(titulo("Carga masiva", f"Pega o carga hasta {db.MAX_SKUS} SKU para crear una orden de despacho o retiro."))

    clientes = {c["id_cliente"]: c["razon_social"] for c in repo.clientes()}

    with st.container(border=True):
        col_folio, col_cliente = st.columns(2)
        col_folio.text_input("Folio de guía u orden", placeholder="Ej: GUIA-2026-003", max_chars=MAX_FOLIO, key="cm_folio", help="Forma: GUIA, el año y un número. Ejemplo: GUIA-2026-003")
        col_cliente.selectbox("Cliente", list(clientes), format_func=clientes.get, index=None, placeholder="Elige el cliente", key="cm_cliente")
        col_tipo, col_modalidad = st.columns(2)
        tipo = col_tipo.selectbox("Tipo de movimiento", list(db.MODALIDADES_POR_TIPO), key="cm_tipo")
        etiqueta = "Modalidad" if tipo == "Despacho" else "Motivo del retiro"
        col_modalidad.selectbox(etiqueta, db.MODALIDADES_POR_TIPO[tipo], key=f"cm_modalidad_{tipo}")
        st.text_area("Pega los SKU (uno por línea)", height=180, placeholder="SD-63A20-0314\nSD-63A20-0315\nST-0042\n…", key="cm_texto")
        st.file_uploader("O carga un archivo .txt o .csv con un SKU por línea", type=["txt", "csv"], key="cm_archivo")

        skus = db.skus_limpios(_lineas(ss))
        if skus:
            if len(skus) > db.MAX_SKUS:
                mostrar(banner("error", f"Se detectaron {len(skus)} SKU", f"El límite permitido es {db.MAX_SKUS}."))
            else:
                mostrar(banner("info", f"SKU detectados: {len(skus)}"))
                mostrar(tabla([("#", "bp-oculto-movil"), ("SKU", "bp-sku")], [[i, s] for i, s in enumerate(skus, start=1)]))
        if ss.get("cm_error"):
            mostrar(banner("error", ss.cm_error))

        st.button(
            "Cargar orden",
            key="cm_cargar",
            type="primary",
            on_click=_cargar,
            args=(repo,),
            disabled=not skus or len(skus) > db.MAX_SKUS,
        )
