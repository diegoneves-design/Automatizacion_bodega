-- MVP 3/5. Funcion nueva del MVP (solo PostgreSQL / Supabase). Ejecutar despues de mvp_folio.sql y funciones.sql.
-- Se puede volver a ejecutar sin error.
--
-- crear_pedido: crea una orden nueva con su folio y sus lineas. Hasta ahora las ordenes de la demo ya existian y
-- cargar_pedido solo las rellenaba; el MVP necesita crear las suyas. Sigue el mismo estilo que las otras funciones:
-- valida TODO antes de guardar y rechaza con P0001, el mensaje exacto y el campo (hint).
--
-- A diferencia de las otras cinco, NO se le da a anon: la pagina publica no necesita crear ordenes. Solo la ejecuta el
-- rol del MVP (mvp_rol.sql).

create or replace function public.crear_pedido(
  p_folio         text,
  p_id_cliente    integer,
  p_id_usuario    integer,
  p_tipo          text,
  p_modalidad     text,
  p_motivo_retiro text,
  p_skus          text[]
)
returns integer
language plpgsql
security definer
set search_path = public
as $$
declare
  c_max constant integer := 60;  -- el mismo maximo que cargar_pedido y que el prototipo
  v_folio text := upper(_limpiar(p_folio));
  v_skus  text[];
  v_sku   text;
  v_n     integer;
  v_orden integer;
  v_id    integer;
begin
  v_skus := _skus_limpios(p_skus);
  v_n := coalesce(array_length(v_skus, 1), 0);

  if v_folio !~ '^GUIA-[0-9]{4}-[0-9]{3,6}$' then
    perform _fallo('El folio debe tener la forma GUIA-2026-001.', 'folio');
  end if;
  if exists (select 1 from ordenes where folio = v_folio) then
    perform _fallo('Ya existe una orden con ese folio. Usa otro.', 'folio');
  end if;
  if p_id_cliente is null or not exists (select 1 from clientes where id_cliente = p_id_cliente) then
    perform _fallo('Elige el cliente.', 'cliente');
  end if;
  if p_id_usuario is null or not exists (select 1 from usuarios where id_usuario = p_id_usuario and activo) then
    perform _fallo('Elige quién carga el pedido.', 'usuario');
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

  -- Con el candado tomado se vuelve a mirar el folio: dos personas con el mismo folio a la vez no pasan las dos.
  if exists (select 1 from ordenes where folio = v_folio) then
    perform _fallo('Ya existe una orden con ese folio. Usa otro.', 'folio');
  end if;

  select coalesce(max(id_orden), 3000) + 1 into v_orden from ordenes;
  insert into ordenes (id_orden, id_cliente, id_usuario_carga, fecha_orden, tipo_movimiento, modalidad, motivo_retiro, estado, folio)
  values (
    v_orden, p_id_cliente, p_id_usuario, now(), p_tipo,
    case when p_tipo = 'despacho' then p_modalidad end,
    case when p_tipo = 'retiro'   then p_motivo_retiro end,
    'pendiente', v_folio
  );

  select coalesce(max(id_detalle), 9000) into v_id from detalle_orden;
  foreach v_sku in array v_skus loop
    v_id := v_id + 1;
    insert into detalle_orden (id_detalle, id_orden, id_equipo, sku_informado, resultado_validacion, vigente)
    values (v_id, v_orden, null, v_sku, 'pendiente', true);
  end loop;

  return v_orden;
end;
$$;

-- Nadie la llama desde la API publica. Supabase da permisos por omision a anon y authenticated en lo que se crea
-- despues, asi que se quitan de forma explicita. El permiso para el rol del MVP esta en mvp_rol.sql.
revoke all on function public.crear_pedido(text, integer, integer, text, text, text, text[]) from public, anon, authenticated;

notify pgrst, 'reload schema';
