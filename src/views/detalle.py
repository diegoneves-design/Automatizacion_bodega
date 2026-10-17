"""Pantalla 2: Detalle de la orden."""

import streamlit as st

import ui_datos
from ui_components import banner, ficha_orden, mostrar, pill, subtitulo, tabla, titulo
from ui_nav import boton_volver, ir


def _validar(folio):
    """Callback: pide la validacion de la orden y abre el resultado."""
    st.session_state.validadas.add(folio)
    ir("validacion", folio)


def render(app):
    ss = st.session_state
    folio = ss.folio
    boton_volver("← Volver a órdenes", "ordenes", "volver_ordenes")
    mostrar(titulo("Detalle de la orden", "Revisa los equipos y valida su información."))

    resumen = app.obtener_resumen_ordenes()
    fila = resumen[resumen["folio"] == folio] if folio else resumen.iloc[0:0]
    if fila.empty:
        mostrar(banner("info", "No hay una orden seleccionada", "Elige una desde Órdenes."))
        return
    fila = fila.iloc[0]

    log = app.obtener_log_cambios()
    estado = ui_datos.estado_orden(folio, set(log["folio"]), set(ss.guias))
    mostrar(
        ficha_orden(
            folio,
            pill(estado, ui_datos.TONO_ESTADO[estado]),
            [
                ("Tipo de movimiento", fila["tipo_movimiento"]),
                ("Modalidad", fila["modalidad"]),
                ("Fecha", ui_datos.fecha_corta(fila["fecha_carga"])),
            ],
        )
    )

    validada = app.validar_orden(folio)
    mostrar(subtitulo(f"Equipos en la orden ({len(validada)})"))

    ya_validada = folio in ss.validadas
    modificaciones = ui_datos.ultimas_modificaciones(log, folio)
    filas = []
    for i, f in enumerate(validada.itertuples(), start=1):
        if ya_validada:
            etiqueta, tono, _ = ui_datos.describir_resultado(f.resultado, f.stock_disponible)
        else:
            etiqueta, tono = "Sin validar", "error"
        cambio = modificaciones.get(f.sku)
        filas.append(
            [
                i,
                f.sku,
                f.descripcion if isinstance(f.descripcion, str) else "—",
                pill(etiqueta, tono),
                ui_datos.fecha_hora_corta(cambio) if cambio else "-",
            ]
        )
    mostrar(
        tabla(
            [("#", "bp-oculto-movil"), ("SKU", "bp-sku"), ("Equipo", ""), ("Estado", ""), ("Última modificación", "")],
            filas,
        )
    )

    _, col_boton = st.columns([3, 1.4])
    col_boton.button(
        "Validar SKUs →",
        key="validar_skus",
        type="primary",
        on_click=_validar,
        args=(folio,),
        use_container_width=True,
        disabled=validada.empty,
    )
