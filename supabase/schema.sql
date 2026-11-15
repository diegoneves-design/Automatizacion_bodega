-- Modelo de datos de Automatizacion_bodega (docs/datos/estructura_datos.md).
-- Compatible con PostgreSQL (Supabase) y con SQLite, para poder probarlo sin internet.
-- Las reglas del negocio viven aqui como restricciones: la base es la ultima capa de validacion.

create table clientes (
  id_cliente   integer primary key,
  razon_social text not null,
  rut          text not null,
  direccion    text not null
);

create table usuarios (
  id_usuario integer primary key,
  nombre     text    not null,
  correo     text    not null unique,
  telefono   text,
  rol        text    not null check (rol in ('jefe_bodega', 'mantenimiento', 'comercial', 'gerente')),
  activo     boolean not null default true
);

create table equipos (
  id_equipo   integer primary key,
  sku         text not null unique,
  descripcion text not null,
  estado      text not null check (estado in ('disponible', 'arrendado', 'en_mantencion', 'fuera_servicio')),
  ubicacion   text not null check (ubicacion in ('bodega', 'cliente', 'taller')),
  -- estado y ubicacion cuentan la misma historia (el equipo arrendado esta en el cliente, etc.)
  check (
    (estado = 'disponible'    and ubicacion = 'bodega') or
    (estado = 'arrendado'     and ubicacion = 'cliente') or
    (estado = 'en_mantencion' and ubicacion = 'taller') or
    (estado = 'fuera_servicio')
  )
);

create table ordenes (
  id_orden         integer primary key,
  id_cliente       integer   not null references clientes (id_cliente),
  id_usuario_carga integer   not null references usuarios (id_usuario),
  fecha_orden      timestamp not null,
  tipo_movimiento  text      not null check (tipo_movimiento in ('despacho', 'retiro')),
  modalidad        text      check (modalidad in ('convencional', 'alternativo')),
  motivo_retiro    text      check (motivo_retiro in ('mantencion_preventiva', 'falla')),
  estado           text      not null check (estado in ('pendiente', 'bloqueada', 'validada', 'emitida')),
  -- modalidad solo existe en el despacho y motivo_retiro solo en el retiro; cada uno es obligatorio en el suyo
  check (
    (tipo_movimiento = 'despacho' and modalidad is not null and motivo_retiro is null) or
    (tipo_movimiento = 'retiro'   and motivo_retiro is not null and modalidad is null)
  )
);

create table detalle_orden (
  id_detalle           integer primary key,
  id_orden             integer not null references ordenes (id_orden),
  id_equipo            integer references equipos (id_equipo),
  sku_informado        text    not null,
  resultado_validacion text    not null check (resultado_validacion in ('pendiente', 'ok', 'no_existe', 'no_disponible')),
  vigente              boolean not null default true,
  -- un SKU que no existe no tiene equipo, y uno que existe si lo tiene (salvo que aun este pendiente)
  check (
    (resultado_validacion = 'no_existe' and id_equipo is null) or
    (resultado_validacion = 'pendiente') or
    (resultado_validacion in ('ok', 'no_disponible') and id_equipo is not null)
  )
);

create table guias (
  id_guia          integer primary key,
  id_orden         integer   not null unique references ordenes (id_orden),
  id_usuario_emite integer   not null references usuarios (id_usuario),
  numero_guia      integer   not null unique,
  fecha_emision    timestamp not null,
  archivo_pdf      text
);

create table registro_cambios (
  id_cambio         integer primary key,
  id_orden          integer   not null references ordenes (id_orden),
  id_equipo_sale    integer   not null references equipos (id_equipo),
  id_equipo_entra   integer   not null references equipos (id_equipo),
  id_usuario        integer   not null references usuarios (id_usuario),
  fecha_hora_cambio timestamp not null,
  -- el motivo es obligatorio y no puede ser solo espacios
  motivo_cambio     text      not null check (length(trim(motivo_cambio)) > 0),
  check (id_equipo_sale <> id_equipo_entra)
);
