"""
Portal de Vercel (portal/): una pagina estatica con un unico boton hacia el MVP.

Revisiones estaticas: que la direccion de la aplicacion viva en un solo lugar, que el portal no enlace al prototipo ni al dashboard
del prototipo, que no lleve claves ni dependencias externas ni codigo en linea (tiene su propia politica de seguridad) y que haya
un solo boton visible. El comportamiento del boton (desactivado o enlace) se prueba en tests/js/portal.test.js.
"""

import json
import re
from pathlib import Path
from urllib.parse import urlparse

RAIZ = Path(__file__).resolve().parent.parent
PORTAL = RAIZ / "portal"
ARCHIVOS = ["index.html", "config.js", "portal.js", "estilos.css", "icono.svg", "vercel.json"]


def leer(nombre):
    return (PORTAL / nombre).read_text(encoding="utf-8")


def test_el_portal_tiene_todos_sus_archivos_y_nada_mas():
    presentes = sorted(p.name for p in PORTAL.iterdir() if p.is_file())
    assert presentes == sorted(ARCHIVOS + ["LEEME.md"])


def test_la_direccion_de_la_aplicacion_vive_en_un_solo_lugar():
    config = leer("config.js")
    asignaciones = re.findall(r"URL_APLICACION\s*:\s*'([^']*)'", config)
    assert len(asignaciones) == 1
    valor = asignaciones[0]
    # vacia (portal publicado antes que el MVP) o una direccion https sin usuario ni contrasena
    if valor:
        u = urlparse(valor)
        assert u.scheme == "https" and u.hostname and not u.username and not u.password, valor
    # ningun otro archivo la define ni la repite: portal.js solo la lee de config.js
    for nombre in ("index.html", "estilos.css", "vercel.json"):
        assert "URL_APLICACION" not in leer(nombre), nombre
    assert "config.URL_APLICACION" in leer("portal.js") and not re.search(r"URL_APLICACION\s*[:=]", leer("portal.js"))
    if valor:
        for nombre in ARCHIVOS:
            if nombre != "config.js":
                assert valor not in leer(nombre), nombre


def test_el_portal_no_enlaza_al_prototipo_ni_a_su_dashboard():
    # el LEEME explica por que no se enlaza; las paginas del portal no lo mencionan en absoluto
    for nombre in ARCHIVOS:
        texto = leer(nombre).lower()
        for prohibido in ("bodega-prototipo", "vercel.app", "prototipo", "dashboard"):
            assert prohibido not in texto, (nombre, prohibido)


def test_sin_claves_sin_supabase_y_sin_dependencias_externas():
    for nombre in ARCHIVOS:
        texto = leer(nombre)
        assert not re.search(r"sb_(publishable|secret)_|eyJ[A-Za-z0-9_-]{20,}\.|service_role|supabase|createClient|DATABASE_URL", texto, re.I), nombre
    html = leer("index.html")
    externas = [u for u in re.findall(r"""(?:src|href|action)\s*=\s*["']([^"']+)["']""", html) if re.match(r"(?i)(https?:)?//", u)]
    assert externas == [], externas
    # solo el espacio de nombres del SVG puede parecer una direccion
    for nombre in ("index.html", "estilos.css", "portal.js", "config.js"):
        for u in re.findall(r"https?://[^\s\"')]+", leer(nombre)):
            assert u.startswith("http://www.w3.org/2000/svg") or nombre == "config.js", (nombre, u)
    assert "@import" not in leer("estilos.css") and "url(" not in leer("estilos.css")


def test_la_pagina_no_lleva_codigo_en_linea_y_tiene_su_politica_de_seguridad():
    html = leer("index.html")
    assert not re.search(r"<script(?![^>]*\ssrc=)[^>]*>\s*\S", html), "script en linea"
    assert not re.search(r"<style", html, re.I) and not re.search(r"\sstyle\s*=", html, re.I), "estilos en linea"
    assert not re.search(r"\son[a-z]+\s*=", html, re.I), "manejadores en linea (onclick...)"
    politica = re.search(r'Content-Security-Policy" content="([^"]+)"', html).group(1)
    directivas = dict(d.strip().split(" ", 1) for d in politica.split(";"))
    assert directivas["default-src"] == "'none'" and directivas["script-src"] == "'self'" and directivas["style-src"] == "'self'"
    assert "unsafe" not in politica and "*" not in politica and "connect-src" not in politica  # default-src 'none' ya cierra la red


def test_hay_un_solo_boton_visible_y_sus_textos_son_los_pedidos():
    html = leer("index.html")
    assert html.count("<button") == 1 and len(re.findall(r"<a\b", html)) == 1
    pendiente = re.search(r"<button[^>]*>(.*?)</button>", html, re.S)
    assert "disabled" in pendiente.group(0) and pendiente.group(1).strip() == "Aplicación en despliegue"
    enlace = re.search(r"<a\b[^>]*>(.*?)</a>", html, re.S)
    assert " hidden" in enlace.group(0) and "href" not in enlace.group(0) and enlace.group(1).strip() == "Abrir la aplicación"
    assert 'rel="noopener noreferrer"' in enlace.group(0)
    assert "<noscript>" in html  # sin JavaScript queda el boton desactivado y un aviso


def test_la_pagina_es_responsive_y_esta_en_espanol():
    html, css = leer("index.html"), leer("estilos.css")
    assert 'lang="es"' in html and 'name="viewport"' in html
    assert "@media (min-width: 600px)" in css and "prefers-reduced-motion" in css and ":focus-visible" in css
    assert "[hidden] { display: none !important; }" in css  # el atributo hidden manda sobre el estilo del boton
    assert "<h1>" in html and html.count("<h1>") == 1


def test_vercel_json_es_valido_y_agrega_encabezados_de_seguridad():
    config = json.loads(leer("vercel.json"))
    encabezados = {h["key"]: h["value"] for regla in config["headers"] for h in regla["headers"]}
    assert encabezados["X-Frame-Options"] == "DENY" and encabezados["X-Content-Type-Options"] == "nosniff"
    assert "frame-ancestors 'none'" in encabezados["Content-Security-Policy"]
    assert "buildCommand" not in config and "installCommand" not in config  # un sitio estatico no se construye


def test_vercel_no_ejecuta_el_script_de_configuracion_del_prototipo_en_el_portal():
    """El Build Command antiguo (node generar-config.mjs) no existe dentro de portal/: se avisa en el LEEME."""
    assert not (PORTAL / "generar-config.mjs").exists()
    leeme = leer("LEEME.md")
    assert "Root Directory" in leeme and "Build Command" in leeme and "generar-config" in leeme
