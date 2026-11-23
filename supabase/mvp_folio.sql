-- MVP 1/5. Folio de la orden (solo PostgreSQL / Supabase). Ejecutar PRIMERO, antes de funciones.sql.
-- Se puede volver a ejecutar sin error y no borra nada.
--
-- Agrega ordenes.folio (el nombre con el que la gente llama a la orden: GUIA-2026-001). Es opcional para no romper lo
-- que ya existe, pero cuando hay valor debe ser unico y tener esa forma. Las ordenes 3001 y 3002 de la demo reciben
-- GUIA-2026-001 y GUIA-2026-002. El prototipo no cambia: sigue usando id_orden.
-- (En una base nueva, schema.sql ya trae la columna y la unicidad; aqui solo se agrega lo que falte.)

alter table public.ordenes add column if not exists folio text;

-- Unicidad: solo si la columna todavia no es unica (una base nueva ya lo es por schema.sql)
do $$
declare
  v_attnum smallint;
begin
  select attnum into v_attnum from pg_attribute where attrelid = 'public.ordenes'::regclass and attname = 'folio';
  if not exists (
    select 1 from pg_constraint
     where conrelid = 'public.ordenes'::regclass and contype = 'u' and conkey = array[v_attnum]
  ) then
    alter table public.ordenes add constraint ordenes_folio_key unique (folio);
  end if;
end $$;

-- Forma del folio: GUIA, el anio de cuatro cifras y un correlativo de 3 a 6 cifras. Tercera capa de la regla.
alter table public.ordenes drop constraint if exists ordenes_folio_formato;
alter table public.ordenes add  constraint ordenes_folio_formato
  check (folio is null or folio ~ '^GUIA-[0-9]{4}-[0-9]{3,6}$');

-- Las dos ordenes de la demo. Solo se llenan si no tienen folio, para no pisar uno puesto a mano.
update public.ordenes set folio = 'GUIA-2026-001' where id_orden = 3001 and folio is null;
update public.ordenes set folio = 'GUIA-2026-002' where id_orden = 3002 and folio is null;

notify pgrst, 'reload schema';
