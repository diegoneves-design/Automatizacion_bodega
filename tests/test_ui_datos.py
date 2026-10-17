"""
Pruebas de las funciones puras de la interfaz (ui_datos, ui_components) y de la
consulta nueva obtener_resumen_ordenes de app.py. No requieren abrir Streamlit.
"""

import sys
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import app  # noqa: E402
import ui_components as uc  # noqa: E402
import ui_datos  # noqa: E402


@pytest.fixture
def db(tmp_path, monkeypatch):
    monkeypatch.setattr(app, "DB_PATH", str(tmp_path / "test_bodega.db"))
    app.init_db()
    return tmp_path


# ---------------------------------------------------------------------------
# Fechas
# ---------------------------------------------------------------------------

def test_fecha_corta_desde_texto_iso_date_y_datetime():
    assert ui_datos.fecha_corta("2026-10-10T14:32:05") == "10 oct. 2026"
    assert ui_datos.fecha_corta(date(2026, 1, 5)) == "5 ene. 2026"
    assert ui_datos.fecha_corta(datetime(2026, 12, 31, 23, 59)) == "31 dic. 2026"


def test_fecha_hora_corta_incluye_hora_con_dos_digitos():
    assert ui_datos.fecha_hora_corta("2026-10-10T09:05:00") == "10 oct. 2026 09:05"


def test_fecha_emision_une_fecha_y_hora():
    assert ui_datos.fecha_emision(datetime(2026, 10, 10, 14, 35, 9)) == "10 oct. 2026 - 14:35"


# ---------------------------------------------------------------------------
# Estado de la orden
# ---------------------------------------------------------------------------

def test_estado_orden_prioriza_completada_sobre_revision():
    assert ui_datos.estado_orden("A", {"A"}, {"A"}) == "Completada"


def test_estado_orden_revision_si_hay_cambios():
    assert ui_datos.estado_orden("A", {"A"}, set()) == "En revisión"


def test_estado_orden_pendiente_por_defecto():
    assert ui_datos.estado_orden("A", set(), set()) == "Pendiente"


# ---------------------------------------------------------------------------
# Filtros y conteos
# ---------------------------------------------------------------------------

@pytest.fixture
def resumen():
    return pd.DataFrame(
        {
            "folio": ["PV-001", "PV-002", "PV-003"],
            "tipo_movimiento": ["Despacho", "Retiro", "Despacho"],
            "modalidad": ["Convencional", "Preventivo", "Alternativo"],
            "fecha_carga": ["2026-10-10T08:00:00", "2026-10-10T09:00:00", "2026-10-09T10:00:00"],
            "skus_vigentes": [5, 2, 3],
        }
    )


def test_filtrar_por_fecha(resumen):
    assert list(ui_datos.filtrar_ordenes(resumen, fecha=date(2026, 10, 10))["folio"]) == ["PV-001", "PV-002"]


def test_filtrar_por_tipo(resumen):
    assert list(ui_datos.filtrar_ordenes(resumen, tipo="Retiro")["folio"]) == ["PV-002"]


def test_filtrar_por_texto_ignora_mayusculas_y_espacios(resumen):
    assert list(ui_datos.filtrar_ordenes(resumen, texto="  pv-003 ")["folio"]) == ["PV-003"]


def test_filtrar_texto_no_trata_el_texto_como_expresion_regular(resumen):
    assert ui_datos.filtrar_ordenes(resumen, texto=".*").empty


def test_filtrar_sobre_resumen_vacio_no_falla():
    vacio = pd.DataFrame(columns=["folio", "tipo_movimiento", "modalidad", "fecha_carga", "skus_vigentes"])
    assert ui_datos.filtrar_ordenes(vacio, "Despacho", "x", date(2026, 10, 10)).empty


def test_contar_por_tipo(resumen):
    assert ui_datos.contar_por_tipo(resumen) == (3, 2, 1)
    assert ui_datos.contar_por_tipo(resumen.iloc[0:0]) == (0, 0, 0)


# ---------------------------------------------------------------------------
# Resultado de validacion
# ---------------------------------------------------------------------------

def test_describir_resultado_ok():
    assert ui_datos.describir_resultado("OK") == ("OK", "ok", "En inventario")


def test_describir_resultado_sin_stock_muestra_el_stock():
    assert ui_datos.describir_resultado("SIN STOCK DISPONIBLE", 0) == ("Sin stock", "error", "Stock: 0")


def test_describir_resultado_sku_inexistente():
    etiqueta, tono, detalle = ui_datos.describir_resultado("SKU NO EXISTE EN INVENTARIO", float("nan"))
    assert (etiqueta, tono, detalle) == ("No existe", "error", "No existe en inventario")


def test_contar_validos_con_orden_real(db):
    app.insertar_ordenes("PV-1", ["EXC-001", "MON-050", "XXX-999"], "Despacho", "Convencional")
    assert ui_datos.contar_validos(app.validar_orden("PV-1")) == (1, 3)
    assert ui_datos.contar_validos(app.validar_orden("NO-EXISTE")) == (0, 0)


def test_ultimas_modificaciones_toma_el_ultimo_reemplazo(db):
    app.insertar_ordenes("PV-1", ["MON-050"], "Despacho", "Convencional")
    orden = app.obtener_orden("PV-1")
    app.reemplazar_sku(int(orden.iloc[0]["id"]), "PV-1", "MON-050", "PLA-060", "Ana", "sin stock")
    mods = ui_datos.ultimas_modificaciones(app.obtener_log_cambios(), "PV-1")
    assert list(mods) == ["PLA-060"]
    assert ui_datos.ultimas_modificaciones(app.obtener_log_cambios(), "OTRA") == {}


# ---------------------------------------------------------------------------
# CSV seguro
# ---------------------------------------------------------------------------

def test_neutralizar_csv_antepone_comilla_a_formulas():
    df = pd.DataFrame({"responsable": ['=HYPERLINK("x")', "+1", "-2", "@SUM(1)", "Ana"], "n": [1, 2, 3, 4, 5]})
    limpio = ui_datos.neutralizar_csv(df)
    assert list(limpio["responsable"]) == ["'=HYPERLINK(\"x\")", "'+1", "'-2", "'@SUM(1)", "Ana"]
    assert list(limpio["n"]) == [1, 2, 3, 4, 5]
    assert df["responsable"][0].startswith("=")  # no modifica el original


# ---------------------------------------------------------------------------
# HTML escapado
# ---------------------------------------------------------------------------

def test_esc_escapa_html_y_comillas():
    assert uc.esc('<img src=x onerror="a()">') == "&lt;img src=x onerror=&quot;a()&quot;&gt;"
    assert uc.esc(None) == ""


def test_pill_escapa_el_texto():
    assert "<script>" not in uc.pill("<script>x</script>", "ok")


def test_tabla_escapa_celdas_y_respeta_html_de_confianza():
    html = uc.tabla([("SKU", "bp-sku")], [["<b>x</b>"], [uc.pill("OK", "ok")]])
    assert "&lt;b&gt;x&lt;/b&gt;" in html
    assert 'class="bp-pill bp-pill-ok"' in html


def test_tabla_vacia_muestra_mensaje():
    assert "Sin datos" in uc.tabla([("SKU", "")], [])


# ---------------------------------------------------------------------------
# Consulta nueva de app.py
# ---------------------------------------------------------------------------

def test_obtener_resumen_ordenes_una_fila_por_folio(db):
    app.insertar_ordenes("PV-1", ["EXC-001", "EXC-002"], "Despacho", "Convencional")
    app.insertar_ordenes("PV-2", ["RET-010"], "Retiro", "Por falla")
    df = app.obtener_resumen_ordenes()
    assert sorted(df["folio"]) == ["PV-1", "PV-2"]
    fila = df[df["folio"] == "PV-1"].iloc[0]
    assert fila["tipo_movimiento"] == "Despacho" and fila["modalidad"] == "Convencional"
    assert int(fila["skus_vigentes"]) == 2


def test_obtener_resumen_ordenes_cuenta_solo_skus_vigentes(db):
    app.insertar_ordenes("PV-1", ["EXC-001", "MON-050"], "Despacho", "Convencional")
    orden = app.obtener_orden("PV-1")
    original = orden[orden["sku"] == "MON-050"].iloc[0]
    app.reemplazar_sku(int(original["id"]), "PV-1", "MON-050", "PLA-060", "Ana", "sin stock")
    df = app.obtener_resumen_ordenes()
    assert int(df.iloc[0]["skus_vigentes"]) == 2


def test_obtener_resumen_ordenes_vacio(db):
    assert app.obtener_resumen_ordenes().empty
