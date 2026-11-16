-- Inventario real (solo PostgreSQL / Supabase). Ejecutar DESPUES de schema.sql, acceso.sql, funciones.sql y seed_poc.sql.
-- Se puede volver a ejecutar sin error y no borra nada.
--
-- Agrega a equipos las columnas que trae el Excel de la bodega (todas opcionales, asi que los equipos de demo
-- 501-507 siguen siendo validos) y crea la tabla de extensiones electricas, que no trae estado y por eso no
-- se mezcla con equipos. Los datos se cargan despues con los archivos que genera herramientas/importar_inventario.py.
-- Reglas y supuestos: docs/analisis-inventario.md

alter table public.equipos add column if not exists familia           text;
alter table public.equipos add column if not exists categoria         text;
alter table public.equipos add column if not exists situacion_origen  text;
alter table public.equipos add column if not exists capacidad_valor   numeric;
alter table public.equipos add column if not exists capacidad_unidad  text;

alter table public.equipos drop constraint if exists equipos_familia_dos_letras;
alter table public.equipos add  constraint equipos_familia_dos_letras
  check (familia is null or familia ~ '^[A-Z]{2}$');

alter table public.equipos drop constraint if exists equipos_situacion_origen_valida;
alter table public.equipos add  constraint equipos_situacion_origen_valida
  check (situacion_origen is null or situacion_origen in
    ('BODEGA', 'REPARACIÓN', 'BAJA', 'POR HABILITAR', 'EN BUSCA', 'FUERA DE NORMA',
     'CONTRATO', 'CLIENTE', 'SHOWROOM', 'BODEGA LOS ANGELES'));

alter table public.equipos drop constraint if exists equipos_capacidad_valida;
alter table public.equipos add  constraint equipos_capacidad_valida
  check ((capacidad_valor is null and capacidad_unidad is null)
      or (capacidad_valor > 0 and capacidad_unidad in ('BTU/H', 'TR', 'm3/h', 'kW')));

create table if not exists public.extensiones_electricas (
  id        bigint generated always as identity primary key,
  sku       text    not null unique,
  corriente text    not null,
  largo_m   integer check (largo_m is null or largo_m > 0)
);

alter table public.extensiones_electricas enable row level security;
grant select on public.extensiones_electricas to anon, authenticated;
drop policy if exists "lectura abierta (PoC)" on public.extensiones_electricas;
create policy "lectura abierta (PoC)" on public.extensiones_electricas for select to anon, authenticated using (true);

notify pgrst, 'reload schema';
