-- Datos de ejemplo (solo para comprobar el modelo; para la demo del prototipo usar seed_poc.sql).
-- Datos de ejemplo de docs/datos/estructura_datos.md, seccion 4: una misma manana de bodega.
-- Todos son ficticios (nombres, correos, telefonos y RUT de ejemplo).

insert into clientes (id_cliente, razon_social, rut, direccion) values
  (10, 'Constructora Andes SpA', '11.111.111-1', 'Av. Matta 1200, Santiago'),
  (11, 'Minera Cordillera S.A.', '22.222.222-2', 'Camino a Farellones km 12, Lo Barnechea');

insert into usuarios (id_usuario, nombre, correo, telefono, rol, activo) values
  (1, 'Pedro Soto',   'psoto@ejemplo.cl',  '+56 9 1111 1111', 'jefe_bodega',   true),
  (2, 'Camila Rojas', 'crojas@ejemplo.cl', '+56 9 2222 2222', 'mantenimiento', true);

-- estado y ubicacion al final de la manana
insert into equipos (id_equipo, sku, descripcion, estado, ubicacion) values
  (501, 'SD-63A20-0314', 'Extensión 63 A x 20 m', 'arrendado',     'cliente'),
  (502, 'SD-63A20-0315', 'Extensión 63 A x 20 m', 'arrendado',     'cliente'),
  (503, 'SD-63A20-0316', 'Extensión 63 A x 20 m', 'en_mantencion', 'taller'),
  (504, 'SD-32A10-0102', 'Extensión 32 A x 10 m', 'arrendado',     'cliente'),
  (505, 'SD-32A10-0108', 'Extensión 32 A x 10 m', 'en_mantencion', 'taller'),
  (507, 'MP-0107',       'Manga perforada',       'disponible',    'bodega');

insert into ordenes (id_orden, id_cliente, id_usuario_carga, fecha_orden, tipo_movimiento, modalidad, motivo_retiro, estado) values
  (3001, 10, 1, '2026-10-05 08:15:00', 'despacho', 'convencional', null,                    'emitida'),
  (3002, 11, 1, '2026-10-05 09:40:00', 'retiro',   null,           'falla',                 'bloqueada'),
  (3003, 10, 1, '2026-10-05 10:30:00', 'retiro',   null,           'mantencion_preventiva', 'emitida');

insert into detalle_orden (id_detalle, id_orden, id_equipo, sku_informado, resultado_validacion, vigente) values
  (9001, 3001, 501,  'SD-63A20-0314', 'ok',            true),
  (9002, 3001, 503,  'SD-63A20-0316', 'no_disponible', false),
  (9003, 3001, 502,  'SD-63A20-0315', 'ok',            true),
  (9004, 3002, 504,  'SD-32A10-0102', 'ok',            true),
  (9005, 3002, null, 'SD-63A20-9999', 'no_existe',     true),
  (9006, 3003, 507,  'MP-0107',       'ok',            false),
  (9007, 3003, 505,  'SD-32A10-0108', 'ok',            true);

insert into guias (id_guia, id_orden, id_usuario_emite, numero_guia, fecha_emision, archivo_pdf) values
  (70, 3001, 1, 15230, '2026-10-05 10:02:00', 'guia_15230.pdf'),
  (71, 3003, 1, 15231, '2026-10-05 11:30:00', null);

insert into registro_cambios (id_cambio, id_orden, sku_sale, id_equipo_sale, id_equipo_entra, id_usuario, fecha_hora_cambio, motivo_cambio) values
  (1, 3001, 'SD-63A20-0316', 503, 502, 2, '2026-10-05 09:55:00', 'Equipo en mantención'),
  (2, 3003, 'MP-0107',       507, 505, 1, '2026-10-05 11:10:00', 'Código mal digitado en el pedido');
