"""
Sin emojis en el codigo. Recorre los archivos rastreados por git (git ls-files) y falla listando archivo y linea.

Alcance: .py .js .mjs .html .css .sql .json .yml .yaml .toml, Dockerfile y .env.example (comentarios, docstrings, mensajes y textos
de interfaz incluidos). Se excluyen prototipo/js/vendor/ (codigo de terceros minificado), node_modules/, datos_locales/ y .git/.
Los .md, la bitacora y docs/ no se revisan aqui.

Que cuenta como emoji: los caracteres de presentacion emoji (Emoji_Presentation), los pictograficos que piden el selector U+FE0F,
ese selector, el unidor U+200D cuando une emojis, las banderas (letras regionales), las teclas (U+20E3) y las etiquetas de
subdivision. NO cuenta la tipografia normal: tildes, n con tilde, signos de apertura, comillas angulares, guiones largos,
puntos medios, N.o, >=, <=, x, / ni las flechas planas sin selector de emoji.

Este archivo no lleva emojis literales: los rangos se escriben con escapes y los ejemplos se arman al ejecutar.
"""

import re
import subprocess
from pathlib import Path, PurePosixPath

import pytest

RAIZ = Path(__file__).resolve().parent.parent

EXTENSIONES = {".py", ".js", ".mjs", ".html", ".css", ".sql", ".json", ".yml", ".yaml", ".toml"}
NOMBRES = {"Dockerfile", ".env.example"}
EXCLUIDAS = ("prototipo/js/vendor/", "node_modules/", "datos_locales/", ".git/")

# Emoji_Presentation = Yes: se ven como emoji por omision
PRESENTACION = [
    (0x231A, 0x231B), (0x23E9, 0x23EC), (0x23F0, 0x23F0), (0x23F3, 0x23F3), (0x25FD, 0x25FE), (0x2614, 0x2615), (0x2648, 0x2653),
    (0x267F, 0x267F), (0x2693, 0x2693), (0x26A1, 0x26A1), (0x26AA, 0x26AB), (0x26BD, 0x26BE), (0x26C4, 0x26C5), (0x26CE, 0x26CE),
    (0x26D4, 0x26D4), (0x26EA, 0x26EA), (0x26F2, 0x26F3), (0x26F5, 0x26F5), (0x26FA, 0x26FA), (0x26FD, 0x26FD), (0x2705, 0x2705),
    (0x270A, 0x270B), (0x2728, 0x2728), (0x274C, 0x274C), (0x274E, 0x274E), (0x2753, 0x2755), (0x2757, 0x2757), (0x2795, 0x2797),
    (0x27B0, 0x27B0), (0x27BF, 0x27BF), (0x2B1B, 0x2B1C), (0x2B50, 0x2B50), (0x2B55, 0x2B55), (0x1F004, 0x1F004), (0x1F0CF, 0x1F0CF),
    (0x1F18E, 0x1F18E), (0x1F191, 0x1F19A), (0x1F1E6, 0x1F1FF), (0x1F201, 0x1F201), (0x1F21A, 0x1F21A), (0x1F22F, 0x1F22F),
    (0x1F232, 0x1F236), (0x1F238, 0x1F23A), (0x1F250, 0x1F251), (0x1F300, 0x1F320), (0x1F32D, 0x1F335), (0x1F337, 0x1F37C),
    (0x1F37E, 0x1F393), (0x1F3A0, 0x1F3CA), (0x1F3CF, 0x1F3D3), (0x1F3E0, 0x1F3F0), (0x1F3F4, 0x1F3F4), (0x1F3F8, 0x1F43E),
    (0x1F440, 0x1F440), (0x1F442, 0x1F4FC), (0x1F4FF, 0x1F53D), (0x1F54B, 0x1F54E), (0x1F550, 0x1F567), (0x1F57A, 0x1F57A),
    (0x1F595, 0x1F596), (0x1F5A4, 0x1F5A4), (0x1F5FB, 0x1F64F), (0x1F680, 0x1F6C5), (0x1F6CC, 0x1F6CC), (0x1F6D0, 0x1F6D2),
    (0x1F6D5, 0x1F6D7), (0x1F6DC, 0x1F6DF), (0x1F6EB, 0x1F6EC), (0x1F6F4, 0x1F6FC), (0x1F7E0, 0x1F7EB), (0x1F7F0, 0x1F7F0),
    (0x1F90C, 0x1F93A), (0x1F93C, 0x1F945), (0x1F947, 0x1F9FF), (0x1FA70, 0x1FA7C), (0x1FA80, 0x1FA88), (0x1FA90, 0x1FABD),
    (0x1FABF, 0x1FAC5), (0x1FACE, 0x1FADB), (0x1FAE0, 0x1FAE8), (0x1FAF0, 0x1FAF8),
]

# Extended_Pictographic: todos los pictograficos. Los que no estan en PRESENTACION se ven como texto por omision
# y solo cuentan como emoji si traen detras el selector U+FE0F.
PICTOGRAFICOS = [
    (0x00A9, 0x00A9), (0x00AE, 0x00AE), (0x203C, 0x203C), (0x2049, 0x2049), (0x2122, 0x2122), (0x2139, 0x2139), (0x2194, 0x2199),
    (0x21A9, 0x21AA), (0x231A, 0x231B), (0x2328, 0x2328), (0x2388, 0x2388), (0x23CF, 0x23CF), (0x23E9, 0x23F3), (0x23F8, 0x23FA),
    (0x24C2, 0x24C2), (0x25AA, 0x25AB), (0x25B6, 0x25B6), (0x25C0, 0x25C0), (0x25FB, 0x25FE), (0x2600, 0x2605), (0x2607, 0x2612),
    (0x2614, 0x2685), (0x2690, 0x2705), (0x2708, 0x2712), (0x2714, 0x2714), (0x2716, 0x2716), (0x271D, 0x271D), (0x2721, 0x2721),
    (0x2728, 0x2728), (0x2733, 0x2734), (0x2744, 0x2744), (0x2747, 0x2747), (0x274C, 0x274C), (0x274E, 0x274E), (0x2753, 0x2755),
    (0x2757, 0x2757), (0x2763, 0x2767), (0x2795, 0x2797), (0x27A1, 0x27A1), (0x27B0, 0x27B0), (0x27BF, 0x27BF), (0x2934, 0x2935),
    (0x2B05, 0x2B07), (0x2B1B, 0x2B1C), (0x2B50, 0x2B50), (0x2B55, 0x2B55), (0x3030, 0x3030), (0x303D, 0x303D), (0x3297, 0x3297),
    (0x3299, 0x3299), (0x1F000, 0x1F0FF), (0x1F10D, 0x1F10F), (0x1F12F, 0x1F12F), (0x1F16C, 0x1F171), (0x1F17E, 0x1F17F),
    (0x1F18E, 0x1F18E), (0x1F191, 0x1F19A), (0x1F1AD, 0x1F1E5), (0x1F201, 0x1F20F), (0x1F21A, 0x1F21A), (0x1F22F, 0x1F22F),
    (0x1F232, 0x1F23A), (0x1F23C, 0x1F23F), (0x1F249, 0x1F3FA), (0x1F400, 0x1F53D), (0x1F546, 0x1F64F), (0x1F680, 0x1F6FF),
    (0x1F774, 0x1F77F), (0x1F7D5, 0x1F7FF), (0x1F80C, 0x1F80F), (0x1F848, 0x1F84F), (0x1F85A, 0x1F85F), (0x1F888, 0x1F88F),
    (0x1F8AE, 0x1F8FF), (0x1F90C, 0x1F93A), (0x1F93C, 0x1F945), (0x1F947, 0x1FAFF), (0x1FC00, 0x1FFFD),
]

SELECTOR_EMOJI = 0xFE0F
UNIDOR = 0x200D
TECLA = 0x20E3
ETIQUETAS = (0xE0020, 0xE007F)


def _en(cp, rangos):
    return any(a <= cp <= b for a, b in rangos)


def _es_pictografico(cp):
    return _en(cp, PICTOGRAFICOS) or _en(cp, PRESENTACION)


def emojis_de(texto):
    """[(posicion, punto_de_codigo)] de cada caracter de emoji que hay en el texto."""
    puntos = [ord(c) for c in texto]
    halladas = []
    for i, cp in enumerate(puntos):
        anterior = puntos[i - 1] if i > 0 else None
        siguiente = puntos[i + 1] if i + 1 < len(puntos) else None
        if cp == SELECTOR_EMOJI or cp == TECLA or ETIQUETAS[0] <= cp <= ETIQUETAS[1]:
            halladas.append((i, cp))
        elif cp == UNIDOR:
            if (anterior is not None and (_es_pictografico(anterior) or anterior == SELECTOR_EMOJI)) or (siguiente is not None and _es_pictografico(siguiente)):
                halladas.append((i, cp))
        elif _en(cp, PRESENTACION):
            halladas.append((i, cp))
        elif _en(cp, PICTOGRAFICOS) and siguiente == SELECTOR_EMOJI:
            halladas.append((i, cp))
    return halladas


def revisar(textos):
    """textos: {ruta: contenido}. Devuelve las lineas 'ruta:linea: U+XXXX ...' de lo que encuentre."""
    problemas = []
    for ruta, contenido in textos.items():
        for numero, linea in enumerate(contenido.splitlines(), start=1):
            codigos = [cp for _, cp in emojis_de(linea)]
            if codigos:
                problemas.append(f"{ruta}:{numero}: " + " ".join(f"U+{cp:04X}" for cp in codigos))
    return problemas


def en_alcance(ruta):
    p = PurePosixPath(ruta)
    if any(ruta.startswith(e) or ("/" + e) in ("/" + ruta) for e in EXCLUIDAS):
        return False
    return p.suffix.lower() in EXTENSIONES or p.name in NOMBRES


def archivos_rastreados():
    try:
        salida = subprocess.run(["git", "ls-files", "-z"], cwd=RAIZ, capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("git no esta disponible: no se puede listar lo rastreado")
    return [r for r in salida.decode("utf-8").split("\0") if r and en_alcance(r)]


def test_el_codigo_no_tiene_emojis():
    textos = {}
    for ruta in archivos_rastreados():
        try:
            textos[ruta] = (RAIZ / ruta).read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            continue
    problemas = revisar(textos)
    assert not problemas, "Hay emojis en el codigo (archivo:linea):\n  " + "\n  ".join(problemas)


# ---------------------------------------------------------------------------
# El detector: encuentra lo que debe y deja pasar la tipografia normal. Los ejemplos se arman al ejecutar.
# ---------------------------------------------------------------------------

def test_el_detector_falla_con_un_texto_de_ejemplo_y_dice_archivo_y_linea():
    con_emoji = "linea uno\nListo " + chr(0x2705) + " para usar\nlinea tres"
    problemas = revisar({"src/ejemplo.py": con_emoji})
    assert problemas == ["src/ejemplo.py:2: U+2705"]
    with pytest.raises(AssertionError, match=r"src/ejemplo\.py:2"):
        assert not problemas, "Hay emojis en el codigo (archivo:linea):\n  " + "\n  ".join(problemas)


@pytest.mark.parametrize("partes", [
    [0x1F680],                       # presentacion emoji por omision
    [0x26A0, 0xFE0F],                # pictografico de texto + selector de emoji
    [0x2194, 0xFE0F],                # flecha con selector de emoji
    [0x1F468, 0x200D, 0x1F4BB],      # emojis unidos con U+200D
    [0x1F1E8, 0x1F1F1],              # bandera (letras regionales)
    [0x31, 0xFE0F, 0x20E3],          # tecla
    [0x1F44D, 0x1F3FD],              # con tono de piel
    [0x2705],
    [0x274C],
])
def test_el_detector_encuentra_los_emojis(partes):
    assert emojis_de("x " + "".join(chr(c) for c in partes) + " y"), [f"U+{c:04X}" for c in partes]


def _t(*partes):
    """Texto armado con puntos de codigo (int) y cadenas: este archivo no lleva caracteres especiales literales."""
    return "".join(chr(x) if isinstance(x, int) else x for x in partes)


TIPOGRAFIA_NORMAL = [
    _t("tildes y enes: ", 0xE1, 0xE9, 0xED, 0xF3, 0xFA, " ", 0xF1, " ", 0xBF, " ", 0xA1),
    _t("comillas ", 0xAB, "angulares", 0xBB, " y guiones ", 0x2014, " largos, puntos ", 0xB7, " medios, N.", 0xBA, " interno"),
    _t(0x2265, " ", 0x2264, " ", 0xD7, " ", 0xF7, " ", 0x2192, " ", 0x2190, " ", 0x2191, " ", 0x2193, " ", 0x2026),
    _t(0xA9, " ", 0xAE, " ", 0x2122),                    # simbolos de texto sin selector de emoji
    _t(0x2194, " ", 0x2195, " ", 0x2196),                # flechas planas sin selector de emoji
    _t(0x25B2, " ", 0x25BC, " ", 0x2713, " ", 0x2717),   # triangulos y marcas de texto
    _t("unidor suelto ", 0x200D, " entre palabras"),     # el unidor que no une emojis
    "texto normal, 123 #hashtag * 1.",
]


@pytest.mark.parametrize("texto", TIPOGRAFIA_NORMAL)
def test_el_detector_no_toca_la_tipografia_normal(texto):
    assert emojis_de(texto) == []


def test_este_archivo_no_lleva_caracteres_especiales_literales():
    """Que un emoji o un caracter invisible no se cuele aqui escrito de corrido (ya paso con la herramienta de escritura)."""
    contenido = Path(__file__).read_text(encoding="utf-8")
    assert [c for c in contenido if ord(c) > 0x7F] == []


def test_el_alcance_incluye_lo_pedido_y_excluye_lo_de_terceros():
    incluidos = ["src/app.py", "prototipo/js/app.js", "prototipo/dashboard.html", "prototipo/css/estilos.css", "supabase/schema.sql",
                 "x/datos.json", ".github/workflows/ci.yml", "a/b.yaml", ".streamlit/config.toml", "Dockerfile", ".env.example", "prototipo/generar-config.mjs"]
    excluidos = ["README.md", "docs/guia.md", "docs/bitacora-ia/bitacora.md", "prototipo/js/vendor/echarts.custom.min.js",
                 "node_modules/x/index.js", "datos_locales/carga.sql", "docs/img/captura.png", "requirements.txt"]
    assert all(en_alcance(r) for r in incluidos), [r for r in incluidos if not en_alcance(r)]
    assert not any(en_alcance(r) for r in excluidos), [r for r in excluidos if en_alcance(r)]
