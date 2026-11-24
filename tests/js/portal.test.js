// Pruebas del portal (portal/portal.js): el boton esta desactivado mientras la direccion este vacia o no sirva, y es un enlace
// cuando es una direccion https valida. Se corren con:  node --test
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const RAIZ = path.resolve(__dirname, '..', '..');
const leer = (...p) => fs.readFileSync(path.join(RAIZ, ...p), 'utf8');

/* Una pagina falsa con los tres elementos del portal, en su estado inicial (como viene en index.html) */
function pagina(config) {
  const elemento = (hidden) => ({ hidden, atributos: {}, setAttribute(k, v) { this.atributos[k] = v; } });
  const e = { 'abrir-pendiente': elemento(false), abrir: elemento(true), nota: elemento(false) };
  const caja = { window: {}, document: { getElementById: (id) => e[id] || null }, URL };
  caja.window = caja;
  if (config !== undefined) caja.PORTAL_CONFIG = config;
  vm.createContext(caja);
  vm.runInContext(leer('portal', 'portal.js'), caja);
  return e;
}

test('direccion vacia: queda el boton desactivado y el aviso, y no hay enlace', () => {
  for (const config of [{ URL_APLICACION: '' }, { URL_APLICACION: '   ' }, {}, undefined, { URL_APLICACION: null }]) {
    const e = pagina(config);
    assert.equal(e['abrir-pendiente'].hidden, false);
    assert.equal(e.abrir.hidden, true);
    assert.equal(e.nota.hidden, false);
    assert.equal(e.abrir.atributos.href, undefined);
  }
});

test('direccion https valida: el boton pasa a ser el enlace y se oculta el aviso', () => {
  const e = pagina({ URL_APLICACION: ' https://bodega.ejemplo.cl/app ' });
  assert.equal(e.abrir.hidden, false);
  assert.equal(e['abrir-pendiente'].hidden, true);
  assert.equal(e.nota.hidden, true);
  assert.equal(e.abrir.atributos.href, 'https://bodega.ejemplo.cl/app');
});

test('direcciones que no sirven se ignoran y el boton sigue desactivado', () => {
  const malas = [
    'http://bodega.ejemplo.cl',                 // sin https
    'javascript:alert(1)',                      // codigo
    'data:text/html,<script>alert(1)</script>',
    '//bodega.ejemplo.cl',                      // relativa al protocolo
    '/app',                                     // relativa
    'bodega.ejemplo.cl',                        // sin protocolo
    'https://usuario:clave@bodega.ejemplo.cl',  // con credenciales
    'https://',                                 // sin servidor
    'ftp://bodega.ejemplo.cl',
    42, {}, []
  ];
  for (const URL_APLICACION of malas) {
    const e = pagina({ URL_APLICACION });
    assert.equal(e.abrir.hidden, true, String(URL_APLICACION));
    assert.equal(e['abrir-pendiente'].hidden, false, String(URL_APLICACION));
    assert.equal(e.abrir.atributos.href, undefined, String(URL_APLICACION));
  }
});

test('el portal publicado hoy trae la direccion vacia o una direccion https valida, y se puede cargar sin romperse', () => {
  const caja = { window: {} };
  caja.window = caja;
  vm.createContext(caja);
  vm.runInContext(leer('portal', 'config.js'), caja);
  const valor = caja.PORTAL_CONFIG.URL_APLICACION;
  assert.equal(typeof valor, 'string');
  assert.ok(valor === '' || /^https:\/\/[^/@\s]+/.test(valor), valor);
  assert.ok(Object.isFrozen(caja.PORTAL_CONFIG));
});
