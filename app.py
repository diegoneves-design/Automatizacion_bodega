"""
MVP - Automatizacion de Bodega
Control de carga masiva de SKUs, validacion contra inventario y ajustes de ultima hora.

Ejecutar con: streamlit run app.py
"""

import sqlite3
from datetime import datetime

import pandas as pd
import streamlit as st

DB_PATH = "bodega.db"
MAX_SKUS = 50


# ---------------------------------------------------------------------------
# Capa de datos
# ---------------------------------------------------------------------------

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS inventario (
            sku TEXT PRIMARY KEY,
            descripcion TEXT NOT NULL,
            stock_disponible INTEGER NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS ordenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folio TEXT NOT NULL,
            sku TEXT NOT NULL,
            tipo_movimiento TEXT NOT NULL,
            modalidad TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'CARGADO',
            fecha_carga TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS log_cambios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folio TEXT NOT NULL,
            sku_original TEXT NOT NULL,
            sku_nuevo TEXT NOT NULL,
            responsable TEXT NOT NULL,
            fecha_hora TEXT NOT NULL,
            motivo TEXT
        )
        """
    )

    conn.commit()

    # Inventario simulado inicial (solo si la tabla esta vacia)
    cur.execute("SELECT COUNT(*) FROM inventario")
    if cur.fetchone()[0] == 0:
        inventario_demo = [
            ("EXC-001", "Excavadora CAT 320", 3),
            ("EXC-002", "Excavadora Komatsu PC200", 2),
            ("RET-010", "Retroexcavadora JCB 3CX", 5),
            ("GRU-020", "Grua telescopica 30T", 1),
            ("COM-030", "Compactador de rodillo", 4),
            ("GEN-040", "Generador electrico 100kVA", 6),
            ("MON-050", "Montacargas 3T", 0),
            ("PLA-060", "Plataforma elevadora tijera", 8),
            ("MIX-070", "Mixer de hormigon", 2),
            ("MOT-080", "Motoniveladora CAT 120", 1),
        ]
        cur.executemany(
            "INSERT INTO inventario (sku, descripcion, stock_disponible) VALUES (?, ?, ?)",
            inventario_demo,
        )
        conn.commit()

    conn.close()


def insertar_ordenes(folio, skus, tipo_movimiento, modalidad):
    conn = get_conn()
    cur = conn.cursor()
    fecha = datetime.now().isoformat(timespec="seconds")
    cur.executemany(
        """
        INSERT INTO ordenes (folio, sku, tipo_movimiento, modalidad, estado, fecha_carga)
        VALUES (?, ?, ?, ?, 'CARGADO', ?)
        """,
        [(folio, sku, tipo_movimiento, modalidad, fecha) for sku in skus],
    )
    conn.commit()
    conn.close()


def obtener_folios():
    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT DISTINCT folio FROM ordenes ORDER BY folio DESC", conn
    )
    conn.close()
    return df["folio"].tolist()


def obtener_orden(folio):
    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT * FROM ordenes WHERE folio = ? AND estado = 'CARGADO' ORDER BY id",
        conn,
        params=(folio,),
    )
    conn.close()
    return df


def obtener_inventario():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM inventario ORDER BY sku", conn)
    conn.close()
    return df


def reemplazar_sku(orden_id, folio, sku_original, sku_nuevo, responsable, motivo):
    conn = get_conn()
    cur = conn.cursor()
    fecha_hora = datetime.now().isoformat(timespec="seconds")

    cur.execute(
        "UPDATE ordenes SET estado = 'REEMPLAZADO' WHERE id = ?",
        (orden_id,),
    )
    cur.execute(
        """
        INSERT INTO ordenes (folio, sku, tipo_movimiento, modalidad, estado, fecha_carga)
        SELECT folio, ?, tipo_movimiento, modalidad, 'CARGADO', ?
        FROM ordenes WHERE id = ?
        """,
        (sku_nuevo, fecha_hora, orden_id),
    )
    cur.execute(
        """
        INSERT INTO log_cambios (folio, sku_original, sku_nuevo, responsable, fecha_hora, motivo)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (folio, sku_original, sku_nuevo, responsable, fecha_hora, motivo),
    )
    conn.commit()
    conn.close()


def obtener_log_cambios():
    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT * FROM log_cambios ORDER BY id DESC", conn
    )
    conn.close()
    return df


# ---------------------------------------------------------------------------
# Logica de negocio pura (sin dependencias de Streamlit) - facil de testear
# ---------------------------------------------------------------------------

def deduplicar_skus(skus):
    """Limpia espacios, descarta vacios y elimina duplicados preservando el orden."""
    return list(dict.fromkeys(s.strip() for s in skus if s and s.strip()))


def clasificar_fila(row):
    """Determina el resultado de validacion de una fila orden+inventario ya cruzada."""
    if row["_merge"] == "left_only":
        return "SKU NO EXISTE EN INVENTARIO"
    if row["stock_disponible"] <= 0:
        return "SIN STOCK DISPONIBLE"
    return "OK"


def validar_orden(folio):
    """Cruza los SKUs activos de un folio contra el inventario y clasifica cada fila."""
    orden_df = obtener_orden(folio)
    if orden_df.empty:
        return orden_df

    inventario_df = obtener_inventario()
    merged = orden_df.merge(inventario_df, on="sku", how="left", indicator=True)
    merged["resultado"] = merged.apply(clasificar_fila, axis=1)
    return merged


# ---------------------------------------------------------------------------
# Vistas
# ---------------------------------------------------------------------------

def vista_carga_masiva():
    st.header("Carga masiva de SKUs")
    st.caption(f"Pega o carga hasta {MAX_SKUS} SKUs para generar una orden de despacho o retiro.")

    folio = st.text_input("Folio de guia / orden", placeholder="Ej: GUIA-2026-001")

    col1, col2 = st.columns(2)
    with col1:
        tipo_movimiento = st.selectbox("Tipo de movimiento", ["Despacho", "Retiro"])
    with col2:
        modalidad = st.selectbox("Modalidad", ["Convencional", "Alternativo"])

    texto_skus = st.text_area(
        "Pega los SKUs (uno por linea)",
        height=200,
        placeholder="EXC-001\nEXC-002\nRET-010\n...",
    )

    archivo = st.file_uploader("O carga un archivo .txt / .csv con un SKU por linea", type=["txt", "csv"])

    skus_crudos = []
    if texto_skus.strip():
        skus_crudos.extend(texto_skus.splitlines())
    if archivo is not None:
        contenido = archivo.read().decode("utf-8", errors="ignore")
        skus_crudos.extend(contenido.splitlines())

    skus_unicos = deduplicar_skus(skus_crudos)

    if skus_unicos:
        st.write(f"**SKUs detectados:** {len(skus_unicos)}")
        if len(skus_unicos) > MAX_SKUS:
            st.error(f"Se detectaron {len(skus_unicos)} SKUs. El limite permitido es {MAX_SKUS}.")
        else:
            st.dataframe(pd.DataFrame({"SKU": skus_unicos}), use_container_width=True, hide_index=True)

    if st.button("Cargar orden", type="primary", disabled=not skus_unicos or len(skus_unicos) > MAX_SKUS):
        if not folio.strip():
            st.warning("Debes ingresar un folio antes de cargar la orden.")
        else:
            insertar_ordenes(folio.strip(), skus_unicos, tipo_movimiento, modalidad)
            st.success(f"Orden '{folio}' cargada con {len(skus_unicos)} SKUs.")


def vista_validador():
    st.header("Validador de inventario")
    st.caption("Cruza los SKUs cargados en una orden contra el inventario disponible en bodega.")

    folios = obtener_folios()
    if not folios:
        st.info("Aun no hay ordenes cargadas. Ve a 'Carga masiva' para crear una.")
        return

    folio = st.selectbox("Selecciona un folio", folios)
    merged = validar_orden(folio)

    if merged.empty:
        st.info("Esta orden no tiene SKUs activos (posiblemente todos fueron reemplazados).")
        return

    total = len(merged)
    ok = (merged["resultado"] == "OK").sum()
    discrepancias = total - ok

    col1, col2, col3 = st.columns(3)
    col1.metric("Total SKUs", total)
    col2.metric("Validos", int(ok))
    col3.metric("Con discrepancia", int(discrepancias), delta_color="inverse")

    def resaltar(row):
        color = "" if row["resultado"] == "OK" else "background-color: #ffcccc"
        return [color] * len(row)

    columnas_mostrar = ["sku", "descripcion", "stock_disponible", "tipo_movimiento", "modalidad", "resultado"]
    st.dataframe(
        merged[columnas_mostrar].style.apply(resaltar, axis=1),
        use_container_width=True,
        hide_index=True,
    )

    if discrepancias > 0:
        st.error(f"Se encontraron {discrepancias} discrepancia(s). Revisa antes de despachar.")
    else:
        st.success("Todos los SKUs fueron validados correctamente contra el inventario.")

    st.download_button(
        "Descargar validacion (CSV)",
        data=merged[columnas_mostrar].to_csv(index=False).encode("utf-8"),
        file_name=f"validacion_{folio}.csv",
        mime="text/csv",
    )


def vista_ajuste_ultima_hora():
    st.header("Ajuste de ultima hora")
    st.caption("Reemplaza un SKU ya cargado por otro y deja registro automatico en el log de cambios.")

    folios = obtener_folios()
    if not folios:
        st.info("Aun no hay ordenes cargadas. Ve a 'Carga masiva' para crear una.")
        return

    folio = st.selectbox("Folio a modificar", folios, key="folio_ajuste")
    orden_df = obtener_orden(folio)

    if orden_df.empty:
        st.info("Esta orden no tiene SKUs activos para reemplazar.")
        return

    st.dataframe(
        orden_df[["id", "sku", "tipo_movimiento", "modalidad", "fecha_carga"]],
        use_container_width=True,
        hide_index=True,
    )

    inventario_df = obtener_inventario()
    opciones = {
        f"{row.id} - {row.sku}": row.id for row in orden_df.itertuples()
    }

    with st.form("form_reemplazo"):
        seleccion = st.selectbox("SKU original a reemplazar", list(opciones.keys()))
        sku_nuevo = st.selectbox("SKU de reemplazo", inventario_df["sku"].tolist())
        responsable = st.text_input("Responsable del cambio", placeholder="Nombre de quien autoriza")
        motivo = st.text_area("Motivo del reemplazo (opcional)", placeholder="Ej: equipo en mantenimiento")
        enviar = st.form_submit_button("Registrar reemplazo", type="primary")

    if enviar:
        sku_original = seleccion.split(" - ", 1)[1]
        if not responsable.strip():
            st.warning("Debes indicar el responsable del cambio.")
        elif sku_nuevo == sku_original:
            st.warning("El SKU de reemplazo debe ser distinto al original.")
        else:
            orden_id = opciones[seleccion]
            reemplazar_sku(orden_id, folio, sku_original, sku_nuevo, responsable.strip(), motivo.strip())
            st.success(
                f"SKU '{sku_original}' reemplazado por '{sku_nuevo}' en la orden '{folio}'."
            )
            st.rerun()

    st.subheader("Log de cambios")
    log_df = obtener_log_cambios()
    if log_df.empty:
        st.caption("Sin cambios registrados todavia.")
    else:
        st.dataframe(log_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Descargar log de cambios (CSV)",
            data=log_df.to_csv(index=False).encode("utf-8"),
            file_name="log_cambios.csv",
            mime="text/csv",
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    st.set_page_config(page_title="Automatizacion de Bodega", layout="wide")
    init_db()

    st.sidebar.title("Automatizacion de Bodega")
    vista = st.sidebar.radio(
        "Selecciona una vista",
        ["1. Carga masiva", "2. Validador", "3. Ajuste de ultima hora"],
    )

    if vista == "1. Carga masiva":
        vista_carga_masiva()
    elif vista == "2. Validador":
        vista_validador()
    else:
        vista_ajuste_ultima_hora()


if __name__ == "__main__":
    main()
