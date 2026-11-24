"""
Pagina del Dashboard dentro del MVP (se muestra en un iframe de Streamlit, ver views/dashboard.py).

NO duplica el Dashboard del prototipo: lee los mismos archivos (prototipo/dashboard.html entre sus marcadores,
css/estilos.css, css/dashboard.css, js/filtros.js, js/graficos.js, js/dashboard.js y ECharts) y les suma lo propio del MVP
(src/dashboard_incrustado/: el entorno del iframe, el reemplazo de los datos y el CSS ancho). Asi hay una sola fuente
para la logica y los graficos, y lo que se corrige en una se corrige en las dos.

Los datos del inventario (inventario_dashboard(), cargados por el servidor con el rol app_mvp) van dentro de la pagina:
el navegador no usa la clave publica ni llama a Supabase. La pagina lleva su propia politica de seguridad (CSP) con
connect-src 'none' (no puede hablar con ninguna red), sin scripts ni estilos que no sean los de este archivo (por hash).

Este modulo no importa Streamlit: se prueba sin abrir la aplicacion.
"""

import base64
import hashlib
import json
import os
import re
from functools import lru_cache
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PROTOTIPO = RAIZ / "prototipo"
INCRUSTADO = Path(__file__).resolve().parent / "dashboard_incrustado"

VARIABLE = "DASHBOARD_INVENTARIO"  # la vista solo aparece si vale 1 (el inventario real no se muestra en publico sin permiso)

# Orden en que se ejecutan: ECharts, la logica de filtros, los graficos, el entorno y los datos del MVP, y el Dashboard.
_SCRIPTS = [
    PROTOTIPO / "js" / "vendor" / "echarts.custom.min.js",
    PROTOTIPO / "js" / "filtros.js",
    PROTOTIPO / "js" / "graficos.js",
    INCRUSTADO / "entorno.js",
    INCRUSTADO / "datos.js",
    PROTOTIPO / "js" / "dashboard.js",
]
_ESTILOS = [PROTOTIPO / "css" / "estilos.css", PROTOTIPO / "css" / "dashboard.css", INCRUSTADO / "incrustado.css"]


class ErrorDashboard(Exception):
    """No se pudo armar la pagina (falta un archivo o un marcador de prototipo/dashboard.html)."""


def activo():
    """True si la vista Dashboard esta encendida (DASHBOARD_INVENTARIO=1)."""
    return os.getenv(VARIABLE, "").strip() == "1"


def _leer(ruta):
    try:
        return Path(ruta).read_text(encoding="utf-8")
    except OSError as e:
        raise ErrorDashboard(f"Falta un archivo del Dashboard: {Path(ruta).name}") from e


def _entre_marcadores(html, nombre):
    """Lo que hay entre <!-- dashboard:NOMBRE:inicio ... --> y <!-- dashboard:NOMBRE:fin -->."""
    m = re.search(rf"<!-- dashboard:{nombre}:inicio[^>]*-->(.*?)<!-- dashboard:{nombre}:fin -->", html, re.S)
    if not m:
        raise ErrorDashboard(f"prototipo/dashboard.html perdio el marcador «{nombre}»: el MVP lo necesita")
    return m.group(1).strip("\n")


def _hash(texto):
    """Fuente de CSP por hash: 'sha256-...' del contenido exacto del bloque."""
    return "'sha256-" + base64.b64encode(hashlib.sha256(texto.encode("utf-8")).digest()).decode("ascii") + "'"


def json_seguro(datos):
    """JSON para ir dentro de <script type=application/json>: nada de '<', '>' ni '&' sin escapar (no puede cerrar el bloque)."""
    texto = json.dumps(datos, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    return (texto.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
            .replace("\u2028", "\\u2028").replace("\u2029", "\\u2029"))


@lru_cache(maxsize=1)
def _recursos():
    """Lee y arma una sola vez lo que no cambia entre cargas (la logica, los graficos y los estilos)."""
    html = _leer(PROTOTIPO / "dashboard.html")
    contenido = _entre_marcadores(html, "contenido")
    panel = _entre_marcadores(html, "panel")
    estilos = "\n".join(_leer(r) for r in _ESTILOS)
    scripts = "\n;\n".join(_leer(r) for r in _SCRIPTS)
    for nombre, texto in (("scripts", scripts), ("estilos", estilos)):
        if re.search(r"</(script|style)|<!--", texto, re.I):
            raise ErrorDashboard(f"Los {nombre} del Dashboard no se pueden incrustar tal cual (traen una etiqueta de cierre)")
    return contenido, panel, estilos, scripts


def pagina(datos):
    """HTML completo del Dashboard con los datos ya incrustados. Mismos datos, mismo texto (el iframe no se recarga)."""
    contenido, panel, estilos, scripts = _recursos()
    politica = "; ".join([
        "default-src 'none'",
        f"script-src {_hash(scripts)}",
        f"style-src {_hash(estilos)}",
        "img-src data:",
        "connect-src 'none'",
        "base-uri 'none'",
        "form-action 'none'",
    ])
    return (
        '<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'<meta http-equiv="Content-Security-Policy" content="{politica}">\n'
        "<title>Dashboard del inventario</title>\n"
        f"<style>{estilos}</style>\n</head>\n"
        '<body class="dashboard">\n<div class="app">\n<main id="vista">\n'
        f"{contenido}\n</main>\n</div>\n{panel}\n"
        f'<script type="application/json" id="datos-dashboard">{json_seguro(datos)}</script>\n'
        f"<script>{scripts}</script>\n</body>\n</html>\n"
    )


def hay_equipos(datos):
    """True si el inventario trae al menos un equipo (si no, el Dashboard no tiene nada que mostrar)."""
    try:
        return bool(datos["equipos"]["filas"])
    except (KeyError, TypeError):
        return False
