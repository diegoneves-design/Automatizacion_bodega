"""Pantalla 4: Ajuste de última hora (reemplazo de un SKU con registro del cambio)."""

import streamlit as st

import db
import ui_datos
from ui_components import Html, banner, esc, icono, mostrar, tabla, titulo
from ui_nav import avisar, boton_volver, ir

# Motivos que se ofrecen en la lista (provisorios). Con las observaciones, el texto no puede pasar de 200 caracteres.
MOTIVOS = ["Falla en equipo original", "Sin stock", "Solicitud de mantenimiento", "Otro"]
MAX_OBSERVACIONES = 150  # 26 (el motivo mas largo) + 2 (": ") + 150 = 178, bajo los 200 de la base
MIN_BUSQUEDA = 2
MAX_RESULTADOS = 30


def _guardar(repo, folio):
    """Callback: registra el reemplazo en la base. Si una regla lo rechaza, deja el mensaje exacto en pantalla."""
    ss = st.session_state
    original = ss.get("aj_orig")
    nuevo = ss.get("aj_nuevo")
    texto_motivo = ui_datos.motivo_con_observaciones(ss.get("aj_motivo") or MOTIVOS[0], ss.get("aj_obs"))
    if not nuevo:
        ss.aj_error = "Busca y elige el equipo que entra."
        return
    try:
        repo.registrar_cambio(folio, original, nuevo, ss.get("aj_resp"), texto_motivo)
    except (db.ReglaDeNegocio, db.ErrorDeBase) as e:
        ss.aj_error = getattr(e, "mensaje", str(e))
        return
    ss.aj_error = None
    avisar("ok", f"Cambio registrado: {original} → {nuevo}. Vuelve a validar la orden.")
    ir("validacion", folio)


def _historial(repo, folio):
    with st.container(border=True):
        mostrar(Html('<div class="bp-subtitulo bp-sin-margen">Historial de cambios de la orden</div>'))
        propios = repo.cambios(folio)
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


def render(repo):
    ss = st.session_state
    folio = ss.folio
    boton_volver("← Volver a la validación", "validacion", "volver_validacion")
    mostrar(titulo("Ajuste de última hora", "Reemplaza un equipo y registra el cambio."))

    orden = repo.orden(folio) if folio else None
    lineas = repo.lineas(folio) if orden else None
    if orden is None or lineas.empty:
        mostrar(banner("info", "No hay equipos para ajustar", "Elige una orden con equipos desde Órdenes."))
        return

    if orden["estado"] == "emitida":
        mostrar(banner("info", "Esta orden ya tiene guía emitida", "Una orden con guía no admite cambios."))
        _historial(repo, folio)
        return

    vigentes = list(lineas["sku"])
    descripcion = dict(zip(lineas["sku"], lineas["descripcion"]))
    problemas = [f.sku for f in lineas.itertuples() if f.resultado in ("no_existe", "no_disponible")]
    inicial = ss.sku_corregir if ss.sku_corregir in vigentes else (problemas[0] if problemas else vigentes[0])

    usuarios = {u["id_usuario"]: f'{u["nombre"]} · {ui_datos.nombre_rol(u["rol"])}' for u in repo.usuarios()}
    ids = list(usuarios)
    col_form, col_hist = st.columns([1.15, 1])

    with col_form:
        with st.container(border=True):
            mostrar(Html('<div class="bp-subtitulo bp-sin-margen">Reemplazar equipo</div>'))
            original = st.selectbox("SKU a reemplazar", vigentes, index=vigentes.index(inicial), key="aj_orig")
            desc = descripcion.get(original)
            st.markdown(f'<div class="bp-ayuda">{esc(desc if isinstance(desc, str) else "No existe en el inventario")}</div>', unsafe_allow_html=True)

            st.markdown(f'<div class="bp-flecha-par">{icono("ajuste", 22)}</div>', unsafe_allow_html=True)
            buscar = st.text_input("Buscar el equipo que entra", placeholder="Escribe parte del SKU o de la descripción", key="aj_buscar")
            encontrados = repo.buscar_equipos(buscar, MAX_RESULTADOS) if len((buscar or "").strip()) >= MIN_BUSQUEDA else None
            opciones = {} if encontrados is None else {f.sku: f for f in encontrados.itertuples()}
            nuevo = st.selectbox(
                "Nuevo SKU",
                list(opciones),
                index=None,
                placeholder="Busca arriba y elige uno" if encontrados is None or not opciones else "Elige el equipo",
                format_func=lambda s: f"{s} · {opciones[s].descripcion}" if s in opciones else s,
                key="aj_nuevo",
            )
            if encontrados is not None and encontrados.empty:
                st.markdown('<div class="bp-ayuda">Ningún equipo coincide con la búsqueda.</div>', unsafe_allow_html=True)
            elif encontrados is not None and len(encontrados) == MAX_RESULTADOS:
                st.markdown(f'<div class="bp-ayuda">Se muestran los primeros {MAX_RESULTADOS}: escribe más para acotar.</div>', unsafe_allow_html=True)
            if nuevo and opciones[nuevo].estado != "disponible":
                estado = ui_datos.ESTADOS_EQUIPO.get(opciones[nuevo].estado, opciones[nuevo].estado)
                st.markdown(f'<div class="bp-ayuda">Estado del equipo: {esc(estado)}. La orden seguirá bloqueada.</div>', unsafe_allow_html=True)

            st.selectbox("Motivo del cambio", MOTIVOS, key="aj_motivo")
            st.selectbox(
                "Responsable",
                ids,
                index=ids.index(ss.id_usuario) if ss.id_usuario in ids else 0,
                format_func=usuarios.get,
                key="aj_resp",
            )
            st.text_area("Observaciones (opcional)", max_chars=MAX_OBSERVACIONES, height=90, key="aj_obs")
            if ss.get("aj_error"):
                mostrar(banner("error", ss.aj_error))
            b_cancelar, b_guardar = st.columns(2)
            b_cancelar.button("Cancelar", key="aj_cancelar", on_click=ir, args=("validacion",), use_container_width=True)
            b_guardar.button(
                "Guardar cambio", key="aj_guardar", type="primary", on_click=_guardar, args=(repo, folio), use_container_width=True
            )

    with col_hist:
        _historial(repo, folio)

