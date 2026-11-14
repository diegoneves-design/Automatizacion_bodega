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


def test_cada_funcion_de_la_pagina_tiene_su_permiso():
    funciones = leer("funciones.sql")
    nombres = [n for n in re.findall(r"create or replace function public\.(\w+)", funciones) if not n.startswith("_")]
    assert sorted(nombres) == sorted(
        ["cargar_pedido", "validar_pedido", "registrar_cambio", "preparar_guia", "reiniciar_demo"]
    )
    for n in nombres:
        assert re.search(rf"grant execute on function public\.{n}\(", funciones), n
    # la ayuda interna no se expone
    assert not re.search(r"grant execute on function public\._(fallo|limpiar)", funciones)
    assert "revoke all on function public._limpiar" in funciones


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
            if p.name in ignorados or p.suffix.lower() in {".png", ".pdf", ".docx", ".jpg"}:
                continue
            assert not patron.search(p.read_text(encoding="utf-8", errors="ignore")), f"posible clave en {p}"


def test_config_js_esta_ignorado_por_git():
    gitignore = (RAIZ / ".gitignore").read_text(encoding="utf-8")
    assert "prototipo/js/config.js" in gitignore
    assert re.search(r"^\.env$", gitignore, re.M)


def test_reiniciar_demo_no_borra_sin_where():
    """Supabase rechaza un DELETE sin WHERE desde la API (pg_safeupdate): hay que escribir where true."""
    funciones = leer("funciones.sql")
    cuerpo = funciones[funciones.index("function public.reiniciar_demo"):]
    cuerpo = cuerpo[:cuerpo.index("$$;", cuerpo.index("as $$") + 5)]
    borrados = re.findall(r"delete from [^;]*;", cuerpo)
    assert len(borrados) == 4 and all(" where " in b for b in borrados), borrados


def test_el_texto_se_limpia_con_tabulaciones_y_saltos_de_linea():
    """btrim() solo quita espacios: el texto debe pasar por _limpiar en cargar_pedido y registrar_cambio."""
    funciones = leer("funciones.sql")
    assert "btrim(t.x)" not in funciones
    for usado in ("_limpiar(t.x)", "_limpiar(p_sku_sale)", "_limpiar(p_sku_entra)", "_limpiar(p_motivo)"):
        assert usado in funciones, usado
    # la lista de caracteres se escribe con secuencias de escape, no con caracteres invisibles
    assert all(ord(c) >= 32 or c in "\n\r" for c in funciones)
    assert "\xa0" not in funciones
