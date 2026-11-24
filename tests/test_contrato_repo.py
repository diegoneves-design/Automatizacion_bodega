"""
Pruebas de contrato de la capa de datos (src/db.py): las MISMAS pruebas contra las dos implementaciones.

  sqlite     siempre. Sin red y sin dependencias nuevas.
  postgres   solo si hay DATABASE_URL_TEST. Aplica los SQL de supabase/ a una base DE PRUEBA vacia y conecta con el
             rol limitado app_mvp, asi que tambien prueban sus permisos, las politicas y las vistas. En el CI corre
             contra un servicio de PostgreSQL; en tu computador puedes apuntarla a un PostgreSQL local.

Proteccion: DATABASE_URL_TEST debe apuntar a una base cuyo nombre termina en _test, porque la prueba BORRA y recrea
el esquema public. Nunca lee DATABASE_URL (la de verdad).
"""

import os
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import db  # noqa: E402
from conftest import reiniciar_datos, url_de_prueba  # noqa: E402

JEFE, MANTENIMIENTO = 1, 2
CLIENTE = 10
SKUS_OK = ["SD-63A20-0314", "SD-63A20-0315", "ST-0042"]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(params=["sqlite", "postgres"])
def repo(request):
    if request.param == "sqlite":
        r = db.RepoSqlite(":memory:")
        yield r
        return
    url = request.getfixturevalue("base_postgres")
    import psycopg
    from psycopg.rows import dict_row

    reiniciar_datos(url)
    # la aplicacion se conecta con el rol limitado: aqui, el mismo rol sobre la misma conexion
    r = db.RepoPostgres(lambda: psycopg.connect(url, autocommit=True, row_factory=dict_row, options="-c role=app_mvp"))
    yield r
    r.cerrar()


def pedido(repo, folio="GUIA-2026-003", skus=None, tipo="Despacho", modalidad="Convencional", cliente=CLIENTE, usuario=JEFE):
    return repo.crear_pedido(folio, cliente, usuario, tipo, modalidad, SKUS_OK if skus is None else skus)


def rechazo(llamada):
    with pytest.raises(db.ReglaDeNegocio) as e:
        llamada()
    return e.value.mensaje, e.value.campo


# ---------------------------------------------------------------------------
# Lecturas
# ---------------------------------------------------------------------------

def test_las_dos_ordenes_de_la_demo_tienen_folio(repo):
    df = repo.ordenes()
    assert list(df.columns) == db.COLUMNAS_ORDENES
    assert sorted(df["folio"]) == ["GUIA-2026-001", "GUIA-2026-002"]
    fila = {f.folio: f for f in df.itertuples()}
    assert (fila["GUIA-2026-001"].tipo_movimiento, fila["GUIA-2026-001"].modalidad) == ("Despacho", "Convencional")
    assert (fila["GUIA-2026-002"].tipo_movimiento, fila["GUIA-2026-002"].modalidad) == ("Retiro", "Por falla")
    assert set(df["skus_vigentes"]) == {4}
    assert set(df["estado"]) == {"pendiente"}


def test_clientes_y_usuarios_sin_datos_personales(repo):
    assert [c["id_cliente"] for c in repo.clientes()] == [10, 11]
    assert set(repo.clientes()[0]) == {"id_cliente", "razon_social"}
    usuarios = repo.usuarios()
    assert [u["id_usuario"] for u in usuarios] == [1, 2]
    assert set(usuarios[0]) == {"id_usuario", "nombre", "rol"}


def test_lineas_de_una_orden_nueva_estan_sin_validar(repo):
    df = repo.lineas("GUIA-2026-001")
    assert list(df.columns) == db.COLUMNAS_LINEAS
    assert list(df["sku"]) == ["SD-63A20-0314", "SD-63A20-0315", "ST-0042", "MP-0107"]
    assert set(df["resultado"]) == {"pendiente"}


def test_buscar_equipos_por_sku_y_por_descripcion(repo):
    assert list(repo.buscar_equipos("st-004")["sku"]) == ["ST-0042"]
    assert list(repo.buscar_equipos("manga")["sku"]) == ["MP-0107"]
    assert len(repo.buscar_equipos("Extensión", limite=3)) == 3


def test_buscar_equipos_trata_los_comodines_como_texto(repo):
    assert repo.buscar_equipos("%").empty
    assert repo.buscar_equipos("_").empty


def test_una_orden_que_no_existe_se_rechaza_con_su_mensaje(repo):
    esperado = ("Esa orden no existe. Elige otra.", "orden")
    assert rechazo(lambda: repo.validar("GUIA-2026-999")) == esperado
    assert rechazo(lambda: repo.registrar_cambio("GUIA-2026-999", "A", "B", JEFE, "x")) == esperado
    assert rechazo(lambda: repo.preparar_guia("GUIA-2026-999", JEFE)) == esperado


# ---------------------------------------------------------------------------
# crear_pedido
# ---------------------------------------------------------------------------

def test_crear_pedido_deja_la_orden_pendiente_con_sus_lineas_limpias(repo):
    folio = repo.crear_pedido("guia-2026-003", CLIENTE, JEFE, "Despacho", "Alternativo", [" sd-63a20-0314 ", "ST-0042", "", "sd-63a20-0314", "\t"])
    assert folio == "GUIA-2026-003"
    o = repo.orden("GUIA-2026-003")
    assert (o["tipo_movimiento"], o["modalidad"], o["estado"], o["skus_vigentes"]) == ("Despacho", "Alternativo", "pendiente", 2)
    assert list(repo.lineas("GUIA-2026-003")["sku"]) == ["SD-63A20-0314", "ST-0042"]


def test_crear_pedido_de_retiro_guarda_el_motivo(repo):
    pedido(repo, "GUIA-2026-004", tipo="Retiro", modalidad="Preventivo")
    o = repo.orden("GUIA-2026-004")
    assert (o["tipo_movimiento"], o["modalidad"]) == ("Retiro", "Preventivo")


def test_crear_pedido_acepta_60_y_rechaza_61(repo):
    assert pedido(repo, "GUIA-2026-005", skus=[f"X-{i}" for i in range(60)])
    assert rechazo(lambda: pedido(repo, "GUIA-2026-006", skus=[f"X-{i}" for i in range(61)])) == (
        "Hay 61 productos y el máximo es 60. Quita 1 para continuar.", "skus")
    assert repo.orden("GUIA-2026-006") is None  # el rechazo no dejo nada


REGLAS_CREAR = [
    ({"folio": "GUIA-1"}, "El folio debe tener la forma GUIA-2026-001.", "folio"),
    ({"folio": "   "}, "El folio debe tener la forma GUIA-2026-001.", "folio"),
    ({"folio": "FACTURA-2026-001"}, "El folio debe tener la forma GUIA-2026-001.", "folio"),
    ({"folio": "GUIA-2026-" + "0" * 7}, "El folio debe tener la forma GUIA-2026-001.", "folio"),  # 7 cifras, una de mas: armado al ejecutar para no parecer telefono
    ({"folio": "GUIA-2026-001"}, "Ya existe una orden con ese folio. Usa otro.", "folio"),
    ({"folio": " guia-2026-002 "}, "Ya existe una orden con ese folio. Usa otro.", "folio"),
    ({"cliente": 99}, "Elige el cliente.", "cliente"),
    ({"cliente": None}, "Elige el cliente.", "cliente"),
    ({"usuario": 99}, "Elige quién carga el pedido.", "usuario"),
    ({"usuario": None}, "Elige quién carga el pedido.", "usuario"),
    ({"skus": []}, "Pega al menos un SKU, uno por línea. Ejemplo: SD-63A20-0314", "skus"),
    ({"skus": ["  ", "", "\t", "\r\n"]}, "Pega al menos un SKU, uno por línea. Ejemplo: SD-63A20-0314", "skus"),
    ({"tipo": "Otro"}, "Elige el tipo de movimiento.", "tipo"),
    ({"tipo": None}, "Elige el tipo de movimiento.", "tipo"),
    ({"modalidad": None}, "Elige la modalidad del despacho.", "modalidad"),
    ({"modalidad": "Por falla"}, "Elige la modalidad del despacho.", "modalidad"),
    ({"tipo": "Retiro", "modalidad": None}, "Elige el motivo del retiro.", "motivo_retiro"),
    ({"tipo": "Retiro", "modalidad": "Convencional"}, "Elige el motivo del retiro.", "motivo_retiro"),
]


@pytest.mark.parametrize("cambios, mensaje, campo", REGLAS_CREAR)
def test_crear_pedido_rechaza_con_el_mensaje_exacto(repo, cambios, mensaje, campo):
    argumentos = {"folio": "GUIA-2026-003", "skus": None, "tipo": "Despacho", "modalidad": "Convencional", "cliente": CLIENTE, "usuario": JEFE}
    argumentos.update(cambios)
    antes = len(repo.ordenes())
    assert rechazo(lambda: pedido(repo, **argumentos)) == (mensaje, campo)
    assert len(repo.ordenes()) == antes  # un rechazo no deja nada a medias


def test_dos_pedidos_seguidos_no_comparten_numero_de_orden_ni_de_linea(repo):
    pedido(repo, "GUIA-2026-010")
    pedido(repo, "GUIA-2026-011")
    df = repo.ordenes()
    assert len(df) == 4 and df["folio"].is_unique
    ids = list(repo.lineas("GUIA-2026-010")["id"]) + list(repo.lineas("GUIA-2026-011")["id"])
    assert len(set(ids)) == len(ids) == 6


# ---------------------------------------------------------------------------
# validar
# ---------------------------------------------------------------------------

def test_validar_marca_ok_no_existe_y_no_disponible(repo):
    repo.validar("GUIA-2026-001")
    assert set(repo.lineas("GUIA-2026-001")["resultado"]) == {"ok"}
    assert repo.orden("GUIA-2026-001")["estado"] == "validada"

    repo.validar("GUIA-2026-002")
    resultados = dict(zip(repo.lineas("GUIA-2026-002")["sku"], repo.lineas("GUIA-2026-002")["resultado"]))
    assert resultados["SD-63A20-9999"] == "no_existe"
    assert sum(1 for r in resultados.values() if r == "ok") == 3
    assert repo.orden("GUIA-2026-002")["estado"] == "bloqueada"

    pedido(repo, "GUIA-2026-003", skus=["SD-63A20-0316"])  # el 503 esta en mantencion
    repo.validar("GUIA-2026-003")
    fila = repo.lineas("GUIA-2026-003").iloc[0]
    assert (fila["resultado"], fila["estado_equipo"]) == ("no_disponible", "en_mantencion")


# ---------------------------------------------------------------------------
# registrar_cambio
# ---------------------------------------------------------------------------

CAMBIO = dict(sku_sale="SD-63A20-9999", sku_entra="SD-63A20-0315", id_usuario=MANTENIMIENTO, motivo="Código mal digitado")

REGLAS_CAMBIO = [
    ({"sku_sale": ""}, "Elige el equipo que sale.", "sale"),
    ({"sku_sale": "SD-63A20-0316"}, "Ese equipo no está en el pedido. Elige otro.", "sale"),
    ({"sku_entra": ""}, "Elige el equipo que entra.", "entra"),
    ({"sku_entra": "SD-63A20-9999"}, "El equipo que entra debe ser distinto del que sale.", "entra"),
    ({"sku_entra": "SD-00000-0000"}, "Ese SKU no existe en el inventario. Elige uno de la lista.", "entra"),
    ({"sku_entra": "ST-0042"}, "Ese equipo ya está en el pedido. Elige otro.", "entra"),
    ({"motivo": ""}, "Elige el motivo del cambio.", "motivo"),
    ({"motivo": "   "}, "Elige el motivo del cambio.", "motivo"),
    ({"motivo": None}, "Elige el motivo del cambio.", "motivo"),
    ({"motivo": "\t\t"}, "Elige el motivo del cambio.", "motivo"),
    ({"motivo": "x" * 201}, "El motivo es muy largo: máximo 200 caracteres.", "motivo"),
    ({"id_usuario": 99}, "Elige quién registra el cambio.", "responsable"),
    ({"id_usuario": None}, "Elige quién registra el cambio.", "responsable"),
]


@pytest.mark.parametrize("cambios, mensaje, campo", REGLAS_CAMBIO)
def test_registrar_cambio_rechaza_con_el_mensaje_exacto(repo, cambios, mensaje, campo):
    argumentos = dict(CAMBIO, **cambios)
    assert rechazo(lambda: repo.registrar_cambio("GUIA-2026-002", **argumentos)) == (mensaje, campo)
    assert repo.cambios().empty  # los rechazos no dejan registro
    assert "SD-63A20-9999" in set(repo.lineas("GUIA-2026-002")["sku"])


def test_registrar_cambio_acepta_un_motivo_de_200_caracteres(repo):
    repo.registrar_cambio("GUIA-2026-002", **dict(CAMBIO, motivo="x" * 200))
    assert len(repo.cambios("GUIA-2026-002")) == 1


def test_un_cambio_reemplaza_la_linea_y_deja_el_registro(repo):
    repo.validar("GUIA-2026-002")
    repo.registrar_cambio("GUIA-2026-002", **CAMBIO)

    skus = list(repo.lineas("GUIA-2026-002")["sku"])
    assert "SD-63A20-9999" not in skus and "SD-63A20-0315" in skus and len(skus) == 4  # la vieja ya no cuenta, pero no se borra
    assert repo.orden("GUIA-2026-002")["estado"] == "pendiente"  # hay que volver a validar
    nueva = repo.lineas("GUIA-2026-002").set_index("sku").loc["SD-63A20-0315"]
    assert nueva["resultado"] == "pendiente" and nueva["ultima_modificacion"] is not None

    log = repo.cambios("GUIA-2026-002")
    assert list(log.columns) == db.COLUMNAS_CAMBIOS
    fila = log.iloc[0]
    assert (fila["folio"], fila["sku_original"], fila["sku_nuevo"], fila["responsable"], fila["motivo"]) == (
        "GUIA-2026-002", "SD-63A20-9999", "SD-63A20-0315", "Camila Rojas", "Código mal digitado")
    assert repo.cambios("GUIA-2026-001").empty
    assert len(repo.cambios()) == 1


def test_el_historial_va_del_mas_reciente_al_mas_antiguo(repo):
    repo.registrar_cambio("GUIA-2026-002", **CAMBIO)
    repo.registrar_cambio("GUIA-2026-002", "SD-63A20-0315", "SD-63A20-0314", JEFE, "Segundo cambio")
    assert list(repo.cambios()["motivo"]) == ["Segundo cambio", "Código mal digitado"]


# ---------------------------------------------------------------------------
# preparar_guia
# ---------------------------------------------------------------------------

def test_no_se_prepara_la_guia_sin_validar_ni_con_otro_usuario_ni_con_productos_malos(repo):
    assert rechazo(lambda: repo.preparar_guia("GUIA-2026-001", JEFE)) == ("Valida el pedido antes de preparar la guía.", "productos")
    assert rechazo(lambda: repo.preparar_guia("GUIA-2026-001", MANTENIMIENTO)) == ("Solo el jefe de bodega puede preparar la guía.", "usuario")
    assert rechazo(lambda: repo.preparar_guia("GUIA-2026-001", 99)) == ("Solo el jefe de bodega puede preparar la guía.", "usuario")
    repo.validar("GUIA-2026-002")
    assert rechazo(lambda: repo.preparar_guia("GUIA-2026-002", JEFE)) == ("Corrige 1 producto para continuar.", "productos")
    assert repo.guia("GUIA-2026-001") is None and repo.guia("GUIA-2026-002") is None


def test_el_camino_completo_corrige_valida_y_emite_la_guia(repo):
    repo.validar("GUIA-2026-002")
    repo.registrar_cambio("GUIA-2026-002", **CAMBIO)
    assert rechazo(lambda: repo.preparar_guia("GUIA-2026-002", JEFE)) == ("Valida el pedido antes de preparar la guía.", "productos")
    repo.validar("GUIA-2026-002")
    assert repo.orden("GUIA-2026-002")["estado"] == "validada"

    guia = repo.preparar_guia("GUIA-2026-002", JEFE)
    assert guia["numero_guia"] == 15230 and guia["fecha_emision"] is not None
    assert repo.guia("GUIA-2026-002")["numero_guia"] == 15230
    assert repo.orden("GUIA-2026-002")["estado"] == "emitida"

    repo.validar("GUIA-2026-001")
    assert repo.preparar_guia("GUIA-2026-001", JEFE)["numero_guia"] == 15231  # consecutiva


def test_una_orden_con_guia_ya_no_admite_cambios(repo):
    repo.validar("GUIA-2026-001")
    repo.preparar_guia("GUIA-2026-001", JEFE)
    ya_tiene = ("Esta orden ya tiene la guía preparada. Presiona Reiniciar demo para volver a empezar.", "orden")
    assert rechazo(lambda: repo.preparar_guia("GUIA-2026-001", JEFE)) == ya_tiene
    assert rechazo(lambda: repo.validar("GUIA-2026-001")) == ya_tiene
    assert rechazo(lambda: repo.registrar_cambio("GUIA-2026-001", "ST-0042", "SD-63A20-0316", JEFE, "x")) == ya_tiene


def test_la_fecha_de_la_guia_es_de_hoy(repo):
    from datetime import datetime

    repo.validar("GUIA-2026-001")
    fecha = repo.preparar_guia("GUIA-2026-001", JEFE)["fecha_emision"]
    assert abs((datetime.now() - fecha).total_seconds()) < 24 * 3600


# ---------------------------------------------------------------------------
# Solo PostgreSQL: el rol limitado y el reinicio de la demo
# ---------------------------------------------------------------------------

def _solo_postgres(repo):
    if repo.modo != "postgres":
        pytest.skip("Solo aplica a PostgreSQL.")


def test_el_rol_del_mvp_no_puede_escribir_directo_ni_leer_datos_personales_ni_reiniciar(repo):
    _solo_postgres(repo)
    import psycopg

    repo.ordenes()  # abre la conexion del rol
    con = repo._con
    columna = {"clientes": "razon_social", "usuarios": "nombre", "equipos": "descripcion", "ordenes": "estado",
               "detalle_orden": "vigente", "guias": "numero_guia", "registro_cambios": "motivo_cambio",
               "extensiones_electricas": "corriente"}
    prohibidas = [
        "select correo from public.usuarios", "select telefono from public.usuarios", "select * from public.usuarios",
        "select rut from public.clientes", "select direccion from public.clientes", "select * from public.clientes",
        "select public.reiniciar_demo()",
        "create table public.x (a int)",
    ]
    for t, c in columna.items():  # ninguna tabla admite escritura directa
        prohibidas += [f"insert into public.{t} default values", f"update public.{t} set {c} = {c} where true",
                       f"delete from public.{t} where true", f"truncate public.{t}"]
    for sql in prohibidas:
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            con.execute(sql)


def test_el_rol_del_mvp_puede_leer_el_dashboard_y_solo_eso_de_datos_agregados(repo):
    _solo_postgres(repo)

    repo.ordenes()  # abre la conexion del rol
    datos = repo._con.execute("select public.inventario_dashboard() as d").fetchone()["d"]
    assert set(datos) == {"equipos", "extensiones", "actividad"}
    assert datos["equipos"]["columnas"] == ["id_equipo", "sku", "descripcion", "familia", "categoria", "estado",
                                            "situacion_origen", "capacidad_valor", "capacidad_unidad"]
    assert "correo" not in str(datos) and "telefono" not in str(datos)


def test_la_clave_publicable_no_lee_datos_personales_de_clientes_ni_usuarios(repo):
    _solo_postgres(repo)
    import psycopg

    with psycopg.connect(url_de_prueba(), autocommit=True, options="-c role=anon") as c:
        assert len(c.execute("select id_cliente, razon_social from public.clientes").fetchall()) == 2  # lo que usa el prototipo
        for sql in ("select rut from public.clientes", "select direccion from public.clientes", "select * from public.clientes",
                    "select correo from public.usuarios", "select telefono from public.usuarios"):
            with pytest.raises(psycopg.errors.InsufficientPrivilege):
                c.execute(sql)


def test_las_funciones_nuevas_no_estan_abiertas_a_la_api_publica(repo):
    _solo_postgres(repo)
    import psycopg

    for rol in ("anon", "authenticated"):
        with psycopg.connect(url_de_prueba(), autocommit=True, options=f"-c role={rol}") as c:
            for sql in ("select public.crear_pedido('GUIA-2026-099', 10, 1, 'despacho', 'convencional', null, array['A'])",
                        "select * from public.v_ordenes_resumen", "select * from public.v_detalle_orden", "select * from public.v_historial_cambios"):
                with pytest.raises(psycopg.errors.InsufficientPrivilege):
                    c.execute(sql)


def test_reiniciar_la_demo_no_borra_lo_que_se_creo_desde_el_mvp(repo):
    _solo_postgres(repo)
    import psycopg

    pedido(repo, "GUIA-2026-020", skus=["ST-0042", "MP-0107"])
    repo.validar("GUIA-2026-020")
    repo.preparar_guia("GUIA-2026-020", JEFE)
    repo.registrar_cambio("GUIA-2026-002", **CAMBIO)

    with psycopg.connect(url_de_prueba(), autocommit=True, options="-c role=anon") as c:
        c.execute("select public.reiniciar_demo()")  # como lo hace el prototipo, con la clave publica

    assert repo.guia("GUIA-2026-020")["numero_guia"] == 15230  # la orden y su guia siguen
    assert repo.orden("GUIA-2026-020")["estado"] == "emitida"
    assert repo.cambios().empty  # los cambios de la demo si se limpian
    assert set(repo.lineas("GUIA-2026-002")["resultado"]) == {"pendiente"} and "SD-63A20-9999" in set(repo.lineas("GUIA-2026-002")["sku"])
    assert repo.orden("GUIA-2026-002")["estado"] == "pendiente"
    assert sorted(repo.ordenes()["folio"]) == ["GUIA-2026-001", "GUIA-2026-002", "GUIA-2026-020"]


def test_reiniciar_la_demo_no_pisa_los_ids_de_las_lineas_de_otras_ordenes(repo):
    _solo_postgres(repo)
    import psycopg

    pedido(repo, "GUIA-2026-021", skus=["ST-0042", "MP-0107", "SD-63A20-0314"])
    antes = list(repo.lineas("GUIA-2026-021")["id"])
    with psycopg.connect(url_de_prueba(), autocommit=True, options="-c role=anon") as c:
        c.execute("select public.reiniciar_demo()")
        c.execute("select public.reiniciar_demo()")  # dos veces seguidas
    assert list(repo.lineas("GUIA-2026-021")["id"]) == antes
    todas = [r[0] for r in psycopg.connect(url_de_prueba(), autocommit=True).execute("select id_detalle from public.detalle_orden").fetchall()]
    assert len(todas) == len(set(todas)) == 11


# ---------------------------------------------------------------------------
# .env local y eleccion de la base
# ---------------------------------------------------------------------------

def test_cargar_env_lee_el_archivo_sin_pisar_lo_que_ya_esta_definido(tmp_path, monkeypatch):
    archivo = tmp_path / ".env"
    archivo.write_text(
        "# comentario\nNUEVA_UNO=valor1\nNUEVA_DOS = \"con comillas\" \nYA_DEFINIDA=del_archivo\nVACIA=\nsin_igual\n  \nNUEVA_TRES='simples'\n",
        encoding="utf-8",
    )
    for k in ("NUEVA_UNO", "NUEVA_DOS", "NUEVA_TRES", "VACIA"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("YA_DEFINIDA", "del_hosting")
    monkeypatch.delenv("BODEGA_NO_CARGAR_ENV")
    db.cargar_env(archivo)
    assert os.environ["NUEVA_UNO"] == "valor1" and os.environ["NUEVA_DOS"] == "con comillas" and os.environ["NUEVA_TRES"] == "simples"
    assert os.environ["YA_DEFINIDA"] == "del_hosting"  # el hosting manda
    assert "VACIA" not in os.environ  # un valor vacio no cuenta
    for k in ("NUEVA_UNO", "NUEVA_DOS", "NUEVA_TRES"):
        monkeypatch.delenv(k, raising=False)


def test_cargar_env_se_puede_apagar_y_no_falla_sin_archivo(tmp_path, monkeypatch):
    archivo = tmp_path / ".env"
    archivo.write_text("SOLO_SI_NO_SE_APAGA=1\n", encoding="utf-8")
    monkeypatch.delenv("SOLO_SI_NO_SE_APAGA", raising=False)
    db.cargar_env(archivo)  # BODEGA_NO_CARGAR_ENV=1 lo pone el conftest en todas las pruebas
    assert "SOLO_SI_NO_SE_APAGA" not in os.environ
    monkeypatch.delenv("BODEGA_NO_CARGAR_ENV")
    db.cargar_env(tmp_path / "no_existe.env")  # sin archivo no pasa nada


def test_abrir_elige_postgres_solo_si_hay_database_url(tmp_path, monkeypatch):
    monkeypatch.setenv("BODEGA_MVP_DB", str(tmp_path / "local.db"))
    assert db.abrir().modo == "sqlite"
    # armada al ejecutar: escrita de corrido, el buscador de correos del repositorio la tomaria por un correo
    monkeypatch.setenv("DATABASE_URL", "postgresql://" + "usuario" + "@" + "servidor.invalido" + ":5432/base")
    r = db.abrir()
    assert r.modo == "postgres" and "servidor" not in repr(r)  # y nunca muestra la cadena


def test_un_servidor_inalcanzable_da_un_mensaje_claro_sin_detalles_de_la_conexion(monkeypatch):
    pytest.importorskip("psycopg")
    # la contrasena falsa se arma al ejecutar: ningun archivo del repositorio lleva una cadena con contrasena
    monkeypatch.setenv("DATABASE_URL", "postgresql://" + "alguien" + ":" + "secreto123" + "@127.0.0.1:1/base?connect_timeout=2")
    r = db.abrir()
    with pytest.raises(db.ErrorDeBase) as e:
        r.ordenes()
    assert "secreto123" not in str(e.value) and "127.0.0.1" not in str(e.value)
    assert "No se pudo conectar" in str(e.value)
