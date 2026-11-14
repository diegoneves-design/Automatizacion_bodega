"""El kit de la prueba con usuarios, la linea base y el checklist del celular se mantienen coherentes entre si
y con el instrumento del Avance 6 (docs/prueba-usuarios.md y docs/pauta-validacion.md)."""

import re
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "herramientas"))

import calcular_linea_base as lb  # noqa: E402
import md_a_pdf  # noqa: E402

DOCS = RAIZ / "docs"
KIT = DOCS / "kit-prueba"


def leer(ruta):
    return Path(ruta).read_text(encoding="utf-8")


def documentos_nuevos():
    return sorted(KIT.glob("*.md")) + [DOCS / "linea-base.md", DOCS / "checklist-celular.md"]


# ---------------------------------------------------------------- existen y se enlazan

def test_existen_todas_las_piezas_del_kit():
    for nombre in ["README.md", "consentimiento.md", "consentimiento.pdf", "planilla_registro.csv", "ensayo-interno.md",
                   "plan-sesiones.md", "regla-decision.md", "regla-decision.pdf", "revision-avance6.md"]:
        assert (KIT / nombre).exists(), nombre
    for ruta in [DOCS / "linea-base.md", DOCS / "checklist-celular.md", DOCS / "plantillas" / "linea_base_registro.csv"]:
        assert ruta.exists(), ruta


def test_el_readme_enlaza_el_kit_la_linea_base_y_el_checklist():
    readme = leer(RAIZ / "README.md")
    for destino in ["docs/prueba-usuarios.md", "docs/pauta-validacion.md", "docs/kit-prueba/", "docs/linea-base.md",
                    "docs/checklist-celular.md"]:
        assert destino in readme, f"el README no enlaza {destino}"


@pytest.mark.parametrize("doc", documentos_nuevos(), ids=lambda p: p.name)
def test_los_enlaces_relativos_de_los_documentos_nuevos_existen(doc):
    for destino in re.findall(r"\]\(([^)\s]+)\)", leer(doc)):
        if destino.startswith(("http://", "https://", "mailto:", "#")):
            continue
        ruta = (doc.parent / destino.split("#")[0]).resolve()
        assert ruta.exists(), f"{doc.name} enlaza {destino} y no existe"


def test_el_gitignore_bloquea_la_evidencia():
    gi = leer(RAIZ / ".gitignore")
    for patron in ["evidencia/", "datos-medicion/", "*.mp4", "*.mov", "*.wav", "*.m4a"]:
        assert re.search(rf"^{re.escape(patron)}\s*$", gi, re.M), patron


# ---------------------------------------------------------------- consentimiento

def test_el_consentimiento_cubre_los_cuatro_puntos_que_pide_la_pauta():
    c = leer(KIT / "consentimiento.md")
    for punto in ["**Qué registramos.**", "**Para qué.**", "**Quién lo ve.**", "**Cuánto tiempo se conserva.**"]:
        assert punto in c, punto
    assert "pantalla y la voz" in c and "Nunca su cara" in c
    assert "se borran al terminar el semestre" in c


def test_el_consentimiento_no_pide_nombre_ni_datos_de_contacto():
    c = leer(KIT / "consentimiento.md").lower()
    assert "nombre:" not in c and "firma" not in c.replace("no se firma", "") and "rut" not in re.findall(r"\b\w+\b", c)
    assert "código de participante" in c
    assert "su nombre, su correo, su teléfono" in c            # lo que NO se registra


def test_el_consentimiento_dice_lo_mismo_que_el_texto_oral_de_la_pauta():
    c, pauta = leer(KIT / "consentimiento.md"), leer(DOCS / "pauta-validacion.md")
    for hecho in ["pantalla y la voz", "profesora del curso", "se borra al terminar el semestre", "carpeta privada"]:
        oral = hecho in pauta
        # la hoja puede decirlo en plural ("se borran"); lo importante es que el hecho este en las dos
        escrito = hecho in c or hecho.replace("se borra", "se borran") in c
        assert oral and escrito, hecho
    assert "20 minutos como máximo" in c and "el máximo es 20" in pauta


# ---------------------------------------------------------------- regla de decision y umbrales

def test_la_regla_de_decision_tiene_las_tres_severidades():
    r = leer(KIT / "regla-decision.md")
    for s in ["Bloquea", "Entorpece", "Estético"]:
        assert f"**{s}**" in r
    assert "2 o más de 5" in r and "antes de construir" in r


def test_los_umbrales_de_la_hoja_coinciden_con_prueba_usuarios():
    hoja, prueba = leer(KIT / "regla-decision.md"), leer(DOCS / "prueba-usuarios.md")
    for numero in ["4 o 5 de 5", "3 de 5", "2 o menos", "1 o menos", "3 minutos", "5 minutos", "68", "3 o más"]:
        assert numero in hoja, f"la hoja no trae '{numero}'"
        assert numero in prueba, f"prueba-usuarios.md no trae '{numero}'"
    assert "1 vez como máximo" in prueba and "2 veces como máximo" in prueba   # los desvios de las tareas 1 y 2


def test_la_planilla_de_registro_tiene_las_seis_columnas_del_enunciado():
    cabecera = leer(KIT / "planilla_registro.csv").strip()
    assert cabecera == "participante,tarea,minuto,observado,interpretado,severidad"


# ---------------------------------------------------------------- plan de sesiones

def test_el_plan_de_sesiones_asigna_los_tres_papeles_y_protege_la_evidencia():
    p = leer(KIT / "plan-sesiones.md")
    for papel in ["**Facilitador**", "**Registrador**", "**Resguardo de evidencia**"]:
        assert papel in p
    assert "20 minutos como máximo" in p and "fuera del repositorio" in p.lower() or "Nunca** en el repositorio" in p
    assert "acceso restringido" in p and "Reiniciar demo" in p
    assert "pantalla y voz" in p.lower() and "sin rostro" in p.lower()


def test_el_plan_registra_diez_sesiones_con_usuarios_y_cuatro_consultas():
    p = leer(KIT / "plan-sesiones.md")
    codigos = re.findall(r"^\| ([PS]\d{2}) \|", p, re.M)
    assert [c for c in codigos if c.startswith("P")] == [f"P{i:02d}" for i in range(1, 11)]
    assert [c for c in codigos if c.startswith("S")] == [f"S{i:02d}" for i in range(1, 5)]


# ---------------------------------------------------------------- linea base

def test_linea_base_documenta_todas_las_columnas_y_el_comando():
    doc = leer(DOCS / "linea-base.md")
    for columna in lb.COLUMNAS:
        assert f"`{columna}`" in doc, columna
    for causa in lb.CAUSAS:
        assert f"`{causa}`" in doc, causa
    assert "py herramientas/calcular_linea_base.py" in doc
    assert "(guías con `error_detectado = no` **y** `se_rehizo = no`) ÷ (guías medidas) × 100" in doc
    assert str(lb.MINIMO_MEDICIONES) in doc and "Mínimo: 5 guías" in doc


def test_linea_base_tiene_la_tabla_antes_y_con_la_prueba_de_concepto_vacia():
    doc = leer(DOCS / "linea-base.md")
    fila = re.search(r"^\| Guías emitidas sin errores ni reprocesos \| \| \|", doc, re.M)
    assert fila, "la fila del indicador debe tener las columnas Antes y Con la PoC vacias"
    assert "| Indicador | Antes (a mano) | Con la prueba de concepto |" in doc


# ---------------------------------------------------------------- sin datos personales

CORREO = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
TELEFONO = re.compile(r"(?<![\w.])\+?\d[\d\s().-]{7,}\d(?![\d])")
NOMBRES_DEL_EQUIPO = ["Carmona", "Ynchaustegui", "Neves", "Vargas"]
RUT = re.compile(r"(?<![\w.])\d{1,2}\.\d{3}\.\d{3}-[\dkK](?!\w)")
RUT_FICTICIOS = {"76.123.456-7", "77.987.654-3"}   # los de las empresas de ejemplo del modelo de datos


def archivos_de_texto():
    carpetas = [DOCS, RAIZ / "herramientas", RAIZ / "prototipo", RAIZ / "supabase", RAIZ / "tests"]
    for carpeta in carpetas:
        for p in carpeta.rglob("*"):
            if p.is_file() and p.suffix.lower() in {".md", ".csv", ".py", ".js", ".html", ".sql", ".mjs"} \
                    and "__pycache__" not in p.parts and p.name != "config.js":
                yield p
    yield RAIZ / "README.md"
    yield RAIZ / ".env.example"


def es_ficticio(telefono):
    digitos = re.sub(r"\D", "", telefono)
    return len(set(digitos[-8:])) == 1                     # +56 9 1111 1111, 900000000, (2) 0000-0000


def test_los_correos_y_telefonos_del_repositorio_son_ficticios():
    for p in archivos_de_texto():
        t = leer(p)
        for c in CORREO.findall(t):
            assert c.endswith("@ejemplo.cl"), f"{p.relative_to(RAIZ)}: correo que no es de ejemplo: {c}"
        for rut in RUT.findall(t):
            assert rut in RUT_FICTICIOS, f"{p.relative_to(RAIZ)}: RUT que no es de los ficticios del modelo: {rut}"
        for tel in TELEFONO.findall(RUT.sub(" ", t)):
            if re.fullmatch(r"\d{4}-\d{2}-\d{2}", tel.strip()) or re.fullmatch(r"[\d.\s-]*\d{4}[-/]\d{2}[-/]\d{2}[\d:\s-]*", tel.strip()):
                continue                                       # fechas y horas
            if len(re.sub(r"\D", "", tel)) < 9:
                continue
            assert es_ficticio(tel), f"{p.relative_to(RAIZ)}: telefono que no parece ficticio: {tel.strip()}"


@pytest.mark.parametrize("doc", documentos_nuevos(), ids=lambda p: p.name)
def test_los_documentos_nuevos_no_nombran_a_integrantes_ni_participantes(doc):
    t = leer(doc)
    for nombre in NOMBRES_DEL_EQUIPO:
        assert nombre not in t, f"{doc.name} nombra a {nombre}"


# ---------------------------------------------------------------- PDF imprimibles

def planas(nombre):
    return md_a_pdf.contar_planas(DOCS / nombre if "/" not in nombre else DOCS / Path(nombre))


def test_la_pauta_imprimible_tiene_dos_planas_o_menos():
    assert 1 <= planas("pauta-validacion.pdf") <= 2


def test_la_hoja_de_la_regla_cabe_en_una_plana():
    assert planas("kit-prueba/regla-decision.pdf") == 1


def test_el_consentimiento_imprimible_cabe_en_dos_planas():
    assert 1 <= planas("kit-prueba/consentimiento.pdf") <= 2


@pytest.mark.parametrize("pdf, md, frase", [
    ("pauta-validacion.pdf", "pauta-validacion.md", "Reiniciar demo"),
    ("pauta-validacion.pdf", "pauta-validacion.md", "antes de dejar lista la guía, ¿qué revisó?"),
    ("kit-prueba/regla-decision.pdf", "kit-prueba/regla-decision.md", "Entorpece"),
    ("kit-prueba/consentimiento.pdf", "kit-prueba/consentimiento.md", "No tiene espacio para el nombre"),
])
def test_el_pdf_esta_al_dia_con_su_texto(pdf, md, frase):
    pypdf = pytest.importorskip("pypdf")
    texto_pdf = " ".join(" ".join(pg.extract_text().split()) for pg in pypdf.PdfReader(str(DOCS / pdf)).pages)
    assert frase in leer(DOCS / md)
    assert frase in texto_pdf, f"{pdf} no trae '{frase}': hay que regenerarlo con herramientas/md_a_pdf.py"


# ---------------------------------------------------------------- sin emojis

# Emojis y pictogramas. No incluye simbolos tipograficos como el check, la cruz o las flechas, que el prototipo usa
# junto a un texto (check ok, cruz no existe) y que no son emojis. Los rangos se arman con chr() para que este
# archivo no tenga ningun emoji escrito.
RANGOS = [(0x1F300, 0x1FAFF), (0x2600, 0x26FF), (0x2700, 0x27BF), (0x2B50, 0x2B50), (0x2B55, 0x2B55), (0xFE0F, 0xFE0F), (0x200D, 0x200D)]
EMOJI = re.compile("[" + "".join(chr(a) + "-" + chr(b) for a, b in RANGOS) + "]")
PERMITIDOS = {chr(0x2713), chr(0x2715), chr(0x2717), chr(0x2718)}


def test_el_repositorio_no_tiene_emojis():
    for p in archivos_de_texto():
        for c in EMOJI.findall(leer(p)):
            assert c in PERMITIDOS, f"{p.relative_to(RAIZ)} tiene el emoji U+{ord(c):04X}"
    assert EMOJI.search(leer(RAIZ / "README.md")) is None


# ---------------------------------------------------------------- decisiones del 14 de noviembre de 2026

def preguntas_numeradas(texto, titulo):
    inicio = texto.index(titulo)
    fin = texto.find("\n## ", inicio + 5)
    fin = len(texto) if fin == -1 else fin
    return re.findall(r"^\d+\. (.+)$", texto[inicio:fin], re.M)


def test_prueba_usuarios_y_pauta_no_llevan_nombres_de_personas():
    for doc in (DOCS / "prueba-usuarios.md", DOCS / "pauta-validacion.md"):
        t = leer(doc)
        for nombre in NOMBRES_DEL_EQUIPO + ["Sebasti", "Oscar", "Diego", "Bastián"]:
            assert nombre not in t, f"{doc.name} nombra a {nombre}"


def test_prueba_usuarios_usa_roles_en_el_plan_de_sesiones():
    t = leer(DOCS / "prueba-usuarios.md")
    assert "| Sesión | Facilitador" in t and "Registrador" in t and "Resguardo de evidencia" in t
    assert "Integrante A" in t and "Integrante B" in t
    assert "no van en el repositorio" in t


def test_el_integrante_de_la_bodega_no_ve_las_grabaciones_en_el_plan_ni_en_el_consentimiento():
    """El consentimiento promete que esa persona no ve las grabaciones: el plan no puede contradecirlo."""
    plan = leer(DOCS / "prueba-usuarios.md")
    fila = [f for f in plan.splitlines() if f.startswith("| Participantes de la bodega del caso")][0]
    celdas = [c.strip() for c in fila.strip("|").split("|")]
    assert "Integrante B" not in celdas[1:], "el integrante B no puede tener ningun papel en las sesiones con su gente"
    assert "ni mira la grabación" in plan
    assert "no ve las grabaciones" in leer(KIT / "consentimiento.md").replace("ni ve las grabaciones", "no ve las grabaciones")


def test_los_resultados_se_leen_en_tres_tramos_sin_zonas_sin_regla():
    t = leer(DOCS / "prueba-usuarios.md")
    assert "| 4 o 5 | **Se cumple** |" in t and "| 3 | **Entorpece** |" in t and "| 2 o menos | **Bloquea** |" in t
    assert "No queda ninguna zona sin regla" in t
    assert "(3 de 5 entorpece; 2 o menos bloquea)" in t
    assert "Nos equivocamos si** solo 2 o menos" in t


def test_la_pauta_deja_al_menos_un_minuto_de_holgura():
    total, etapas = md_a_pdf.minutos_de_las_etapas(leer(DOCS / "pauta-validacion.md"))
    assert len(etapas) == 6 and total <= 19, f"las etapas suman {total} min"


def test_la_pauta_tiene_dos_preguntas_de_contexto_sin_las_que_sugerian():
    pauta = leer(DOCS / "pauta-validacion.md")
    contexto = preguntas_numeradas(pauta, "## 2. Preguntas de contexto")
    assert len(contexto) == 2
    assert contexto[1] == "Esa vez, antes de dejar lista la guía, ¿qué revisó?"
    assert "cómo revisó que los códigos" not in pauta
    cierre = preguntas_numeradas(pauta, "## 6. Preguntas de cierre")
    assert cierre[1] == "Cuando lo hace en su trabajo, ¿en qué se parece o en qué no se parece a lo que acaba de hacer?"
    assert "¿Qué hizo distinto" not in pauta


def test_la_frase_1_del_sus_se_queda():
    assert "Le gustaría usar este sistema con frecuencia" in leer(DOCS / "pauta-validacion.md")


def test_el_exito_de_la_tarea_2_se_verifica_de_oido():
    t = leer(DOCS / "prueba-usuarios.md")
    assert "La persona dice en voz alta cuál es el código marcado" in t
    assert "con el cursor" not in t


def test_la_regla_de_fallas_del_sistema_esta_como_propuesta_aceptada():
    for doc in (DOCS / "prueba-usuarios.md", KIT / "plan-sesiones.md", KIT / "regla-decision.md"):
        t = leer(doc)
        assert "a favor ni en contra" in t, doc.name
        assert "propuesta" in t, doc.name


def test_la_pauta_anuncia_la_misma_duracion_que_suman_sus_etapas():
    pauta = leer(DOCS / "pauta-validacion.md")
    total, _ = md_a_pdf.minutos_de_las_etapas(pauta)
    assert f"**Dura {total} minutos en total**" in pauta
