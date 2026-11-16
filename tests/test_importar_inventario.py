"""Pruebas del importador del inventario. Todas las filas son ficticias: el Excel real no se usa ni se versiona."""
import re
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "herramientas"))
import importar_inventario as imp  # noqa: E402

CATALOGO = {"AA": "AIRE DE PRUEBA", "BB": "VENTILACION", "CC": None}


def fila(sku, desc="Equipo de prueba", ubic="BODEGA"):
    return (sku, 1, desc, sku[:2], ubic)


# ---------- mapeo de ubicacion ----------
@pytest.mark.parametrize("entrada,esperado", [
    ("BODEGA", ("disponible", "bodega", "BODEGA")),
    ("  bodega  ", ("disponible", "bodega", "BODEGA")),
    ("BODEGA LOS ANGELES", ("disponible", "bodega", "BODEGA LOS ANGELES")),
    ("SHOWROOM", ("disponible", "bodega", "SHOWROOM")),
    ("REPARACIÓN", ("en_mantencion", "taller", "REPARACIÓN")),
    ("reparacion", ("en_mantencion", "taller", "REPARACIÓN")),
    ("BAJA", ("fuera_servicio", "bodega", "BAJA")),
    ("POR  HABILITAR", ("fuera_servicio", "bodega", "POR HABILITAR")),
    ("EN BUSCA", ("fuera_servicio", "bodega", "EN BUSCA")),
    ("FUERA DE NORMA", ("fuera_servicio", "bodega", "FUERA DE NORMA")),
    (4501, ("arrendado", "cliente", "CONTRATO")),
    (4501.0, ("arrendado", "cliente", "CONTRATO")),
    ("4501", ("arrendado", "cliente", "CONTRATO")),
    ("Cliente Ficticio Uno", ("arrendado", "cliente", "CLIENTE")),
])
def test_mapeo_de_ubicacion(entrada, esperado):
    assert imp.mapear_ubicacion(entrada)[:3] == esperado


def test_un_texto_ajeno_no_se_guarda_en_ninguna_parte():
    estado, lugar, situacion, regla = imp.mapear_ubicacion("Nombre Ficticio de Persona")
    assert "Nombre" not in f"{estado}{lugar}{situacion}{regla}"
    assert situacion == "CLIENTE" and regla == "otro_texto"


@pytest.mark.parametrize("vacio", [None, "", "   "])
def test_una_ubicacion_vacia_aborta(vacio):
    with pytest.raises(ValueError):
        imp.mapear_ubicacion(vacio)


def test_toda_salida_del_mapeo_cumple_las_restricciones_de_la_tabla():
    permitido = {("disponible", "bodega"), ("arrendado", "cliente"), ("en_mantencion", "taller"), ("fuera_servicio", "bodega")}
    for v in ("BODEGA", "SHOWROOM", "REPARACION", "BAJA", "POR HABILITAR", "EN BUSCA", "FUERA DE NORMA", 7, "x"):
        estado, lugar, situacion, _ = imp.mapear_ubicacion(v)
        assert (estado, lugar) in permitido
        assert situacion in imp.SITUACIONES


# ---------- capacidad ----------
@pytest.mark.parametrize("texto,esperado", [
    ("Equipo X modelo Z1 14.000 BTU/H bomba", (14000, "BTU/H")),
    ("Equipo X 120 MBTUH modelo Q", (120000, "BTU/H")),
    ("Equipo X 9000 BTU", (9000, "BTU/H")),
    ("Equipo X modelo Q 4 TR", (4, "TR")),
    ("Equipo X modelo Q 7.5 TR", (7.5, "TR")),
    ("Equipo X modelo Q 18.000 M3/H", (18000, "m3/h")),
    ("Equipo X modelo Q 8.000 m³/h", (8000, "m3/h")),
    ("Equipo X; CAUDAL 8.000 M3/H", (8000, "m3/h")),
    ("Equipo X potencia 15 KW", (15, "kW")),
    ("Equipo X 33 m(3,3 kW)", (3.3, "kW")),
])
def test_extraccion_de_capacidad(texto, esperado):
    assert imp.extraer_capacidad(texto) == esperado


@pytest.mark.parametrize("texto", ["Tablero electrico", "Manga perforada 20 m", "Equipo con 15 A y 220 V", "", None])
def test_sin_capacidad_devuelve_nulos(texto):
    assert imp.extraer_capacidad(texto) == (None, None)


# ---------- extensiones ----------
@pytest.mark.parametrize("valor,esperado", [(20, 20), ("20", 20), ("07", 7), (" 15 ", 15), (10.0, 10), ("abc", None), ("", None), (None, None), (7.5, None), (-3, None)])
def test_largo_de_extensiones(valor, esperado):
    assert imp.convertir_largo(valor) == esperado


def test_formato_estandar_de_sku_de_extension():
    assert imp.sku_extension_estandar("SD-63A20-00314")
    assert not imp.sku_extension_estandar("SD-CC400V20-00241")
    assert not imp.sku_extension_estandar("SD-125A20-00241")


def test_preparar_extensiones_cuenta_lo_no_estandar():
    filas = [("SD-63A20-00001", 1, "63a", 20), ("SD-CC400V20-00002", 2, "400A", "x"), ("SD-32A10-00003", 3, "32A", "07")]
    ext, ag = imp.preparar_extensiones(filas)
    assert ag["extensiones_en_total"] == 3
    assert ag["extensiones_con_sku_de_formato_no_estandar"] == 1
    assert ag["extensiones_con_largo_no_numerico"] == 1
    assert [e["largo_m"] for e in ext] == [None, 7, 20] or sorted(e["largo_m"] or 0 for e in ext) == [0, 7, 20]
    assert {e["corriente"] for e in ext} == {"63A", "400A", "32A"}


# ---------- equipos ----------
def test_preparar_equipos_ids_desde_1000_y_categorias():
    filas = [fila("AA-X-00002", "Equipo 12.000 BTU/H", "BODEGA"), fila("BB-X-00001", "Ventilador 18.000 M3/H", 123), fila("CC-X-00003", "Otro", "BAJA"),
             fila("ZZ-X-00004", "Sin catalogo", "EN BUSCA")]
    equipos, ag = imp.preparar_equipos(filas, CATALOGO)
    assert [e["id_equipo"] for e in equipos] == [1000, 1001, 1002, 1003]      # ordenados por SKU
    por_sku = {e["sku"]: e for e in equipos}
    assert por_sku["BB-X-00001"]["categoria"] == "VENTILACIÓN"             # se normaliza la tilde
    assert por_sku["CC-X-00003"]["categoria"] == "SIN CATEGORÍA"           # catalogo sin categoria
    assert por_sku["ZZ-X-00004"]["categoria"] == "SIN CATEGORÍA"           # prefijo sin catalogo
    assert por_sku["AA-X-00002"]["categoria"] == "AIRE DE PRUEBA"
    assert ag["prefijos_sin_catalogo"] == {"ZZ": 1}
    assert ag["equipos_sin_categoria"] == 2
    assert ag["equipos_sin_capacidad_extraida"] == 2
    assert ag["filas_por_estado"] == {"arrendado": 1, "disponible": 1, "fuera_servicio": 2}


def test_sku_repetido_aborta():
    with pytest.raises(ValueError, match="repetidos"):
        imp.preparar_equipos([fila("AA-X-00001"), fila("AA-X-00001")], CATALOGO)


def test_sku_de_la_demo_aborta_con_mensaje_claro():
    with pytest.raises(ValueError, match="demo"):
        imp.preparar_equipos([fila("ST-0042")], CATALOGO)


def test_los_sku_de_demo_son_los_de_seed_poc():
    seed = (RAIZ / "supabase" / "seed_poc.sql").read_text(encoding="utf-8")
    en_seed = set(re.findall(r"\(50\d, '([^']+)'", seed))
    assert en_seed == set(imp.SKU_DEMO)


def test_el_reporte_no_trae_skus_ni_descripciones_ni_ubicaciones():
    filas = [fila("AA-SECRETO-00001", "Descripcion Secreta", "Persona Ficticia Reservada"), fila("AA-SECRETO-00002", "Otra", "BODEGA")]
    _, ag1 = imp.preparar_equipos(filas, CATALOGO)
    _, ag2 = imp.preparar_extensiones([("SD-63A20-00009", 1, "63A", 20)])
    texto = str({**ag1, **ag2})
    for prohibido in ("SECRETO", "Secreta", "Persona", "Reservada", "SD-63A20"):
        assert prohibido not in texto


# ---------- archivos generados ----------
def test_los_trozos_no_pasan_de_300_filas_y_el_sql_escapa_comillas(tmp_path):
    filas = [fila(f"AA-X-{i:05d}", "Equipo d'prueba", "BODEGA") for i in range(650)]
    ext = [("SD-63A20-%05d" % i, i, "63A", 20) for i in range(319)]
    reporte = imp.generar(filas, ext, CATALOGO, tmp_path)
    trozos = sorted(tmp_path.glob("carga_inventario_*.sql"))
    assert [t.name for t in trozos] == ["carga_inventario_01.sql", "carga_inventario_02.sql", "carga_inventario_03.sql"]
    cuentas = [len(re.findall(r"^  \(\d+, 'AA-", t.read_text(encoding="utf-8"), re.M)) for t in trozos]
    assert cuentas == [300, 300, 50]
    assert "d''prueba" in trozos[0].read_text(encoding="utf-8")
    assert "on conflict (sku) do update" in trozos[0].read_text(encoding="utf-8")
    assert (tmp_path / "carga_extensiones.sql").read_text(encoding="utf-8").count("insert into") == 2   # 300 + 19
    assert reporte["equipos_en_total"] == 650 and reporte["extensiones_en_total"] == 319


def test_una_segunda_corrida_no_deja_trozos_viejos(tmp_path):
    imp.generar([fila(f"AA-X-{i:05d}") for i in range(400)], [("SD-63A20-00001", 1, "63A", 20)], CATALOGO, tmp_path)
    imp.generar([fila(f"AA-X-{i:05d}") for i in range(10)], [("SD-63A20-00001", 1, "63A", 20)], CATALOGO, tmp_path)
    assert [t.name for t in tmp_path.glob("carga_inventario_*.sql")] == ["carga_inventario_01.sql"]


def test_el_importador_no_tiene_rutas_fijas_ni_conexiones():
    codigo = (RAIZ / "herramientas" / "importar_inventario.py").read_text(encoding="utf-8")
    assert not re.search(r"[A-Za-z]:\\\\Users|OneDrive|supabase\.co|requests|urllib|socket|psycopg", codigo)


def test_sin_argumentos_el_importador_falla_con_ayuda():
    r = subprocess.run([sys.executable, "-I", str(RAIZ / "herramientas" / "importar_inventario.py")], capture_output=True, text=True)
    assert r.returncode != 0


# ---------- SQL y proteccion de datos ----------
def test_gitignore_cubre_el_excel_y_datos_locales():
    g = (RAIZ / ".gitignore").read_text(encoding="utf-8")
    assert re.search(r"^\*\.xlsx$", g, re.M) and re.search(r"^datos_locales/$", g, re.M)


def test_seed_poc_se_detiene_si_hay_inventario_real():
    seed = (RAIZ / "supabase" / "seed_poc.sql").read_text(encoding="utf-8")
    assert "id_equipo >= 1000" in seed
    assert seed.index("id_equipo >= 1000") < seed.index("truncate table")


def test_reiniciar_demo_no_toca_equipos_reales():
    f = (RAIZ / "supabase" / "funciones.sql").read_text(encoding="utf-8")
    cuerpo = f[f.index("function public.reiniciar_demo"):]
    cuerpo = cuerpo[:cuerpo.index("$$;", cuerpo.index("as $$") + 5)]
    assert not re.search(r"delete from (public\.)?equipos|truncate", cuerpo, re.I)
    assert "on conflict (id_equipo) do update" in cuerpo
    ids = [int(x) for x in re.findall(r"^\s*\((\d{3,4}), '", cuerpo, re.M) if int(x) < 3000]
    assert ids and all(501 <= i <= 507 for i in ids)


def test_inventario_sql_es_idempotente_y_cierra_el_acceso():
    s = (RAIZ / "supabase" / "inventario.sql").read_text(encoding="utf-8")
    assert s.count("add column if not exists") == 5
    assert "create table if not exists public.extensiones_electricas" in s
    assert "enable row level security" in s and "grant select on public.extensiones_electricas" in s
    assert not re.search(r"grant (insert|update|delete|all)", s, re.I)
    assert not re.search(r"\bdrop table|\btruncate|delete from", s, re.I)
