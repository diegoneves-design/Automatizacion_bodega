"""
Piezas compartidas por las pruebas que pueden correr contra PostgreSQL (opcionales: solo si hay DATABASE_URL_TEST).

Proteccion: DATABASE_URL_TEST debe apuntar a una base cuyo nombre termina en _test, porque la preparacion BORRA y
recrea el esquema public. Estas pruebas nunca leen DATABASE_URL (la de verdad).
"""

import os
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
SQL = RAIZ / "supabase"
# Orden de ejecucion de docs/mvp-supabase.md sobre una base nueva (funciones.sql va antes de seed_poc.sql)
ORDEN_SQL = ["schema.sql", "acceso.sql", "funciones.sql", "seed_poc.sql", "inventario.sql", "dashboard.sql",
             "mvp_folio.sql", "funciones.sql", "mvp_funciones.sql", "mvp_vistas.sql", "mvp_rol.sql"]


@pytest.fixture(autouse=True)
def _nunca_la_base_de_verdad(monkeypatch):
    """Ninguna prueba lee el .env real ni usa DATABASE_URL: las que quieren PostgreSQL lo piden con DATABASE_URL_TEST."""
    monkeypatch.setenv("BODEGA_NO_CARGAR_ENV", "1")
    monkeypatch.delenv("DATABASE_URL", raising=False)


def url_de_prueba():
    """DATABASE_URL_TEST, o salta la prueba si no esta o no apunta a una base *_test."""
    url = os.getenv("DATABASE_URL_TEST", "").strip()
    if not url:
        pytest.skip("Sin DATABASE_URL_TEST: la prueba contra PostgreSQL es opcional.")
    psycopg = pytest.importorskip("psycopg")
    nombre = psycopg.conninfo.conninfo_to_dict(url).get("dbname") or ""
    if not nombre.endswith("_test"):
        pytest.skip("DATABASE_URL_TEST debe apuntar a una base cuyo nombre termina en _test (la prueba borra el esquema public).")
    return url


def como_rol_mvp(url):
    """La misma URL, pero conectando con los permisos del rol limitado app_mvp (SET ROLE al abrir la sesion)."""
    return url + ("&" if "?" in url else "?") + "options=-c%20role%3Dapp_mvp"


@pytest.fixture(scope="session")
def base_postgres():
    """Deja una base de PRUEBA nueva con todos los SQL de supabase/ aplicados, una sola vez por ejecucion."""
    url = url_de_prueba()
    import psycopg

    with psycopg.connect(url, autocommit=True) as c:
        c.execute("drop schema if exists public cascade")
        c.execute("create schema public")
        for rol in ("anon", "authenticated"):  # los que Supabase ya trae
            c.execute(f"do $$ begin if not exists (select 1 from pg_roles where rolname = '{rol}') then create role {rol} nologin; end if; end $$")
        c.execute("grant usage on schema public to anon, authenticated")
        for archivo in ORDEN_SQL:
            c.execute((SQL / archivo).read_text(encoding="utf-8"))
    return url


def reiniciar_datos(url):
    """Estado inicial limpio: sin las ordenes que dejo la prueba anterior y con la demo reiniciada (como superusuario)."""
    import psycopg

    with psycopg.connect(url, autocommit=True) as admin:
        admin.execute("truncate table guias, registro_cambios, detalle_orden, ordenes")
        admin.execute("select public.reiniciar_demo()")
