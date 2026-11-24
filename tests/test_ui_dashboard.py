"""
Dashboard dentro del MVP: la pagina que se arma (src/ui_dashboard.py), la bandera DASHBOARD_INVENTARIO y la vista.

Todos los datos son ficticios. Los graficos y la logica de filtros son los del prototipo (prototipo/js/*) y se prueban aparte con
node --test; aqui se prueba lo que arma el MVP alrededor: que la pagina no lleve claves ni llame a ninguna red, que su politica
de seguridad coincida con su contenido, que los datos viajen escapados y que la vista falle con un mensaje claro.
"""

import base64
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import db  # noqa: E402
import ui_dashboard  # noqa: E402

COLUMNAS = ["id_equipo", "sku", "descripcion", "familia", "categoria", "estado", "situacion_origen", "capacidad_valor", "capacidad_unidad"]


def datos_ficticios(descripcion="Equipo de prueba"):
    return {
        "equipos": {
            "columnas": COLUMNAS,
            "filas": [
                [1000, "XX-AAAAA-00001", descripcion, "AA", "CAT", "disponible", "BODEGA", 12000, "BTU/H"],
                [1001, "XX-AAAAA-00002", "Otro equipo", "AA", "CAT", "arrendado", "CONTRATO", None, None],
            ],
        },
        "extensiones": {"columnas": ["sku", "corriente", "largo_m"], "filas": [["YY-BBBBB-00001", "63A", 10]]},
        "actividad": {"ordenes_por_estado": {"pendiente": 2}, "cambios_por_motivo": {}},
    }


# ---------------------------------------------------------------------------
# La pagina
# ---------------------------------------------------------------------------

def bloques(html):
    return re.findall(r"<script>(.*?)</script>", html, re.S), re.findall(r"<style>(.*?)</style>", html, re.S)


def hash_csp(texto):
    return "'sha256-" + base64.b64encode(hashlib.sha256(texto.encode("utf-8")).digest()).decode("ascii") + "'"


def test_la_pagina_reutiliza_el_dashboard_del_prototipo_y_no_trae_clave_ni_red():
    html = ui_dashboard.pagina(datos_ficticios())
    for propio in ('id="indicadores"', 'id="graficos"', 'id="tabla-casos"', 'id="panel"', 'id="descargar"', "Lectura de los datos"):
        assert propio in html, propio
    minusculas = html.lower()
    for ajeno in ("supabase", "config.js", "sb_publishable", "createclient", "cdn.jsdelivr", "window.config"):
        assert ajeno not in minusculas, ajeno
    # nada que descargar: ni scripts ni hojas de estilo externos (todo va dentro de la pagina)
    assert not re.search(r"<script[^>]*\ssrc=", html) and not re.search(r"<link[^>]*>", html)


def test_la_politica_de_seguridad_coincide_con_el_contenido_y_no_deja_salir_nada():
    html = ui_dashboard.pagina(datos_ficticios())
    scripts, estilos = bloques(html)
    assert len(scripts) == 1 and len(estilos) == 1
    politica = re.search(r'Content-Security-Policy" content="([^"]+)"', html).group(1)
    directivas = dict(d.strip().split(" ", 1) for d in politica.split(";"))
    assert directivas["default-src"] == "'none'" and directivas["connect-src"] == "'none'"
    assert directivas["script-src"] == hash_csp(scripts[0]) and directivas["style-src"] == hash_csp(estilos[0])
    assert "unsafe" not in politica and "*" not in politica


def test_los_datos_viajan_escapados_y_se_leen_igual():
    peligrosa = 'Equipo </script><script>alert(1)</script><!-- & "comillas"  '
    datos = datos_ficticios(peligrosa)
    html = ui_dashboard.pagina(datos)
    assert "</script><script>alert(1)" not in html
    bloque = re.search(r'<script type="application/json" id="datos-dashboard">(.*?)</script>', html, re.S).group(1)
    assert "<" not in bloque and ">" not in bloque and "&" not in bloque and " " not in bloque
    assert json.loads(bloque) == datos  # el navegador lee exactamente lo que mando el servidor


def test_la_misma_entrada_da_la_misma_pagina_para_que_el_iframe_no_se_recargue():
    assert ui_dashboard.pagina(datos_ficticios()) == ui_dashboard.pagina(datos_ficticios())
    assert ui_dashboard.pagina(datos_ficticios()) != ui_dashboard.pagina(datos_ficticios("Cambiado"))


def test_hay_equipos_solo_con_filas():
    assert ui_dashboard.hay_equipos(datos_ficticios())
    assert not ui_dashboard.hay_equipos({"equipos": {"columnas": COLUMNAS, "filas": []}})
    assert not ui_dashboard.hay_equipos({}) and not ui_dashboard.hay_equipos(None)


def test_si_el_prototipo_pierde_un_marcador_el_mvp_falla_con_un_mensaje_claro(tmp_path, monkeypatch):
    copia = tmp_path / "prototipo"
    shutil.copytree(RAIZ / "prototipo", copia, ignore=shutil.ignore_patterns("config.js"))
    html = (copia / "dashboard.html").read_text(encoding="utf-8").replace("dashboard:panel:fin", "borrado")
    (copia / "dashboard.html").write_text(html, encoding="utf-8")
    monkeypatch.setattr(ui_dashboard, "PROTOTIPO", copia)
    monkeypatch.setattr(ui_dashboard, "_SCRIPTS", [copia / "js" / "filtros.js"])
    monkeypatch.setattr(ui_dashboard, "_ESTILOS", [copia / "css" / "estilos.css"])
    ui_dashboard._recursos.cache_clear()
    try:
        with pytest.raises(ui_dashboard.ErrorDashboard, match="panel"):
            ui_dashboard.pagina(datos_ficticios())
    finally:
        ui_dashboard._recursos.cache_clear()


def test_el_prototipo_conserva_sus_marcadores_y_no_se_le_cambio_la_pagina():
    html = (RAIZ / "prototipo" / "dashboard.html").read_text(encoding="utf-8")
    for nombre in ("contenido", "panel"):
        assert re.search(rf"<!-- dashboard:{nombre}:inicio[^>]*-->", html) and f"<!-- dashboard:{nombre}:fin -->" in html
    # sigue cargando lo de siempre, con su propia clave y su propia politica (el prototipo no cambia de comportamiento)
    assert "js/api.js" in html and "js/config.js" in html and "connect-src 'self' https://*.supabase.co" in html


def test_el_css_ancho_define_las_tres_distribuciones_y_no_toca_los_estilos_del_prototipo():
    css = (RAIZ / "src" / "dashboard_incrustado" / "incrustado.css").read_text(encoding="utf-8")
    assert "max-width: none" in css                                    # usa todo el ancho
    assert re.search(r"min-width: 720px\)[^}]*repeat\(5", css, re.S)    # indicadores en una fila
    assert re.search(r"min-width: 760px\)[^}]*repeat\(2", css, re.S)    # 2 columnas en pantallas medianas
    assert re.search(r"min-width: 1180px\)[^}]*repeat\(3", css, re.S)   # 3 columnas en pantallas grandes
    assert "min-height" in css and "panel-acoplado" in css
    proto = (RAIZ / "prototipo" / "css" / "dashboard.css").read_text(encoding="utf-8")
    assert "repeat(3" not in proto  # el rediseno vive solo en el MVP


def test_streamlit_esta_fijo_y_docker_no_copia_la_clave_local_del_prototipo():
    assert re.search(r"^streamlit==\d+\.\d+\.\d+\s*$", (RAIZ / "requirements.txt").read_text(encoding="utf-8"), re.M)
    lineas = [l for l in (RAIZ / "Dockerfile").read_text(encoding="utf-8").splitlines() if l.startswith("COPY")]
    assert not any(re.match(r"COPY prototipo/?\s", l) for l in lineas), "nunca la carpeta entera del prototipo"
    assert not any("config.js" in l or "api.js" in l for l in lineas), "ni la clave publica local ni el cliente de Supabase"
    copiado = " ".join(lineas)
    for necesario in ("dashboard.html", "estilos.css", "dashboard.css", "filtros.js", "graficos.js", "dashboard.js", "echarts.custom.min.js"):
        assert necesario in copiado, necesario


def test_la_bandera_viene_apagada_en_el_ejemplo_de_entorno():
    ejemplo = (RAIZ / ".env.example").read_text(encoding="utf-8")
    assert re.search(r"^DASHBOARD_INVENTARIO=\s*$", ejemplo, re.M)


@pytest.mark.parametrize("valor, esperado", [("1", True), (" 1 ", True), ("", False), ("0", False), ("si", False), ("true", False)])
def test_solo_el_valor_1_enciende_la_vista(monkeypatch, valor, esperado):
    monkeypatch.setenv("DASHBOARD_INVENTARIO", valor)
    assert ui_dashboard.activo() is esperado


def test_sin_la_variable_esta_apagada(monkeypatch):
    monkeypatch.delenv("DASHBOARD_INVENTARIO", raising=False)
    assert ui_dashboard.activo() is False


# ---------------------------------------------------------------------------
# La vista dentro de la aplicacion (Streamlit AppTest, base local SQLite)
# ---------------------------------------------------------------------------

pytest.importorskip("streamlit.testing.v1")
from streamlit.testing.v1 import AppTest  # noqa: E402

APP = str(RAIZ / "src" / "app.py")


@pytest.fixture
def app(tmp_path, monkeypatch):
    import streamlit as st

    monkeypatch.setenv("BODEGA_MVP_DB", str(tmp_path / "mvp.db"))
    monkeypatch.setenv("DASHBOARD_INVENTARIO", "1")
    st.cache_resource.clear()
    st.cache_data.clear()
    yield lambda **kw: AppTest.from_file(APP, default_timeout=30, **kw)
    st.cache_resource.clear()
    st.cache_data.clear()


def texto(at):
    return " ".join(m.value for m in at.markdown)


def test_apagada_no_hay_boton_en_el_menu_y_la_direccion_no_la_abre(app, monkeypatch):
    monkeypatch.setenv("DASHBOARD_INVENTARIO", "")
    at = app()
    at.query_params["vista"] = "dashboard"
    at.run()
    assert not at.exception
    assert "menu_dashboard" not in [b.key for b in at.button]
    assert at.session_state.vista == "ordenes"


def test_encendida_aparece_en_el_menu_y_la_direccion_la_abre(app):
    at = app().run()
    assert "menu_dashboard" in [b.key for b in at.button]
    assert at.session_state.vista == "ordenes"  # sin direccion especial, abre en Ordenes

    abierta = app()
    abierta.query_params["vista"] = "dashboard"
    abierta.run()
    assert abierta.session_state.vista == "dashboard" and not abierta.exception


def test_sin_inventario_real_avisa_en_vez_de_mostrar_un_dashboard_vacio(app):
    at = app().run()
    at.button(key="menu_dashboard").click().run()
    assert at.session_state.vista == "dashboard"
    assert "Todavía no hay inventario cargado" in texto(at)
    assert len(at.get("iframe")) == 0


def test_con_inventario_muestra_el_dashboard_en_un_iframe_con_los_datos_dentro(app, monkeypatch):
    monkeypatch.setattr(db.RepoSqlite, "dashboard", lambda self: datos_ficticios())
    at = app().run()
    at.button(key="menu_dashboard").click().run()
    assert not at.exception
    marcos = at.get("iframe")
    assert len(marcos) == 1
    assert "XX-AAAAA-00001" in str(marcos[0].proto.srcdoc)  # los datos van dentro de la pagina, no en el navegador


def test_si_no_hay_conexion_muestra_un_mensaje_claro_con_boton_para_reintentar(app, monkeypatch):
    def sin_conexion(self):
        raise db.ErrorDeBase("No se pudo conectar con la base de datos. Intenta de nuevo en unos segundos.")

    monkeypatch.setattr(db.RepoSqlite, "dashboard", sin_conexion)
    at = app().run()
    at.button(key="menu_dashboard").click().run()
    assert not at.exception
    assert "No se pudo cargar el Dashboard" in texto(at) and "No se pudo conectar con la base de datos" in texto(at)
    assert "dash_reintentar" in [b.key for b in at.button]
    assert len(at.get("iframe")) == 0


def test_si_el_prototipo_pierde_un_marcador_la_vista_lo_dice_sin_romperse(app, monkeypatch):
    def sin_marcador(datos):
        raise ui_dashboard.ErrorDashboard("prototipo/dashboard.html perdio el marcador «panel»: el MVP lo necesita")

    monkeypatch.setattr(db.RepoSqlite, "dashboard", lambda self: datos_ficticios())
    monkeypatch.setattr(ui_dashboard, "pagina", sin_marcador)
    at = app().run()
    at.button(key="menu_dashboard").click().run()
    assert not at.exception and "No se pudo cargar el Dashboard" in texto(at)


def test_el_dashboard_usa_todo_el_ancho_y_las_otras_vistas_no(app):
    at = app().run()
    assert "max-width: none" not in texto(at)  # Ordenes conserva su ancho de lectura
    at.button(key="menu_dashboard").click().run()
    assert "max-width: none" in texto(at)
    at.button(key="menu_ordenes").click().run()
    assert "max-width: none" not in texto(at)
