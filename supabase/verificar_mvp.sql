-- Verificacion del MVP (solo PostgreSQL / Supabase). Solo LEE: no cambia ningun dato ni permiso.
-- Ejecutar en el editor SQL de Supabase despues de los cinco archivos del MVP (ver docs/mvp-supabase.md).
-- Cada fila trae lo esperado y lo real. Si alguna dice FALLA, avisa antes de seguir.

with
datos as (
  select
    (select count(*) from public.equipos where id_equipo >= 1000)                         as equipos_reales,
    (select count(*) from public.extensiones_electricas)                                  as extensiones,
    (select count(*) from public.equipos where id_equipo between 501 and 507)            as equipos_demo,
    (select count(*) from public.ordenes where id_orden in (3001, 3002) and folio in ('GUIA-2026-001', 'GUIA-2026-002')) as ordenes_demo_con_folio
),
rol as (
  select * from pg_roles where rolname = 'app_mvp'
),
tablas as (
  select unnest(array['clientes', 'usuarios', 'equipos', 'ordenes', 'detalle_orden', 'guias', 'registro_cambios',
                      'extensiones_electricas']) as t
),
funciones as (
  select * from (values
    ('public.cargar_pedido(integer, text, text, text, text[])', true),
    ('public.validar_pedido(integer)',                          true),
    ('public.registrar_cambio(integer, text, text, integer, text)', true),
    ('public.preparar_guia(integer, integer)',                  true),
    ('public.crear_pedido(text, integer, integer, text, text, text, text[])', true),
    ('public.reiniciar_demo()',                                 false),
    ('public.inventario_dashboard()',                           true),
    ('public._fallo(text, text)',                               false),
    ('public._limpiar(text)',                                   false),
    ('public._skus_limpios(text[])',                            false)
  ) as f(firma, esperado)
),
comprobaciones as (
  -- Los datos que ya estaban
  select 'Equipos reales (id >= 1000)' as comprobacion, '1617' as esperado, equipos_reales::text as real from datos
  union all select 'Extensiones electricas', '319', extensiones::text from datos
  union all select 'Equipos de demo (501 a 507)', '7', equipos_demo::text from datos
  union all select 'Ordenes 3001 y 3002 con su folio', '2', ordenes_demo_con_folio::text from datos

  -- El rol existe y es limitado
  union all select 'El rol app_mvp existe', 'true', exists (select 1 from rol)::text
  union all select 'app_mvp no es superusuario ni crea roles ni bases', 'false',
         coalesce((select (rolsuper or rolcreaterole or rolcreatedb)::text from rol), 'sin rol')
  union all select 'app_mvp no se salta la RLS (bypassrls)', 'false', coalesce((select rolbypassrls::text from rol), 'sin rol')
  union all select 'app_mvp puede iniciar sesion', 'true', coalesce((select rolcanlogin::text from rol), 'sin rol')
  union all select 'app_mvp tiene limite de conexiones (5)', '5', coalesce((select rolconnlimit::text from rol), 'sin rol')
  union all select 'app_mvp tiene statement_timeout', 'true',
         coalesce((select (array_to_string(rolconfig, ',') like '%statement_timeout=%')::text from rol), 'sin rol')
  union all select 'app_mvp tiene search_path fijo', 'true',
         coalesce((select (array_to_string(rolconfig, ',') like '%search_path=%')::text from rol), 'sin rol')
  union all select 'app_mvp NO puede crear objetos en public', 'false',
         has_schema_privilege('app_mvp', 'public', 'create')::text

  -- Sin escritura directa en ninguna tabla (debe dar 0 en cada una)
  union all
  select 'Escritura directa de app_mvp en ' || t, 'false',
         (has_table_privilege('app_mvp', 'public.' || t, 'insert') or has_table_privilege('app_mvp', 'public.' || t, 'update')
          or has_table_privilege('app_mvp', 'public.' || t, 'delete') or has_table_privilege('app_mvp', 'public.' || t, 'truncate')
          or has_any_column_privilege('app_mvp', 'public.' || t, 'insert') or has_any_column_privilege('app_mvp', 'public.' || t, 'update'))::text
    from tablas

  -- Datos personales que no se ven
  union all select 'app_mvp NO lee usuarios.correo', 'false', has_column_privilege('app_mvp', 'public.usuarios', 'correo', 'select')::text
  union all select 'app_mvp NO lee usuarios.telefono', 'false', has_column_privilege('app_mvp', 'public.usuarios', 'telefono', 'select')::text
  union all select 'app_mvp NO lee clientes.rut', 'false', has_column_privilege('app_mvp', 'public.clientes', 'rut', 'select')::text
  union all select 'app_mvp NO lee clientes.direccion', 'false', has_column_privilege('app_mvp', 'public.clientes', 'direccion', 'select')::text
  union all select 'app_mvp SI lee usuarios.nombre', 'true', has_column_privilege('app_mvp', 'public.usuarios', 'nombre', 'select')::text

  -- La clave publicable (anon) tampoco ve datos personales de clientes ni de usuarios
  union all select 'anon NO lee clientes.rut', 'false', has_column_privilege('anon', 'public.clientes', 'rut', 'select')::text
  union all select 'anon NO lee clientes.direccion', 'false', has_column_privilege('anon', 'public.clientes', 'direccion', 'select')::text
  union all select 'anon NO lee usuarios.correo', 'false', has_column_privilege('anon', 'public.usuarios', 'correo', 'select')::text
  union all select 'anon NO lee usuarios.telefono', 'false', has_column_privilege('anon', 'public.usuarios', 'telefono', 'select')::text
  union all select 'anon SI lee clientes.razon_social (lo usa el prototipo)', 'true', has_column_privilege('anon', 'public.clientes', 'razon_social', 'select')::text

  -- Funciones: solo las del flujo
  union all select 'app_mvp ejecuta ' || firma, esperado::text, has_function_privilege('app_mvp', firma, 'execute')::text from funciones

  -- La API publica (anon) no ve nada de lo nuevo
  union all select 'anon NO ejecuta crear_pedido', 'false',
         has_function_privilege('anon', 'public.crear_pedido(text, integer, integer, text, text, text, text[])', 'execute')::text
  union all select 'anon NO lee v_ordenes_resumen', 'false', has_table_privilege('anon', 'public.v_ordenes_resumen', 'select')::text
  union all select 'anon NO lee v_detalle_orden', 'false', has_table_privilege('anon', 'public.v_detalle_orden', 'select')::text
  union all select 'anon NO lee v_historial_cambios', 'false', has_table_privilege('anon', 'public.v_historial_cambios', 'select')::text
  union all select 'authenticated NO ejecuta crear_pedido', 'false',
         has_function_privilege('authenticated', 'public.crear_pedido(text, integer, integer, text, text, text, text[])', 'execute')::text

  -- Las politicas de lectura del rol existen en las 7 tablas del flujo
  union all select 'Politicas de lectura de app_mvp (7 tablas)', '7',
         (select count(*) from pg_policies where schemaname = 'public' and policyname = 'lectura app_mvp' and 'app_mvp' = any(roles))::text
)
select comprobacion, esperado, real, case when esperado = real then 'OK' else 'FALLA' end as resultado
  from comprobaciones
 order by (esperado = real), comprobacion;
