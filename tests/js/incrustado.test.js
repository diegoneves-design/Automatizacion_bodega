// Pruebas del Dashboard dentro del MVP (modo incrustado). Se corren con:  node --test
// Todos los datos son ficticios. La logica de filtros y los graficos se prueban en prototipo/pruebas; aqui se prueba que:
//  - los datos que el servidor incrusta en la pagina producen las MISMAS cifras que la carga desde Supabase del prototipo;
//  - el entorno del iframe lee y escribe los filtros en la direccion de la pagina padre y ajusta el alto, sin romperse si no puede.
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const RAIZ = path.resolve(__dirname, '..', '..');
const F = require(path.join(RAIZ, 'prototipo', 'js', 'filtros.js'));
const leer = (...partes) => fs.readFileSync(path.join(RAIZ, ...partes), 'utf8');
// lo que sale de un contexto aislado (vm) tiene otro prototipo: se compara por su contenido
const plano = (x) => JSON.parse(JSON.stringify(x));

const COLUMNAS = ['id_equipo', 'sku', 'descripcion', 'familia', 'categoria', 'estado', 'situacion_origen', 'capacidad_valor', 'capacidad_unidad'];

/* Lo que devuelve inventario_dashboard(): columnas y filas. Con textos que podrian romper una pagina si no se escaparan. */
function datosFicticios() {
  const filas = [];
  let id = 1000;
  const agrega = (n, familia, estado, situacion, desc, cap) => {
    for (let i = 0; i < n; i++, id++) {
      filas.push([id, 'XX-' + familia + '-' + String(id).padStart(5, '0'), desc + ' MODELO M' + familia + ' ' + i, familia, 'CAT-' + familia, estado, situacion, cap ? cap[0] : null, cap ? cap[1] : null]);
    }
  };
  agrega(10, 'AA', 'disponible', 'BODEGA', 'Equipo <b>de</b> prueba & "otro"', [12000, 'BTU/H']);
  agrega(5, 'AA', 'arrendado', 'CONTRATO', 'Equipo de prueba', [18000, 'BTU/H']);
  agrega(3, 'AA', 'fuera_servicio', 'POR HABILITAR', 'Equipo </script><script>alert(1)</script>', null);
  agrega(6, 'BB', 'disponible', 'BODEGA', 'Otro equipo', [7.5, 'kW']);
  agrega(2, 'BB', 'en_mantencion', 'REPARACIÓN', 'Otro equipo', null);
  return {
    equipos: { columnas: COLUMNAS, filas },
    extensiones: { columnas: ['sku', 'corriente', 'largo_m'], filas: [['YY-63A-00001', '63A', 10], ['YY-63A-00002', '63A', 20], ['YY-32A-00001', '32A', 10]] },
    actividad: { ordenes_por_estado: { pendiente: 2, emitida: 1 }, cambios_por_motivo: { 'Código mal digitado': 1 } }
  };
}

/* Igual que ui_dashboard.json_seguro (Python): nada de <, > ni & sin escapar dentro del bloque JSON de la pagina */
function jsonSeguro(d) {
  return JSON.stringify(d).replace(/</g, '\\u003c').replace(/>/g, '\\u003e').replace(/&/g, '\\u0026').replace(/\u2028/g, '\\u2028').replace(/\u2029/g, '\\u2029');
}

function cargarDatosJs(textoDelBloque) {
  const caja = { window: {}, document: { getElementById: (id) => (id === 'datos-dashboard' && textoDelBloque !== null ? { textContent: textoDelBloque } : null) } };
  vm.createContext(caja);
  vm.runInContext(leer('src', 'dashboard_incrustado', 'datos.js'), caja);
  return caja.window.API;
}

/* Todo lo que el Dashboard calcula con los datos, sin dibujar nada */
function cifras(respuesta) {
  const d = respuesta.datos;
  const equipos = F.prepararEquipos(d.equipos);
  const ext = F.prepararExtensiones(d.extensiones);
  const filtros = F.filtrosVacios();
  const lista = F.aplicar(equipos, filtros);
  return {
    total: equipos.length,
    indicadores: F.indicadores(lista, equipos.length),
    hallazgos: F.hallazgos(lista, F.aplicarExtensiones(ext, filtros), equipos.length, false, false),
    csv: F.aCsv(F.ordenar(lista, 'sku', 'asc')),
    actividad: d.actividad,
    fuera: F.indicadores(F.aplicar(equipos, F.filtrosDeVista('mantencion')), equipos.length)
  };
}

test('modo incrustado: los datos del servidor producen las mismas cifras que la carga desde Supabase', async () => {
  const original = datosFicticios();
  // lo que entrega api.js en el prototipo: { datos: r.data }
  const desdeSupabase = { datos: JSON.parse(JSON.stringify(original)) };
  // lo que entrega el MVP: el bloque JSON escapado de la pagina, leido por datos.js
  const incrustado = await cargarDatosJs(jsonSeguro(original)).leerDashboard();

  assert.deepEqual(plano(incrustado), desdeSupabase);
  assert.deepEqual(plano(cifras(incrustado)), plano(cifras(desdeSupabase)));
  assert.equal(cifras(incrustado).total, 26);
  assert.equal(cifras(incrustado).indicadores.disponible.n, 16);
});

test('modo incrustado: un texto con etiquetas llega al navegador como texto, sin romper el bloque', async () => {
  const bloque = jsonSeguro(datosFicticios());
  assert.ok(!/[<>&]/.test(bloque), 'el bloque no debe tener <, > ni & sin escapar');
  const r = await cargarDatosJs(bloque).leerDashboard();
  assert.ok(r.datos.equipos.filas.some((f) => f[2].includes('</script><script>alert(1)</script>')));
});

test('modo incrustado: si el bloque esta danado, entrega un error claro y no revienta', async () => {
  for (const malo of ['{no es json', '', null]) {
    const r = await cargarDatosJs(malo).leerDashboard();
    assert.equal(r.datos, undefined);
    assert.match(r.error.mensaje, /No se pudieron leer los datos del Dashboard/);
  }
});

/* ---------- entorno.js ---------- */

function entorno({ padreHash = '#estado=arrendado', conPadre = true, padreFalla = false, anchoHijo = 1400, altoPadre = 900 } = {}) {
  const llamadas = { replaceState: [], listeners: [], estiloAlto: null };
  const hijoLoc = { hash: '#propio', pathname: '/hijo', search: '' };
  const padre = {
    innerHeight: altoPadre,
    location: { hash: padreHash, pathname: '/app', search: '?vista=dashboard' },
    history: { replaceState: (a, b, url) => { llamadas.replaceState.push(url); padre.location.hash = url.includes('#') ? '#' + url.split('#')[1] : ''; } },
    addEventListener: (nombre, cb) => llamadas.listeners.push([nombre, cb])
  };
  if (padreFalla) Object.defineProperty(padre, 'location', { get() { throw new Error('SecurityError'); } });
  const marco = { style: {} };
  const caja = { innerWidth: anchoHijo, location: hijoLoc, history: { replaceState: () => llamadas.replaceState.push('HIJO') }, addEventListener: () => {} };
  caja.window = caja;
  caja.parent = conPadre ? padre : caja;
  caja.frameElement = conPadre ? marco : null;
  vm.createContext(caja);
  vm.runInContext(leer('src', 'dashboard_incrustado', 'entorno.js'), caja);
  return { E: caja.DASHBOARD_ENTORNO, llamadas, marco, padre };
}

test('entorno: lee y escribe los filtros en la direccion de la pagina padre', () => {
  const { E, llamadas, padre } = entorno();
  assert.equal(E.leerHash(), '#estado=arrendado');
  E.guardarHash('estado=disponible&familia=AC');
  assert.deepEqual(llamadas.replaceState, ['/app?vista=dashboard#estado=disponible&familia=AC']);  // conserva ?vista=dashboard
  assert.equal(padre.location.hash, '#estado=disponible&familia=AC');
  E.guardarHash('estado=disponible&familia=AC');  // sin cambios: no vuelve a escribir
  assert.equal(llamadas.replaceState.length, 1);
  E.guardarHash('');                               // quitar todos los filtros deja la direccion limpia
  assert.equal(llamadas.replaceState[1], '/app?vista=dashboard');
});

test('entorno: avisa cuando cambia la direccion de la pagina padre', () => {
  const { E, llamadas } = entorno();
  const cb = () => {};
  E.alCambiarHash(cb);
  assert.deepEqual(llamadas.listeners.filter(([n]) => n === 'hashchange'), [['hashchange', cb]]);
});

test('entorno: ajusta el alto del iframe al de la ventana, con un minimo', () => {
  assert.equal(entorno({ altoPadre: 900 }).marco.style.height, '804px');
  assert.equal(entorno({ altoPadre: 500 }).marco.style.height, '560px');  // nunca mas bajo que el minimo
  const { llamadas } = entorno();
  assert.ok(llamadas.listeners.some(([n]) => n === 'resize'), 'se reajusta cuando cambia la ventana');
});

test('entorno: el panel se acopla solo en pantallas anchas', () => {
  assert.equal(entorno({ anchoHijo: 1400 }).E.panelAcoplado(), true);
  assert.equal(entorno({ anchoHijo: 1100 }).E.panelAcoplado(), true);
  assert.equal(entorno({ anchoHijo: 1099 }).E.panelAcoplado(), false);
  assert.equal(entorno({ anchoHijo: 375 }).E.panelAcoplado(), false);
});

test('entorno: si no puede tocar la pagina padre, usa la direccion del propio iframe y sigue funcionando', () => {
  for (const opciones of [{ padreFalla: true }, { conPadre: false }]) {
    const { E, marco } = entorno(opciones);
    assert.equal(E.leerHash(), '#propio');
    assert.doesNotThrow(() => E.guardarHash('estado=arrendado'));
    assert.doesNotThrow(() => E.alCambiarHash(() => {}));
    assert.equal(marco.style.height, undefined);  // sin acceso al marco no toca el alto
  }
});
