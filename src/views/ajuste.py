"""Pantalla 4: Ajuste de última hora (reemplazo de un SKU con registro en log_cambios)."""

import streamlit as st

import ui_datos
from ui_components import Html, banner, esc, icono, mostrar, tabla, titulo
from ui_nav import boton_volver, ir, avisar

# Motivos que se ofrecen en la lista (provisorios): se guardan como texto en log_cambios.motivo.
MOTIVOS = ["Falla en equipo original", "Sin stock", "Solicitud de mantenimiento", "Otro"]
MAX_RESPONSABLE = 60
MAX_OBSERVACIONES = 300


def _guardar(app, folio):
    """Callback: valida el formulario y registra el reemplazo con la logica existente."""
    ss = st.session_state
    original = ss.get("aj_orig")
    nuevo = ss.get("aj_nuevo")
    responsable = (ss.get("aj_resp") or "").strip()
    observaciones = (ss.get("aj_obs") or "").strip()
    motivo = ss.get("aj_motivo") or MOTIVOS[0]

    orden = app.obtener_orden(folio)
    vigentes = list(orden["sku"])
    if original not in vigentes:
        ss.aj_error = "El SKU a reemplazar ya no está en la orden."
    elif not nuevo:
        ss.aj_error = "Indica el nuevo SKU."
    elif nuevo == original:
        ss.aj_error = "El nuevo SKU debe ser distinto del original."
    elif nuevo in vigentes:
        ss.aj_error = f"El SKU {nuevo} ya está en la orden."
    elif not responsable:
        ss.aj_error = "Indica quién autoriza el cambio."
    else:
        ss.aj_error = None

    if ss.aj_error:
        return

    texto_motivo = f"{motivo}: {observaciones}" if observaciones else motivo
    fila = orden[orden["sku"] == original].iloc[0]
    app.reemplazar_sku(int(fila["id"]), folio, original, nuevo, responsable, texto_motivo)
    ss.validadas.add(folio)
    avisar("ok", f"Cambio registrado: {original} → {nuevo}.")
    ir("validacion", folio)


def render(app):
    ss = st.session_state
    folio = ss.folio
    boton_volver("← Volver a la validación", "validacion", "volver_validacion")
    mostrar(titulo("Ajuste de última hora", "Reemplaza un equipo y registra el cambio."))

    orden = app.obtener_orden(folio) if folio else None
    if orden is None or orden.empty:
        mostrar(banner("info", "No hay equipos para ajustar", "Elige una orden con equipos desde Órdenes."))
        return

    inventario = app.obtener_inventario()
    descripcion = dict(zip(inventario["sku"], inventario["descripcion"]))
    stock = dict(zip(inventario["sku"], inventario["stock_disponible"]))
    vigentes = list(orden["sku"])
    validada = app.validar_orden(folio)
    problemas = [f.sku for f in validada.itertuples() if f.resultado != "OK"]
    inicial = ss.sku_corregir if ss.sku_corregir in vigentes else (problemas[0] if problemas else vigentes[0])

    if folio in ss.guias:
        mostrar(banner("info", "Esta orden ya tiene guía emitida", "El cambio queda registrado, pero no modifica la guía ya emitida."))

    col_form, col_hist = st.columns([1.15, 1])

    with col_form:
        with st.container(border=True):
            mostrar(Html('<div class="bp-subtitulo bp-sin-margen">Reemplazar equipo</div>'))
            c_orig, c_flecha, c_nuevo = st.columns([5, 0.9, 5])
            original = c_orig.selectbox("SKU a reemplazar", vigentes, index=vigentes.index(inicial), key="aj_orig")
            c_orig.markdown(f'<div class="bp-ayuda">{esc(descripcion.get(original, ""))}</div>', unsafe_allow_html=True)
            c_flecha.markdown(f'<div class="bp-flecha-par">{icono("ajuste", 22)}</div>', unsafe_allow_html=True)
            nuevo = c_nuevo.selectbox(
                "Nuevo SKU", list(inventario["sku"]), index=None, placeholder="Buscar SKU…", key="aj_nuevo"
            )
            if nuevo:
                aviso_stock = ""
                if stock.get(nuevo, 0) <= 0:
                    aviso_stock = " · sin stock: la orden seguirá bloqueada"
                c_nuevo.markdown(
                    f'<div class="bp-ayuda">{esc(descripcion.get(nuevo, ""))}{esc(aviso_stock)}</div>', unsafe_allow_html=True
                )
            st.selectbox("Motivo del cambio", MOTIVOS, key="aj_motivo")
            st.text_input("Responsable", placeholder="Nombre de quien autoriza", max_chars=MAX_RESPONSABLE, key="aj_resp")
            st.text_area("Observaciones (opcional)", max_chars=MAX_OBSERVACIONES, height=90, key="aj_obs")
            if ss.get("aj_error"):
                mostrar(banner("error", ss.aj_error))
            b_cancelar, b_guardar = st.columns(2)
            b_cancelar.button("Cancelar", key="aj_cancelar", on_click=ir, args=("validacion",), use_container_width=True)
            b_guardar.button(
                "Guardar cambio", key="aj_guardar", type="primary", on_click=_guardar, args=(app, folio), use_container_width=True
            )

    with col_hist:
        with st.container(border=True):
            mostrar(Html('<div class="bp-subtitulo bp-sin-margen">Historial de cambios de la orden</div>'))
            log = app.obtener_log_cambios()
            propios = log[log["folio"] == folio].sort_values("id", ascending=False)
            filas = [
                [ui_datos.fecha_hora_corta(f.fecha_hora), f.sku_original, f.sku_nuevo, f.responsable]
                for f in propios.itertuples()
            ]
            if filas:
                mostrar(
                    tabla(
                        [("Fecha y hora", ""), ("SKU original", "bp-sku"), ("SKU nuevo", "bp-sku"), ("Responsable", "")],
                        filas,
                        clase="bp-compacta",
                    )
                )
            else:
                mostrar(banner("info", "Aún no hay cambios en esta orden"))
            mostrar(
                banner(
                    "info",
                    "El SKU original no se borra",
                    "Queda en el registro para mantener la trazabilidad.",
                )
            )
