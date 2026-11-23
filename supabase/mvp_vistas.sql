-- MVP 4/5. Vistas de solo lectura del MVP (solo PostgreSQL / Supabase). Ejecutar despues de mvp_funciones.sql.
-- Se puede volver a ejecutar sin error y no cambia ningun dato.
--
-- Son consultas ya armadas (con uniones y conteos) que la aplicacion lee. Corren con los permisos de quien las
-- consulta (security_invoker): el rol del MVP solo ve lo que sus permisos y politicas le dejan ver, asi que una vista
-- no abre nada que las tablas tengan cerrado. Ninguna se le da a anon ni a authenticated.

-- Una fila por orden: lo que muestra la lista de ordenes.
create or replace view public.v_ordenes_resumen with (security_invoker = true) as
select o.id_orden,
       o.folio,
       o.tipo_movimiento,
       o.modalidad,
       o.motivo_retiro,
       o.estado,
       o.fecha_orden,
       o.id_cliente,
       c.razon_social,
       count(d.id_detalle) filter (where d.vigente) as skus_vigentes,
       g.numero_guia,
       g.fecha_emision
  from public.ordenes o
  left join public.clientes c on c.id_cliente = o.id_cliente
  left join public.detalle_orden d on d.id_orden = o.id_orden
  left join public.guias g on g.id_orden = o.id_orden
 group by o.id_orden, o.folio, o.tipo_movimiento, o.modalidad, o.motivo_retiro, o.estado, o.fecha_orden,
          o.id_cliente, c.razon_social, g.numero_guia, g.fecha_emision;

-- Una fila por linea del pedido, con el equipo y la ultima vez que se cambio.
create or replace view public.v_detalle_orden with (security_invoker = true) as
select d.id_detalle,
       d.id_orden,
       o.folio,
       d.sku_informado as sku,
       e.descripcion,
       e.estado as estado_equipo,
       d.resultado_validacion,
       d.vigente,
       (select max(r.fecha_hora_cambio)
          from public.registro_cambios r
         where r.id_orden = d.id_orden and r.id_equipo_entra = d.id_equipo) as ultima_modificacion
  from public.detalle_orden d
  join public.ordenes o on o.id_orden = d.id_orden
  left join public.equipos e on e.id_equipo = d.id_equipo;

-- Los cambios de ultima hora, con el SKU que sale, el que entra y quien los hizo.
create or replace view public.v_historial_cambios with (security_invoker = true) as
select r.id_cambio,
       r.id_orden,
       o.folio,
       r.sku_sale,
       e.sku as sku_entra,
       e.descripcion as descripcion_entra,
       u.nombre as responsable,
       r.fecha_hora_cambio,
       r.motivo_cambio
  from public.registro_cambios r
  join public.ordenes o on o.id_orden = r.id_orden
  join public.equipos e on e.id_equipo = r.id_equipo_entra
  join public.usuarios u on u.id_usuario = r.id_usuario;

-- Nadie las lee desde la API publica (Supabase da permisos por omision a lo nuevo, asi que se quitan de forma
-- explicita). El permiso para el rol del MVP esta en mvp_rol.sql.
revoke all on public.v_ordenes_resumen, public.v_detalle_orden, public.v_historial_cambios from public, anon, authenticated;
