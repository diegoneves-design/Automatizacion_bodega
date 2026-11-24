"""Calcula la linea base de como se hace hoy una guia de despacho o retiro, a partir del CSV de mediciones.

Uso:
    py herramientas/calcular_linea_base.py ruta/al/archivo.csv          # resumen en texto
    py herramientas/calcular_linea_base.py ruta/al/archivo.csv --md     # tabla "antes" para pegar en docs/linea-base.md

El CSV tiene una fila por guia medida y las columnas de docs/plantillas/linea_base_registro.csv. El protocolo
(que se mide, como se cronometra y que significa cada columna) esta en docs/linea-base.md.

El archivo con mediciones reales NO se sube al repositorio: se guarda en Drive o en la carpeta datos-medicion/
(ignorada por git). Aqui solo se sube el resumen. Por eso el script se niega a leer filas que parezcan llevar un
correo o un telefono: las mediciones se anotan sin nombres.

Solo usa la biblioteca estandar.
"""

import csv
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

COLUMNAS = [
    "id_medicion",
    "fecha",
    "tipo_movimiento",
    "n_productos",
    "tiempo_armado",
    "n_cambios_ultimo_minuto",
    "error_detectado",
    "se_rehizo",
    "causa",
    "observaciones",
]

TIPOS = ("despacho", "retiro")
SI_NO = ("si", "no")
CAUSAS = (
    "sku_mal_digitado",
    "cambio_ultimo_minuto",
    "producto_sin_stock",
    "cantidad_incorrecta",
    "datos_del_cliente",
    "otro",
)
MAX_PRODUCTOS = 60          # maximo de productos por guia en el ERP
MAX_MINUTOS = 240           # una guia que demora mas de 4 horas es casi seguro un error de anotacion
MINIMO_MEDICIONES = 5       # lo que pide el protocolo

_FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_CORREO = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")
_TELEFONO = re.compile(r"(?<!\d)\+?\d[\d\s().-]{7,}\d(?!\d)")


def parsear_tiempo(texto):
    """'12:30' -> 12.5 minutos; '1:02:10' -> horas, minutos y segundos; '12,5' o '12.5' -> minutos decimales."""
    t = (texto or "").strip().replace(",", ".")
    if not t:
        raise ValueError("falta el tiempo")
    if ":" in t:
        partes = t.split(":")
        if len(partes) not in (2, 3) or not all(p.isdigit() for p in partes):
            raise ValueError(f"tiempo '{texto}': usa mm:ss, por ejemplo 12:30")
        numeros = [int(p) for p in partes]
        if len(numeros) == 2:
            minutos, segundos = numeros
            horas = 0
        else:
            horas, minutos, segundos = numeros
        if segundos >= 60 or (len(numeros) == 3 and minutos >= 60):
            raise ValueError(f"tiempo '{texto}': los segundos y minutos van de 00 a 59")
        total = horas * 60 + minutos + segundos / 60
    else:
        try:
            total = float(t)
        except ValueError:
            raise ValueError(f"tiempo '{texto}': usa mm:ss (12:30) o minutos (12.5)") from None
    if total <= 0:
        raise ValueError(f"tiempo '{texto}': debe ser mayor que cero")
    if total > MAX_MINUTOS:
        raise ValueError(f"tiempo '{texto}': mas de {MAX_MINUTOS} minutos, revisa si es un error")
    return total


def formatear_tiempo(minutos):
    """12.5 -> '12:30'"""
    segundos = round(minutos * 60)
    return f"{segundos // 60}:{segundos % 60:02d}"


def _entero(texto, nombre, minimo, maximo=None):
    t = (texto or "").strip()
    if not t.isdigit():
        raise ValueError(f"{nombre} '{texto}': debe ser un numero entero")
    n = int(t)
    if n < minimo or (maximo is not None and n > maximo):
        rango = f"entre {minimo} y {maximo}" if maximo is not None else f"al menos {minimo}"
        raise ValueError(f"{nombre} {n}: debe ser {rango}")
    return n


def validar_fila(fila):
    """Devuelve (fila_limpia, [errores]). No lanza excepciones por datos malos."""
    errores = []
    limpia = {}

    # Solo en las columnas de texto libre: las demas (fecha, numeros, si/no, listas) se validan con formatos estrictos
    for campo in ("id_medicion", "causa", "observaciones"):
        valor = fila.get(campo) or ""
        if _CORREO.search(valor) or _TELEFONO.search(valor):
            errores.append(f"'{campo}' parece llevar un correo o un telefono; las mediciones no llevan datos personales")

    def tomar(nombre, funcion):
        try:
            limpia[nombre] = funcion()
        except ValueError as e:
            errores.append(str(e))

    ident = (fila.get("id_medicion") or "").strip()
    if not ident:
        errores.append("falta id_medicion (por ejemplo M01)")
    limpia["id_medicion"] = ident

    fecha = (fila.get("fecha") or "").strip()
    if not _FECHA.match(fecha):
        errores.append(f"fecha '{fecha}': usa AAAA-MM-DD")
    limpia["fecha"] = fecha

    tipo = (fila.get("tipo_movimiento") or "").strip().lower()
    if tipo not in TIPOS:
        errores.append(f"tipo_movimiento '{tipo}': debe ser despacho o retiro")
    limpia["tipo_movimiento"] = tipo

    tomar("n_productos", lambda: _entero(fila.get("n_productos"), "n_productos", 1, MAX_PRODUCTOS))
    tomar("minutos", lambda: parsear_tiempo(fila.get("tiempo_armado")))
    tomar("n_cambios_ultimo_minuto", lambda: _entero(fila.get("n_cambios_ultimo_minuto"), "n_cambios_ultimo_minuto", 0))

    for nombre in ("error_detectado", "se_rehizo"):
        v = (fila.get(nombre) or "").strip().lower()
        if v not in SI_NO:
            errores.append(f"{nombre} '{v}': debe ser si o no")
        limpia[nombre] = v

    causa = (fila.get("causa") or "").strip().lower()
    hubo_problema = limpia["error_detectado"] == "si" or limpia["se_rehizo"] == "si"
    if hubo_problema and not causa:
        errores.append("hubo un error o se rehizo la guia: falta la causa")
    elif causa and not hubo_problema:
        errores.append("hay una causa pero la guia no tuvo errores ni se rehizo: borra la causa o corrige las columnas si/no")
    elif causa and causa not in CAUSAS:
        errores.append(f"causa '{causa}': debe ser una de {', '.join(CAUSAS)}")
    limpia["causa"] = causa

    limpia["observaciones"] = (fila.get("observaciones") or "").strip()
    return limpia, errores


def leer_csv(ruta):
    """Lee el CSV. Devuelve (filas, errores); cada error indica la linea del archivo (la 1 es el encabezado)."""
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        lector = csv.DictReader(f)
        encabezado = [c.strip() for c in (lector.fieldnames or [])]
        faltan = [c for c in COLUMNAS if c not in encabezado]
        sobran = [c for c in encabezado if c not in COLUMNAS]
        if faltan or sobran:
            partes = []
            if faltan:
                partes.append("faltan columnas: " + ", ".join(faltan))
            if sobran:
                partes.append("columnas desconocidas: " + ", ".join(sobran))
            return [], ["encabezado: " + "; ".join(partes)]
        filas, errores, vistos = [], [], set()
        for numero, cruda in enumerate(lector, start=2):
            fila = {(k or "").strip(): (v or "") for k, v in cruda.items() if k is not None}
            if not any(v.strip() for v in fila.values()):
                continue                                  # linea vacia
            limpia, errs = validar_fila(fila)
            if limpia["id_medicion"] in vistos:
                errs.append(f"id_medicion {limpia['id_medicion']} repetido")
            vistos.add(limpia["id_medicion"])
            for e in errs:
                errores.append(f"linea {numero}: {e}")
            if not errs:
                filas.append(limpia)
    return filas, errores


def _porcentaje(parte, total):
    return round(100 * parte / total, 1) if total else 0.0


def calcular(filas):
    """Metricas de la linea base. Falla con ValueError si no hay filas."""
    if not filas:
        raise ValueError("no hay mediciones")
    n = len(filas)
    tiempos = [f["minutos"] for f in filas]
    segundos_por_producto = [f["minutos"] * 60 / f["n_productos"] for f in filas]
    sin_problemas = [f for f in filas if f["error_detectado"] == "no" and f["se_rehizo"] == "no"]
    rehechas = [f for f in filas if f["se_rehizo"] == "si"]
    con_error = [f for f in filas if f["error_detectado"] == "si"]
    con_cambios = [f for f in filas if f["n_cambios_ultimo_minuto"] > 0]
    causas = Counter(f["causa"] for f in filas if f["causa"])
    ordenadas = sorted(causas.items(), key=lambda par: (-par[1], par[0]))
    return {
        "n": n,
        "alcanza_el_minimo": n >= MINIMO_MEDICIONES,
        "mediana_minutos": statistics.median(tiempos),
        "minimo_minutos": min(tiempos),
        "maximo_minutos": max(tiempos),
        "mediana_productos": statistics.median(f["n_productos"] for f in filas),
        "mediana_segundos_por_producto": statistics.median(segundos_por_producto),
        "n_rehechas": len(rehechas),
        "pct_rehechas": _porcentaje(len(rehechas), n),
        "n_con_error": len(con_error),
        "pct_con_error": _porcentaje(len(con_error), n),
        "n_sin_errores_ni_reprocesos": len(sin_problemas),
        "pct_sin_errores_ni_reprocesos": _porcentaje(len(sin_problemas), n),
        "cambios_total": sum(f["n_cambios_ultimo_minuto"] for f in filas),
        "cambios_promedio_por_guia": round(sum(f["n_cambios_ultimo_minuto"] for f in filas) / n, 2),
        "pct_guias_con_cambios": _porcentaje(len(con_cambios), n),
        "causas": ordenadas,
    }


def formatear(r, markdown=False):
    causas = ", ".join(f"{c} ({k})" for c, k in r["causas"]) or "ninguna"
    aviso = ""
    if not r["alcanza_el_minimo"]:
        aviso = f"ATENCION: hay {r['n']} mediciones y el protocolo pide al menos {MINIMO_MEDICIONES}. No uses estos numeros como linea base todavia."
    if markdown:
        filas = [
            ("Guías medidas", str(r["n"])),
            ("Tiempo por guía (mediana)", f"{formatear_tiempo(r['mediana_minutos'])} min"),
            ("Tiempo por guía (mínimo y máximo)", f"{formatear_tiempo(r['minimo_minutos'])} y {formatear_tiempo(r['maximo_minutos'])} min"),
            ("Productos por guía (mediana)", f"{r['mediana_productos']:g}"),
            ("Segundos por producto (mediana)", f"{r['mediana_segundos_por_producto']:.0f}"),
            ("Guías rehechas", f"{r['pct_rehechas']}% ({r['n_rehechas']} de {r['n']})"),
            ("Guías emitidas sin errores ni reprocesos", f"{r['pct_sin_errores_ni_reprocesos']}% ({r['n_sin_errores_ni_reprocesos']} de {r['n']})"),
            ("Cambios de último minuto por guía (promedio)", f"{r['cambios_promedio_por_guia']:g}"),
            ("Guías con al menos un cambio de último minuto", f"{r['pct_guias_con_cambios']}%"),
            ("Causas más frecuentes", causas),
        ]
        texto = "| Indicador | Antes (a mano) |\n|---|---|\n" + "\n".join(f"| {a} | {b} |" for a, b in filas)
        return (aviso + "\n\n" if aviso else "") + texto
    lineas = [
        f"Guias medidas:                              {r['n']}",
        f"Tiempo por guia, mediana:                   {formatear_tiempo(r['mediana_minutos'])} min",
        f"Tiempo por guia, minimo y maximo:           {formatear_tiempo(r['minimo_minutos'])} y {formatear_tiempo(r['maximo_minutos'])} min",
        f"Productos por guia, mediana:                {r['mediana_productos']:g}",
        f"Segundos por producto, mediana:             {r['mediana_segundos_por_producto']:.0f}",
        f"Guias rehechas:                             {r['pct_rehechas']}% ({r['n_rehechas']} de {r['n']})",
        f"Guias con algun error detectado:            {r['pct_con_error']}% ({r['n_con_error']} de {r['n']})",
        f"Guias sin errores ni reprocesos:            {r['pct_sin_errores_ni_reprocesos']}% ({r['n_sin_errores_ni_reprocesos']} de {r['n']})",
        f"Cambios de ultimo minuto, promedio por guia: {r['cambios_promedio_por_guia']:g} (total {r['cambios_total']})",
        f"Guias con al menos un cambio:               {r['pct_guias_con_cambios']}%",
        f"Causas mas frecuentes:                      {causas}",
    ]
    return (aviso + "\n" if aviso else "") + "\n".join(lineas)


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    markdown = "--md" in argv
    rutas = [a for a in argv if not a.startswith("--")]
    if len(rutas) != 1:
        print(__doc__)
        return 2
    ruta = Path(rutas[0])
    if not ruta.exists():
        print(f"No existe el archivo {ruta}")
        return 2
    filas, errores = leer_csv(ruta)
    if errores:
        print("El archivo tiene problemas; corrígelos y vuelve a ejecutar:")
        for e in errores:
            print("  -", e)
        return 1
    if not filas:
        print("El archivo no tiene mediciones todavia.")
        return 1
    print(formatear(calcular(filas), markdown=markdown))
    return 0


if __name__ == "__main__":
    sys.exit(main())
