"""
Recorrido de la interfaz del MVP (Streamlit AppTest) sobre la base local SQLite: sin red y sin abrir un navegador.

Comprueba que las pantallas hablan con db.py: la lista de ordenes, el flujo cargar -> validar -> corregir -> emitir
guia, y que los mensajes de las reglas llegan tal cual a la pantalla. No reemplaza probarlo a mano en el navegador.
"""

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

pytest.importorskip("streamlit.testing.v1")
from streamlit.testing.v1 import AppTest  # noqa: E402
from conftest import como_rol_mvp, reiniciar_datos  # noqa: E402

APP = str(RAIZ / "src" / "app.py")


@pytest.fixture(params=["sqlite", "postgres"])
def at(request, tmp_path, monkeypatch):
    import streamlit as st

    if request.param == "postgres":  # opcional: solo con DATABASE_URL_TEST, y conectando con el rol limitado
        url = request.getfixturevalue("base_postgres")
        reiniciar_datos(url)
        monkeypatch.setenv("DATABASE_URL", como_rol_mvp(url))
    else:
        monkeypatch.delenv("DATABASE_URL", raising=False)  # las pruebas con SQLite nunca usan la base de verdad
        monkeypatch.setenv("BODEGA_MVP_DB", str(tmp_path / "mvp.db"))
    st.cache_resource.clear()
    app = AppTest.from_file(APP, default_timeout=30).run()
    assert not app.exception, app.exception
    app.modo_prueba = request.param
    yield app
    st.cache_resource.clear()


def textos(app):
    """Todo el texto visible (markdown y avisos) de la pantalla."""
    return " ".join(m.value for m in app.markdown)


def test_la_lista_muestra_las_dos_ordenes_de_la_demo_y_la_base_usada(at):
    texto = textos(at)
    assert "GUIA-2026-001" in texto and "GUIA-2026-002" in texto
    esperado = {"sqlite": "Base local de pruebas (SQLite)", "postgres": "Base: Supabase (PostgreSQL)"}
    assert [c.value for c in at.caption] == [esperado[at.modo_prueba]]
    assert at.selectbox(key="id_usuario").value == 1  # por omision, el jefe de bodega


def test_flujo_completo_valida_corrige_y_emite_la_guia(at):
    at.button(key="ver_GUIA-2026-002").click().run()
    assert at.session_state.vista == "detalle" and "SD-63A20-9999" in textos(at)

    at.button(key="validar_skus").click().run()
    assert at.session_state.vista == "validacion"
    assert "Validación con diferencias" in textos(at)
    assert at.button(key="validacion_emitir").disabled  # con un SKU que no existe no se puede emitir

    at.button(key="validacion_corregir").click().run()
    assert at.session_state.vista == "ajuste" and at.selectbox(key="aj_orig").value == "SD-63A20-9999"

    at.text_input(key="aj_buscar").set_value("0315").run()
    at.selectbox(key="aj_nuevo").select("SD-63A20-0315").run()
    at.selectbox(key="aj_resp").select(2).run()  # el cambio lo registra Camila, no quien opera
    at.button(key="aj_guardar").click().run()
    assert at.session_state.vista == "validacion" and "Cambio registrado" in textos(at)
    assert "aún no se valida" in textos(at)  # tras el cambio hay que volver a validar

    at.button(key="validacion_validar").click().run()
    assert "Validación completada" in textos(at)
    at.button(key="validacion_emitir").click().run()
    assert at.session_state.vista == "guia" and "15230" in textos(at)

    at.button(key="guia_historial").click().run()
    assert "Camila Rojas" in textos(at)  # el responsable del cambio sale en el historial (el menu muestra a Pedro Soto)


def test_el_ajuste_rechaza_con_el_mensaje_de_la_regla(at):
    at.button(key="ver_GUIA-2026-002").click().run()
    at.button(key="validar_skus").click().run()
    at.button(key="validacion_corregir").click().run()
    at.text_input(key="aj_buscar").set_value("ST-0042").run()
    at.selectbox(key="aj_nuevo").select("ST-0042").run()  # ya esta en el pedido
    at.button(key="aj_guardar").click().run()
    assert at.session_state.vista == "ajuste"
    assert "Ese equipo ya está en el pedido. Elige otro." in textos(at)


def test_solo_el_jefe_de_bodega_puede_emitir(at):
    at.button(key="ver_GUIA-2026-001").click().run()
    at.button(key="validar_skus").click().run()
    at.selectbox(key="id_usuario").select(2).run()  # Camila, de mantenimiento
    at.button(key="validacion_emitir").click().run()
    assert at.session_state.vista == "validacion"
    assert "Solo el jefe de bodega puede preparar la guía." in textos(at)


def test_carga_masiva_crea_la_orden_y_abre_su_detalle(at):
    at.button(key="menu_carga").click().run()
    at.text_input(key="cm_folio").set_value("GUIA-2026-050")
    at.selectbox(key="cm_cliente").select(10)
    at.text_area(key="cm_texto").set_value("st-0042\n ST-0042 \n\nmp-0107").run()
    assert "SKU detectados: 2" in textos(at)  # limpia y quita repetidos
    at.button(key="cm_cargar").click().run()
    assert at.session_state.vista == "detalle" and at.session_state.folio == "GUIA-2026-050"
    assert "Orden GUIA-2026-050 cargada con 2 SKU" in textos(at)


def test_carga_masiva_muestra_el_mensaje_de_la_regla_y_no_borra_lo_escrito(at):
    at.button(key="menu_carga").click().run()
    at.text_input(key="cm_folio").set_value("GUIA-2026-001")  # ya existe
    at.selectbox(key="cm_cliente").select(10)
    at.text_area(key="cm_texto").set_value("ST-0042").run()
    at.button(key="cm_cargar").click().run()
    assert at.session_state.vista == "carga"
    assert "Ya existe una orden con ese folio. Usa otro." in textos(at)
    assert at.text_area(key="cm_texto").value == "ST-0042"  # no se pierde lo que escribio la persona


def test_carga_masiva_sin_cliente_avisa(at):
    at.button(key="menu_carga").click().run()
    at.text_input(key="cm_folio").set_value("GUIA-2026-051")
    at.text_area(key="cm_texto").set_value("ST-0042").run()
    at.button(key="cm_cargar").click().run()
    assert "Elige el cliente." in textos(at)


def test_la_carga_no_pasa_de_60_sku(at):
    at.button(key="menu_carga").click().run()
    at.text_area(key="cm_texto").set_value("\n".join(f"X-{i}" for i in range(61))).run()
    assert "Se detectaron 61 SKU" in textos(at) and at.button(key="cm_cargar").disabled
