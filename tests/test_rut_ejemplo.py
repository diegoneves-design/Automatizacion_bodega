"""Los RUT de las empresas de ejemplo son marcadores y no pueden coincidir con los de empresas reales."""

import sqlite3
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SQL = RAIZ / "supabase"


def test_los_rut_de_ejemplo_son_los_decididos_por_el_equipo():
    """Las empresas de ejemplo usan 11.111.111-1 y 22.222.222-2, no RUT que podrian ser de empresas reales."""
    anteriores = ("76.123.456" + "-7", "77.987.654" + "-3")   # escritos por partes para que este archivo no los contenga
    for ruta in (SQL / "seed_ejemplo.sql", RAIZ / "docs" / "datos" / "estructura_datos.md"):
        texto = ruta.read_text(encoding="utf-8")
        assert "11.111.111-1" in texto and "22.222.222-2" in texto, ruta.name
        assert not any(a in texto for a in anteriores), f"{ruta.name} conserva un RUT anterior"


def test_la_semilla_de_ejemplo_carga_con_los_rut_nuevos():
    con = sqlite3.connect(":memory:")
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript((SQL / "schema.sql").read_text(encoding="utf-8"))
    con.executescript((SQL / "seed_ejemplo.sql").read_text(encoding="utf-8"))
    ruts = [f[0] for f in con.execute("select rut from clientes order by id_cliente")]
    con.close()
    assert ruts == ["11.111.111-1", "22.222.222-2"]
