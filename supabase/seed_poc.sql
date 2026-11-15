-- 4/4 Datos de la demo del prototipo (solo PostgreSQL / Supabase). Ejecutar despues de funciones.sql.
-- Todos los datos son ficticios.
--
-- Deja EXACTAMENTE el estado inicial que usa la prueba de usuarios (docs/prueba-usuarios.md):
--   orden 3001: despacho convencional, 4 productos, todos se pueden despachar.
--   orden 3002: retiro por falla, con un SKU que no existe (SD-63A20-9999).
-- Reemplaza cualquier dato anterior (por ejemplo, el de seed_ejemplo.sql). Se puede volver a ejecutar.

truncate table guias, registro_cambios, detalle_orden, ordenes, equipos, usuarios, clientes;

insert into clientes (id_cliente, razon_social, rut, direccion) values
  (10, 'Constructora Andes SpA', '11.111.111-1', 'Av. Matta 1200, Santiago'),
  (11, 'Minera Cordillera S.A.', '22.222.222-2', 'Camino a Farellones km 12, Lo Barnechea');

insert into usuarios (id_usuario, nombre, correo, telefono, rol, activo) values
  (1, 'Pedro Soto',   'psoto@ejemplo.cl',  '+56 9 1111 1111', 'jefe_bodega',   true),
  (2, 'Camila Rojas', 'crojas@ejemplo.cl', '+56 9 2222 2222', 'mantenimiento', true);

-- Inventario al inicio del dia: todo disponible en bodega, salvo el 503, que esta en el taller
insert into equipos (id_equipo, sku, descripcion, estado, ubicacion) values
  (501, 'SD-63A20-0314', 'Extensión 63 A x 20 m', 'disponible',    'bodega'),
  (502, 'SD-63A20-0315', 'Extensión 63 A x 20 m', 'disponible',    'bodega'),
  (503, 'SD-63A20-0316', 'Extensión 63 A x 20 m', 'en_mantencion', 'taller'),
  (504, 'SD-32A10-0102', 'Extensión 32 A x 10 m', 'disponible',    'bodega'),
  (505, 'SD-32A10-0108', 'Extensión 32 A x 10 m', 'disponible',    'bodega'),
  (506, 'ST-0042',       'Tablero',               'disponible',    'bodega'),
  (507, 'MP-0107',       'Manga perforada',       'disponible',    'bodega');

-- Las dos ordenes y sus productos
select public.reiniciar_demo();
