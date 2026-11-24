"""Prueba la base real de Supabase llamando a la API con la clave PUBLICABLE, igual que el navegador.

Que comprueba: lectura de tablas, que no se pueda escribir directo ni leer correo y telefono, y cada una de las
cinco funciones (casos que funcionan y casos que deben ser rechazados con su mensaje exacto).

ATENCION: modifica los datos compartidos de la demo (carga pedidos, registra cambios, prepara guias) y al final
llama a reiniciar_demo. No lo ejecutes mientras alguien hace una sesion de prueba de usuarios.

Solo mira las ordenes 3001 y 3002 y los equipos 501 a 507 (la demo): puede haber, ademas, el inventario real
(equipos desde 1000) y las ordenes que se crean desde el MVP, que esta prueba no toca ni cuenta.

Uso (desde la raiz del repositorio, con SUPABASE_URL y SUPABASE_PUBLISHABLE_KEY en .env o en el entorno):
    py supabase/probar_en_supabase.py --si          # muestra solo las fallas
    py supabase/probar_en_supabase.py --si -v       # muestra todas las comprobaciones

Solo usa la biblioteca estandar. No necesita (ni debe recibir) la clave secreta ni service_role.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

if "--si" not in sys.argv:
    print("Esta prueba modifica y reinicia los datos compartidos de la demo. Ejecutala con --si para confirmar.")
    sys.exit(2)

env = dict(os.environ)
archivo_env = Path(__file__).resolve().parent.parent / ".env"
if archivo_env.exists():
    for linea in archivo_env.read_text(encoding="utf-8").splitlines():
        if "=" in linea and not linea.lstrip().startswith("#"):
            k, v = linea.split("=", 1)
            env.setdefault(k.strip(), v.strip())
if not env.get("SUPABASE_URL") or not env.get("SUPABASE_PUBLISHABLE_KEY"):
    print("Faltan SUPABASE_URL y SUPABASE_PUBLISHABLE_KEY (en .env o en el entorno).")
    sys.exit(2)
if not env["SUPABASE_PUBLISHABLE_KEY"].startswith("sb_publishable_"):
    print("SUPABASE_PUBLISHABLE_KEY debe ser la clave publicable. No uses la clave secreta.")
    sys.exit(2)
URL = env["SUPABASE_URL"].rstrip("/") + "/rest/v1"
KEY = env["SUPABASE_PUBLISHABLE_KEY"]
H = {"apikey": KEY, "Content-Type": "application/json"}

resultados = []

# La demo: dos ordenes (3001 y 3002) y siete equipos (501 a 507). Lo demas de la base no es de esta prueba.
DEMO = "id_orden=in.(3001,3002)"
EQUIPOS_DEMO = "id_equipo=gte.501&id_equipo=lte.507"


def llamar(metodo, ruta, cuerpo=None, extra=None):
    h = dict(H)
    if extra:
        h.update(extra)
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    req = urllib.request.Request(URL + ruta, data=datos, headers=h, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            txt = r.read().decode()
            return r.status, (json.loads(txt) if txt else None)
    except urllib.error.HTTPError as e:
        txt = e.read().decode()
        try:
            return e.code, json.loads(txt)
        except Exception:
            return e.code, txt


def rpc(nombre, **args):
    return llamar("POST", "/rpc/" + nombre, args)


def prueba(nombre, ok, detalle=""):
    resultados.append((nombre, bool(ok), detalle))


def regla(nombre, resp, mensaje, campo):
    """La llamada debe ser rechazada con P0001, el mensaje exacto y el campo."""
    st, cuerpo = resp
    ok = st == 400 and isinstance(cuerpo, dict) and cuerpo.get("code") == "P0001" \
        and cuerpo.get("message") == mensaje and cuerpo.get("hint") == campo
    prueba(nombre, ok, "" if ok else f"HTTP {st} {json.dumps(cuerpo, ensure_ascii=False)[:220]}")


def exito(nombre, resp):
    st, cuerpo = resp
    prueba(nombre, st in (200, 204), "" if st in (200, 204) else f"HTTP {st} {json.dumps(cuerpo, ensure_ascii=False)[:220]}")
    return cuerpo


def lineas(orden):
    st, c = llamar("GET", f"/detalle_orden?id_orden=eq.{orden}&select=sku_informado,resultado_validacion,vigente,id_equipo&order=id_detalle")
    return c



_reinicio_fallo = []


def restaurar():
    """Deja las dos ordenes como seed_poc.sql usando solo cargar_pedido (por si reiniciar_demo falla)."""
    rpc("cargar_pedido", p_id_orden=3001, p_tipo="despacho", p_modalidad="convencional", p_motivo_retiro=None,
        p_skus=["SD-63A20-0314", "SD-63A20-0315", "ST-0042", "MP-0107"])
    rpc("cargar_pedido", p_id_orden=3002, p_tipo="retiro", p_modalidad=None, p_motivo_retiro="falla",
        p_skus=["SD-32A10-0102", "SD-63A20-9999", "ST-0042", "MP-0107"])


def reiniciar():
    st, cuerpo = rpc("reiniciar_demo")
    if st not in (200, 204):
        if not _reinicio_fallo:
            _reinicio_fallo.append(1)
            prueba("reiniciar_demo se puede llamar con la clave publicable", False, f"HTTP {st} {json.dumps(cuerpo, ensure_ascii=False)[:200]}")
        restaurar()
        return False
    return True

# ------------------------------------------------------------------ estado inicial
reiniciar()
st, c = llamar("GET", "/clientes?select=id_cliente")
prueba("Lectura de clientes (2)", st == 200 and len(c) == 2, f"HTTP {st} {c if st != 200 else len(c)}")
st, c = llamar("GET", "/usuarios?select=id_usuario,nombre,rol,activo")
prueba("Lectura de usuarios con columnas públicas (2)", st == 200 and len(c) == 2, f"HTTP {st}")
st, c = llamar("GET", "/usuarios?select=correo")
prueba("El correo de usuarios NO se puede leer", st in (401, 403) or (isinstance(c, dict) and c.get("code") == "42501"), f"HTTP {st} {str(c)[:120]}")
st, c = llamar("GET", "/usuarios?select=telefono")
prueba("El teléfono de usuarios NO se puede leer", st in (401, 403) or (isinstance(c, dict) and c.get("code") == "42501"), f"HTTP {st}")
st, c = llamar("GET", f"/equipos?select=id_equipo&{EQUIPOS_DEMO}")
prueba("Lectura de equipos de la demo (7)", st == 200 and len(c) == 7, f"HTTP {st}")
st, c = llamar("GET", f"/ordenes?select=id_orden,detalle_orden(id_detalle)&{DEMO}&order=id_orden")
prueba("Lectura de órdenes con sus líneas (2 órdenes, 4 + 4)", st == 200 and [len(o["detalle_orden"]) for o in c] == [4, 4], f"HTTP {st} {str(c)[:120]}")
st, c = llamar("GET", f"/guias?select=id_guia&{DEMO}")
prueba("Lectura de guías de la demo (0)", st == 200 and c == [], f"HTTP {st}")
st, c = llamar("GET", "/ordenes?select=id_orden,folio&id_orden=in.(3001,3002)&order=id_orden")
prueba("Las órdenes de la demo tienen su folio", st == 200 and c == [{"id_orden": 3001, "folio": "GUIA-2026-001"}, {"id_orden": 3002, "folio": "GUIA-2026-002"}], f"HTTP {st} {str(c)[:120]}")
st, c = llamar("GET", "/clientes?select=rut")
prueba("El RUT de clientes NO se puede leer con la clave pública", st in (401, 403) or (isinstance(c, dict) and c.get("code") == "42501"), f"HTTP {st}")
st, c = llamar("GET", "/clientes?select=direccion")
prueba("La dirección de clientes NO se puede leer con la clave pública", st in (401, 403) or (isinstance(c, dict) and c.get("code") == "42501"), f"HTTP {st}")
st, c = llamar("GET", "/clientes?select=id_cliente,razon_social")
prueba("La razón social de clientes SÍ se puede leer (la usa el prototipo)", st == 200 and len(c) >= 2, f"HTTP {st}")

# ------------------------------------------------------------------ escritura directa: debe estar cerrada
for tabla, cuerpo in [("clientes", {"id_cliente": 99, "razon_social": "x", "rut": "x", "direccion": "x"}),
                      ("equipos", {"id_equipo": 99, "sku": "X", "descripcion": "x", "estado": "disponible", "ubicacion": "bodega"}),
                      ("guias", {"id_guia": 99, "id_orden": 3001, "id_usuario_emite": 1, "numero_guia": 1, "fecha_emision": "2026-01-01"})]:
    st, c = llamar("POST", "/" + tabla, cuerpo)
    prueba(f"INSERT directo en {tabla} rechazado", st in (401, 403), f"HTTP {st} {str(c)[:100]}")
st, c = llamar("PATCH", "/equipos?id_equipo=eq.501", {"estado": "fuera_servicio"})
st2, c2 = llamar("GET", "/equipos?id_equipo=eq.501&select=estado")
prueba("UPDATE directo en equipos rechazado y sin efecto", st in (401, 403) and c2[0]["estado"] == "disponible", f"HTTP {st} estado={c2}")
st, c = llamar("DELETE", "/ordenes?id_orden=eq.3001")
st2, c2 = llamar("GET", f"/ordenes?select=id_orden&{DEMO}")
prueba("DELETE directo en ordenes rechazado y sin efecto", st in (401, 403) and len(c2) == 2, f"HTTP {st} ordenes={len(c2)}")
st, c = rpc("_fallo", p_mensaje="x")
prueba("La función interna _fallo no es llamable", st in (401, 403, 404), f"HTTP {st}")
st, c = rpc("_skus_limpios", p_skus=["a"])
prueba("La función interna _skus_limpios no es llamable", st in (401, 403, 404), f"HTTP {st}")
st, c = rpc("crear_pedido", p_folio="GUIA-2026-990", p_id_cliente=10, p_id_usuario=1, p_tipo="despacho", p_modalidad="convencional", p_motivo_retiro=None, p_skus=["ST-0042"])
prueba("crear_pedido NO se puede llamar con la clave pública (solo el rol del MVP)", st in (401, 403, 404), f"HTTP {st} {str(c)[:100]}")
for vista in ("v_ordenes_resumen", "v_detalle_orden", "v_historial_cambios"):
    st, c = llamar("GET", "/" + vista + "?select=*&limit=1")
    prueba(f"La vista {vista} NO se puede leer con la clave pública", st in (401, 403, 404), f"HTTP {st}")

# ------------------------------------------------------------------ cargar_pedido
base = dict(p_id_orden=3001, p_tipo="despacho", p_modalidad="convencional", p_motivo_retiro=None)
regla("cargar: orden inexistente", rpc("cargar_pedido", **{**base, "p_id_orden": 9999}, p_skus=["A"]), "Esa orden no existe. Elige otra.", "orden")
regla("cargar: listado vacío", rpc("cargar_pedido", **base, p_skus=[]), "Pega al menos un SKU, uno por línea. Ejemplo: SD-63A20-0314", "skus")
regla("cargar: solo espacios y líneas vacías", rpc("cargar_pedido", **base, p_skus=["  ", "", "\t"]), "Pega al menos un SKU, uno por línea. Ejemplo: SD-63A20-0314", "skus")
regla("cargar: solo tabulaciones y saltos de linea", rpc("cargar_pedido", **base, p_skus=["\t", "\r\n", " \t "]), "Pega al menos un SKU, uno por línea. Ejemplo: SD-63A20-0314", "skus")
regla("cargar: 61 productos", rpc("cargar_pedido", **base, p_skus=[f"X-{i}" for i in range(61)]), "Hay 61 productos y el máximo es 60. Quita 1 para continuar.", "skus")
regla("cargar: tipo inválido", rpc("cargar_pedido", **{**base, "p_tipo": "otro"}, p_skus=["A"]), "Elige el tipo de movimiento.", "tipo")
regla("cargar: despacho sin modalidad", rpc("cargar_pedido", **{**base, "p_modalidad": None}, p_skus=["A"]), "Elige la modalidad del despacho.", "modalidad")
regla("cargar: retiro sin motivo", rpc("cargar_pedido", **{**base, "p_tipo": "retiro", "p_modalidad": None}, p_skus=["A"]), "Elige el motivo del retiro.", "motivo_retiro")
prueba("Los rechazos no tocaron los datos (4 líneas en 3001)", len(lineas(3001)) == 4)
exito("cargar: 60 productos se aceptan", rpc("cargar_pedido", **base, p_skus=[f"X-{i}" for i in range(60)]))
prueba("cargar: quedaron 60 líneas pendientes", len(lineas(3001)) == 60 and all(l["resultado_validacion"] == "pendiente" for l in lineas(3001)))
exito("cargar: normaliza (mayúsculas, espacios, repetidos y orden)", rpc("cargar_pedido", **base, p_skus=[" sd-63a20-0314 ", "SD-63A20-0315", "sd-63a20-0314", "", "st-0042", "MP-0107"]))
l = lineas(3001)
prueba("cargar: 4 líneas en mayúsculas, sin repetidos y en orden", [x["sku_informado"] for x in l] == ["SD-63A20-0314", "SD-63A20-0315", "ST-0042", "MP-0107"], str([x["sku_informado"] for x in l]))
exito("cargar: retiro con motivo cambia el tipo de 3002", rpc("cargar_pedido", p_id_orden=3002, p_tipo="retiro", p_modalidad=None, p_motivo_retiro="mantencion_preventiva", p_skus=["SD-32A10-0102", "SD-63A20-9999", "ST-0042", "MP-0107"]))
st, c = llamar("GET", "/ordenes?id_orden=eq.3002&select=tipo_movimiento,modalidad,motivo_retiro,estado")
prueba("cargar: 3002 es retiro, sin modalidad, motivo mantención preventiva", c == [{"tipo_movimiento": "retiro", "modalidad": None, "motivo_retiro": "mantencion_preventiva", "estado": "pendiente"}], str(c))
exito("cargar: despacho cambia el tipo y limpia el motivo", rpc("cargar_pedido", p_id_orden=3002, p_tipo="despacho", p_modalidad="alternativo", p_motivo_retiro="falla", p_skus=["MP-0107"]))
st, c = llamar("GET", "/ordenes?id_orden=eq.3002&select=tipo_movimiento,modalidad,motivo_retiro")
prueba("cargar: despacho deja modalidad y borra el motivo de retiro", c == [{"tipo_movimiento": "despacho", "modalidad": "alternativo", "motivo_retiro": None}], str(c))
reiniciar()

# ------------------------------------------------------------------ validar_pedido
regla("validar: orden inexistente", rpc("validar_pedido", p_id_orden=9999), "Esa orden no existe. Elige otra.", "orden")
exito("validar 3001", rpc("validar_pedido", p_id_orden=3001))
prueba("validar 3001: las 4 líneas ok y con equipo", all(x["resultado_validacion"] == "ok" and x["id_equipo"] for x in lineas(3001)), str(lineas(3001)))
st, c = llamar("GET", "/ordenes?id_orden=eq.3001&select=estado")
prueba("validar 3001: la orden queda 'validada'", c == [{"estado": "validada"}], str(c))
exito("validar 3002", rpc("validar_pedido", p_id_orden=3002))
l = {x["sku_informado"]: x for x in lineas(3002)}
prueba("validar 3002: SD-63A20-9999 no existe y no tiene equipo", l["SD-63A20-9999"]["resultado_validacion"] == "no_existe" and l["SD-63A20-9999"]["id_equipo"] is None, str(l["SD-63A20-9999"]))
prueba("validar 3002: los otros 3 quedan ok", sum(1 for x in l.values() if x["resultado_validacion"] == "ok") == 3)
st, c = llamar("GET", "/ordenes?id_orden=eq.3002&select=estado")
prueba("validar 3002: la orden queda 'bloqueada'", c == [{"estado": "bloqueada"}], str(c))
exito("cargar con SKU en mantención (503) y validar", rpc("cargar_pedido", **{**base, "p_id_orden": 3001}, p_skus=["SD-63A20-0316"]))
rpc("validar_pedido", p_id_orden=3001)
prueba("validar: equipo en mantención da no_disponible", lineas(3001)[0]["resultado_validacion"] == "no_disponible", str(lineas(3001)))
reiniciar()

# ------------------------------------------------------------------ preparar_guia (antes de corregir)
regla("guía: orden inexistente", rpc("preparar_guia", p_id_orden=9999, p_id_usuario=1), "Esa orden no existe. Elige otra.", "orden")
regla("guía: sin validar", rpc("preparar_guia", p_id_orden=3001, p_id_usuario=1), "Valida el pedido antes de preparar la guía.", "productos")
regla("guía: usuario que no es jefe de bodega", rpc("preparar_guia", p_id_orden=3001, p_id_usuario=2), "Solo el jefe de bodega puede preparar la guía.", "usuario")
regla("guía: usuario inexistente", rpc("preparar_guia", p_id_orden=3001, p_id_usuario=999), "Solo el jefe de bodega puede preparar la guía.", "usuario")
rpc("validar_pedido", p_id_orden=3002)
regla("guía: con un SKU que no existe", rpc("preparar_guia", p_id_orden=3002, p_id_usuario=1), "Corrige 1 producto para continuar.", "productos")
st, c = llamar("GET", f"/guias?select=id_guia&{DEMO}")
prueba("guía: los rechazos no crearon ninguna guía", c == [], str(c))

# ------------------------------------------------------------------ registrar_cambio
cam = dict(p_id_orden=3002, p_sku_sale="SD-63A20-9999", p_sku_entra="SD-63A20-0315", p_id_usuario=2, p_motivo="Código mal digitado")
regla("cambio: orden inexistente", rpc("registrar_cambio", **{**cam, "p_id_orden": 9999}), "Esa orden no existe. Elige otra.", "orden")
regla("cambio: sin equipo que sale", rpc("registrar_cambio", **{**cam, "p_sku_sale": ""}), "Elige el equipo que sale.", "sale")
regla("cambio: el que sale no está en el pedido", rpc("registrar_cambio", **{**cam, "p_sku_sale": "SD-63A20-0316"}), "Ese equipo no está en el pedido. Elige otro.", "sale")
regla("cambio: sin equipo que entra", rpc("registrar_cambio", **{**cam, "p_sku_entra": ""}), "Elige el equipo que entra.", "entra")
regla("cambio: entra igual a sale", rpc("registrar_cambio", **{**cam, "p_sku_entra": "SD-63A20-9999"}), "El equipo que entra debe ser distinto del que sale.", "entra")
regla("cambio: el que entra no existe", rpc("registrar_cambio", **{**cam, "p_sku_entra": "SD-00000-0000"}), "Ese SKU no existe en el inventario. Elige uno de la lista.", "entra")
regla("cambio: el que entra ya está en el pedido", rpc("registrar_cambio", **{**cam, "p_sku_entra": "ST-0042"}), "Ese equipo ya está en el pedido. Elige otro.", "entra")
regla("cambio: motivo vacío", rpc("registrar_cambio", **{**cam, "p_motivo": ""}), "Elige el motivo del cambio.", "motivo")
regla("cambio: motivo solo espacios", rpc("registrar_cambio", **{**cam, "p_motivo": "   "}), "Elige el motivo del cambio.", "motivo")
regla("cambio: motivo nulo", rpc("registrar_cambio", **{**cam, "p_motivo": None}), "Elige el motivo del cambio.", "motivo")
regla("cambio: motivo de más de 200 caracteres", rpc("registrar_cambio", **{**cam, "p_motivo": "x" * 201}), "El motivo es muy largo: máximo 200 caracteres.", "motivo")
regla("cambio: motivo solo tabulacion", rpc("registrar_cambio", **{**cam, "p_motivo": "\t\t"}), "Elige el motivo del cambio.", "motivo")
regla("cambio: motivo solo salto de linea", rpc("registrar_cambio", **{**cam, "p_motivo": "\n"}), "Elige el motivo del cambio.", "motivo")
regla("cambio: usuario inexistente", rpc("registrar_cambio", **{**cam, "p_id_usuario": 999}), "Elige quién registra el cambio.", "responsable")
st, c = llamar("GET", f"/registro_cambios?select=id_cambio&{DEMO}")
prueba("cambio: los rechazos no dejaron registro", c == [], str(c))
exito("cambio: 9999 → 0315 con motivo", rpc("registrar_cambio", **cam))
st, c = llamar("GET", f"/registro_cambios?select=sku_sale,id_equipo_sale,id_equipo_entra,id_usuario,motivo_cambio,fecha_hora_cambio&{DEMO}")
prueba("cambio: queda registrado con SKU anterior, sin equipo anterior, motivo, usuario y hora",
       len(c) == 1 and c[0]["sku_sale"] == "SD-63A20-9999" and c[0]["id_equipo_sale"] is None and c[0]["id_equipo_entra"] == 502
       and c[0]["id_usuario"] == 2 and c[0]["motivo_cambio"] == "Código mal digitado" and c[0]["fecha_hora_cambio"], str(c))
l = lineas(3002)
prueba("cambio: la línea vieja queda no vigente (no se borra) y la nueva vigente y pendiente",
       any(x["sku_informado"] == "SD-63A20-9999" and not x["vigente"] for x in l)
       and any(x["sku_informado"] == "SD-63A20-0315" and x["vigente"] and x["resultado_validacion"] == "pendiente" for x in l), str(l))
st, c = llamar("GET", "/ordenes?id_orden=eq.3002&select=estado")
prueba("cambio: la orden vuelve a 'pendiente'", c == [{"estado": "pendiente"}], str(c))
regla("guía: tras el cambio, aún sin revalidar", rpc("preparar_guia", p_id_orden=3002, p_id_usuario=1), "Valida el pedido antes de preparar la guía.", "productos")
exito("validar 3002 tras el cambio", rpc("validar_pedido", p_id_orden=3002))
prueba("validar: las 4 vigentes ok", all(x["resultado_validacion"] == "ok" for x in lineas(3002) if x["vigente"]) and sum(1 for x in lineas(3002) if x["vigente"]) == 4)

# ------------------------------------------------------------------ preparar_guia (camino feliz)
# El MVP tambien emite guias: los numeros son consecutivos a partir del mayor que ya exista (15230 si no hay ninguno).
st, existentes = llamar("GET", "/guias?select=numero_guia&order=numero_guia.desc&limit=1")
base_guia = existentes[0]["numero_guia"] if st == 200 and existentes else 15229
st, g = rpc("preparar_guia", p_id_orden=3002, p_id_usuario=1)
prueba("guía 3002: se prepara", st == 200 and isinstance(g, dict) and g.get("numero_guia") == base_guia + 1 and g.get("fecha_emision"), f"HTTP {st} {g}")
st, c = llamar("GET", f"/guias?select=numero_guia,id_usuario_emite,id_orden,fecha_emision&{DEMO}")
prueba("guía 3002: queda guardada con el número siguiente y el jefe de bodega", len(c) == 1 and c[0]["id_orden"] == 3002 and c[0]["id_usuario_emite"] == 1 and c[0]["numero_guia"] == base_guia + 1, str(c))
st, c = llamar("GET", "/ordenes?id_orden=eq.3002&select=estado")
prueba("guía 3002: la orden queda 'emitida'", c == [{"estado": "emitida"}], str(c))
regla("guía: no se prepara dos veces", rpc("preparar_guia", p_id_orden=3002, p_id_usuario=1), "Esta orden ya tiene la guía preparada. Presiona Reiniciar demo para volver a empezar.", "orden")
regla("orden con guía: no admite cargar", rpc("cargar_pedido", p_id_orden=3002, p_tipo="retiro", p_modalidad=None, p_motivo_retiro="falla", p_skus=["A"]), "Esta orden ya tiene la guía preparada. Presiona Reiniciar demo para volver a empezar.", "orden")
regla("orden con guía: no admite validar", rpc("validar_pedido", p_id_orden=3002), "Esta orden ya tiene la guía preparada. Presiona Reiniciar demo para volver a empezar.", "orden")
regla("orden con guía: no admite cambios", rpc("registrar_cambio", p_id_orden=3002, p_sku_sale="SD-63A20-0315", p_sku_entra="SD-63A20-0314", p_id_usuario=2, p_motivo="x"), "Esta orden ya tiene la guía preparada. Presiona Reiniciar demo para volver a empezar.", "orden")
rpc("validar_pedido", p_id_orden=3001)
st, g = rpc("preparar_guia", p_id_orden=3001, p_id_usuario=1)
prueba("guía 3001: se prepara con número consecutivo", st == 200 and g.get("numero_guia") == base_guia + 2, f"HTTP {st} {g}")

# ------------------------------------------------------------------ reinicio
ok_final = reiniciar()
prueba("reiniciar_demo responde (reinicio final)", ok_final)
st, c = llamar("GET", f"/guias?select=id_guia&{DEMO}")
prueba("reiniciar: las órdenes de la demo quedan sin guías", c == [])
st, c = llamar("GET", f"/registro_cambios?select=id_cambio&{DEMO}")
prueba("reiniciar: las órdenes de la demo quedan sin cambios", c == [])
st, c = llamar("GET", f"/ordenes?select=id_orden,tipo_movimiento,modalidad,motivo_retiro,estado,detalle_orden(sku_informado,vigente,resultado_validacion)&{DEMO}&order=id_orden")
ok = (len(c) == 2 and c[0]["id_orden"] == 3001 and c[0]["modalidad"] == "convencional" and c[1]["motivo_retiro"] == "falla"
      and all(o["estado"] == "pendiente" for o in c)
      and [len(o["detalle_orden"]) for o in c] == [4, 4]
      and all(d["vigente"] and d["resultado_validacion"] == "pendiente" for o in c for d in o["detalle_orden"]))
prueba("reiniciar: 3001 despacho convencional y 3002 retiro por falla, 4 líneas pendientes cada una", ok, str(c)[:200])
skus3002 = sorted(d["sku_informado"] for d in c[1]["detalle_orden"])
prueba("reiniciar: 3002 trae SD-63A20-9999", "SD-63A20-9999" in skus3002, str(skus3002))
st, c = llamar("GET", f"/equipos?select=id_equipo,estado,ubicacion&{EQUIPOS_DEMO}&order=id_equipo")
prueba("los equipos de la demo no cambiaron (el 503 sigue en mantención en el taller)", len(c) == 7 and c[2] == {"id_equipo": 503, "estado": "en_mantencion", "ubicacion": "taller"} and all(e["estado"] == "disponible" for i, e in enumerate(c) if i != 2), str(c))

# ------------------------------------------------------------------ informe
fallas = [r for r in resultados if not r[1]]
print(f"PRUEBAS CONTRA SUPABASE: {len(resultados)} · OK: {len(resultados) - len(fallas)} · FALLAS: {len(fallas)}")
for nombre, ok, det in resultados:
    if not ok:
        print("FALLA:", nombre, "->", det)
if "-v" in sys.argv:
    for nombre, ok, det in resultados:
        print(("OK    " if ok else "FALLA ") + nombre)

sys.exit(1 if fallas else 0)
