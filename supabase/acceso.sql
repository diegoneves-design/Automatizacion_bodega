-- 2/4 Acceso (solo PostgreSQL / Supabase). Ejecutar despues de schema.sql.
--
-- El proyecto se creo con "no exponer automaticamente las tablas nuevas" y con RLS automatico, asi que
-- aqui todo es explicito: RLS activado, permisos (GRANT) y politicas.
--
-- SOLO PARA LA PRUEBA DE CONCEPTO CON DATOS FICTICIOS. El prototipo no tiene inicio de sesion, asi que las
-- politicas son ABIERTAS: cualquier persona con el enlace puede LEER. Escribir solo se puede a traves de las
-- funciones de funciones.sql, que validan antes de guardar; las tablas no aceptan INSERT, UPDATE ni DELETE
-- directos desde la API. Antes de usar datos reales hay que agregar sesion y cerrar las politicas por rol.

alter table public.clientes         enable row level security;
alter table public.usuarios         enable row level security;
alter table public.equipos          enable row level security;
alter table public.ordenes          enable row level security;
alter table public.detalle_orden    enable row level security;
alter table public.guias            enable row level security;
alter table public.registro_cambios enable row level security;

-- Punto de partida limpio: ningun permiso heredado
revoke all on all tables    in schema public from anon, authenticated;
revoke all on all functions in schema public from public, anon, authenticated;

grant usage on schema public to anon, authenticated;

-- Lectura de las tablas del flujo
grant select on public.clientes, public.equipos, public.ordenes, public.detalle_orden,
                public.guias, public.registro_cambios
  to anon, authenticated;

-- De usuarios solo se leen estas columnas: el correo y el telefono no salen por la API
grant select (id_usuario, nombre, rol, activo) on public.usuarios to anon, authenticated;

-- Politicas abiertas de lectura (se pueden volver a ejecutar sin error)
drop policy if exists "lectura abierta (PoC)" on public.clientes;
drop policy if exists "lectura abierta (PoC)" on public.usuarios;
drop policy if exists "lectura abierta (PoC)" on public.equipos;
drop policy if exists "lectura abierta (PoC)" on public.ordenes;
drop policy if exists "lectura abierta (PoC)" on public.detalle_orden;
drop policy if exists "lectura abierta (PoC)" on public.guias;
drop policy if exists "lectura abierta (PoC)" on public.registro_cambios;

create policy "lectura abierta (PoC)" on public.clientes         for select to anon, authenticated using (true);
create policy "lectura abierta (PoC)" on public.usuarios         for select to anon, authenticated using (true);
create policy "lectura abierta (PoC)" on public.equipos          for select to anon, authenticated using (true);
create policy "lectura abierta (PoC)" on public.ordenes          for select to anon, authenticated using (true);
create policy "lectura abierta (PoC)" on public.detalle_orden    for select to anon, authenticated using (true);
create policy "lectura abierta (PoC)" on public.guias            for select to anon, authenticated using (true);
create policy "lectura abierta (PoC)" on public.registro_cambios for select to anon, authenticated using (true);
