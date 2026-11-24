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


def fecha_emision(valor):
    """10 oct. 2026 - 14:35 (fecha de emision de una guia)."""
    d = _a_datetime(valor)
    return f"{fecha_corta(d)} - {d:%H:%M}"


def unir_lineas(texto, contenido_archivo=None):
    """Lineas de SKU pegadas en el cuadro de texto mas las de un archivo (bytes), sin limpiar."""
    lineas = []
    if texto and texto.strip():
        lineas.extend(texto.splitlines())
    if contenido_archivo:
        lineas.extend(contenido_archivo.decode("utf-8", errors="ignore").splitlines())
    return lineas


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


# Resultado de app.validar_orden -> (etiqueta, tono de la etiqueta, texto de detalle)
RESULTADOS = {
    "OK": ("OK", "ok", "En inventario"),
    "SIN STOCK DISPONIBLE": ("Sin stock", "error", "Stock: 0"),
    "SKU NO EXISTE EN INVENTARIO": ("No existe", "error", "No existe en inventario"),
}


def describir_resultado(resultado, stock=None):
    """(etiqueta, tono, detalle) de un resultado de validacion; el stock se muestra si hay."""
    etiqueta, tono, detalle = RESULTADOS.get(resultado, (str(resultado), "error", ""))
    if resultado == "SIN STOCK DISPONIBLE" and stock is not None and not pd.isna(stock):
        detalle = f"Stock: {int(stock)}"
    return etiqueta, tono, detalle


def contar_validos(validada):
    """(validos, total) de un DataFrame devuelto por app.validar_orden."""
    if validada.empty:
        return 0, 0
    return int((validada["resultado"] == "OK").sum()), len(validada)


def ultimas_modificaciones(log, folio):
    """{sku_nuevo: fecha_hora} del ultimo reemplazo de cada SKU en una orden."""
    if log.empty:
        return {}
    propios = log[log["folio"] == folio].sort_values("id")
    return dict(zip(propios["sku_nuevo"], propios["fecha_hora"]))


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


# ---------------------------------------------------------------------------
# MVP con base real (src/db.py): el estado y el resultado de cada linea vienen guardados en la base.
# Lo anterior (estado_orden, RESULTADOS, describir_resultado, contar_validos) sigue para la interfaz clasica.
# ---------------------------------------------------------------------------

# estado de la orden en la base -> (etiqueta, tono de la etiqueta)
ESTADOS_ORDEN = {
    "pendiente": (ESTADO_PENDIENTE, "pendiente"),
    "bloqueada": ("Bloqueada", "error"),
    "validada": ("Validada", "ok"),
    "emitida": (ESTADO_COMPLETADA, "completada"),
}

ESTADOS_EQUIPO = {
    "disponible": "Disponible",
    "arrendado": "Arrendado",
    "en_mantencion": "En mantención",
    "fuera_servicio": "Fuera de servicio",
}


ROLES = {"jefe_bodega": "Jefe de bodega", "mantenimiento": "Mantenimiento", "comercial": "Comercial", "gerente": "Gerente"}


def nombre_rol(rol):
    """Nombre del rol para mostrar."""
    return ROLES.get(rol, str(rol))


def estado_visible(estado):
    """(etiqueta, tono) del estado de una orden tal como lo guarda la base."""
    return ESTADOS_ORDEN.get(estado, (str(estado), "neutro"))


def describir_resultado_base(resultado, estado_equipo=None):
    """(etiqueta, tono, detalle) del resultado guardado de una linea: ok, pendiente, no_existe o no_disponible."""
    if resultado == "ok":
        return "OK", "ok", "Disponible en bodega"
    if resultado == "pendiente":
        return "Sin validar", "pendiente", "Aún sin validar"
    if resultado == "no_existe":
        return "No existe", "error", "No existe en inventario"
    if resultado == "no_disponible":
        estado = ESTADOS_EQUIPO.get(estado_equipo, "Sin stock") if isinstance(estado_equipo, str) else "Sin stock"
        return "No disponible", "error", estado
    return str(resultado), "error", ""


def contar_validos_lineas(lineas):
    """(validos, total) de un DataFrame de db.Repositorio.lineas."""
    if lineas.empty:
        return 0, 0
    return int((lineas["resultado"] == "ok").sum()), len(lineas)


def sin_validar(lineas):
    """True si alguna linea todavia no se valida."""
    return (not lineas.empty) and bool((lineas["resultado"] == "pendiente").any())


def texto_o_guion(valor, convertir=str):
    """El valor como texto, o un guion si falta (None, NaN o NaT)."""
    if valor is None or (not isinstance(valor, str) and pd.isna(valor)):
        return "-"
    return convertir(valor)


MAX_MOTIVO = 200  # el motivo de un cambio no puede pasar de esto (regla de la base)


def motivo_con_observaciones(motivo, observaciones):
    """El motivo de la lista y, si hay, las observaciones: 'Sin stock: el equipo llego danado'."""
    observaciones = (observaciones or "").strip()
    return f"{motivo}: {observaciones}" if observaciones else motivo


def texto_guia(guia, orden, lineas):
    """
    Texto plano de la guia emitida. guia: {numero_guia, fecha_emision}; orden: fila de db.ordenes();
    lineas: DataFrame de db.lineas (solo las vigentes).
    """
    ancho_sku, ancho_desc = 18, 40
    filas = [
        "GUIA DE DESPACHO / RETIRO",
        f"N de guia: {guia['numero_guia']}",
        f"Folio: {orden['folio']}",
        f"Cliente: {orden.get('cliente') or '-'}",
        f"Tipo de movimiento: {orden['tipo_movimiento']} ({orden['modalidad']})",
        f"Fecha de emision: {fecha_emision(guia['fecha_emision'])}",
        "",
        f"{'SKU':<{ancho_sku}}{'Descripcion':<{ancho_desc}}",
        "-" * (ancho_sku + ancho_desc),
    ]
    for f in lineas.itertuples():
        descripcion = f.descripcion if isinstance(f.descripcion, str) else "(sin descripcion)"
        filas.append(f"{f.sku:<{ancho_sku}}{descripcion:<{ancho_desc}}")
    filas += ["-" * (ancho_sku + ancho_desc), f"Total de equipos: {len(lineas)}"]
    return "\n".join(filas)
