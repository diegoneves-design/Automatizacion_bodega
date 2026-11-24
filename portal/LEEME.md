# Portal

Página estática mínima que Vercel publica como entrada pública del proyecto. Tiene un solo botón que lleva a la aplicación (el MVP de `src/`). Streamlit necesita un servidor siempre encendido y no corre en Vercel, así que Vercel solo muestra esta entrada.

No enlaza al prototipo ni a su dashboard: el prototipo (`prototipo/`) quedó como archivo histórico del repositorio.

## Cómo cambiar la dirección de la aplicación

Hay un único lugar: `config.js`, la línea `URL_APLICACION`.

- **Vacía** (así está hasta que el MVP esté publicado): el botón aparece desactivado con el texto «Aplicación en despliegue».
- **Con una dirección `https`**: el botón pasa a «Abrir la aplicación» y lleva a esa dirección. Solo se aceptan direcciones `https` sin usuario ni contraseña; cualquier otra cosa se ignora y el botón queda desactivado.

Después de cambiarla hay que volver a publicar (con Vercel conectado al repositorio, basta un commit en la rama de producción).

## Probarlo en el computador

Desde esta carpeta: `py -m http.server 8001 --bind 127.0.0.1` y abrir `http://127.0.0.1:8001`. Para ver el botón activo, pon una dirección `https` en `config.js` **sin subir ese cambio**.

## Configuración en Vercel

El proyecto de Vercel debe tener **Root Directory = `portal`**. Si el proyecto conserva el **Build Command** `node generar-config.mjs` del prototipo, la publicación falla: ese archivo no existe aquí, y el portal no se construye. Quita el Build Command (déjalo sin definir, con Framework Preset «Other»). Las variables `SUPABASE_URL` y `SUPABASE_PUBLISHABLE_KEY` ya no se necesitan para el portal. Los pasos completos están en el README del repositorio.

`vercel.json` solo agrega encabezados de seguridad; no define ningún comando de construcción.
