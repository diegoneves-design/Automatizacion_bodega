"""Revisiones estaticas de los scripts de Supabase y de la configuracion del prototipo.

No sustituyen probar los scripts en Supabase (PostgreSQL): solo atrapan olvidos que no necesitan una base,
como una tabla sin RLS, una funcion sin permiso o una clave subida al repositorio.
"""

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SQL = RAIZ / "supabase"


def leer(nombre):
    return (SQL / nombre).read_text(encoding="utf-8")


def tablas():
    return re.findall(r"create table (\w+)", leer("schema.sql"))


def test_hay_siete_tablas():
    assert sorted(tablas()) == sorted(
        ["clientes", "usuarios", "equipos", "ordenes", "detalle_orden", "guias", "registro_cambios"]
    )


def test_cada_tabla_tiene_rls_y_una_politica_de_lectura():
    acceso = leer("acceso.sql")
    for t in tablas():
        assert f"alter table public.{t}" in acceso and "enable row level security" in acceso, t
        assert re.search(rf'create policy "[^"]+" on public\.{t}\s+for select', acceso), f"{t} sin politica"


def test_ninguna_politica_permite_escribir_directo_en_las_tablas():
    acceso = leer("acceso.sql")
    assert not re.search(r"for\s+(insert|update|delete|all)", acceso, re.I)
    assert not re.search(r"grant\s+(insert|update|delete|all)", acceso, re.I)


def test_usuarios_no_expone_correo_ni_telefono():
    acceso = leer("acceso.sql")
    columnas = re.search(r"grant select \(([^)]*)\) on public\.usuarios", acceso).group(1)
    assert "correo" not in columnas and "telefono" not in columnas


def test_clientes_no_expone_rut_ni_direccion():
    acceso = leer("acceso.sql")
    columnas = re.search(r"grant select \(([^)]*)\) on public\.clientes", acceso).group(1)
    assert "rut" not in columnas and "direccion" not in columnas and "razon_social" in columnas
    # y no hay un permiso de tabla completa que los vuelva a abrir
    for g in re.findall(r"grant select on ([^;]*?) to", acceso, re.S):
        assert "clientes" not in g, g


def test_cada_funcion_de_la_pagina_tiene_su_permiso():
    funciones = leer("funciones.sql")
    nombres = [n for n in re.findall(r"create or replace function public\.(\w+)", funciones) if not n.startswith("_")]
    assert sorted(nombres) == sorted(
        ["cargar_pedido", "validar_pedido", "registrar_cambio", "preparar_guia", "reiniciar_demo"]
    )
    for n in nombres:
        assert re.search(rf"grant execute on function public\.{n}\(", funciones), n
    # la ayuda interna no se expone
    assert not re.search(r"grant execute on function public\._(fallo|limpiar|skus_limpios)", funciones)
    assert "revoke all on function public._limpiar" in funciones
    assert "revoke all on function public._skus_limpios" in funciones


def test_las_funciones_fijan_search_path_y_corren_como_el_dueno():
    funciones = leer("funciones.sql")
    publicas = re.split(r"create or replace function ", funciones)[1:]
    for cuerpo in publicas:
        assert "set search_path = public" in cuerpo.split("as $$")[0]
    assert len(re.findall(r"^security definer$", funciones, re.M)) == 5


def test_la_regla_del_motivo_obligatorio_esta_en_la_funcion_y_en_la_tabla():
    assert "Elige el motivo del cambio." in leer("funciones.sql")
    assert "length(trim(motivo_cambio)) > 0" in leer("schema.sql")


def test_el_limite_de_la_base_y_el_del_prototipo_coinciden():
    en_sql = int(re.search(r"c_max constant integer := (\d+)", leer("funciones.sql")).group(1))
    en_js = int(re.search(r"MAX_SKUS:\s*(\d+)", (RAIZ / "prototipo" / "js" / "reglas.js").read_text(encoding="utf-8")).group(1))
    assert en_sql == en_js == 60


def test_env_example_no_trae_valores():
    ejemplo = (RAIZ / ".env.example").read_text(encoding="utf-8")
    assert re.search(r"^SUPABASE_URL=\s*$", ejemplo, re.M)
    assert re.search(r"^SUPABASE_PUBLISHABLE_KEY=\s*$", ejemplo, re.M)


def test_no_hay_claves_en_los_archivos_versionables():
    """config.js y .env son locales y estan ignorados; el resto no puede llevar claves."""
    patron = re.compile(r"sb_(publishable|secret)_[A-Za-z0-9_-]{16,}|eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}|service_role\s*[:=]\s*['\"]")
    ignorados = {"config.js", ".env"}
    revisar = [RAIZ / "prototipo", RAIZ / "supabase", RAIZ / "docs", RAIZ / "README.md", RAIZ / ".env.example"]
    for base in revisar:
        archivos = [base] if base.is_file() else [p for p in base.rglob("*") if p.is_file()]
        for p in archivos:
            if p.name in ignorados or "__pycache__" in p.parts or p.suffix.lower() in {".png", ".pdf", ".docx", ".jpg", ".pyc"}:
                continue
            assert not patron.search(p.read_text(encoding="utf-8", errors="ignore")), f"posible clave en {p}"


def test_config_js_esta_ignorado_por_git():
    gitignore = (RAIZ / ".gitignore").read_text(encoding="utf-8")
    assert "prototipo/js/config.js" in gitignore
    assert re.search(r"^\.env$", gitignore, re.M)


def _cuerpo_reiniciar_demo():
    funciones = leer("funciones.sql")
    cuerpo = funciones[funciones.index("function public.reiniciar_demo"):]
    return cuerpo[:cuerpo.index("$$;", cuerpo.index("as $$") + 5)]


def test_reiniciar_demo_no_borra_sin_where():
    """Supabase rechaza un DELETE sin WHERE desde la API (pg_safeupdate): todo borrado lleva su where."""
    borrados = re.findall(r"delete from [^;]*;", _cuerpo_reiniciar_demo())
    assert len(borrados) == 3 and all(" where " in b for b in borrados), borrados


def test_reiniciar_demo_solo_toca_las_ordenes_de_la_demo():
    """Lo que se crea desde el MVP no se pierde: se borra solo lo de 3001 y 3002, y nunca la tabla de ordenes entera."""
    cuerpo = _cuerpo_reiniciar_demo()
    assert not re.search(r"delete from ordenes|truncate", cuerpo, re.I)
    for b in re.findall(r"delete from [^;]*;", cuerpo):
        assert "where id_orden in (3001, 3002)" in b, b
    assert "'GUIA-2026-001'" in cuerpo and "'GUIA-2026-002'" in cuerpo


def test_el_texto_se_limpia_con_tabulaciones_y_saltos_de_linea():
    """btrim() solo quita espacios: el texto debe pasar por _limpiar en cargar_pedido y registrar_cambio."""
    funciones = leer("funciones.sql")
    assert "btrim(t.x)" not in funciones
    for usado in ("_limpiar(t.x)", "_limpiar(p_sku_sale)", "_limpiar(p_sku_entra)", "_limpiar(p_motivo)"):
        assert usado in funciones, usado
    # la lista de caracteres se escribe con secuencias de escape, no con caracteres invisibles
    assert all(ord(c) >= 32 or c in "\n\r" for c in funciones)
    assert "\xa0" not in funciones


# ---------------------------------------------------------------------------
# Archivos del MVP (mvp_*.sql): rol limitado, funcion nueva, vistas y folio
# ---------------------------------------------------------------------------

TABLAS_DEL_FLUJO = ["clientes", "usuarios", "equipos", "ordenes", "detalle_orden", "guias", "registro_cambios"]


def sin_comentarios(sql):
    return "\n".join(l for l in sql.splitlines() if not l.lstrip().startswith("--"))


def test_mvp_rol_no_trae_contrasena_ni_en_el_sql_ejecutable():
    rol = leer("mvp_rol.sql")
    ejecutable = sin_comentarios(rol)
    assert not re.search(r"password", ejecutable, re.I), "la contrasena la escribe quien ejecuta, no el archivo"
    assert "REEMPLAZA-ESTE-TEXTO" in rol  # solo el ejemplo, dentro de un comentario
    assert re.search(r"create role app_mvp login nosuperuser nocreatedb nocreaterole noinherit noreplication nobypassrls", ejecutable)


def test_mvp_rol_no_puede_escribir_directo_ni_reiniciar_la_demo():
    ejecutable = sin_comentarios(leer("mvp_rol.sql"))
    assert not re.search(r"grant\s+(insert|update|delete|truncate|references|trigger|all|create)", ejecutable, re.I)
    assert not re.search(r"grant\s+select[^;]*\bto\s+(anon|authenticated|public)", ejecutable, re.I)
    assert not re.search(r"reiniciar_demo\(\)\s+to", ejecutable, re.I)
    assert not re.search(r"for\s+(insert|update|delete|all)", ejecutable, re.I)
    ejecutables = re.findall(r"grant execute on function public\.(\w+)", ejecutable)
    assert sorted(ejecutables) == sorted(
        ["cargar_pedido", "validar_pedido", "registrar_cambio", "preparar_guia", "crear_pedido", "inventario_dashboard"]
    )


def test_mvp_rol_tiene_limites_y_politicas_para_las_tablas_que_lee():
    ejecutable = sin_comentarios(leer("mvp_rol.sql"))
    for limite in ("connection limit 5", "set statement_timeout", "set search_path = public"):
        assert limite in ejecutable, limite
    for t in TABLAS_DEL_FLUJO:
        assert re.search(rf'create policy "lectura app_mvp" on public\.{t}\s+for select to app_mvp', ejecutable), t


def test_mvp_rol_no_ve_correo_telefono_rut_ni_direccion():
    ejecutable = sin_comentarios(leer("mvp_rol.sql"))
    for tabla in ("usuarios", "clientes"):
        columnas = re.search(rf"grant select \(([^)]*)\)\s+on public\.{tabla}", ejecutable).group(1)
        for prohibida in ("correo", "telefono", "rut", "direccion"):
            assert prohibida not in columnas, (tabla, prohibida)


def test_crear_pedido_no_se_expone_a_la_api_publica():
    sql = leer("mvp_funciones.sql")
    assert "revoke all on function public.crear_pedido(text, integer, integer, text, text, text, text[]) from public, anon, authenticated" in sql
    assert not re.search(r"grant execute on function public\.crear_pedido[^;]*\b(anon|authenticated)", sql)
    cabecera = sql.split("as $$")[0]
    assert "security definer" in cabecera and "set search_path = public" in cabecera


def test_las_vistas_del_mvp_consultan_con_los_permisos_de_quien_las_lee_y_no_se_dan_a_la_api_publica():
    sql = leer("mvp_vistas.sql")
    vistas = re.findall(r"create or replace view public\.(\w+)", sql)
    assert sorted(vistas) == ["v_detalle_orden", "v_historial_cambios", "v_ordenes_resumen"]
    assert len(re.findall(r"with \(security_invoker = true\)", sql)) == 3
    assert re.search(r"revoke all on [^;]*v_ordenes_resumen[^;]*from public, anon, authenticated", sql)
    assert not re.search(r"grant\s", sin_comentarios(sql), re.I)


def test_el_folio_tiene_columna_unicidad_y_forma_en_el_esquema_y_en_la_migracion():
    assert re.search(r"^\s*folio\s+text\s+unique,", leer("schema.sql"), re.M)
    migracion = leer("mvp_folio.sql")
    assert "add column if not exists folio text" in migracion
    assert "GUIA-[0-9]{4}-[0-9]{3,6}" in migracion
    assert "'GUIA-2026-001'" in migracion and "'GUIA-2026-002'" in migracion


def test_el_limite_de_60_es_el_mismo_en_las_funciones_y_en_la_capa_de_datos():
    import sys

    sys.path.insert(0, str(RAIZ / "src"))
    import db

    en_funciones = re.findall(r"c_max constant integer := (\d+)", leer("funciones.sql") + leer("mvp_funciones.sql"))
    assert en_funciones == ["60", "60"] and db.MAX_SKUS == 60


def test_el_mvp_pide_psycopg_con_version_fija_y_solo_lo_importa_al_conectar():
    pedidos = (RAIZ / "requirements.txt").read_text(encoding="utf-8")
    assert re.search(r"^psycopg\[binary\]==\d+\.\d+\.\d+\s*$", pedidos, re.M)
    codigo = (RAIZ / "src" / "db.py").read_text(encoding="utf-8")
    assert not re.search(r"^(import psycopg|from psycopg)", codigo, re.M), "psycopg se importa dentro de las funciones, no al inicio"


def test_las_credenciales_de_la_base_nunca_van_al_repositorio():
    """Ninguna cadena de conexion con contrasena, y los archivos locales de secretos estan ignorados."""
    gitignore = (RAIZ / ".gitignore").read_text(encoding="utf-8")
    assert re.search(r"^\.streamlit/secrets\.toml$", gitignore, re.M) and re.search(r"^\.env$", gitignore, re.M)
    ejemplo = (RAIZ / ".env.example").read_text(encoding="utf-8")
    assert re.search(r"^DATABASE_URL=\s*$", ejemplo, re.M) and re.search(r"^DATABASE_URL_TEST=\s*$", ejemplo, re.M)
    # usuario:contrasena@servidor; los marcadores entre <...> o [...] de la documentacion no cuentan
    cadena = re.compile(r"postgres(?:ql)?://[^\s:@/<\[]+:[^\s@/<\[]+@")
    revisar = [RAIZ / "src", RAIZ / "supabase", RAIZ / "docs", RAIZ / "tests", RAIZ / ".github", RAIZ / "README.md", RAIZ / ".env.example", RAIZ / "Dockerfile"]
    for base in revisar:
        archivos = [base] if base.is_file() else [p for p in base.rglob("*") if p.is_file()]
        for p in archivos:
            if "__pycache__" in p.parts or p.suffix.lower() in {".png", ".pdf", ".docx", ".jpg", ".pyc"} or p.name == "test_supabase_scripts.py":
                continue
            assert not cadena.search(p.read_text(encoding="utf-8", errors="ignore")), f"cadena de conexion con contrasena en {p}"
