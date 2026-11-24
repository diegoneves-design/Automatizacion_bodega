"""Pruebas de herramientas/md_a_pdf.py (convertidor de Markdown a PDF imprimible)."""

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "herramientas"))

import md_a_pdf as pdf  # noqa: E402


# ---------------------------------------------------------------- Markdown a HTML

def test_titulos_parrafos_y_formato_en_linea():
    h = pdf.md_a_html("# Pauta\n\n## 1. Bienvenida (2 min)\n\nTexto con **negrita**, *cursiva* y `codigo`.\n")
    assert "<h1>Pauta</h1>" in h and "<h2>1. Bienvenida (2 min)</h2>" in h
    assert "<strong>negrita</strong>" in h and "<em>cursiva</em>" in h and "<code>codigo</code>" in h
    assert "<title>Pauta</title>" in h and 'lang="es"' in h


def test_citas_listas_y_tablas():
    md = "> Primera linea\n> segunda linea\n>\n> otro parrafo\n\n1. uno\n2. dos\n\n- a\n- b\n\n| N.º | Frase |\n|---|---|\n| 1 | Hola |\n| 2 | Chao |\n"
    h = pdf.md_a_html(md)
    assert "<blockquote><p>Primera linea segunda linea</p><p>otro parrafo</p></blockquote>" in h
    assert "<ol><li>uno</li><li>dos</li></ol>" in h and "<ul><li>a</li><li>b</li></ul>" in h
    assert "<th>N.º</th><th>Frase</th>" in h and "<td>2</td><td>Chao</td>" in h


def test_el_texto_se_escapa_y_los_enlaces_peligrosos_se_quitan():
    h = pdf.md_a_html("Mira <script>alert(1)</script> y [mal](javascript:alert(1)) y [bien](https://ejemplo.cl/a?b=1&c=2).")
    assert "<script>" not in h.split("</style>")[1]
    assert "&lt;script&gt;" in h
    assert "javascript:" not in h.split("</style>")[1]
    assert '<a href="https://ejemplo.cl/a?b=1&amp;c=2">bien</a>' in h


def test_un_asterisco_suelto_no_rompe_el_texto():
    assert "2 * 3 = 6" in pdf.md_a_html("Cuenta: 2 * 3 = 6")


# ---------------------------------------------------------------- minutos de las etapas

def test_suma_de_minutos_de_las_etapas():
    total, etapas = pdf.minutos_de_las_etapas("## 1. A (2 min)\n\n## 2. B (3 min)\n\n### Sub (5 min)\n\n## 3. Sin tiempo\n")
    assert total == 10 and [m for _, m in etapas] == [2, 3, 5]


def test_la_pauta_del_proyecto_dura_20_minutos_o_menos():
    texto = (RAIZ / "docs" / "pauta-validacion.md").read_text(encoding="utf-8")
    total, etapas = pdf.minutos_de_las_etapas(texto)
    assert len(etapas) == 6, etapas
    assert total <= 20, f"las etapas suman {total} min: {etapas}"


# ---------------------------------------------------------------- planas

def pdf_minimo(n):
    objetos = "".join(f"<< /Type /Page /Parent 1 0 R >>\n" for _ in range(n))
    return (f"%PDF-1.4\n<< /Type /Pages /Count {n} >>\n" + objetos + "%%EOF").encode()


def test_contar_planas_sin_pypdf(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "pypdf", None)          # simula que pypdf no esta instalado
    archivo = tmp_path / "a.pdf"
    archivo.write_bytes(pdf_minimo(3))
    assert pdf.contar_planas(archivo) == 3                    # /Type /Pages no se cuenta como plana


# ---------------------------------------------------------------- PDF real (necesita Chrome o Edge)

navegador = pdf.buscar_navegador()
requiere_navegador = pytest.mark.skipif(navegador is None, reason="no hay Chrome ni Edge instalado")


@requiere_navegador
def test_un_documento_corto_cabe_en_una_plana(tmp_path):
    md = tmp_path / "corto.md"
    md.write_text("# Corto\n\nUn parrafo.\n", encoding="utf-8")
    assert pdf.generar_pdf(md, tmp_path / "corto.pdf") == 1


@requiere_navegador
def test_un_documento_largo_pasa_de_una_plana(tmp_path):
    md = tmp_path / "largo.md"
    md.write_text("# Largo\n\n" + "\n\n".join(f"Parrafo numero {i} " + "texto " * 60 for i in range(60)), encoding="utf-8")
    assert pdf.generar_pdf(md, tmp_path / "largo.pdf") >= 2


@requiere_navegador
def test_la_pauta_imprimible_no_pasa_de_dos_planas(tmp_path):
    planas = pdf.generar_pdf(RAIZ / "docs" / "pauta-validacion.md", tmp_path / "pauta.pdf")
    assert planas <= 2, f"la pauta ocupa {planas} planas"


def test_main_falla_si_las_etapas_pasan_del_maximo(tmp_path, capsys):
    md = tmp_path / "larga.md"
    md.write_text("# X\n\n## 1. A (15 min)\n\n## 2. B (10 min)\n", encoding="utf-8")
    if navegador is None:
        pytest.skip("no hay Chrome ni Edge instalado")
    codigo = pdf.main([str(md), str(tmp_path / "x.pdf"), "--max-minutos", "20"])
    assert codigo == 1 and "suman mas de lo permitido" in capsys.readouterr().out


def test_main_sin_argumentos(capsys):
    assert pdf.main([]) == 2
