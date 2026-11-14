"""Pruebas de herramientas/calcular_linea_base.py con mediciones ficticias (los resultados esperados se calcularon a mano)."""

import csv
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "herramientas"))

import calcular_linea_base as lb  # noqa: E402

ENCABEZADO = ",".join(lb.COLUMNAS)

# 6 guias ficticias. Tiempos: 10, 15, 6.5, 12, 4 y 25 minutos.
FILAS = [
    "M01,2026-11-16,despacho,20,10:00,0,no,no,,",
    "M02,2026-11-16,despacho,50,15:00,2,si,si,cambio_ultimo_minuto,cambio de comercial",
    "M03,2026-11-17,retiro,8,06:30,0,no,no,,",
    "M04,2026-11-17,despacho,35,12:00,1,si,no,sku_mal_digitado,",
    "M05,2026-11-18,retiro,4,04:00,0,no,no,,",
    "M06,2026-11-18,despacho,60,25:00,3,si,si,cambio_ultimo_minuto,",
]


def escribir(tmp_path, filas, encabezado=ENCABEZADO):
    ruta = tmp_path / "mediciones.csv"
    ruta.write_text("\n".join([encabezado] + filas) + "\n", encoding="utf-8")
    return ruta


# ---------------------------------------------------------------- plantillas

def test_la_plantilla_de_la_linea_base_solo_tiene_el_encabezado():
    texto = (RAIZ / "docs" / "plantillas" / "linea_base_registro.csv").read_text(encoding="utf-8")
    assert texto.strip() == ENCABEZADO


def test_la_planilla_de_registro_de_la_prueba_solo_tiene_el_encabezado():
    texto = (RAIZ / "docs" / "kit-prueba" / "planilla_registro.csv").read_text(encoding="utf-8")
    assert texto.strip() == "participante,tarea,minuto,observado,interpretado,severidad"


def test_la_plantilla_vacia_se_rechaza_con_un_mensaje_claro(tmp_path, capsys):
    ruta = escribir(tmp_path, [])
    assert lb.main([str(ruta)]) == 1
    assert "no tiene mediciones" in capsys.readouterr().out


# ---------------------------------------------------------------- tiempo

@pytest.mark.parametrize("texto, esperado", [
    ("12:30", 12.5), ("00:30", 0.5), ("12.5", 12.5), ("12,5", 12.5), ("7", 7.0), ("1:02:30", 62.5),
])
def test_parsear_tiempo_acepta_mm_ss_y_decimales(texto, esperado):
    assert lb.parsear_tiempo(texto) == pytest.approx(esperado)


@pytest.mark.parametrize("texto", ["", "abc", "12:75", "0", "0:00", "-3", "300", "12:30:75", "1:2:3:4", "12:ab"])
def test_parsear_tiempo_rechaza_lo_que_no_sirve(texto):
    with pytest.raises(ValueError):
        lb.parsear_tiempo(texto)


def test_formatear_tiempo():
    assert lb.formatear_tiempo(12.5) == "12:30"
    assert lb.formatear_tiempo(4.0) == "4:00"
    assert lb.formatear_tiempo(11.0) == "11:00"


# ---------------------------------------------------------------- calculo

def test_las_metricas_coinciden_con_el_calculo_a_mano(tmp_path):
    filas, errores = lb.leer_csv(escribir(tmp_path, FILAS))
    assert errores == [] and len(filas) == 6
    r = lb.calcular(filas)
    assert r["n"] == 6 and r["alcanza_el_minimo"]
    assert r["mediana_minutos"] == pytest.approx(11.0)           # (10 + 12) / 2
    assert r["minimo_minutos"] == 4.0 and r["maximo_minutos"] == 25.0
    assert r["mediana_productos"] == 27.5                         # (20 + 35) / 2
    assert r["mediana_segundos_por_producto"] == pytest.approx(27.5)
    assert (r["n_rehechas"], r["pct_rehechas"]) == (2, 33.3)
    assert (r["n_con_error"], r["pct_con_error"]) == (3, 50.0)
    assert (r["n_sin_errores_ni_reprocesos"], r["pct_sin_errores_ni_reprocesos"]) == (3, 50.0)
    assert r["cambios_total"] == 6 and r["cambios_promedio_por_guia"] == 1.0
    assert r["pct_guias_con_cambios"] == 50.0
    assert r["causas"] == [("cambio_ultimo_minuto", 2), ("sku_mal_digitado", 1)]


def test_el_indicador_exige_que_no_haya_ni_error_ni_reproceso(tmp_path):
    # M04 tuvo un error corregido sin rehacer la guia: no cuenta como "sin errores ni reprocesos"
    filas, _ = lb.leer_csv(escribir(tmp_path, FILAS))
    sin = [f["id_medicion"] for f in filas if f["error_detectado"] == "no" and f["se_rehizo"] == "no"]
    assert sin == ["M01", "M03", "M05"]


def test_los_empates_de_causas_se_ordenan_alfabeticamente(tmp_path):
    filas = [
        "M01,2026-11-16,despacho,10,05:00,0,si,no,sku_mal_digitado,",
        "M02,2026-11-16,despacho,10,05:00,0,si,no,producto_sin_stock,",
    ]
    r = lb.calcular(lb.leer_csv(escribir(tmp_path, filas))[0])
    assert r["causas"] == [("producto_sin_stock", 1), ("sku_mal_digitado", 1)]


def test_con_menos_de_cinco_mediciones_avisa(tmp_path):
    r = lb.calcular(lb.leer_csv(escribir(tmp_path, FILAS[:3]))[0])
    assert not r["alcanza_el_minimo"]
    assert "ATENCION" in lb.formatear(r) and "al menos 5" in lb.formatear(r)
    assert "ATENCION" not in lb.formatear(lb.calcular(lb.leer_csv(escribir(tmp_path, FILAS))[0]))


def test_calcular_sin_filas_falla():
    with pytest.raises(ValueError):
        lb.calcular([])


def test_la_salida_en_texto_y_en_tabla(tmp_path):
    r = lb.calcular(lb.leer_csv(escribir(tmp_path, FILAS))[0])
    texto = lb.formatear(r)
    assert "11:00 min" in texto and "50.0% (3 de 6)" in texto
    tabla = lb.formatear(r, markdown=True)
    assert tabla.startswith("| Indicador | Antes (a mano) |")
    assert "| Guías emitidas sin errores ni reprocesos | 50.0% (3 de 6) |" in tabla
    assert "cambio_ultimo_minuto (2), sku_mal_digitado (1)" in tabla


# ---------------------------------------------------------------- validacion

def probar_fila(**cambios):
    base = dict(zip(lb.COLUMNAS, next(csv.reader([FILAS[0]]))))
    base.update(cambios)
    return lb.validar_fila(base)[1]


def test_una_fila_correcta_no_tiene_errores():
    assert probar_fila() == []


@pytest.mark.parametrize("cambios, trozo", [
    ({"fecha": "16/11/2026"}, "AAAA-MM-DD"),
    ({"tipo_movimiento": "traslado"}, "despacho o retiro"),
    ({"n_productos": "0"}, "n_productos"),
    ({"n_productos": "61"}, "entre 1 y 60"),
    ({"n_productos": "doce"}, "numero entero"),
    ({"tiempo_armado": "12:99"}, "00 a 59"),
    ({"n_cambios_ultimo_minuto": "-1"}, "numero entero"),
    ({"error_detectado": "tal vez"}, "si o no"),
    ({"se_rehizo": ""}, "si o no"),
    ({"id_medicion": ""}, "falta id_medicion"),
])
def test_los_datos_mal_escritos_se_rechazan_con_un_motivo(cambios, trozo):
    errores = probar_fila(**cambios)
    assert errores and any(trozo in e for e in errores), errores


def test_la_causa_es_obligatoria_si_hubo_error_o_reproceso_y_solo_entonces():
    assert any("falta la causa" in e for e in probar_fila(error_detectado="si"))
    assert any("falta la causa" in e for e in probar_fila(se_rehizo="si"))
    assert any("no tuvo errores" in e for e in probar_fila(causa="otro"))
    assert any("debe ser una de" in e for e in probar_fila(error_detectado="si", causa="inventada"))
    assert probar_fila(error_detectado="si", causa="otro") == []


@pytest.mark.parametrize("texto", ["avisar a persona@ejemplo.cl", "llamar al +56 9 0000 0000", "fono 900000000", "(2) 0000-0000"])
def test_se_niega_a_leer_correos_y_telefonos(texto):
    errores = probar_fila(observaciones=texto)
    assert any("correo o un telefono" in e for e in errores), errores


def test_la_fecha_y_los_numeros_no_se_confunden_con_telefonos():
    assert probar_fila(fecha="2026-11-16", n_productos="60", tiempo_armado="1:02:30") == []


def test_el_archivo_con_problemas_informa_la_linea_y_no_calcula(tmp_path, capsys):
    ruta = escribir(tmp_path, [FILAS[0], "M02,2026-11-16,despacho,50,15:00,2,si,no,,", FILAS[2]])
    assert lb.main([str(ruta)]) == 1
    salida = capsys.readouterr().out
    assert "linea 3" in salida and "falta la causa" in salida
    assert "Tiempo por guia" not in salida


def test_un_id_repetido_se_rechaza(tmp_path):
    _, errores = lb.leer_csv(escribir(tmp_path, [FILAS[0], FILAS[0]]))
    assert any("repetido" in e for e in errores)


def test_el_encabezado_incorrecto_se_rechaza(tmp_path):
    _, errores = lb.leer_csv(escribir(tmp_path, [FILAS[0]], encabezado="id_medicion,fecha"))
    assert len(errores) == 1 and "faltan columnas" in errores[0] and "columnas desconocidas" not in errores[0]
    _, errores = lb.leer_csv(escribir(tmp_path, [FILAS[0]], encabezado="id_medicion,fecha,tiempo"))
    assert "faltan columnas" in errores[0] and "columnas desconocidas: tiempo" in errores[0]
    _, errores = lb.leer_csv(escribir(tmp_path, [], encabezado=ENCABEZADO + ",nombre"))
    assert "columnas desconocidas: nombre" in errores[0]


def test_las_lineas_vacias_se_ignoran(tmp_path):
    filas, errores = lb.leer_csv(escribir(tmp_path, [FILAS[0], ",,,,,,,,,", FILAS[2]]))
    assert errores == [] and len(filas) == 2


def test_main_sin_argumentos_o_con_archivo_inexistente(tmp_path, capsys):
    assert lb.main([]) == 2
    assert lb.main([str(tmp_path / "no_existe.csv")]) == 2
    assert "No existe el archivo" in capsys.readouterr().out


def test_main_imprime_el_resumen(tmp_path, capsys):
    assert lb.main([str(escribir(tmp_path, FILAS))]) == 0
    assert "11:00 min" in capsys.readouterr().out
    assert lb.main([str(escribir(tmp_path, FILAS)), "--md"]) == 0
    assert "| Indicador | Antes (a mano) |" in capsys.readouterr().out
