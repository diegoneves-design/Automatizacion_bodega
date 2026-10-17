"""
Funciones puras (sin Streamlit ni base de datos) que preparan datos para las pantallas:
fechas en español, estado de una orden, filtros y conteos. Se prueban en tests/test_ui_datos.py.
"""

from datetime import date, datetime

import pandas as pd

MESES = ("ene.", "feb.", "mar.", "abr.", "may.", "jun.", "jul.", "ago.", "sep.", "oct.", "nov.", "dic.")

ESTADO_PENDIENTE = "Pendiente"
ESTADO_REVISION = "En revisión"
ESTADO_COMPLETADA = "Completada"

TONO_ESTADO = {
    ESTADO_PENDIENTE: "pendiente",
    ESTADO_REVISION: "revision",
    ESTADO_COMPLETADA: "completada",
}


def _a_datetime(valor):
    if isinstance(valor, datetime):
        return valor
    if isinstance(valor, date):
        return datetime(valor.year, valor.month, valor.day)
    return datetime.fromisoformat(str(valor))


def fecha_corta(valor):
    """10 oct. 2026"""
    d = _a_datetime(valor)
    return f"{d.day} {MESES[d.month - 1]} {d.year}"


def fecha_hora_corta(valor):
    """10 oct. 2026 14:32"""
    d = _a_datetime(valor)
    return f"{fecha_corta(d)} {d:%H:%M}"


def estado_orden(folio, folios_con_cambios, folios_emitidos):
    """
    Estado de una orden, DERIVADO (la base no guarda estados de orden):
      Completada  si se emitio su guia en esta sesion
      En revisión si tiene cambios de ultima hora registrados
      Pendiente   en cualquier otro caso
    """
    if folio in folios_emitidos:
        return ESTADO_COMPLETADA
    if folio in folios_con_cambios:
        return ESTADO_REVISION
    return ESTADO_PENDIENTE


def filtrar_ordenes(resumen, tipo="todas", texto="", fecha=None):
    """
    resumen: DataFrame de app.obtener_resumen_ordenes().
    tipo: 'todas', 'Despacho' o 'Retiro'. texto: parte del folio. fecha: date de la carga.
    """
    df = resumen
    if fecha is not None and not df.empty:
        df = df[pd.to_datetime(df["fecha_carga"]).dt.date == fecha]
    texto = (texto or "").strip().lower()
    if texto and not df.empty:
        df = df[df["folio"].str.lower().str.contains(texto, regex=False)]
    if tipo in ("Despacho", "Retiro") and not df.empty:
        df = df[df["tipo_movimiento"] == tipo]
    return df


def contar_por_tipo(resumen):
    """(total, despachos, retiros) de un resumen ya filtrado por fecha y texto."""
    if resumen.empty:
        return 0, 0, 0
    despachos = int((resumen["tipo_movimiento"] == "Despacho").sum())
    retiros = int((resumen["tipo_movimiento"] == "Retiro").sum())
    return len(resumen), despachos, retiros


def neutralizar_csv(df):
    """
    Evita la inyeccion de formulas al abrir un CSV en Excel: antepone una comilla a los
    textos que empiezan con = + - @. Solo toca columnas de texto.
    """
    limpio = df.copy()
    for col in limpio.columns:
        if limpio[col].dtype == object or str(limpio[col].dtype).startswith("str"):
            limpio[col] = limpio[col].map(
                lambda v: "'" + v if isinstance(v, str) and v[:1] in ("=", "+", "-", "@") else v
            )
    return limpio
