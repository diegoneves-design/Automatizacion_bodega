"""Convierte el Excel del inventario real en archivos SQL para cargar a Supabase.

Uso:
    py herramientas/importar_inventario.py "RUTA\\al\\Excel.xlsx" [--salida datos_locales]

No se conecta a Supabase ni a internet: solo lee el Excel y escribe archivos en la carpeta de salida
(por defecto datos_locales/, que esta en .gitignore). Los archivos generados traen DATOS REALES y no se
suben al repositorio.

  carga_inventario_01.sql, 02, ...   hasta 300 equipos por archivo (insert ... on conflict (sku) do update)
  carga_extensiones.sql              las extensiones electricas
  reporte_calidad.json               SOLO agregados: sin SKU, sin descripciones, sin textos de ubicacion

Requiere openpyxl (pip install openpyxl). No esta en requirements.txt porque la app no lo usa.
Reglas y supuestos: docs/analisis-inventario.md
"""
import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

ID_INICIAL = 1000          # los equipos reales parten en 1000; los de demo (501-507) no se tocan
FILAS_POR_TROZO = 300
SKU_DEMO = ("SD-63A20-0314", "SD-63A20-0315", "SD-63A20-0316", "SD-32A10-0102", "SD-32A10-0108", "ST-0042", "MP-0107")

# Ubicacion de la hoja AFO -> (estado, ubicacion, situacion_origen). La clave va sin tildes y en mayusculas.
REGLAS_UBICACION = {
    "BODEGA": ("disponible", "bodega", "BODEGA"),
    "BODEGA LOS ANGELES": ("disponible", "bodega", "BODEGA LOS ANGELES"),
    "SHOWROOM": ("disponible", "bodega", "SHOWROOM"),
    "REPARACION": ("en_mantencion", "taller", "REPARACIÓN"),
    "BAJA": ("fuera_servicio", "bodega", "BAJA"),
    "POR HABILITAR": ("fuera_servicio", "bodega", "POR HABILITAR"),
    "EN BUSCA": ("fuera_servicio", "bodega", "EN BUSCA"),
    "FUERA DE NORMA": ("fuera_servicio", "bodega", "FUERA DE NORMA"),
}
SITUACIONES = sorted({v[2] for v in REGLAS_UBICACION.values()} | {"CONTRATO", "CLIENTE"})

SIN_CATEGORIA = "SIN CATEGORÍA"
CATEGORIAS_NORMALIZADAS = {"VENTILACION": "VENTILACIÓN"}

SKU_EXTENSION_ESTANDAR = re.compile(r"^SD-\d{2}A\d{2}-\d{5}$")


def _sin_tildes(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def limpiar_texto(valor):
    """Quita espacios de los extremos y colapsa los repetidos. Devuelve '' si no hay valor."""
    if valor is None:
        return ""
    return re.sub(r"\s+", " ", str(valor)).strip()


def mapear_ubicacion(valor):
    """(estado, ubicacion, situacion_origen, regla). `regla` solo sirve para contar; nunca guarda el texto original."""
    if isinstance(valor, bool):
        raise ValueError("ubicacion con un valor que no es texto ni numero")
    if isinstance(valor, (int, float)):
        return ("arrendado", "cliente", "CONTRATO", "numerico")
    texto = limpiar_texto(valor)
    if texto == "":
        raise ValueError("fila sin ubicacion")
    if re.fullmatch(r"\d+([.,]\d+)?", texto):
        return ("arrendado", "cliente", "CONTRATO", "numerico")
    clave = _sin_tildes(texto).upper()
    if clave in REGLAS_UBICACION:
        estado, lugar, situacion = REGLAS_UBICACION[clave]
        return (estado, lugar, situacion, "conocida:" + situacion)
    return ("arrendado", "cliente", "CLIENTE", "otro_texto")


def normalizar_categoria(valor):
    texto = limpiar_texto(valor).upper()
    if texto == "":
        return SIN_CATEGORIA
    return CATEGORIAS_NORMALIZADAS.get(_sin_tildes(texto), texto)


def prefijo_familia(sku):
    return limpiar_texto(sku)[:2].upper()


def _numero(texto):
    """'14.000' -> 14000 (punto de miles); '7.5' y '3,3' -> decimales."""
    t = texto.strip()
    if re.fullmatch(r"\d{1,3}(\.\d{3})+", t):
        return float(t.replace(".", ""))
    return float(t.replace(",", "."))


_N = r"(\d+(?:[.,]\d+)*)"
_PATRONES_CAPACIDAD = (
    ("BTU/H", re.compile(_N + r"\s*(M?)\s*BTU\s*/?\s*H?\b", re.I)),
    ("TR", re.compile(_N + r"\s*()TR\b", re.I)),
    ("m3/h", re.compile(_N + r"\s*()M\s*[3³]\s*/?\s*H\b", re.I)),
    ("kW", re.compile(_N + r"\s*()KW\b", re.I)),
)


def extraer_capacidad(descripcion):
    """(valor, unidad) con BTU/H, TR, m3/h o kW leidos de la descripcion; (None, None) si no se puede.
    'MBTUH' son miles de BTU/H."""
    texto = limpiar_texto(descripcion)
    for unidad, patron in _PATRONES_CAPACIDAD:
        m = patron.search(texto)
        if not m:
            continue
        try:
            valor = _numero(m.group(1))
        except ValueError:
            continue
        if m.group(2):
            valor *= 1000
        if valor <= 0:
            continue
        return (int(valor) if valor == int(valor) else valor, unidad)
    return (None, None)


def convertir_largo(valor):
    """Largo en metros como entero; None si no se puede convertir ('07' -> 7, 20 -> 20, 'abc' -> None)."""
    if isinstance(valor, bool) or valor is None:
        return None
    if isinstance(valor, (int, float)):
        return int(valor) if float(valor).is_integer() and valor >= 0 else None
    texto = limpiar_texto(valor)
    return int(texto) if re.fullmatch(r"\d{1,4}", texto) else None


def sku_extension_estandar(sku):
    return bool(SKU_EXTENSION_ESTANDAR.match(limpiar_texto(sku)))


def literal(valor):
    """Valor como literal SQL."""
    if valor is None:
        return "null"
    if isinstance(valor, (int, float)):
        return repr(valor)
    return "'" + str(valor).replace("'", "''") + "'"


def preparar_equipos(filas_afo, catalogo):
    """filas_afo: [(sku, n, descripcion, familia, ubicacion)]. catalogo: {prefijo: categoria o None}.
    Devuelve (equipos, agregados). Falla si hay SKU repetidos, SKU de la demo o filas sin ubicacion."""
    skus = [limpiar_texto(f[0]) for f in filas_afo]
    repetidos = [s for s, n in Counter(skus).items() if n > 1]
    if repetidos:
        raise ValueError(f"hay {len(repetidos)} SKU repetidos en la hoja AFO; corrijalos en el Excel")
    choques = sorted(set(skus) & set(SKU_DEMO))
    if choques:
        raise ValueError(f"{len(choques)} SKU del Excel coinciden con equipos de demo (501-507); no se genera nada para no pisarlos")
    equipos = []
    por_estado, por_regla = Counter(), Counter()
    sin_catalogo, sin_categoria, sin_capacidad = Counter(), 0, 0
    por_unidad = Counter()
    for orden, fila in enumerate(sorted(filas_afo, key=lambda f: limpiar_texto(f[0])), start=ID_INICIAL):
        sku, descripcion = limpiar_texto(fila[0]), limpiar_texto(fila[2])
        if not sku or not descripcion:
            raise ValueError("hay una fila de AFO sin SKU o sin descripcion")
        estado, lugar, situacion, regla = mapear_ubicacion(fila[4])
        familia = prefijo_familia(sku)
        if familia not in catalogo:
            sin_catalogo[familia] += 1
            categoria = SIN_CATEGORIA
        else:
            categoria = normalizar_categoria(catalogo[familia])
        if categoria == SIN_CATEGORIA:
            sin_categoria += 1
        valor, unidad = extraer_capacidad(descripcion)
        if valor is None:
            sin_capacidad += 1
        else:
            por_unidad[unidad] += 1
        por_estado[estado] += 1
        por_regla[regla] += 1
        equipos.append({"id_equipo": orden, "sku": sku, "descripcion": descripcion, "estado": estado, "ubicacion": lugar,
                        "familia": familia, "categoria": categoria, "situacion_origen": situacion,
                        "capacidad_valor": valor, "capacidad_unidad": unidad})
    agregados = {
        "equipos_en_total": len(equipos),
        "filas_por_estado": dict(sorted(por_estado.items())),
        "filas_por_regla_de_ubicacion": dict(sorted(por_regla.items())),
        "equipos_por_familia": dict(sorted(Counter(e["familia"] for e in equipos).items())),
        "prefijos_sin_catalogo": dict(sorted(sin_catalogo.items())),
        "equipos_sin_categoria": sin_categoria,
        "equipos_con_capacidad_por_unidad": dict(sorted(por_unidad.items())),
        "equipos_sin_capacidad_extraida": sin_capacidad,
    }
    return equipos, agregados


def preparar_extensiones(filas_ext):
    """filas_ext: [(sku, n, corriente, largo)]. Devuelve (extensiones, agregados)."""
    skus = [limpiar_texto(f[0]) for f in filas_ext]
    if len(set(skus)) != len(skus):
        raise ValueError("hay SKU repetidos en la hoja de extensiones electricas")
    extensiones, no_estandar, largos_no_numericos = [], 0, 0
    for fila in sorted(filas_ext, key=lambda f: limpiar_texto(f[0])):
        sku = limpiar_texto(fila[0])
        largo = convertir_largo(fila[3])
        if largo is None:
            largos_no_numericos += 1
        if not sku_extension_estandar(sku):
            no_estandar += 1
        extensiones.append({"sku": sku, "corriente": limpiar_texto(fila[2]).upper(), "largo_m": largo})
    agregados = {
        "extensiones_en_total": len(extensiones),
        "extensiones_por_corriente": dict(sorted(Counter(e["corriente"] for e in extensiones).items())),
        "extensiones_con_sku_de_formato_no_estandar": no_estandar,
        "extensiones_con_largo_no_numerico": largos_no_numericos,
    }
    return extensiones, agregados


COLUMNAS_EQUIPOS = ("id_equipo", "sku", "descripcion", "estado", "ubicacion", "familia", "categoria", "situacion_origen",
                    "capacidad_valor", "capacidad_unidad")
ACTUALIZAR = ("descripcion", "estado", "ubicacion", "familia", "categoria", "situacion_origen", "capacidad_valor", "capacidad_unidad")


def sql_equipos(trozo, numero, total):
    lineas = [f"-- Carga del inventario real, parte {numero} de {total} ({len(trozo)} equipos). DATOS REALES: no se sube al repositorio.",
              "-- Se puede volver a ejecutar: actualiza por SKU y no duplica.",
              f"insert into public.equipos ({', '.join(COLUMNAS_EQUIPOS)}) values"]
    filas = ["  (" + ", ".join(literal(e[c]) for c in COLUMNAS_EQUIPOS) + ")" for e in trozo]
    lineas.append(",\n".join(filas))
    lineas.append("on conflict (sku) do update set " + ", ".join(f"{c} = excluded.{c}" for c in ACTUALIZAR) + ";")
    return "\n".join(lineas) + "\n"


def sql_extensiones(extensiones):
    partes = ["-- Carga de extensiones electricas reales. DATOS REALES: no se sube al repositorio.",
              "-- Se puede volver a ejecutar: actualiza por SKU y no duplica."]
    for i in range(0, len(extensiones), FILAS_POR_TROZO):
        trozo = extensiones[i:i + FILAS_POR_TROZO]
        filas = ["  (" + ", ".join(literal(e[c]) for c in ("sku", "corriente", "largo_m")) + ")" for e in trozo]
        partes.append("insert into public.extensiones_electricas (sku, corriente, largo_m) values\n" + ",\n".join(filas) +
                      "\non conflict (sku) do update set corriente = excluded.corriente, largo_m = excluded.largo_m;")
    return "\n".join(partes) + "\n"


def leer_excel(ruta):
    try:
        import openpyxl
    except ImportError:
        sys.exit("Falta openpyxl. Instalalo con:  py -m pip install openpyxl")
    libro = openpyxl.load_workbook(ruta, data_only=True, read_only=True)

    def hoja(nombre_parcial):
        for nombre in libro.sheetnames:
            if _sin_tildes(nombre).upper() == _sin_tildes(nombre_parcial).upper():
                return [f for f in list(libro[nombre].iter_rows(values_only=True))[1:] if any(c is not None and str(c).strip() for c in f)]
        sys.exit(f"No encuentro la hoja '{nombre_parcial}'. Hojas del libro: {', '.join(libro.sheetnames)}")

    afo = hoja("AFO")
    ext = hoja("AF Extensiones electricas")
    cat = hoja("Detalle Familias")
    catalogo = {limpiar_texto(f[0]).upper(): (limpiar_texto(f[3]) or None) for f in cat if limpiar_texto(f[0])}
    return afo, ext, catalogo


def generar(afo, ext, catalogo, salida):
    equipos, ag_eq = preparar_equipos(afo, catalogo)
    extensiones, ag_ex = preparar_extensiones(ext)
    salida.mkdir(parents=True, exist_ok=True)
    for viejo in salida.glob("carga_inventario_*.sql"):
        viejo.unlink()                         # no dejar trozos de una corrida anterior
    trozos = [equipos[i:i + FILAS_POR_TROZO] for i in range(0, len(equipos), FILAS_POR_TROZO)]
    archivos = []
    for n, trozo in enumerate(trozos, start=1):
        nombre = f"carga_inventario_{n:02d}.sql"
        (salida / nombre).write_text(sql_equipos(trozo, n, len(trozos)), encoding="utf-8")
        archivos.append(nombre)
    (salida / "carga_extensiones.sql").write_text(sql_extensiones(extensiones), encoding="utf-8")
    archivos.append("carga_extensiones.sql")
    reporte = {**ag_eq, **ag_ex, "archivos_generados": archivos, "filas_por_archivo_maximo": FILAS_POR_TROZO}
    (salida / "reporte_calidad.json").write_text(json.dumps(reporte, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return reporte


def main(argv=None):
    ap = argparse.ArgumentParser(description="Genera los SQL de carga del inventario a partir del Excel.")
    ap.add_argument("excel", help="ruta del archivo .xlsx")
    ap.add_argument("--salida", default=str(Path(__file__).resolve().parent.parent / "datos_locales"),
                    help="carpeta de salida (por defecto datos_locales/ en la raiz del repositorio)")
    args = ap.parse_args(argv)
    ruta = Path(args.excel)
    if not ruta.is_file():
        sys.exit("No existe el archivo indicado.")
    afo, ext, catalogo = leer_excel(ruta)
    try:
        reporte = generar(afo, ext, catalogo, Path(args.salida))
    except ValueError as error:
        sys.exit(f"No se genero nada: {error}")
    print(json.dumps(reporte, ensure_ascii=False, indent=2))
    print(f"\nArchivos escritos en {args.salida} (esa carpeta no se versiona).")


if __name__ == "__main__":
    main()
