-- 3/4 Funciones (solo PostgreSQL / Supabase). Ejecutar despues de schema.sql y acceso.sql.
--
-- Son la capa de "servidor" de la prueba de concepto: la pagina las llama con supabase.rpc(...) y ellas
-- validan TODO de nuevo antes de guardar, aunque el navegador ya lo haya revisado. Las restricciones de
-- schema.sql son la tercera capa.
--
-- Cuando una regla falla se lanza un error con codigo P0001, el mensaje exacto que ve la persona (message) y el
-- campo de la pantalla al que corresponde (hint). Cualquier otro error es un problema del sistema.
--
-- Todas corren con los permisos del dueno (security definer) y fijan search_path para que no se puedan engañar.

-- ---------------------------------------------------------------------------------------------------------
-- Ayuda interna (no se expone a la API)
-- ---------------------------------------------------------------------------------------------------------
create or replace function public._fallo(p_mensaje text, p_campo text default '')
returns void
language plpgsql
set search_path = public
as $$
begin
  raise exception '%', p_mensaje using errcode = 'P0001', hint = coalesce(p_campo, '');
end;
$$;

-- Quita espacios, tabulaciones, saltos de linea y espacios duros de los extremos. btrim() solo quita espacios
-- normales, y una linea con solo una tabulacion pasaria por texto.
create or replace function public._limpiar(p_texto text)
returns text
language sql
immutable
set search_path = public
as $$
  select btrim(coalesce(p_texto, ''), E' \t\r\n\f\v' || chr(160));
$$;

-- ---------------------------------------------------------------------------------------------------------
-- cargar_pedido: crea las lineas del pedido (HU-02). Reemplaza lo que hubiera cargado antes para esa orden.
-- ---------------------------------------------------------------------------------------------------------
create or replace function public.cargar_pedido(
  p_id_orden      integer,
  p_tipo          text,
  p_modalidad     text,
  p_motivo_retiro text,
  p_skus          text[]
)
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
  c_max constant integer := 60;  -- maximo de productos por guia en el ERP
  v_skus text[];
  v_sku  text;
  v_n    integer;
  v_id   integer;
begin
  -- Limpieza: mayusculas, sin espacios, sin lineas vacias ni repetidos (se conserva el orden)
  select coalesce(array_agg(s.sku order by s.primero), '{}')
    into v_skus
    from (
      select upper(_limpiar(t.x)) as sku, min(t.ord) as primero
        from unnest(coalesce(p_skus, '{}'::text[])) with ordinality as t(x, ord)
       where _limpiar(t.x) <> ''
       group by upper(_limpiar(t.x))
    ) s;
  v_n := coalesce(array_length(v_skus, 1), 0);

  if not exists (select 1 from ordenes where id_orden = p_id_orden) then
    perform _fallo('Esa orden no existe. Elige otra.', 'orden');
  end if;
  if exists (select 1 from guias where id_orden = p_id_orden) then
    perform _fallo('Esta orden ya tiene la guía preparada. Presiona Reiniciar demo para volver a empezar.', 'orden');
  end if;
  if v_n = 0 then
    perform _fallo('Pega al menos un SKU, uno por línea. Ejemplo: SD-63A20-0314', 'skus');
  end if;
  if v_n > c_max then
    perform _fallo(format('Hay %s productos y el máximo es %s. Quita %s para continuar.', v_n, c_max, v_n - c_max), 'skus');
  end if;
  if p_tipo is null or p_tipo not in ('despacho', 'retiro') then
    perform _fallo('Elige el tipo de movimiento.', 'tipo');
  end if;
  if p_tipo = 'despacho' and (p_modalidad is null or p_modalidad not in ('convencional', 'alternativo')) then
    perform _fallo('Elige la modalidad del despacho.', 'modalidad');
  end if;
  if p_tipo = 'retiro' and (p_motivo_retiro is null or p_motivo_retiro not in ('mantencion_preventiva', 'falla')) then
    perform _fallo('Elige el motivo del retiro.', 'motivo_retiro');
  end if;

  perform pg_advisory_xact_lock(7001);

  update ordenes
     set tipo_movimiento = p_tipo,
         modalidad       = case when p_tipo = 'despacho' then p_modalidad end,
         motivo_retiro   = case when p_tipo = 'retiro'   then p_motivo_retiro end,
         estado          = 'pendiente'
   where id_orden = p_id_orden;

  delete from registro_cambios where id_orden = p_id_orden;
  delete from detalle_orden    where id_orden = p_id_orden;

  select coalesce(max(id_detalle), 9000) into v_id from detalle_orden;
  foreach v_sku in array v_skus loop
    v_id := v_id + 1;
    insert into detalle_orden (id_detalle, id_orden, id_equipo, sku_informado, resultado_validacion, vigente)
    values (v_id, p_id_orden, null, v_sku, 'pendiente', true);
  end loop;
end;
$$;

-- ---------------------------------------------------------------------------------------------------------
-- validar_pedido: contrasta cada linea vigente con el inventario (HU-01).
-- ---------------------------------------------------------------------------------------------------------
create or replace function public.validar_pedido(p_id_orden integer)
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  if not exists (select 1 from ordenes where id_orden = p_id_orden) then
    perform _fallo('Esa orden no existe. Elige otra.', 'orden');
  end if;
  if exists (select 1 from guias where id_orden = p_id_orden) then
    perform _fallo('Esta orden ya tiene la guía preparada. Presiona Reiniciar demo para volver a empezar.', 'orden');
  end if;
  if not exists (select 1 from detalle_orden where id_orden = p_id_orden and vigente) then
    perform _fallo('El pedido no tiene productos. Cárgalo primero.', 'skus');
  end if;

  update detalle_orden d
     set id_equipo = x.id_equipo,
         resultado_validacion = case
           when x.id_equipo is null     then 'no_existe'
           when x.estado <> 'disponible' then 'no_disponible'
           else 'ok'
         end
    from (
      select l.id_detalle, e.id_equipo, e.estado
        from detalle_orden l
        left join equipos e on e.sku = l.sku_informado
       where l.id_orden = p_id_orden and l.vigente
    ) x
   where d.id_detalle = x.id_detalle;

  update ordenes
     set estado = case
       when exists (select 1 from detalle_orden
                     where id_orden = p_id_orden and vigente and resultado_validacion <> 'ok')
       then 'bloqueada' else 'validada' end
   where id_orden = p_id_orden;
end;
$$;

-- ---------------------------------------------------------------------------------------------------------
-- registrar_cambio: reemplaza un equipo del pedido y deja el registro (HU-03, HU-04).
-- El motivo es obligatorio. La linea anterior no se borra: queda como no vigente.
-- ---------------------------------------------------------------------------------------------------------
create or replace function public.registrar_cambio(
  p_id_orden   integer,
  p_sku_sale   text,
  p_sku_entra  text,
  p_id_usuario integer,
  p_motivo     text
)
returns void
language plpgsql
security definer
set search_path = public
as $$
declare
  v_sale    text := upper(_limpiar(p_sku_sale));
  v_entra   text := upper(_limpiar(p_sku_entra));
  v_motivo  text := _limpiar(p_motivo);
  v_linea   detalle_orden%rowtype;
  v_equipo  equipos%rowtype;
  v_id      integer;
begin
  if not exists (select 1 from ordenes where id_orden = p_id_orden) then
    perform _fallo('Esa orden no existe. Elige otra.', 'orden');
  end if;
  if exists (select 1 from guias where id_orden = p_id_orden) then
    perform _fallo('Esta orden ya tiene la guía preparada. Presiona Reiniciar demo para volver a empezar.', 'orden');
  end if;

  if v_sale = '' then
    perform _fallo('Elige el equipo que sale.', 'sale');
  end if;
  select * into v_linea
    from detalle_orden
   where id_orden = p_id_orden and vigente and sku_informado = v_sale;
  if not found then
    perform _fallo('Ese equipo no está en el pedido. Elige otro.', 'sale');
  end if;

  if v_entra = '' then
    perform _fallo('Elige el equipo que entra.', 'entra');
  end if;
  if v_entra = v_sale then
    perform _fallo('El equipo que entra debe ser distinto del que sale.', 'entra');
  end if;
  select * into v_equipo from equipos where sku = v_entra;
  if not found then
    perform _fallo('Ese SKU no existe en el inventario. Elige uno de la lista.', 'entra');
  end if;
  if exists (select 1 from detalle_orden where id_orden = p_id_orden and vigente and sku_informado = v_entra) then
    perform _fallo('Ese equipo ya está en el pedido. Elige otro.', 'entra');
  end if;

  if v_motivo = '' then
    perform _fallo('Elige el motivo del cambio.', 'motivo');
  end if;
  if length(v_motivo) > 200 then
    perform _fallo('El motivo es muy largo: máximo 200 caracteres.', 'motivo');
  end if;
  if not exists (select 1 from usuarios where id_usuario = p_id_usuario and activo) then
    perform _fallo('Elige quién registra el cambio.', 'responsable');
  end if;

  perform pg_advisory_xact_lock(7001);

  update detalle_orden set vigente = false where id_detalle = v_linea.id_detalle;

  select coalesce(max(id_detalle), 9000) + 1 into v_id from detalle_orden;
  insert into detalle_orden (id_detalle, id_orden, id_equipo, sku_informado, resultado_validacion, vigente)
  values (v_id, p_id_orden, v_equipo.id_equipo, v_equipo.sku, 'pendiente', true);

  insert into registro_cambios
    (id_cambio, id_orden, sku_sale, id_equipo_sale, id_equipo_entra, id_usuario, fecha_hora_cambio, motivo_cambio)
  values (
    (select coalesce(max(id_cambio), 0) + 1 from registro_cambios),
    p_id_orden,
    v_sale,
    (select id_equipo from equipos where sku = v_sale),
    v_equipo.id_equipo,
    p_id_usuario,
    now(),
    v_motivo
  );

  update ordenes set estado = 'pendiente' where id_orden = p_id_orden;
end;
$$;

-- ---------------------------------------------------------------------------------------------------------
-- preparar_guia: deja la guia solo si TODOS los productos vigentes estan validados y siguen disponibles (HU-05).
-- No confia en lo que diga la pagina: vuelve a mirar el inventario. Solo el jefe de bodega puede prepararla.
-- Sin sesion, quien se identifica lo dice la pagina: esto NO es seguridad, solo coherencia en la demo.
-- ---------------------------------------------------------------------------------------------------------
create or replace function public.preparar_guia(p_id_orden integer, p_id_usuario integer)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_total     integer;
  v_pendiente integer;
  v_malos     integer;
  v_numero    integer;
  v_fecha     timestamptz := now();
begin
  if not exists (select 1 from ordenes where id_orden = p_id_orden) then
    perform _fallo('Esa orden no existe. Elige otra.', 'orden');
  end if;
  if exists (select 1 from guias where id_orden = p_id_orden) then
    perform _fallo('Esta orden ya tiene la guía preparada. Presiona Reiniciar demo para volver a empezar.', 'orden');
  end if;
  if not exists (select 1 from usuarios where id_usuario = p_id_usuario and activo and rol = 'jefe_bodega') then
    perform _fallo('Solo el jefe de bodega puede preparar la guía.', 'usuario');
  end if;

  select count(*),
         count(*) filter (where l.resultado_validacion = 'pendiente'),
         count(*) filter (where e.id_equipo is null or e.estado <> 'disponible')
    into v_total, v_pendiente, v_malos
    from detalle_orden l
    left join equipos e on e.sku = l.sku_informado
   where l.id_orden = p_id_orden and l.vigente;

  if v_total = 0 then
    perform _fallo('El pedido no tiene productos. Cárgalo primero.', 'productos');
  end if;
  if v_pendiente > 0 then
    perform _fallo('Valida el pedido antes de preparar la guía.', 'productos');
  end if;
  if v_malos > 0 then
    perform _fallo(
      format('Corrige %s %s para continuar.', v_malos, case when v_malos = 1 then 'producto' else 'productos' end),
      'productos');
  end if;

  perform pg_advisory_xact_lock(7001);

  select coalesce(max(numero_guia), 15229) + 1 into v_numero from guias;
  insert into guias (id_guia, id_orden, id_usuario_emite, numero_guia, fecha_emision, archivo_pdf)
  values ((select coalesce(max(id_guia), 69) + 1 from guias), p_id_orden, p_id_usuario, v_numero, v_fecha, null);

  update ordenes set estado = 'emitida' where id_orden = p_id_orden;

  return jsonb_build_object('numero_guia', v_numero, 'fecha_emision', v_fecha);
end;
$$;

-- ---------------------------------------------------------------------------------------------------------
-- reiniciar_demo: vuelve las ordenes, sus lineas, los cambios y las guias al estado inicial de la demo.
-- No toca clientes, usuarios ni equipos. Abierta a cualquiera, porque la demo no tiene sesion.
-- ---------------------------------------------------------------------------------------------------------
create or replace function public.reiniciar_demo()
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
  perform pg_advisory_xact_lock(7001);

  -- Solo lo de demo: los equipos 501-507 vuelven a su estado inicial. Los equipos reales (id_equipo >= 1000) no se tocan.
  insert into equipos (id_equipo, sku, descripcion, estado, ubicacion) values
    (501, 'SD-63A20-0314', 'Extensión 63 A x 20 m', 'disponible',    'bodega'),
    (502, 'SD-63A20-0315', 'Extensión 63 A x 20 m', 'disponible',    'bodega'),
    (503, 'SD-63A20-0316', 'Extensión 63 A x 20 m', 'en_mantencion', 'taller'),
    (504, 'SD-32A10-0102', 'Extensión 32 A x 10 m', 'disponible',    'bodega'),
    (505, 'SD-32A10-0108', 'Extensión 32 A x 10 m', 'disponible',    'bodega'),
    (506, 'ST-0042',       'Tablero',               'disponible',    'bodega'),
    (507, 'MP-0107',       'Manga perforada',       'disponible',    'bodega')
  on conflict (id_equipo) do update
    set sku = excluded.sku, descripcion = excluded.descripcion, estado = excluded.estado, ubicacion = excluded.ubicacion;

  -- "where true": desde la API Supabase rechaza un DELETE sin WHERE (pg_safeupdate)
  delete from guias            where true;
  delete from registro_cambios where true;
  delete from detalle_orden    where true;
  delete from ordenes          where true;

  insert into ordenes (id_orden, id_cliente, id_usuario_carga, fecha_orden, tipo_movimiento, modalidad, motivo_retiro, estado) values
    (3001, 10, 1, now(), 'despacho', 'convencional', null,    'pendiente'),
    (3002, 11, 1, now(), 'retiro',   null,           'falla', 'pendiente');

  -- 3001 se puede despachar completa; 3002 trae un SKU que no existe (SD-63A20-9999)
  insert into detalle_orden (id_detalle, id_orden, id_equipo, sku_informado, resultado_validacion, vigente) values
    (9001, 3001, null, 'SD-63A20-0314', 'pendiente', true),
    (9002, 3001, null, 'SD-63A20-0315', 'pendiente', true),
    (9003, 3001, null, 'ST-0042',       'pendiente', true),
    (9004, 3001, null, 'MP-0107',       'pendiente', true),
    (9005, 3002, null, 'SD-32A10-0102', 'pendiente', true),
    (9006, 3002, null, 'SD-63A20-9999', 'pendiente', true),
    (9007, 3002, null, 'ST-0042',       'pendiente', true),
    (9008, 3002, null, 'MP-0107',       'pendiente', true);
end;
$$;

-- ---------------------------------------------------------------------------------------------------------
-- Permisos: solo las funciones de la pagina se pueden llamar desde la API; la ayuda interna no.
-- ---------------------------------------------------------------------------------------------------------
revoke all on function public._fallo(text, text) from public, anon, authenticated;
revoke all on function public._limpiar(text)     from public, anon, authenticated;

revoke all on function public.cargar_pedido(integer, text, text, text, text[]) from public;
revoke all on function public.validar_pedido(integer)                          from public;
revoke all on function public.registrar_cambio(integer, text, text, integer, text) from public;
revoke all on function public.preparar_guia(integer, integer)                  from public;
revoke all on function public.reiniciar_demo()                                 from public;

grant execute on function public.cargar_pedido(integer, text, text, text, text[]) to anon, authenticated;
grant execute on function public.validar_pedido(integer)                          to anon, authenticated;
grant execute on function public.registrar_cambio(integer, text, text, integer, text) to anon, authenticated;
grant execute on function public.preparar_guia(integer, integer)                  to anon, authenticated;
grant execute on function public.reiniciar_demo()                                 to anon, authenticated;

-- Tercera capa para el motivo: debe tener al menos un caracter que no sea espacio, tabulacion ni salto de linea.
-- (La restriccion de schema.sql, que tambien se prueba en SQLite, solo mira espacios normales.)
alter table public.registro_cambios drop constraint if exists registro_cambios_motivo_con_texto;
alter table public.registro_cambios add constraint registro_cambios_motivo_con_texto check (motivo_cambio ~ '\S');

-- Que la API vea las funciones nuevas sin esperar
notify pgrst, 'reload schema';
