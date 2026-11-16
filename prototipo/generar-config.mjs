// Crea prototipo/js/config.js con la direccion de Supabase y su clave publicable.
//
// Los valores salen de variables de entorno (en Vercel: Settings > Environment Variables) o, si no estan,
// de un archivo .env en la raiz del repositorio. config.js NO se sube a git (esta en .gitignore).
//
//   Vercel, "Build Command":  node generar-config.mjs        (si la carpeta raiz del proyecto es prototipo/)
//                             node prototipo/generar-config.mjs   (si es la raiz del repositorio)
//   En el computador:         node prototipo/generar-config.mjs
//
// La clave publicable esta pensada para ir en el navegador: lo que protege los datos son las reglas de la base
// (RLS y funciones), no esconder la clave. Nunca se usa aqui la clave secreta (service_role).

import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const aqui = dirname(fileURLToPath(import.meta.url));

function leerEnv(ruta) {
  const valores = {};
  if (!existsSync(ruta)) return valores;
  for (const linea of readFileSync(ruta, 'utf8').split(/\r?\n/)) {
    const m = linea.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*?)\s*$/);
    if (m && !linea.trim().startsWith('#')) valores[m[1]] = m[2].replace(/^['"]|['"]$/g, '');
  }
  return valores;
}

const archivo = leerEnv(join(aqui, '..', '.env'));
const url = process.env.SUPABASE_URL || archivo.SUPABASE_URL || '';
const clave = process.env.SUPABASE_PUBLISHABLE_KEY || archivo.SUPABASE_PUBLISHABLE_KEY || '';

if (!/^https:\/\/[a-z0-9-]+\.supabase\.co\/?$/.test(url)) {
  console.error('Falta SUPABASE_URL o no tiene la forma https://<proyecto>.supabase.co');
  process.exit(1);
}
if (!/^sb_publishable_/.test(clave)) {
  console.error('SUPABASE_PUBLISHABLE_KEY debe ser la clave publicable (empieza con sb_publishable_). No uses la clave secreta.');
  process.exit(1);
}

const contenido =
  '/* Generado por generar-config.mjs. No se sube a git. */\n' +
  'window.CONFIG = ' + JSON.stringify({ SUPABASE_URL: url.replace(/\/$/, ''), SUPABASE_KEY: clave }, null, 2) + ';\n';

writeFileSync(join(aqui, 'js', 'config.js'), contenido);
console.log('prototipo/js/config.js creado.');
