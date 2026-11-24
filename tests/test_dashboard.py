"""Revisiones del Dashboard: funcion de datos, pagina, scripts y biblioteca de graficos. Sin datos reales."""
import re
import shutil
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
PROTO = RAIZ / "prototipo"
NUEVE = ["id_equipo", "sku", "descripcion", "familia", "categoria", "estado", "situacion_origen", "capacidad_valor", "capacidad_unidad"]


def leer(ruta):
    return Path(ruta).read_text(encoding="utf-8")


def cuerpo_funcion():
    sql = leer(RAIZ / "supabase" / "dashboard.sql")
    return sql[sql.index("as $$"):sql.index("$$;")]


# ---------- funcion de datos ----------
def test_inventario_dashboard_devuelve_solo_las_nueve_columnas():
    cuerpo = cuerpo_funcion()
    columnas = re.search(r"'equipos'.*?jsonb_build_array\(([^)]*)\)", cuerpo, re.S).group(1)
    assert re.findall(r"'(\w+)'", columnas) == NUEVE
    fila = re.search(r"jsonb_build_array\((e\.[^)]*)\)", cuerpo).group(1)
    assert re.findall(r"e\.(\w+)", fila) == NUEVE


def test_inventario_dashboard_no_toca_personas_ni_textos_libres():
    cuerpo = cuerpo_funcion().lower()
    for prohibido in ("usuarios", "clientes", "correo", "telefono", "nombre", "razon_social", "rut", "direccion", "ubicacion"):
        assert not re.search(r"\b" + prohibido + r"\b", cuerpo), prohibido
    assert "motivo_cambio in (" in cuerpo and "else 'otro'" in cuerpo       # el texto libre se cuenta como 'Otro'


def test_inventario_dashboard_es_security_definer_y_solo_lee():
    sql = leer(RAIZ / "supabase" / "dashboard.sql")
    assert "security definer" in sql and "set search_path = public" in sql and "stable" in sql
    assert "grant execute on function public.inventario_dashboard() to anon, authenticated" in sql
    assert "revoke all on function public.inventario_dashboard() from public" in sql
    codigo = "\n".join(l for l in sql.splitlines() if not l.strip().startswith("--"))
    assert not re.search(r"\b(insert|update|delete|truncate|drop table)\b", codigo, re.I)
    assert "id_equipo >= 1000" in sql


def test_los_motivos_de_cambio_del_sql_son_los_del_prototipo():
    en_sql = set(re.findall(r"'([^']+)'", re.search(r"motivo_cambio in \(([^)]*)\)", cuerpo_funcion()).group(1)))
    en_js = set(re.findall(r"valor: '([^']+)', etiqueta", leer(PROTO / "js" / "reglas.js").split("motivos_cambio")[1]))
    assert en_sql == en_js


# ---------- pagina y scripts ----------
def test_pagina_sin_estilos_ni_scripts_en_linea_y_con_csp():
    html = leer(PROTO / "dashboard.html")
    assert "Content-Security-Policy" in html and "'unsafe-inline'" not in html and "'unsafe-eval'" not in html
    assert not re.search(r"\sstyle=", html) and not re.search(r"<style", html)
    for tag in re.findall(r"<script\b[^>]*>", html):
        assert "src=" in tag, "script en linea"
    externos = re.findall(r'src="(https?://[^"]+)"', html)
    assert all(u.startswith("https://cdn.jsdelivr.net/") for u in externos)
    assert "echarts" not in " ".join(externos), "ECharts va copiado localmente, sin CDN"
    assert 'src="js/vendor/echarts.custom.min.js"' in html


@pytest.mark.parametrize("archivo", ["dashboard.js", "graficos.js"])
def test_el_codigo_no_genera_atributos_style(archivo):
    assert not re.search(r"style=[\"']", leer(PROTO / "js" / archivo)), "la CSP bloquea los atributos style en HTML"


def test_filtros_js_no_depende_del_navegador():
    codigo = re.sub(r"/\*.*?\*/", "", leer(PROTO / "js" / "filtros.js"), flags=re.S)
    assert not re.search(r"\b(document|window|localStorage|fetch|XMLHttpRequest|echarts)\b", codigo)


def test_echarts_local_pesa_menos_de_un_megabyte_y_trae_su_licencia():
    peso = (PROTO / "js" / "vendor" / "echarts.custom.min.js").stat().st_size
    assert 100_000 < peso < 1_000_000
    leeme = leer(PROTO / "js" / "vendor" / "LEEME.md")
    assert "Apache" in leeme and "5.5.1" in leeme


def test_los_doce_graficos_estan_definidos():
    g = leer(PROTO / "js" / "graficos.js")
    assert re.findall(r"\{ id: (\d+), construir", g) == [str(i) for i in range(1, 13)]
    for tipo in ("'pie'", "'bar'", "'line'", "'heatmap'", "'treemap'", "'boxplot'"):
        assert tipo in g
    assert "1 TR = 12.000 BTU/H" in g                                # la conversion se declara en la nota
    assert "o más equipos" in g                                      # criterio de la tasa de arriendo


@pytest.mark.skipif(shutil.which("node") is None, reason="node no esta instalado")
def test_sintaxis_de_los_scripts_del_dashboard():
    for nombre in ("filtros.js", "graficos.js", "dashboard.js", "api.js"):
        r = subprocess.run(["node", "--check", str(PROTO / "js" / nombre)], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr


@pytest.mark.skipif(shutil.which("node") is None, reason="node no esta instalado")
def test_pruebas_de_node_del_dashboard():
    r = subprocess.run(["node", "--test", str(PROTO / "pruebas" / "filtros.test.js")], capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stdout[-2000:]


def test_el_importador_pide_openpyxl_aparte_de_la_app():
    assert "openpyxl" not in leer(RAIZ / "requirements.txt").lower()
    assert "openpyxl" in leer(RAIZ / "requirements-herramientas.txt").lower()
    assert "requirements-herramientas.txt" in leer(RAIZ / "herramientas" / "importar_inventario.py")


def test_sin_emojis_en_los_archivos_nuevos():
    patron = re.compile("[" + chr(0x1F300) + "-" + chr(0x1FAFF) + chr(0x2600) + "-" + chr(0x27BF) + "]")
    for ruta in [PROTO / "dashboard.html", PROTO / "css" / "dashboard.css", PROTO / "js" / "dashboard.js", PROTO / "js" / "graficos.js", PROTO / "js" / "filtros.js",
                 RAIZ / "supabase" / "dashboard.sql", RAIZ / "docs" / "analisis-inventario.md"]:
        assert not patron.search(leer(ruta)), ruta.name


def test_el_dashboard_es_una_vista_mas_del_menu_y_se_puede_volver():
    """El menu es igual en las dos paginas y cada una marca la suya como activa."""
    index, dash = leer(PROTO / "index.html"), leer(PROTO / "dashboard.html")
    for html, activa in ((index, "index.html"), (dash, "dashboard.html")):
        menu = re.search(r'<nav class="menu"[^>]*>(.*?)</nav>', html, re.S).group(1)
        enlaces = re.findall(r'<a href="([^"]+)"([^>]*)>([^<]+)</a>', menu)
        assert [(h, t) for h, _, t in enlaces] == [("index.html", "Pedidos"), ("dashboard.html", "Dashboard")]
        assert [h for h, extra, _ in enlaces if 'aria-current="page"' in extra] == [activa]


def test_la_interfaz_no_usa_la_palabra_tablero():
    for ruta in [PROTO / "index.html", PROTO / "dashboard.html", PROTO / "js" / "dashboard.js", PROTO / "js" / "graficos.js", PROTO / "css" / "dashboard.css"]:
        assert not re.search(r"tablero", leer(ruta), re.I), ruta.name
    assert (PROTO / "dashboard.html").exists() and not (PROTO / "tablero.html").exists()
