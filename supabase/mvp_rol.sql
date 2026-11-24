-- MVP 5/5. Rol limitado de la aplicacion (solo PostgreSQL / Supabase). Ejecutar al final, cuando ya existen las
-- funciones y las vistas (mvp_folio, funciones, mvp_funciones y mvp_vistas). Se puede volver a ejecutar sin error.
--
-- La aplicacion Streamlit se conecta a la base con ESTE rol y no con postgres. Puede:
--   * leer lo que la pantalla muestra (con permisos por columna: sin correo ni telefono de usuarios, sin RUT ni
--     direccion de clientes);
--   * ejecutar las cinco funciones del flujo (cargar_pedido, validar_pedido, registrar_cambio, preparar_guia y
--     crear_pedido);
--   * leer el Dashboard con inventario_dashboard() (solo lectura: nueve columnas de equipos, extensiones y conteos,
--     sin datos personales). Esa funcion la crea dashboard.sql, que debe estar ejecutado antes.
-- No puede: insertar, actualizar ni borrar directo en ninguna tabla, llamar a reiniciar_demo, ni crear objetos.
--
-- LA CONTRASENA NO VA EN ESTE ARCHIVO. Despues de ejecutarlo, en el editor SQL de Supabase, escribela tu (una larga
-- y unica, que no uses en ningun otro lugar) con una linea como esta, cambiando el texto de ejemplo:
--
--     alter role app_mvp password 'REEMPLAZA-ESTE-TEXTO-POR-TU-CONTRASENA';
--
-- No la pegues en el chat, en el repositorio ni en un archivo versionado: va solo en DATABASE_URL (ver docs/mvp-supabase.md).

do $$
begin
  if not exists (select 1 from pg_roles where rolname = 'app_mvp') then
    create role app_mvp login nosuperuser nocreatedb nocreaterole noinherit noreplication nobypassrls;
  end if;
end $$;

-- Limites: pocas conexiones, consultas que no se quedan colgadas y un search_path fijo
alter role app_mvp connection limit 5;
alter role app_mvp set statement_timeout = '10s';
alter role app_mvp set lock_timeout = '5s';
alter role app_mvp set idle_in_transaction_session_timeout = '30s';
alter role app_mvp set search_path = public;

-- Punto de partida limpio: ningun permiso heredado de ejecuciones anteriores
revoke all on all tables    in schema public from app_mvp;
revoke all on all sequences in schema public from app_mvp;
revoke all on all functions in schema public from app_mvp;

grant usage on schema public to app_mvp;
revoke create on schema public from app_mvp;

-- Lectura de las tablas, solo de las columnas que la aplicacion usa
grant select (id_cliente, razon_social)                                          on public.clientes to app_mvp;
grant select (id_usuario, nombre, rol, activo)                                   on public.usuarios to app_mvp;
grant select (id_equipo, sku, descripcion, estado, ubicacion)                    on public.equipos  to app_mvp;
grant select (id_guia, id_orden, id_usuario_emite, numero_guia, fecha_emision)   on public.guias    to app_mvp;
grant select on public.ordenes, public.detalle_orden, public.registro_cambios to app_mvp;

-- Las vistas del MVP (consultan con los permisos de este rol, asi que no abren nada mas)
grant select on public.v_ordenes_resumen, public.v_detalle_orden, public.v_historial_cambios to app_mvp;

-- Politicas de lectura (las tablas tienen RLS activado: sin una politica el rol veria cero filas)
drop policy if exists "lectura app_mvp" on public.clientes;
drop policy if exists "lectura app_mvp" on public.usuarios;
drop policy if exists "lectura app_mvp" on public.equipos;
drop policy if exists "lectura app_mvp" on public.ordenes;
drop policy if exists "lectura app_mvp" on public.detalle_orden;
drop policy if exists "lectura app_mvp" on public.guias;
drop policy if exists "lectura app_mvp" on public.registro_cambios;

create policy "lectura app_mvp" on public.clientes         for select to app_mvp using (true);
create policy "lectura app_mvp" on public.usuarios         for select to app_mvp using (true);
create policy "lectura app_mvp" on public.equipos          for select to app_mvp using (true);
create policy "lectura app_mvp" on public.ordenes          for select to app_mvp using (true);
create policy "lectura app_mvp" on public.detalle_orden    for select to app_mvp using (true);
create policy "lectura app_mvp" on public.guias            for select to app_mvp using (true);
create policy "lectura app_mvp" on public.registro_cambios for select to app_mvp using (true);

-- Escritura: solo a traves de las funciones (que validan todo y corren con los permisos del dueno).
-- reiniciar_demo NO esta en esta lista a proposito: borra y rehace las ordenes de la demo.
grant execute on function public.cargar_pedido(integer, text, text, text, text[])            to app_mvp;
grant execute on function public.validar_pedido(integer)                                     to app_mvp;
grant execute on function public.registrar_cambio(integer, text, text, integer, text)        to app_mvp;
grant execute on function public.preparar_guia(integer, integer)                             to app_mvp;
grant execute on function public.crear_pedido(text, integer, integer, text, text, text, text[]) to app_mvp;

-- Solo lectura, para la vista Dashboard del MVP. Requiere dashboard.sql; va al final para que, si faltara, el resto
-- del archivo ya este aplicado y verificar_mvp.sql lo marque.
grant execute on function public.inventario_dashboard() to app_mvp;

notify pgrst, 'reload schema';
