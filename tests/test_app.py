"""
Tests de la capa de datos y logica de negocio de app.py.

Cada test usa una base de datos SQLite temporal e independiente
(monkeypatch de app.DB_PATH) para no interferir entre si ni con
la base de datos real usada por la app en ejecucion.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import app  # noqa: E402


@pytest.fixture
def db(tmp_path, monkeypatch):
    """Redirige app.DB_PATH a un archivo temporal e inicializa el esquema."""
    ruta = tmp_path / "test_bodega.db"
    monkeypatch.setattr(app, "DB_PATH", str(ruta))
    app.init_db()
    return ruta


# ---------------------------------------------------------------------------
# deduplicar_skus
# ---------------------------------------------------------------------------

def test_deduplicar_skus_elimina_duplicados_y_vacios():
    entrada = ["EXC-001", " EXC-002 ", "", "EXC-001", "   ", "RET-010"]
    resultado = app.deduplicar_skus(entrada)
    assert resultado == ["EXC-001", "EXC-002", "RET-010"]


def test_deduplicar_skus_preserva_orden_de_aparicion():
    entrada = ["C", "A", "B", "A", "C"]
    assert app.deduplicar_skus(entrada) == ["C", "A", "B"]


def test_deduplicar_skus_lista_vacia():
    assert app.deduplicar_skus([]) == []


# ---------------------------------------------------------------------------
# init_db / inventario semilla
# ---------------------------------------------------------------------------

def test_init_db_crea_inventario_semilla(db):
    inventario = app.obtener_inventario()
    assert len(inventario) == 10
    assert "sku" in inventario.columns
    assert "MON-050" in inventario["sku"].values


def test_init_db_es_idempotente(db):
    filas_antes = len(app.obtener_inventario())
    app.init_db()  # segunda llamada no debe duplicar la semilla
    filas_despues = len(app.obtener_inventario())
    assert filas_antes == filas_despues == 10


# ---------------------------------------------------------------------------
# insertar_ordenes / obtener_orden / obtener_folios
# ---------------------------------------------------------------------------

def test_insertar_ordenes_y_obtener_orden(db):
    skus = ["EXC-001", "EXC-002", "RET-010"]
    app.insertar_ordenes("GUIA-001", skus, "Despacho", "Convencional")

    orden = app.obtener_orden("GUIA-001")
    assert len(orden) == 3
    assert set(orden["sku"]) == set(skus)
    assert (orden["estado"] == "CARGADO").all()
    assert (orden["tipo_movimiento"] == "Despacho").all()


def test_obtener_orden_folio_inexistente_retorna_vacio(db):
    orden = app.obtener_orden("NO-EXISTE")
    assert orden.empty


def test_obtener_folios_lista_folios_unicos(db):
    app.insertar_ordenes("GUIA-001", ["EXC-001"], "Despacho", "Convencional")
    app.insertar_ordenes("GUIA-002", ["EXC-002"], "Retiro", "Alternativo")

    folios = app.obtener_folios()
    assert set(folios) == {"GUIA-001", "GUIA-002"}


# ---------------------------------------------------------------------------
# reemplazar_sku / log_cambios
# ---------------------------------------------------------------------------

def test_reemplazar_sku_archiva_original_y_crea_nuevo(db):
    app.insertar_ordenes("GUIA-001", ["MON-050"], "Despacho", "Convencional")
    orden = app.obtener_orden("GUIA-001")
    orden_id = int(orden.iloc[0]["id"])

    app.reemplazar_sku(orden_id, "GUIA-001", "MON-050", "PLA-060", "Bastian Vargas", "Mantenimiento")

    orden_activa = app.obtener_orden("GUIA-001")
    assert list(orden_activa["sku"]) == ["PLA-060"]
    assert (orden_activa["estado"] == "CARGADO").all()


def test_reemplazar_sku_registra_log_de_cambios(db):
    app.insertar_ordenes("GUIA-001", ["MON-050"], "Despacho", "Convencional")
    orden_id = int(app.obtener_orden("GUIA-001").iloc[0]["id"])

    app.reemplazar_sku(orden_id, "GUIA-001", "MON-050", "PLA-060", "Bastian Vargas", "Mantenimiento")

    log = app.obtener_log_cambios()
    assert len(log) == 1
    fila = log.iloc[0]
    assert fila["folio"] == "GUIA-001"
    assert fila["sku_original"] == "MON-050"
    assert fila["sku_nuevo"] == "PLA-060"
    assert fila["responsable"] == "Bastian Vargas"
    assert fila["fecha_hora"]  # no vacio


# ---------------------------------------------------------------------------
# validar_orden (validador de inventario)
# ---------------------------------------------------------------------------

def test_validar_orden_marca_ok_cuando_hay_stock(db):
    app.insertar_ordenes("GUIA-001", ["EXC-001"], "Despacho", "Convencional")
    resultado = app.validar_orden("GUIA-001")
    assert resultado.iloc[0]["resultado"] == "OK"


def test_validar_orden_marca_sin_stock(db):
    # MON-050 tiene stock_disponible = 0 en la semilla de datos
    app.insertar_ordenes("GUIA-001", ["MON-050"], "Despacho", "Convencional")
    resultado = app.validar_orden("GUIA-001")
    assert resultado.iloc[0]["resultado"] == "SIN STOCK DISPONIBLE"


def test_validar_orden_marca_sku_inexistente(db):
    app.insertar_ordenes("GUIA-001", ["SKU-FANTASMA"], "Despacho", "Convencional")
    resultado = app.validar_orden("GUIA-001")
    assert resultado.iloc[0]["resultado"] == "SKU NO EXISTE EN INVENTARIO"


def test_validar_orden_folio_sin_skus_activos_retorna_vacio(db):
    resultado = app.validar_orden("FOLIO-INEXISTENTE")
    assert resultado.empty


def test_validar_orden_mixta_cuenta_correctamente(db):
    app.insertar_ordenes(
        "GUIA-001",
        ["EXC-001", "MON-050", "SKU-FANTASMA"],
        "Despacho",
        "Convencional",
    )
    resultado = app.validar_orden("GUIA-001")
    conteo = resultado["resultado"].value_counts().to_dict()
    assert conteo.get("OK") == 1
    assert conteo.get("SIN STOCK DISPONIBLE") == 1
    assert conteo.get("SKU NO EXISTE EN INVENTARIO") == 1
