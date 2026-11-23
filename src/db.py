"""
Capa de datos del MVP: una sola interfaz (Repositorio) y dos implementaciones.

  RepoPostgres  produccion. Se conecta con DATABASE_URL (psycopg, sin ORM) y NO reimplementa las reglas del
                negocio: llama a las funciones SQL de Supabase (crear_pedido, validar_pedido, registrar_cambio,
                preparar_guia), que ya validan todo y son la fuente unica de verdad. Lee con consultas de solo
                lectura sobre las vistas de supabase/mvp_vistas.sql.
  RepoSqlite    pruebas y desarrollo local sin red. Usa el mismo esquema (supabase/schema.sql) y repite en Python
                las mismas reglas con los mismos mensajes. Para que no se desvien, tests/test_contrato_repo.py
                corre las mismas pruebas contra las dos (la de PostgreSQL solo si hay DATABASE_URL_TEST).

La implementacion se elige con la variable de entorno DATABASE_URL: si esta definida, PostgreSQL; si no, SQLite.
La cadena de conexion nunca se guarda en el repositorio ni se escribe en pantallas ni en mensajes de error.

psycopg se importa solo cuando hace falta (al conectar a PostgreSQL): las pruebas con SQLite no lo necesitan.
"""

import os
import re
import sqlite3
import threading
from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import pandas as pd

MAX_SKUS = 60  # el mismo maximo que cargar_pedido y crear_pedido en SQL, y que el prototipo
ZONA_HORARIA = "America/Santiago"  # las fechas se muestran en hora de Chile (la conversion la hace la base)

MODALIDADES_POR_TIPO = {
    "Despacho": ["Convencional", "Alternativo"],
    "Retiro": ["Preventivo", "Por falla"],
}

_TIPO_A_BASE = {"Despacho": "despacho", "Retiro": "retiro"}
_TIPO_DESDE_BASE = {v: k for k, v in _TIPO_A_BASE.items()}
_MODALIDAD_A_BASE = {
    "Convencional": "convencional",
    "Alternativo": "alternativo",
    "Preventivo": "mantencion_preventiva",
    "Por falla": "falla",
}
_MODALIDAD_DESDE_BASE = {v: k for k, v in _MODALIDAD_A_BASE.items()}

ESTADOS_EQUIPO = {
    "disponible": "Disponible",
    "arrendado": "Arrendado",
    "en_mantencion": "En mantención",
    "fuera_servicio": "Fuera de servicio",
}

COLUMNAS_ORDENES = ["folio", "tipo_movimiento", "modalidad", "fecha_carga", "skus_vigentes", "estado", "cliente", "numero_guia"]
COLUMNAS_LINEAS = ["id", "sku", "descripcion", "estado_equipo", "resultado", "ultima_modificacion"]
COLUMNAS_CAMBIOS = ["id", "folio", "sku_original", "sku_nuevo", "responsable", "fecha_hora", "motivo"]
COLUMNAS_EQUIPOS = ["sku", "descripcion", "estado"]

_FOLIO = re.compile(r"GUIA-[0-9]{4}-[0-9]{3,6}")
_ESPACIOS = " \t\r\n\f\v\xa0"  # los mismos que quita _limpiar en SQL


class ReglaDeNegocio(Exception):
    """Una regla del negocio rechazo la operacion. mensaje es el texto exacto para la persona; campo, el campo."""

    def __init__(self, mensaje, campo=""):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.campo = campo or ""


class ErrorDeBase(Exception):
    """Problema del sistema (conexion, permisos, tiempo agotado). El mensaje es generico a proposito: no filtra detalles."""


def limpiar(texto):
    """Quita espacios, tabulaciones, saltos de linea y espacios duros de los extremos (igual que _limpiar en SQL)."""
    return (texto or "").strip(_ESPACIOS)


def skus_limpios(skus):
    """Mayusculas, sin espacios, sin lineas vacias ni repetidos, en orden de aparicion (igual que _skus_limpios en SQL)."""
    vistos = {}
    for s in skus or []:
        limpio = limpiar(s).upper()
        if limpio and limpio not in vistos:
            vistos[limpio] = True
    return list(vistos)


def _etiqueta_modalidad(fila):
    clave = fila.get("modalidad") or fila.get("motivo_retiro")
    return _MODALIDAD_DESDE_BASE.get(clave, "")


def _ordenes_df(filas):
    datos = [
        {
            "folio": f["folio"],
            "tipo_movimiento": _TIPO_DESDE_BASE.get(f["tipo_movimiento"], f["tipo_movimiento"]),
            "modalidad": _etiqueta_modalidad(f),
            "fecha_carga": pd.to_datetime(f["fecha_orden"]),
            "skus_vigentes": int(f["skus_vigentes"] or 0),
            "estado": f["estado"],
            "cliente": f.get("razon_social") or "",
            "numero_guia": f.get("numero_guia"),
        }
        for f in filas
    ]
    return pd.DataFrame(datos, columns=COLUMNAS_ORDENES)


def _escapar_like(texto):
    return texto.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


class Repositorio(ABC):
    """Lo que necesitan las pantallas. Todas las fechas salen como datetime sin zona, en hora de Chile."""

    modo = ""  # "postgres" o "sqlite": las pantallas lo muestran para que se sepa contra que base se trabaja

    @abstractmethod
    def clientes(self):
        """Lista de dicts {id_cliente, razon_social}."""

    @abstractmethod
    def usuarios(self):
        """Lista de dicts {id_usuario, nombre, rol} de los usuarios activos."""

    @abstractmethod
    def ordenes(self):
        """DataFrame (COLUMNAS_ORDENES), una fila por orden con folio, la mas reciente primero."""

    @abstractmethod
    def lineas(self, folio):
        """DataFrame (COLUMNAS_LINEAS) con las lineas vigentes del pedido."""

    @abstractmethod
    def cambios(self, folio=None):
        """DataFrame (COLUMNAS_CAMBIOS): los cambios de ultima hora, el mas reciente primero. Con folio, solo los de esa orden."""

    @abstractmethod
    def buscar_equipos(self, texto, limite=30):
        """DataFrame (COLUMNAS_EQUIPOS) con los equipos cuyo SKU o descripcion contiene el texto."""

    @abstractmethod
    def crear_pedido(self, folio, id_cliente, id_usuario, tipo, modalidad, skus):
        """Crea la orden con sus lineas y devuelve el folio. tipo y modalidad son las etiquetas de pantalla."""

    @abstractmethod
    def validar(self, folio):
        """Contrasta cada linea con el inventario y deja el resultado guardado."""

    @abstractmethod
    def registrar_cambio(self, folio, sku_sale, sku_entra, id_usuario, motivo):
        """Reemplaza un equipo del pedido y deja el registro del cambio."""

    @abstractmethod
    def preparar_guia(self, folio, id_usuario):
        """Prepara la guia (solo si todo esta validado) y devuelve {numero_guia, fecha_emision}."""

    def orden(self, folio):
        """Fila de la orden como dict, o None si no existe."""
        df = self.ordenes()
        fila = df[df["folio"] == folio]
        return None if fila.empty else fila.iloc[0].to_dict()

    def guia(self, folio):
        """{numero_guia, fecha_emision} de la guia de la orden, o None si todavia no tiene."""
        o = self.orden(folio)
        if not o or o["numero_guia"] is None or pd.isna(o["numero_guia"]):
            return None
        return {"numero_guia": int(o["numero_guia"]), "fecha_emision": self._fecha_guia(folio)}

    @abstractmethod
    def _fecha_guia(self, folio):
        """Fecha y hora de emision de la guia de esa orden."""


# ---------------------------------------------------------------------------
# PostgreSQL (Supabase): llama a las funciones SQL
# ---------------------------------------------------------------------------

def _conectar_url(url):
    import psycopg  # solo aqui: las pruebas con SQLite no lo necesitan
    from psycopg.rows import dict_row

    # prepare_threshold=None: sin sentencias preparadas, para que funcione igual con el pooler de Supabase
    return psycopg.connect(url, autocommit=True, row_factory=dict_row, connect_timeout=10, prepare_threshold=None)


class RepoPostgres(Repositorio):
    modo = "postgres"

    def __init__(self, conectar):
        """conectar: funcion sin argumentos que devuelve una conexion psycopg abierta (autocommit, filas como dict)."""
        self._conectar = conectar
        self._con = None
        self._candado = threading.RLock()

    def __repr__(self):
        return "RepoPostgres()"  # nunca muestra la cadena de conexion

    def cerrar(self):
        with self._candado:
            if self._con is not None:
                try:
                    self._con.close()
                except Exception:  # noqa: BLE001 - cerrar nunca debe romper
                    pass
                self._con = None

    def _ejecutar(self, sql, params=(), reintentar=True):
        """Ejecuta una consulta. Una lectura se reintenta una vez con una conexion nueva si la anterior se corto;
        una escritura no (podria ejecutarse dos veces): antes de escribir se llama a _asegurar()."""
        import psycopg

        with self._candado:
            for intento in (1, 2):
                try:
                    if self._con is None or self._con.closed:
                        self._con = self._conectar()
                    cur = self._con.execute(sql, params)
                    return cur.fetchall() if cur.description else []
                except psycopg.errors.RaiseException as e:  # P0001: una regla del negocio dijo que no
                    raise ReglaDeNegocio(e.diag.message_primary or "No se pudo completar la operación.", e.diag.message_hint or "") from None
                except (psycopg.OperationalError, psycopg.InterfaceError) as e:
                    self.cerrar()  # una conexion cortada (se durmio, el pooler la cerro)
                    if intento == 2 or not reintentar:
                        raise ErrorDeBase("No se pudo conectar con la base de datos. Intenta de nuevo en unos segundos.") from None
                    del e
                except psycopg.Error:
                    raise ErrorDeBase("La base de datos no pudo completar la operación. Intenta de nuevo.") from None

    def _asegurar(self):
        """Antes de escribir: comprueba que la conexion sigue viva (y la reabre si no), para no reintentar una escritura."""
        self._ejecutar("select 1")

    def _escribir(self, sql, params):
        self._asegurar()
        return self._ejecutar(sql, params, reintentar=False)

    def _id_orden(self, folio):
        filas = self._ejecutar("select id_orden from public.v_ordenes_resumen where folio = %s", (folio,))
        if not filas:
            raise ReglaDeNegocio("Esa orden no existe. Elige otra.", "orden")
        return filas[0]["id_orden"]

    def clientes(self):
        return self._ejecutar("select id_cliente, razon_social from public.clientes order by razon_social")

    def usuarios(self):
        return self._ejecutar("select id_usuario, nombre, rol from public.usuarios where activo order by id_usuario")

    def ordenes(self):
        filas = self._ejecutar(
            f"select folio, tipo_movimiento, modalidad, motivo_retiro, estado, razon_social, numero_guia, skus_vigentes, "
            f"       (fecha_orden at time zone '{ZONA_HORARIA}') as fecha_orden "
            f"  from public.v_ordenes_resumen where folio is not null order by fecha_orden desc, folio desc"
        )
        return _ordenes_df(filas)

    def lineas(self, folio):
        filas = self._ejecutar(
            f"select id_detalle as id, sku, descripcion, estado_equipo, resultado_validacion as resultado, "
            f"       (ultima_modificacion at time zone '{ZONA_HORARIA}') as ultima_modificacion "
            f"  from public.v_detalle_orden where folio = %s and vigente order by id_detalle",
            (folio,),
        )
        return pd.DataFrame(filas, columns=COLUMNAS_LINEAS)

    def cambios(self, folio=None):
        donde, params = ("where folio = %s", (folio,)) if folio else ("", ())
        filas = self._ejecutar(
            f"select id_cambio as id, folio, sku_sale as sku_original, sku_entra as sku_nuevo, responsable, "
            f"       (fecha_hora_cambio at time zone '{ZONA_HORARIA}') as fecha_hora, motivo_cambio as motivo "
            f"  from public.v_historial_cambios {donde} order by id_cambio desc",
            params,
        )
        return pd.DataFrame(filas, columns=COLUMNAS_CAMBIOS)

    def buscar_equipos(self, texto, limite=30):
        patron = "%" + _escapar_like(limpiar(texto)) + "%"
        filas = self._ejecutar(
            "select sku, descripcion, estado from public.equipos "
            "where sku ilike %s escape '\\' or descripcion ilike %s escape '\\' order by sku limit %s",
            (patron, patron, int(limite)),
        )
        return pd.DataFrame(filas, columns=COLUMNAS_EQUIPOS)

    def crear_pedido(self, folio, id_cliente, id_usuario, tipo, modalidad, skus):
        p_tipo = _TIPO_A_BASE.get(tipo)
        base = _MODALIDAD_A_BASE.get(modalidad)
        self._escribir(
            "select public.crear_pedido(%s::text, %s::integer, %s::integer, %s::text, %s::text, %s::text, %s::text[])",
            (folio, id_cliente, id_usuario, p_tipo,
             base if p_tipo == "despacho" else None, base if p_tipo == "retiro" else None, list(skus or [])),
        )
        return limpiar(folio).upper()

    def validar(self, folio):
        self._escribir("select public.validar_pedido(%s::integer)", (self._id_orden(folio),))

    def registrar_cambio(self, folio, sku_sale, sku_entra, id_usuario, motivo):
        self._escribir(
            "select public.registrar_cambio(%s::integer, %s::text, %s::text, %s::integer, %s::text)",
            (self._id_orden(folio), sku_sale, sku_entra, id_usuario, motivo),
        )

    def preparar_guia(self, folio, id_usuario):
        self._escribir("select public.preparar_guia(%s::integer, %s::integer)", (self._id_orden(folio), id_usuario))
        return self.guia(folio)

    def _fecha_guia(self, folio):
        filas = self._ejecutar(
            f"select (fecha_emision at time zone '{ZONA_HORARIA}') as f from public.v_ordenes_resumen where folio = %s", (folio,)
        )
        return filas[0]["f"] if filas else None


# ---------------------------------------------------------------------------
# SQLite: mismo esquema, mismas reglas, para pruebas y desarrollo sin red
# ---------------------------------------------------------------------------

RUTA_ESQUEMA = Path(__file__).resolve().parent.parent / "supabase" / "schema.sql"

_DEMO_CLIENTES = [
    (10, "Constructora Andes SpA", "11.111.111-1", "Av. Matta 1200, Santiago"),
    (11, "Minera Cordillera S.A.", "22.222.222-2", "Camino a Farellones km 12, Lo Barnechea"),
]
_DEMO_USUARIOS = [
    (1, "Pedro Soto", "psoto@ejemplo.cl", "+56 9 1111 1111", "jefe_bodega", 1),
    (2, "Camila Rojas", "crojas@ejemplo.cl", "+56 9 2222 2222", "mantenimiento", 1),
]
_DEMO_EQUIPOS = [
    (501, "SD-63A20-0314", "Extensión 63 A x 20 m", "disponible", "bodega"),
    (502, "SD-63A20-0315", "Extensión 63 A x 20 m", "disponible", "bodega"),
    (503, "SD-63A20-0316", "Extensión 63 A x 20 m", "en_mantencion", "taller"),
    (504, "SD-32A10-0102", "Extensión 32 A x 10 m", "disponible", "bodega"),
    (505, "SD-32A10-0108", "Extensión 32 A x 10 m", "disponible", "bodega"),
    (506, "ST-0042", "Tablero", "disponible", "bodega"),
    (507, "MP-0107", "Manga perforada", "disponible", "bodega"),
]


class RepoSqlite(Repositorio):
    modo = "sqlite"

    def __init__(self, ruta=":memory:"):
        self._con = sqlite3.connect(str(ruta), check_same_thread=False, isolation_level=None)
        self._con.row_factory = sqlite3.Row
        self._con.execute("PRAGMA foreign_keys = ON")
        self._candado = threading.RLock()
        self._crear_esquema()

    def __repr__(self):
        return "RepoSqlite()"

    # -- preparacion ------------------------------------------------------
    def _crear_esquema(self):
        if self._con.execute("select count(*) from sqlite_master where name = 'ordenes'").fetchone()[0]:
            return
        self._con.executescript(RUTA_ESQUEMA.read_text(encoding="utf-8"))
        self._con.executemany("insert into clientes values (?, ?, ?, ?)", _DEMO_CLIENTES)
        self._con.executemany("insert into usuarios values (?, ?, ?, ?, ?, ?)", _DEMO_USUARIOS)
        self._con.executemany("insert into equipos values (?, ?, ?, ?, ?)", _DEMO_EQUIPOS)
        ahora = self._ahora()
        cols = "id_orden, id_cliente, id_usuario_carga, fecha_orden, tipo_movimiento, modalidad, motivo_retiro, estado, folio"
        self._con.execute(
            f"insert into ordenes ({cols}) values (3001, 10, 1, ?, 'despacho', 'convencional', null, 'pendiente', 'GUIA-2026-001')", (ahora,)
        )
        self._con.execute(
            f"insert into ordenes ({cols}) values (3002, 11, 1, ?, 'retiro', null, 'falla', 'pendiente', 'GUIA-2026-002')", (ahora,)
        )
        lineas = [(3001, s) for s in ("SD-63A20-0314", "SD-63A20-0315", "ST-0042", "MP-0107")] + [
            (3002, s) for s in ("SD-32A10-0102", "SD-63A20-9999", "ST-0042", "MP-0107")
        ]
        for i, (orden, sku) in enumerate(lineas, start=9001):
            self._con.execute(
                "insert into detalle_orden values (?, ?, null, ?, 'pendiente', 1)", (i, orden, sku)
            )

    @staticmethod
    def _ahora():
        return datetime.now().isoformat(sep=" ", timespec="seconds")

    @contextmanager
    def _transaccion(self):
        """Una operacion completa o nada, y de una en una (igual que el candado de las funciones SQL)."""
        with self._candado:
            self._con.execute("begin immediate")
            try:
                yield self._con
            except BaseException:
                self._con.execute("rollback")
                raise
            else:
                self._con.execute("commit")

    @staticmethod
    def _fallo(mensaje, campo=""):
        raise ReglaDeNegocio(mensaje, campo)

    def _consultar(self, sql, params=()):
        with self._candado:
            return [dict(f) for f in self._con.execute(sql, params).fetchall()]

    # -- lectura ----------------------------------------------------------
    def clientes(self):
        return self._consultar("select id_cliente, razon_social from clientes order by razon_social")

    def usuarios(self):
        return self._consultar("select id_usuario, nombre, rol from usuarios where activo order by id_usuario")

    def ordenes(self):
        filas = self._consultar(
            "select o.folio, o.tipo_movimiento, o.modalidad, o.motivo_retiro, o.estado, o.fecha_orden, c.razon_social, "
            "       g.numero_guia, (select count(*) from detalle_orden d where d.id_orden = o.id_orden and d.vigente) as skus_vigentes "
            "  from ordenes o left join clientes c on c.id_cliente = o.id_cliente "
            "  left join guias g on g.id_orden = o.id_orden "
            " where o.folio is not null order by o.fecha_orden desc, o.folio desc"
        )
        return _ordenes_df(filas)

    def lineas(self, folio):
        filas = self._consultar(
            "select d.id_detalle as id, d.sku_informado as sku, e.descripcion, e.estado as estado_equipo, "
            "       d.resultado_validacion as resultado, "
            "       (select max(r.fecha_hora_cambio) from registro_cambios r "
            "         where r.id_orden = d.id_orden and r.id_equipo_entra = d.id_equipo) as ultima_modificacion "
            "  from detalle_orden d join ordenes o on o.id_orden = d.id_orden left join equipos e on e.id_equipo = d.id_equipo "
            " where o.folio = ? and d.vigente order by d.id_detalle",
            (folio,),
        )
        df = pd.DataFrame(filas, columns=COLUMNAS_LINEAS)
        df["ultima_modificacion"] = pd.to_datetime(df["ultima_modificacion"])
        return df

    def cambios(self, folio=None):
        donde, params = ("where o.folio = ?", (folio,)) if folio else ("", ())
        filas = self._consultar(
            "select r.id_cambio as id, o.folio, r.sku_sale as sku_original, e.sku as sku_nuevo, u.nombre as responsable, "
            "       r.fecha_hora_cambio as fecha_hora, r.motivo_cambio as motivo "
            "  from registro_cambios r join ordenes o on o.id_orden = r.id_orden "
            "  join equipos e on e.id_equipo = r.id_equipo_entra join usuarios u on u.id_usuario = r.id_usuario "
            f" {donde} order by r.id_cambio desc",
            params,
        )
        df = pd.DataFrame(filas, columns=COLUMNAS_CAMBIOS)
        df["fecha_hora"] = pd.to_datetime(df["fecha_hora"])
        return df

    def buscar_equipos(self, texto, limite=30):
        patron = "%" + _escapar_like(limpiar(texto)) + "%"
        filas = self._consultar(
            "select sku, descripcion, estado from equipos "
            "where sku like ? escape '\\' or descripcion like ? escape '\\' order by sku limit ?",
            (patron, patron, int(limite)),
        )
        return pd.DataFrame(filas, columns=COLUMNAS_EQUIPOS)

    def _fecha_guia(self, folio):
        filas = self._consultar(
            "select g.fecha_emision from guias g join ordenes o on o.id_orden = g.id_orden where o.folio = ?", (folio,)
        )
        return pd.to_datetime(filas[0]["fecha_emision"]).to_pydatetime() if filas else None

    # -- escritura: las mismas reglas y mensajes que supabase/funciones.sql y mvp_funciones.sql ---------
    def _orden_de(self, con, folio):
        fila = con.execute("select id_orden from ordenes where folio = ?", (folio,)).fetchone()
        if fila is None:
            self._fallo("Esa orden no existe. Elige otra.", "orden")
        return fila[0]

    def _sin_guia(self, con, id_orden):
        if con.execute("select 1 from guias where id_orden = ?", (id_orden,)).fetchone():
            self._fallo("Esta orden ya tiene la guía preparada. Presiona Reiniciar demo para volver a empezar.", "orden")

    def crear_pedido(self, folio, id_cliente, id_usuario, tipo, modalidad, skus):
        v_folio = limpiar(folio).upper()
        v_skus = skus_limpios(skus)
        p_tipo = _TIPO_A_BASE.get(tipo)
        base = _MODALIDAD_A_BASE.get(modalidad)
        with self._transaccion() as con:
            if not _FOLIO.fullmatch(v_folio):
                self._fallo("El folio debe tener la forma GUIA-2026-001.", "folio")
            if con.execute("select 1 from ordenes where folio = ?", (v_folio,)).fetchone():
                self._fallo("Ya existe una orden con ese folio. Usa otro.", "folio")
            if id_cliente is None or not con.execute("select 1 from clientes where id_cliente = ?", (id_cliente,)).fetchone():
                self._fallo("Elige el cliente.", "cliente")
            if id_usuario is None or not con.execute("select 1 from usuarios where id_usuario = ? and activo", (id_usuario,)).fetchone():
                self._fallo("Elige quién carga el pedido.", "usuario")
            if not v_skus:
                self._fallo("Pega al menos un SKU, uno por línea. Ejemplo: SD-63A20-0314", "skus")
            if len(v_skus) > MAX_SKUS:
                self._fallo(
                    f"Hay {len(v_skus)} productos y el máximo es {MAX_SKUS}. Quita {len(v_skus) - MAX_SKUS} para continuar.", "skus"
                )
            if p_tipo is None:
                self._fallo("Elige el tipo de movimiento.", "tipo")
            if p_tipo == "despacho" and base not in ("convencional", "alternativo"):
                self._fallo("Elige la modalidad del despacho.", "modalidad")
            if p_tipo == "retiro" and base not in ("mantencion_preventiva", "falla"):
                self._fallo("Elige el motivo del retiro.", "motivo_retiro")

            id_orden = con.execute("select coalesce(max(id_orden), 3000) + 1 from ordenes").fetchone()[0]
            con.execute(
                "insert into ordenes (id_orden, id_cliente, id_usuario_carga, fecha_orden, tipo_movimiento, modalidad, "
                "motivo_retiro, estado, folio) values (?, ?, ?, ?, ?, ?, ?, 'pendiente', ?)",
                (id_orden, id_cliente, id_usuario, self._ahora(), p_tipo,
                 base if p_tipo == "despacho" else None, base if p_tipo == "retiro" else None, v_folio),
            )
            id_detalle = con.execute("select coalesce(max(id_detalle), 9000) from detalle_orden").fetchone()[0]
            for sku in v_skus:
                id_detalle += 1
                con.execute("insert into detalle_orden values (?, ?, null, ?, 'pendiente', 1)", (id_detalle, id_orden, sku))
        return v_folio

    def validar(self, folio):
        with self._transaccion() as con:
            id_orden = self._orden_de(con, folio)
            self._sin_guia(con, id_orden)
            if not con.execute("select 1 from detalle_orden where id_orden = ? and vigente", (id_orden,)).fetchone():
                self._fallo("El pedido no tiene productos. Cárgalo primero.", "skus")
            for linea in con.execute("select id_detalle, sku_informado from detalle_orden where id_orden = ? and vigente", (id_orden,)).fetchall():
                eq = con.execute("select id_equipo, estado from equipos where sku = ?", (linea["sku_informado"],)).fetchone()
                if eq is None:
                    resultado, id_equipo = "no_existe", None
                else:
                    resultado, id_equipo = ("ok" if eq["estado"] == "disponible" else "no_disponible"), eq["id_equipo"]
                con.execute(
                    "update detalle_orden set id_equipo = ?, resultado_validacion = ? where id_detalle = ?",
                    (id_equipo, resultado, linea["id_detalle"]),
                )
            hay_malas = con.execute(
                "select 1 from detalle_orden where id_orden = ? and vigente and resultado_validacion <> 'ok'", (id_orden,)
            ).fetchone()
            con.execute("update ordenes set estado = ? where id_orden = ?", ("bloqueada" if hay_malas else "validada", id_orden))

    def registrar_cambio(self, folio, sku_sale, sku_entra, id_usuario, motivo):
        v_sale, v_entra, v_motivo = limpiar(sku_sale).upper(), limpiar(sku_entra).upper(), limpiar(motivo)
        with self._transaccion() as con:
            id_orden = self._orden_de(con, folio)
            self._sin_guia(con, id_orden)
            if v_sale == "":
                self._fallo("Elige el equipo que sale.", "sale")
            linea = con.execute(
                "select id_detalle from detalle_orden where id_orden = ? and vigente and sku_informado = ?", (id_orden, v_sale)
            ).fetchone()
            if linea is None:
                self._fallo("Ese equipo no está en el pedido. Elige otro.", "sale")
            if v_entra == "":
                self._fallo("Elige el equipo que entra.", "entra")
            if v_entra == v_sale:
                self._fallo("El equipo que entra debe ser distinto del que sale.", "entra")
            entra = con.execute("select id_equipo, sku from equipos where sku = ?", (v_entra,)).fetchone()
            if entra is None:
                self._fallo("Ese SKU no existe en el inventario. Elige uno de la lista.", "entra")
            if con.execute(
                "select 1 from detalle_orden where id_orden = ? and vigente and sku_informado = ?", (id_orden, v_entra)
            ).fetchone():
                self._fallo("Ese equipo ya está en el pedido. Elige otro.", "entra")
            if v_motivo == "":
                self._fallo("Elige el motivo del cambio.", "motivo")
            if len(v_motivo) > 200:
                self._fallo("El motivo es muy largo: máximo 200 caracteres.", "motivo")
            if id_usuario is None or not con.execute("select 1 from usuarios where id_usuario = ? and activo", (id_usuario,)).fetchone():
                self._fallo("Elige quién registra el cambio.", "responsable")

            con.execute("update detalle_orden set vigente = 0 where id_detalle = ?", (linea["id_detalle"],))
            nuevo_id = con.execute("select coalesce(max(id_detalle), 9000) + 1 from detalle_orden").fetchone()[0]
            con.execute("insert into detalle_orden values (?, ?, ?, ?, 'pendiente', 1)", (nuevo_id, id_orden, entra["id_equipo"], entra["sku"]))
            sale = con.execute("select id_equipo from equipos where sku = ?", (v_sale,)).fetchone()
            con.execute(
                "insert into registro_cambios (id_cambio, id_orden, sku_sale, id_equipo_sale, id_equipo_entra, id_usuario, "
                "fecha_hora_cambio, motivo_cambio) values ((select coalesce(max(id_cambio), 0) + 1 from registro_cambios), ?, ?, ?, ?, ?, ?, ?)",
                (id_orden, v_sale, sale["id_equipo"] if sale else None, entra["id_equipo"], id_usuario, self._ahora(), v_motivo),
            )
            con.execute("update ordenes set estado = 'pendiente' where id_orden = ?", (id_orden,))

    def preparar_guia(self, folio, id_usuario):
        with self._transaccion() as con:
            id_orden = self._orden_de(con, folio)
            self._sin_guia(con, id_orden)
            if id_usuario is None or not con.execute(
                "select 1 from usuarios where id_usuario = ? and activo and rol = 'jefe_bodega'", (id_usuario,)
            ).fetchone():
                self._fallo("Solo el jefe de bodega puede preparar la guía.", "usuario")
            total, pendientes, malos = con.execute(
                "select count(*), coalesce(sum(l.resultado_validacion = 'pendiente'), 0), "
                "       coalesce(sum(e.id_equipo is null or e.estado <> 'disponible'), 0) "
                "  from detalle_orden l left join equipos e on e.sku = l.sku_informado where l.id_orden = ? and l.vigente",
                (id_orden,),
            ).fetchone()
            if total == 0:
                self._fallo("El pedido no tiene productos. Cárgalo primero.", "productos")
            if pendientes > 0:
                self._fallo("Valida el pedido antes de preparar la guía.", "productos")
            if malos > 0:
                self._fallo(f"Corrige {malos} {'producto' if malos == 1 else 'productos'} para continuar.", "productos")
            numero = con.execute("select coalesce(max(numero_guia), 15229) + 1 from guias").fetchone()[0]
            con.execute(
                "insert into guias (id_guia, id_orden, id_usuario_emite, numero_guia, fecha_emision, archivo_pdf) "
                "values ((select coalesce(max(id_guia), 69) + 1 from guias), ?, ?, ?, ?, null)",
                (id_orden, id_usuario, numero, self._ahora()),
            )
            con.execute("update ordenes set estado = 'emitida' where id_orden = ?", (id_orden,))
        return self.guia(folio)


# ---------------------------------------------------------------------------
# Eleccion de la implementacion
# ---------------------------------------------------------------------------

RUTA_ENV = Path(__file__).resolve().parent.parent / ".env"


def cargar_env(ruta=None):
    """
    Lee el archivo .env local (ignorado por git) y pone sus variables en el entorno SIN pisar las que ya existan:
    en el hosting mandan los secretos del hosting. Streamlit no lee .env por si solo. No imprime ni guarda nada.
    BODEGA_NO_CARGAR_ENV=1 lo desactiva (las pruebas lo usan para no tocar nunca el .env ni la base de verdad).
    """
    if os.getenv("BODEGA_NO_CARGAR_ENV"):
        return
    archivo = Path(ruta) if ruta else RUTA_ENV
    if not archivo.is_file():
        return
    for linea in archivo.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = (x.strip() for x in linea.split("=", 1))
        if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in "\"'":
            valor = valor[1:-1]
        if clave and valor and clave not in os.environ:
            os.environ[clave] = valor


def abrir(ruta_sqlite=None):
    """PostgreSQL si DATABASE_URL esta definida; si no, SQLite local (BODEGA_MVP_DB o bodega_mvp.db)."""
    url = os.getenv("DATABASE_URL", "").strip()
    if url:
        return RepoPostgres(lambda: _conectar_url(url))
    return RepoSqlite(ruta_sqlite or os.getenv("BODEGA_MVP_DB") or "bodega_mvp.db")
