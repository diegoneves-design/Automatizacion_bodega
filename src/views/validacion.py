"""Pantalla 3: Resultado de validación (criterio de la HU-01: sin guía mientras haya SKU con problemas)."""

import streamlit as st

import db
import ui_datos
from ui_components import banner, mostrar, pill, tabla, titulo
from ui_nav import avisar, boton_volver, ir, mostrar_aviso

COLUMNAS_CSV = ["sku", "descripcion", "resultado", "detalle"]


def _validar_ahora(repo, folio):
    """Callback: valida la orden en la base; el resultado queda guardado."""
    try:
        repo.validar(folio)
    except (db.ReglaDeNegocio, db.ErrorDeBase) as e:
        avisar("error", getattr(e, "mensaje", str(e)))


def _emitir(repo, folio):
    """Callback: pide la guia a la base, que vuelve a revisar todo antes de emitirla (solo el jefe de bodega puede)."""
    try:
        repo.preparar_guia(folio, st.session_state.get("id_usuario"))
    except (db.ReglaDeNegocio, db.ErrorDeBase) as e:
        avisar("error", getattr(e, "mensaje", str(e)))
        return
    ir("guia", folio)


def render(repo):
    ss = st.session_state
    folio = ss.folio
    boton_volver("← Volver al detalle", "detalle", "volver_detalle")
    mostrar(titulo("Resultado de validación", "Revisa el estado de cada SKU y corrige si es necesario."))
    mostrar_aviso()

    orden = repo.orden(folio) if folio else None
    lineas = repo.lineas(folio) if orden else None
    if orden is None or lineas.empty:
        mostrar(banner("info", "No hay equipos para validar", "Elige una orden con equipos desde Órdenes."))
        return

    emitida = orden["estado"] == "emitida"
    if ui_datos.sin_validar(lineas) and not emitida:
        mostrar(banner("info", "Esta orden aún no se valida", "Valídala para ver el estado de cada equipo."))
        c_volver, _, c_validar = st.columns(3)
        c_volver.button("← Volver", key="validacion_volver_pend", on_click=ir, args=("detalle",), use_container_width=True)
        c_validar.button(
            "Validar ahora", key="validacion_validar", type="primary", on_click=_validar_ahora, args=(repo, folio), use_container_width=True
        )
        return

    validos, total = ui_datos.contar_validos_lineas(lineas)
    con_problemas = validos != total

    if con_problemas:
        mostrar(banner("error", "Validación con diferencias", f"{validos} de {total} SKU son válidos."))
    else:
        mostrar(banner("ok", "Validación completada", f"{validos} de {total} SKU son válidos."))

    filas = []
    csv = []
    primer_problema = None
    for i, f in enumerate(lineas.itertuples(), start=1):
        etiqueta, tono, detalle = ui_datos.describir_resultado_base(f.resultado, f.estado_equipo)
        descripcion = f.descripcion if isinstance(f.descripcion, str) else "—"
        if tono != "ok" and primer_problema is None:
            primer_problema = f.sku
        filas.append([i, f.sku, descripcion, pill(etiqueta, tono), detalle])
        csv.append({"sku": f.sku, "descripcion": descripcion, "resultado": etiqueta, "detalle": detalle})
    mostrar(
        tabla(
            [("#", "bp-oculto-movil"), ("SKU", "bp-sku"), ("Equipo", ""), ("Estado", ""), ("Detalle", "")],
            filas,
        )
    )

    if con_problemas and not emitida:
        mostrar(
            banner(
                "aviso",
                "No se puede emitir la guía",
                "Existen SKU con problemas. Corrige la información para continuar.",
            )
        )

    c_volver, c_corregir, c_emitir = st.columns(3)
    c_volver.button("← Volver", key="validacion_volver", on_click=ir, args=("detalle",), use_container_width=True)
    if con_problemas and not emitida:
        c_corregir.button(
            "Corregir SKU",
            key="validacion_corregir",
            type="primary",
            on_click=ir,
            args=("ajuste", folio, primer_problema),
            use_container_width=True,
        )
    if emitida:
        c_emitir.button(
            "Ver guía →", key="validacion_ver_guia", type="primary", on_click=ir, args=("guia", folio), use_container_width=True
        )
    else:
        c_emitir.button(
            "Emitir guía →",
            key="validacion_emitir",
            type="primary",
            on_click=_emitir,
            args=(repo, folio),
            disabled=con_problemas,
            use_container_width=True,
        )

    import pandas as pd

    st.download_button(
        "Descargar validación (CSV)",
        data=ui_datos.neutralizar_csv(pd.DataFrame(csv, columns=COLUMNAS_CSV)).to_csv(index=False).encode("utf-8"),
        file_name=f"validacion_{folio}.csv",
        mime="text/csv",
        key="validacion_csv",
    )
