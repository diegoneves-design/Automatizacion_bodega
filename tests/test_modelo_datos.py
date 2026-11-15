"""El modelo de datos de supabase/schema.sql y sus datos de ejemplo cuentan una sola historia.

Se prueba con SQLite (viene con Python) porque el esquema es compatible con PostgreSQL.
"""

import sqlite3
from pathlib import Path

import pytest

SQL = Path(__file__).resolve().parent.parent / "supabase"


@pytest.fixture
def con():
    c = sqlite3.connect(":memory:")
    c.execute("PRAGMA foreign_keys = ON")
    c.executescript((SQL / "schema.sql").read_text(encoding="utf-8"))
    yield c
    c.close()


@pytest.fixture
def con_datos(con):
    con.executescript((SQL / "seed_ejemplo.sql").read_text(encoding="utf-8"))
    return con


def test_los_datos_de_ejemplo_no_tienen_claves_externas_rotas(con_datos):
    assert con_datos.execute("PRAGMA foreign_key_check").fetchall() == []


def test_las_ordenes_del_ejemplo_existen_para_guias_y_cambios(con_datos):
    ordenes = {f[0] for f in con_datos.execute("select id_orden from ordenes")}
    assert {f[0] for f in con_datos.execute("select id_orden from guias")} <= ordenes
    assert {f[0] for f in con_datos.execute("select id_orden from registro_cambios")} <= ordenes


def test_un_equipo_despachado_no_queda_disponible_en_bodega(con_datos):
    # la guia 70 despacho el 501: debe estar arrendado en el cliente
    fila = con_datos.execute("select estado, ubicacion from equipos where id_equipo = 501").fetchone()
    assert fila == ("arrendado", "cliente")


def test_cada_cambio_ocurre_antes_de_la_guia_de_su_orden(con_datos):
    filas = con_datos.execute(
        "select c.fecha_hora_cambio, g.fecha_emision from registro_cambios c join guias g on g.id_orden = c.id_orden"
    ).fetchall()
    assert filas and all(cambio < guia for cambio, guia in filas)


def test_la_orden_bloqueada_tiene_un_sku_que_no_existe_y_no_tiene_guia(con_datos):
    malos = con_datos.execute(
        "select count(*) from detalle_orden where id_orden = 3002 and resultado_validacion = 'no_existe' and vigente"
    ).fetchone()[0]
    assert malos == 1
    assert con_datos.execute("select count(*) from guias where id_orden = 3002").fetchone()[0] == 0


def test_el_motivo_del_cambio_es_obligatorio(con_datos):
    for motivo in (None, "", "   "):
        with pytest.raises(sqlite3.IntegrityError):
            con_datos.execute(
                "insert into registro_cambios values (9, 3002, 504, 507, 1, '2026-10-05 12:00:00', ?)", (motivo,)
            )


def test_la_modalidad_solo_aplica_al_despacho(con_datos):
    ins = "insert into ordenes values (4000, 10, 1, '2026-10-06 08:00:00', ?, ?, ?, 'pendiente')"
    con_datos.execute(ins, ("despacho", "alternativo", None))
    for tipo, modalidad, motivo in [
        ("retiro", "convencional", "falla"),    # un retiro no tiene modalidad
        ("despacho", None, None),               # un despacho exige modalidad
        ("despacho", "convencional", "falla"),  # un despacho no tiene motivo de retiro
    ]:
        with pytest.raises(sqlite3.IntegrityError):
            con_datos.execute(ins.replace("4000", "4010"), (tipo, modalidad, motivo))


def test_el_motivo_del_retiro_solo_aplica_al_retiro(con_datos):
    ins = "insert into ordenes values (4001, 10, 1, '2026-10-06 08:00:00', ?, ?, ?, 'pendiente')"
    con_datos.execute(ins, ("retiro", None, "mantencion_preventiva"))
    with pytest.raises(sqlite3.IntegrityError):
        con_datos.execute(ins.replace("4001", "4002"), ("retiro", None, None))  # un retiro exige motivo


def test_estado_y_ubicacion_del_equipo_deben_coincidir(con):
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("insert into equipos values (1, 'X-1', 'prueba', 'disponible', 'cliente')")


def test_una_clave_externa_rota_se_rechaza(con_datos):
    with pytest.raises(sqlite3.IntegrityError):
        con_datos.execute("insert into guias values (72, 9999, 1, 15232, '2026-10-05 12:00:00', null)")


def test_un_sku_que_no_existe_no_lleva_equipo(con_datos):
    with pytest.raises(sqlite3.IntegrityError):
        con_datos.execute("insert into detalle_orden values (9100, 3002, 504, 'SD-63A20-9999', 'no_existe', true)")


def test_los_rut_de_ejemplo_son_los_decididos_por_el_equipo():
    """Las empresas de ejemplo usan 11.111.111-1 y 22.222.222-2, no RUT que podrian ser de empresas reales."""
    anteriores = ("76.123.456" + "-7", "77.987.654" + "-3")   # escritos por partes para que este archivo no los contenga
    raiz = SQL.parent
    for ruta in (SQL / "seed_ejemplo.sql", raiz / "docs" / "datos" / "estructura_datos.md"):
        texto = ruta.read_text(encoding="utf-8")
        assert "11.111.111-1" in texto and "22.222.222-2" in texto, ruta.name
        assert not any(a in texto for a in anteriores), f"{ruta.name} conserva un RUT anterior"


def test_la_semilla_carga_con_los_rut_nuevos(con_datos):
    ruts = [f[0] for f in con_datos.execute("select rut from clientes order by id_cliente")]
    assert ruts == ["11.111.111-1", "22.222.222-2"]
