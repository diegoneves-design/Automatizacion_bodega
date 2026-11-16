-- Datos del tablero de inventario (solo PostgreSQL / Supabase). Ejecutar despues de inventario.sql y funciones.sql.
-- Se puede volver a ejecutar sin error y no cambia ningun dato.
--
-- inventario_dashboard() devuelve UN jsonb con todo lo que el tablero necesita; el navegador lo carga una vez y filtra en memoria.
--   equipos      columnas + filas, SOLO estas 9 columnas: id_equipo, sku, descripcion, familia, categoria, estado,
--                situacion_origen, capacidad_valor, capacidad_unidad (equipos reales: id_equipo >= 1000, sin los de demo)
--   extensiones  columnas + filas: sku, corriente, largo_m
--   actividad    conteos de las ordenes del MVP por estado y de los cambios por motivo
-- Nunca devuelve nombres de personas, correos, clientes ni textos libres: el motivo de un cambio solo sale si es uno de los
-- tres de la lista del prototipo; cualquier otro texto se cuenta como 'Otro'.
-- Se formatea en columnas y filas (no una lista de objetos) para que el JSON pese menos.

create or replace function public.inventario_dashboard()
returns jsonb
language sql
stable
security definer
set search_path = public
as $$
  select jsonb_build_object(
    'equipos', jsonb_build_object(
      'columnas', jsonb_build_array('id_equipo', 'sku', 'descripcion', 'familia', 'categoria', 'estado',
                                    'situacion_origen', 'capacidad_valor', 'capacidad_unidad'),
      'filas', coalesce((
        select jsonb_agg(
                 jsonb_build_array(e.id_equipo, e.sku, e.descripcion, e.familia, e.categoria, e.estado,
                                   e.situacion_origen, e.capacidad_valor, e.capacidad_unidad)
                 order by e.id_equipo)
        from public.equipos e
        where e.id_equipo >= 1000
      ), '[]'::jsonb)
    ),
    'extensiones', jsonb_build_object(
      'columnas', jsonb_build_array('sku', 'corriente', 'largo_m'),
      'filas', coalesce((
        select jsonb_agg(jsonb_build_array(x.sku, x.corriente, x.largo_m) order by x.id)
        from public.extensiones_electricas x
      ), '[]'::jsonb)
    ),
    'actividad', jsonb_build_object(
      'ordenes_por_estado', coalesce((
        select jsonb_object_agg(t.estado, t.n)
        from (select o.estado, count(*) as n from public.ordenes o group by o.estado) t
      ), '{}'::jsonb),
      'cambios_por_motivo', coalesce((
        select jsonb_object_agg(t.motivo, t.n)
        from (
          select case when c.motivo_cambio in ('Código mal digitado', 'No pasó la prueba eléctrica', 'Equipo en mantención')
                      then c.motivo_cambio else 'Otro' end as motivo,
                 count(*) as n
          from public.registro_cambios c
          group by 1
        ) t
      ), '{}'::jsonb)
    )
  );
$$;

revoke all on function public.inventario_dashboard() from public;
grant execute on function public.inventario_dashboard() to anon, authenticated;

notify pgrst, 'reload schema';
