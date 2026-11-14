"""Convierte un documento Markdown del proyecto en un PDF imprimible y comprueba su largo.

Uso (desde la raiz del repositorio):
    py herramientas/md_a_pdf.py docs/pauta-validacion.md docs/pauta-validacion.pdf --max-planas 2 --max-minutos 20

Que hace: Markdown -> HTML (solo lo que usan estos documentos: titulos, parrafos, citas, listas, tablas,
negrita, cursiva, codigo y enlaces) -> PDF con el Chrome o Edge instalado, en modo sin ventana. Despues cuenta las
planas y, si se pide, suma los minutos de las etapas (los titulos con la forma "(2 min)") y falla si se pasan.

No usa bibliotecas externas. Para contar planas usa pypdf si esta instalado; si no, cuenta las paginas en el
propio archivo.
"""

import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CSS = """
@page { size: Letter; margin: 13mm 15mm; }
* { box-sizing: border-box; }
body { font-family: "Segoe UI", Arial, Helvetica, sans-serif; font-size: 9.4pt; line-height: 1.32; color: #111; margin: 0; }
h1 { font-size: 15pt; margin: 0 0 4pt; }
h2 { font-size: 11pt; margin: 9pt 0 3pt; border-bottom: 1px solid #999; padding-bottom: 1pt; }
h3 { font-size: 10pt; margin: 6pt 0 2pt; }
p { margin: 0 0 4pt; }
blockquote { margin: 3pt 0 5pt; padding: 3pt 8pt; border-left: 3px solid #555; background: #f1f1f1; }
blockquote p { margin: 0 0 3pt; }
ul, ol { margin: 0 0 4pt; padding-left: 16pt; }
li { margin: 0 0 1.5pt; }
table { border-collapse: collapse; width: 100%; margin: 3pt 0 6pt; font-size: 8.8pt; }
th, td { border: 1px solid #777; padding: 2.5pt 4pt; text-align: left; vertical-align: top; }
th { background: #e4e4e4; }
code { font-family: Consolas, "Courier New", monospace; font-size: 8.6pt; background: #eee; padding: 0 2pt; }
a { color: #111; text-decoration: underline; }
hr { border: 0; border-top: 1px solid #999; margin: 6pt 0; }
h1, h2, h3 { break-after: avoid; }
tr, blockquote, li { break-inside: avoid; }
"""

_ENLACE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")


def _inline(texto):
    t = html.escape(texto, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?![\s*])(.+?)(?<![\s*])\*(?![\w*])", r"<em>\1</em>", t)

    def enlace(m):
        destino = m.group(2)
        if re.match(r"^\s*(javascript|data|vbscript):", destino, re.I):
            return m.group(1)
        # el texto ya paso por html.escape: aqui solo falta proteger las comillas del atributo
        return f'<a href="{destino.replace(chr(34), "&quot;")}">{m.group(1)}</a>'

    return _ENLACE.sub(enlace, t)


def _celdas(linea):
    partes = linea.strip().strip("|").split("|")
    return [p.strip() for p in partes]


def md_a_html(texto, titulo=None):
    """Convierte el subconjunto de Markdown usado en los documentos del proyecto a una pagina HTML completa."""
    lineas = texto.replace("\r\n", "\n").split("\n")
    salida = []
    parrafo = []
    i = 0

    def cerrar_parrafo():
        if parrafo:
            salida.append("<p>" + " ".join(_inline(p) for p in parrafo) + "</p>")
            parrafo.clear()

    while i < len(lineas):
        linea = lineas[i]
        s = linea.strip()

        if not s:
            cerrar_parrafo()
            i += 1
            continue

        m = re.match(r"^(#{1,3})\s+(.*)$", s)
        if m:
            cerrar_parrafo()
            n = len(m.group(1))
            salida.append(f"<h{n}>{_inline(m.group(2))}</h{n}>")
            i += 1
            continue

        if re.match(r"^(-{3,}|\*{3,})$", s):
            cerrar_parrafo()
            salida.append("<hr>")
            i += 1
            continue

        if s.startswith(">"):
            cerrar_parrafo()
            bloque = []
            while i < len(lineas) and lineas[i].strip().startswith(">"):
                bloque.append(lineas[i].strip()[1:].strip())
                i += 1
            interior, actual = [], []
            for b in bloque + [""]:
                if b:
                    actual.append(b)
                elif actual:
                    interior.append("<p>" + " ".join(_inline(x) for x in actual) + "</p>")
                    actual = []
            salida.append("<blockquote>" + "".join(interior) + "</blockquote>")
            continue

        if s.startswith("|") and i + 1 < len(lineas) and re.match(r"^\|?\s*:?-{2,}", lineas[i + 1].strip()):
            cerrar_parrafo()
            cabecera = _celdas(s)
            i += 2
            filas = []
            while i < len(lineas) and lineas[i].strip().startswith("|"):
                filas.append(_celdas(lineas[i]))
                i += 1
            salida.append(
                "<table><thead><tr>" + "".join(f"<th>{_inline(c)}</th>" for c in cabecera) + "</tr></thead><tbody>"
                + "".join("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in fila) + "</tr>" for fila in filas)
                + "</tbody></table>"
            )
            continue

        m = re.match(r"^(\d+\.|[-*])\s+(.*)$", s)
        if m:
            cerrar_parrafo()
            ordenada = m.group(1)[0].isdigit()
            items = []
            while i < len(lineas):
                mm = re.match(r"^(\d+\.|[-*])\s+(.*)$", lineas[i].strip())
                if not mm or mm.group(1)[0].isdigit() != ordenada:
                    break
                items.append(mm.group(2))
                i += 1
            etiqueta = "ol" if ordenada else "ul"
            salida.append(f"<{etiqueta}>" + "".join(f"<li>{_inline(x)}</li>" for x in items) + f"</{etiqueta}>")
            continue

        parrafo.append(s)
        i += 1

    cerrar_parrafo()
    if titulo is None:
        m = re.search(r"^#\s+(.*)$", texto, re.M)
        titulo = m.group(1).strip() if m else "Documento"
    return (
        '<!doctype html><html lang="es"><head><meta charset="utf-8">'
        f"<title>{html.escape(titulo)}</title><style>{CSS}</style></head><body>"
        + "\n".join(salida)
        + "</body></html>"
    )


def minutos_de_las_etapas(texto):
    """Suma los minutos de los titulos con la forma '## 2. Preguntas de contexto (3 min)'. Devuelve (total, lista)."""
    etapas = re.findall(r"^#{2,3}\s+(.*?)\s*\((\d+)\s*min\)\s*$", texto, re.M)
    lista = [(nombre, int(minutos)) for nombre, minutos in etapas]
    return sum(m for _, m in lista), lista


def contar_planas(ruta_pdf):
    """Numero de planas de un PDF. Usa pypdf si esta; si no, cuenta los objetos de pagina del archivo."""
    try:
        from pypdf import PdfReader

        return len(PdfReader(str(ruta_pdf)).pages)
    except ImportError:
        datos = Path(ruta_pdf).read_bytes()
        return len(re.findall(rb"/Type\s*/Page(?![a-zA-Z])", datos))


def buscar_navegador():
    """Chrome o Edge instalado, o None."""
    candidatos = [
        os.environ.get("NAVEGADOR_PDF", ""),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        shutil.which("google-chrome") or "",
        shutil.which("chromium") or "",
        shutil.which("chrome") or "",
    ]
    for c in candidatos:
        if c and Path(c).exists():
            return c
    return None


def generar_pdf(ruta_md, ruta_pdf, navegador=None):
    """Genera ruta_pdf desde ruta_md con un Chrome o Edge sin ventana. Devuelve las planas."""
    navegador = navegador or buscar_navegador()
    if not navegador:
        raise RuntimeError("No encontre Chrome ni Edge. Define NAVEGADOR_PDF con la ruta del ejecutable.")
    texto = Path(ruta_md).read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as carpeta:
        pagina = Path(carpeta) / "pagina.html"
        pagina.write_text(md_a_html(texto), encoding="utf-8")
        destino = Path(carpeta) / "salida.pdf"
        perfil = Path(carpeta) / "perfil"
        comando = [
            navegador, "--headless=new", "--disable-gpu", "--no-first-run", f"--user-data-dir={perfil}",
            "--no-pdf-header-footer", f"--print-to-pdf={destino}", pagina.as_uri(),
        ]
        resultado = subprocess.run(comando, capture_output=True, text=True, timeout=120)
        if not destino.exists():
            raise RuntimeError("El navegador no genero el PDF: " + (resultado.stderr or resultado.stdout)[-300:])
        Path(ruta_pdf).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(destino, ruta_pdf)
    return contar_planas(ruta_pdf)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)

    def opcion(nombre):
        if nombre in argv:
            i = argv.index(nombre)
            valor = argv[i + 1]
            del argv[i:i + 2]
            return int(valor)
        return None

    max_planas = opcion("--max-planas")
    max_minutos = opcion("--max-minutos")
    if len(argv) != 2:
        print(__doc__)
        return 2
    origen, destino = Path(argv[0]), Path(argv[1])
    if not origen.exists():
        print(f"No existe {origen}")
        return 2

    texto = origen.read_text(encoding="utf-8")
    codigo = 0
    if max_minutos is not None:
        total, etapas = minutos_de_las_etapas(texto)
        for nombre, minutos in etapas:
            print(f"  {minutos:>2} min  {nombre}")
        print(f"Suma de las etapas: {total} min (maximo {max_minutos})")
        if total > max_minutos:
            print("FALLA: las etapas suman mas de lo permitido")
            codigo = 1
    try:
        planas = generar_pdf(origen, destino)
    except RuntimeError as e:
        print("No se pudo generar el PDF:", e)
        return 1
    print(f"PDF generado: {destino} ({planas} {'plana' if planas == 1 else 'planas'})")
    if max_planas is not None and planas > max_planas:
        print(f"FALLA: tiene {planas} planas y el maximo es {max_planas}")
        codigo = 1
    return codigo


if __name__ == "__main__":
    sys.exit(main())
