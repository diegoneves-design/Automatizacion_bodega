# Portal

Página estática mínima que Vercel publica como entrada pública del proyecto. Tiene un solo botón que lleva a la aplicación (el MVP de `src/`). Streamlit necesita un servidor siempre encendido y no corre en Vercel, así que Vercel solo muestra esta entrada.

No enlaza al prototipo ni a su dashboard. El prototipo (`prototipo/`) sigue publicado aparte, en su propio proyecto de Vercel (`bodega-poc`), para el video del README y para la prueba con usuarios.

## Cómo cambiar la dirección de la aplicación

Hay un único lugar: `config.js`, la línea `URL_APLICACION`.

- **Vacía** (así está hasta que el MVP esté publicado): el botón aparece desactivado con el texto «Aplicación en despliegue».
- **Con una dirección `https`**: el botón pasa a «Abrir la aplicación» y lleva a esa dirección. Solo se aceptan direcciones `https` sin usuario ni contraseña; cualquier otra cosa se ignora y el botón queda desactivado.

Después de cambiarla hay que volver a publicar: con el proyecto de Vercel conectado al repositorio, basta un pull request fusionado en `main`.

## Probarlo en el computador

Desde esta carpeta: `py -m http.server 8001 --bind 127.0.0.1` y abrir `http://127.0.0.1:8001`. Para ver el botón activo, pon una dirección `https` en `config.js` **sin subir ese cambio**.

## Vercel: un segundo proyecto, sin tocar el del prototipo

El portal va en un **proyecto nuevo** de Vercel (nombre sugerido: `bodega-portal`), conectado al mismo repositorio. **No se modifica `bodega-poc`**: ese proyecto conserva su configuración (Root Directory = `prototipo`, Build Command = `node generar-config.mjs` y sus variables), porque el prototipo debe seguir publicado.

El proyecto nuevo se configura así: **Root Directory = `portal`**, *Framework Preset* «Other», **sin Build Command**, sin Install Command, sin Output Directory y **sin variables de entorno** (el portal no usa claves ni Supabase). Los pasos completos y cómo comprobarlos están en el README del repositorio, sección «Portal público en Vercel».

`vercel.json` solo agrega encabezados de seguridad; no define ningún comando de construcción.
