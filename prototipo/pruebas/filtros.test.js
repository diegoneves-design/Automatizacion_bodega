// Pruebas de la logica del tablero. Se corren con:  node --test prototipo/pruebas
// Todos los datos son ficticios.
'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const F = require('../js/filtros.js');

function equipo(id, familia, estado, extra) {
  return Object.assign({ id, sku: 'XX-' + String(id).padStart(5, '0'), descripcion: 'Equipo de prueba ' + id, familia, categoria: 'CAT-' + familia,
    estado, situacion: '', capacidad_valor: null, capacidad_unidad: null, modelo: F.SIN_MODELO }, extra || {});
}

function muestra() {
  const l = [];
  let id = 1;
  const agrega = (n, fam, est, extra) => { for (let i = 0; i < n; i++) l.push(equipo(id++, fam, est, extra)); };
  agrega(10, 'AA', 'disponible');
  agrega(5, 'AA', 'arrendado');
  agrega(3, 'AA', 'fuera_servicio', { situacion: 'POR HABILITAR' });
  agrega(2, 'AA', 'fuera_servicio', { situacion: 'BAJA' });
  agrega(6, 'BB', 'disponible');
  agrega(2, 'BB', 'en_mantencion', { situacion: 'REPARACIÓN' });
  agrega(2, 'CC', 'arrendado');
  return l; // 30 equipos
}

test('filasAObjetos convierte columnas y filas', () => {
  const r = F.filasAObjetos({ columnas: ['a', 'b'], filas: [[1, 'x'], [2, 'y']] });
  assert.deepEqual(r, [{ a: 1, b: 'x' }, { a: 2, b: 'y' }]);
  assert.deepEqual(F.filasAObjetos(null), []);
  assert.deepEqual(F.filasAObjetos({ columnas: ['a'] }), []);
});

test('extraerModelo agrupa variantes de la misma descripcion por modelo', () => {
  assert.equal(F.extraerModelo('Enfriador marca Alfa MODELO ZX801 8.000 m3/h'), 'ZX801');
  assert.equal(F.extraerModelo('Enfriador marca Beta modelo zx801; caudal 9 m3/h'), 'ZX801');
  assert.equal(F.extraerModelo('Otro texto  Modelo   ZX801'), 'ZX801');
  assert.equal(F.extraerModelo('Calefactor MODELO AB-12 15 KW'), 'AB-12');
  assert.equal(F.extraerModelo('Tablero electrico sin dato'), F.SIN_MODELO);
  assert.equal(F.extraerModelo(''), F.SIN_MODELO);
  assert.equal(F.extraerModelo(null), F.SIN_MODELO);
  assert.equal(F.extraerModelo('abcMODELO Z1'), F.SIN_MODELO, 'MODELO debe ser una palabra completa');
});

test('prepararEquipos usa valores por defecto y calcula el modelo', () => {
  const r = F.prepararEquipos({ columnas: ['id_equipo', 'sku', 'descripcion', 'familia', 'categoria', 'estado', 'situacion_origen', 'capacidad_valor', 'capacidad_unidad'],
    filas: [[1, 'S-1', 'Equipo MODELO Q9', null, null, 'disponible', null, '12000', 'BTU/H']] });
  assert.equal(r[0].familia, 'SIN FAMILIA');
  assert.equal(r[0].categoria, 'SIN CATEGORÍA');
  assert.equal(r[0].modelo, 'Q9');
  assert.equal(r[0].capacidad_valor, 12000);
});

test('un filtro de estado deja solo ese estado', () => {
  const l = muestra();
  const f = F.alternar(F.filtrosVacios(), 'estado', 'disponible');
  assert.equal(F.aplicar(l, f).length, 16);
});

test('alternar agrega y, al repetir el clic, quita; no modifica el filtro original', () => {
  const base = F.filtrosVacios();
  const a = F.alternar(base, 'familia', 'AA');
  assert.deepEqual(base.familia, []);
  assert.deepEqual(a.familia, ['AA']);
  const b = F.alternar(a, 'familia', 'AA');
  assert.deepEqual(b.familia, []);
  assert.equal(F.hayFiltros(b), false);
  assert.equal(F.hayFiltros(a), true);
});

test('los filtros se combinan: familia AA y fuera de servicio', () => {
  const l = muestra();
  let f = F.alternar(F.filtrosVacios(), 'familia', 'AA');
  f = F.alternar(f, 'estado', 'fuera_servicio');
  assert.equal(F.aplicar(l, f).length, 5);
});

test('dentro de una misma dimension los valores se suman (O)', () => {
  const l = muestra();
  let f = F.alternar(F.filtrosVacios(), 'familia', 'AA');
  f = F.alternar(f, 'familia', 'CC');
  assert.equal(F.aplicar(l, f).length, 22);
});

test('omitir ignora la dimension del propio grafico', () => {
  const l = muestra();
  let f = F.alternar(F.filtrosVacios(), 'familia', 'AA');
  f = F.alternar(f, 'estado', 'disponible');
  assert.equal(F.aplicar(l, f).length, 10);
  assert.equal(F.aplicar(l, f, ['familia']).length, 16);
  assert.equal(F.aplicar(l, f, ['familia', 'estado']).length, 30);
});

test('alternarPar pone los dos filtros y, si ya estaban, los quita', () => {
  const a = F.alternarPar(F.filtrosVacios(), 'familia', 'AA', 'estado', 'disponible');
  assert.deepEqual([a.familia, a.estado], [['AA'], ['disponible']]);
  const b = F.alternarPar(a, 'familia', 'AA', 'estado', 'disponible');
  assert.equal(F.hayFiltros(b), false);
});

test('filtros de corriente solo afectan a las extensiones', () => {
  const l = muestra();
  const f = F.alternar(F.filtrosVacios(), 'corriente', '32A');
  assert.equal(F.aplicar(l, f).length, 30);
  const ext = [{ sku: 'a', corriente: '32A', largo_m: 10 }, { sku: 'b', corriente: '63A', largo_m: 20 }];
  assert.equal(F.aplicarExtensiones(ext, f).length, 1);
  assert.equal(F.aplicarExtensiones(ext, f, ['corriente']).length, 2);
});

test('hash: ida y vuelta, y valores con espacios y tildes', () => {
  let f = F.alternar(F.filtrosVacios(), 'estado', 'fuera_servicio');
  f = F.alternar(f, 'familia', 'AC');
  assert.equal(F.aHash(f), 'estado=fuera_servicio&familia=AC');
  assert.deepEqual(F.desdeHash('#estado=fuera_servicio&familia=AC'), f);
  const g = F.alternar(F.alternar(F.filtrosVacios(), 'situacion', 'POR HABILITAR'), 'situacion', 'REPARACIÓN');
  assert.deepEqual(F.desdeHash(F.aHash(g)), g);
});

test('hash: ignora dimensiones desconocidas, estados invalidos, basura y valores muy largos', () => {
  const f = F.desdeHash('#estado=hackeado,disponible&xss=<script>&familia=' + 'A'.repeat(200) + '&=vacio&sinvalor&categoria=%E0%A4%A');
  assert.deepEqual(f.estado, ['disponible']);
  assert.deepEqual(f.familia, []);
  assert.deepEqual(f.categoria, []);
  assert.deepEqual(F.desdeHash(''), F.filtrosVacios());
  assert.deepEqual(F.desdeHash(undefined), F.filtrosVacios());
});

test('vistas rapidas: mantencion, despacho y jefe', () => {
  const l = muestra();
  const m = F.aplicar(l, F.filtrosDeVista('mantencion'));
  assert.equal(m.length, 3 + 2);                 // 3 por habilitar + 2 en reparacion
  const d = F.aplicar(l, F.filtrosDeVista('despacho'));
  assert.equal(d.length, 16);
  assert.equal(F.aplicar(l, F.filtrosDeVista('jefe')).length, 30);
  assert.equal(F.vistaActiva(F.filtrosDeVista('despacho')), 'despacho');
  assert.equal(F.vistaActiva(F.filtrosVacios()), 'jefe');
  assert.equal(F.vistaActiva(F.alternar(F.filtrosVacios(), 'familia', 'AA')), null);
  assert.deepEqual(F.VISTAS.despacho.orden, { columna: 'familia', direccion: 'asc' });
});

test('indicadores: cantidades y porcentajes sobre lo filtrado y sobre el total general', () => {
  const l = muestra();
  const i = F.indicadores(l, 30);
  assert.equal(i.total.n, 30);
  assert.equal(i.disponible.n, 16);
  assert.ok(Math.abs(i.disponible.pct - 53.33) < 0.01);
  const sub = F.aplicar(l, F.alternar(F.filtrosVacios(), 'familia', 'AA'));
  const j = F.indicadores(sub, 30);
  assert.equal(j.total.n, 20);
  assert.ok(Math.abs(j.total.pct - 66.67) < 0.01);
  assert.equal(j.disponible.pct, 50);
  assert.equal(F.indicadores([], 30).disponible.pct, 0);
});

test('formatoPct y formatoNumero', () => {
  assert.equal(F.formatoPct(55.6), '55,6 %');
  assert.equal(F.formatoPct(15), '15 %');
  assert.equal(F.formatoPct(81.94), '81,9 %');
  assert.equal(F.formatoNumero(1617), '1.617');
  assert.equal(F.formatoNumero(12), '12');
});

test('tasaArriendo: solo familias con el minimo y promedio general', () => {
  const l = muestra();
  const t = F.tasaArriendo(l, 8);
  assert.deepEqual(t.filas.map(x => x.familia), ['AA', 'BB']);
  assert.equal(t.filas[0].tasa, 25);
  assert.equal(t.filas[1].tasa, 0);
  assert.ok(Math.abs(t.promedio - (7 * 100) / 30) < 1e-9);
  assert.equal(F.tasaArriendo(l).filas.length, 0, 'con el minimo de 30 ninguna familia de la muestra califica');
  assert.equal(F.tasaArriendo(l).minimo, 30);
});

test('estadoPorFamilia: top por tamano, conteos y porcentaje del grupo', () => {
  const l = muestra();
  const e = F.estadoPorFamilia(l, 2);
  assert.deepEqual(e.map(x => x.familia), ['AA', 'BB']);
  assert.equal(e[0].conteo.disponible, 10);
  assert.equal(e[0].pct.disponible, 50);
  assert.equal(Object.values(e[0].pct).reduce((a, b) => a + b, 0), 100);
});

test('fueraDeServicioPorMotivo cuenta los cuatro motivos', () => {
  const r = F.fueraDeServicioPorMotivo(muestra());
  assert.equal(r.total, 5);
  const m = Object.fromEntries(r.filas.map(x => [x.situacion, x.n]));
  assert.deepEqual(m, { 'BAJA': 2, 'POR HABILITAR': 3, 'EN BUSCA': 0, 'FUERA DE NORMA': 0 });
  assert.equal(r.filas[1].pct, 60);
});

test('pareto: acumulado sobre el total (incluye los sin modelo) y orden descendente', () => {
  const l = [];
  const mk = (m, n) => { for (let i = 0; i < n; i++) l.push(equipo(l.length + 1, 'AA', 'disponible', { modelo: m })); };
  mk('M1', 5); mk('M2', 3); mk('M3', 1); mk(F.SIN_MODELO, 1);
  const p = F.pareto(l, 2);
  assert.equal(p.total, 10);
  assert.equal(p.sinModelo, 1);
  assert.equal(p.modelosDistintos, 3);
  assert.deepEqual(p.filas.map(x => x.modelo), ['M1', 'M2']);
  assert.deepEqual(p.filas.map(x => x.acumulado), [50, 80]);
  assert.equal(p.filas[0].pct, 50);
});

test('estadisticaCaja: cuartiles, bigotes y valores atipicos', () => {
  const c = F.estadisticaCaja([1, 2, 3, 4, 5, 6, 7, 8, 9, 100]);
  assert.equal(c.n, 10);
  assert.equal(c.mediana, 5.5);
  assert.equal(c.q1, 3.25);
  assert.equal(c.q3, 7.75);
  assert.deepEqual(c.atipicos, [100]);
  assert.equal(c.max, 9);
  assert.equal(c.min, 1);
  assert.equal(F.estadisticaCaja([]), null);
  assert.equal(F.estadisticaCaja([7]).mediana, 7);
  assert.equal(F.estadisticaCaja([null, undefined, NaN, 4]).n, 1);
});

test('extensiones: por corriente ordenado por amperes y largo por corriente', () => {
  const ext = [
    { sku: 'a', corriente: '125A', largo_m: 10 }, { sku: 'b', corriente: '32A', largo_m: 10 }, { sku: 'c', corriente: '32A', largo_m: 20 },
    { sku: 'd', corriente: '32A', largo_m: null }, { sku: 'e', corriente: '63A', largo_m: 15 }
  ];
  assert.deepEqual(F.extensionesPorCorriente(ext).map(x => x.corriente), ['32A', '63A', '125A']);
  assert.equal(F.extensionesPorCorriente(ext)[0].n, 3);
  const l = F.largoPorCorriente(ext);
  assert.equal(l.sinLargo, 1);
  assert.deepEqual(l.filas.map(x => x.corriente), ['32A', '63A', '125A']);
  assert.equal(l.filas[0].caja.mediana, 15);
});

test('mapaDeCalor: una celda por familia y estado', () => {
  const h = F.mapaDeCalor(muestra());
  assert.equal(h.celdas.length, 3 * 4);
  assert.equal(h.familias[0], 'AA');
  const c = h.celdas.find(x => x.familia === 'AA' && x.estado === 'disponible');
  assert.equal(c.n, 10);
  assert.equal(h.maximo, 10);
});

test('arbol: categoria > familia con totales', () => {
  const a = F.arbol(muestra());
  assert.equal(a[0].nombre, 'CAT-AA');
  assert.equal(a[0].valor, 20);
  assert.equal(a[0].hijos[0].nombre, 'AA');
  assert.equal(a.reduce((s, x) => s + x.valor, 0), 30);
});

test('capacidad: una unidad por vista, TR pasa a BTU/H y se declaran los excluidos', () => {
  const l = [];
  const mk = (fam, valor, unidad, n) => { for (let i = 0; i < n; i++) l.push(equipo(l.length + 1, fam, 'disponible', { capacidad_valor: valor, capacidad_unidad: unidad })); };
  mk('AC', 12000, 'BTU/H', 14); mk('AC', 4, 'TR', 2);            // 16 en BTU/H, 2 convertidos
  mk('EC', 8000, 'm3/h', 20);
  mk('CD', 15, 'kW', 5);                                           // familia pequena en kW
  mk('XX', null, null, 3);                                         // sin capacidad
  const b = F.capacidadPorFamilia(l, 'BTU/H');
  assert.deepEqual(b.filas.map(x => x.familia), ['AC']);
  assert.equal(b.filas[0].caja.n, 16);
  assert.equal(b.convertidosDeTR, 2);
  assert.deepEqual(b.filas[0].caja.atipicos, [48000, 48000]);       // 4 TR = 48.000 BTU/H (queda lejos del resto)
  assert.equal(b.sinCapacidad, 3);
  assert.equal(b.enOtraUnidad, 25);                                // 20 m3/h + 5 kW
  const m = F.capacidadPorFamilia(l, 'm3/h');
  assert.deepEqual(m.filas.map(x => x.familia), ['EC']);
  assert.equal(m.convertidosDeTR, 0);
  const k = F.capacidadPorFamilia(l, 'kW');
  assert.equal(k.filas.length, 0);
  assert.equal(k.enFamiliasPequenas, 5);
  assert.deepEqual(F.unidadesDisponibles(l), ['BTU/H', 'm3/h', 'kW']);
  assert.deepEqual(F.unidadesDisponibles([equipo(1, 'AA', 'disponible')]), []);
});

test('actividad: ordena y suma; vacia no falla', () => {
  const a = F.actividad({ ordenes_por_estado: { pendiente: 2, validada: 1 }, cambios_por_motivo: { 'Código mal digitado': 1 } });
  assert.equal(a.totalOrdenes, 3);
  assert.equal(a.ordenes[0].clave, 'pendiente');
  assert.equal(a.totalCambios, 1);
  const v = F.actividad(null);
  assert.deepEqual([v.totalOrdenes, v.totalCambios], [0, 0]);
});

test('hallazgos: seis, con la frase fija si hay menos de 10 equipos', () => {
  const l = muestra();
  const h = F.hallazgos(l, [], 30, false);
  assert.equal(h.length, 6);
  assert.match(h[0].texto, /^53,3 % de los 30 equipos está disponible/);
  assert.ok(!/En esta selección/.test(h[0].texto));
  const hf = F.hallazgos(l, [], 30, true);
  assert.match(hf[0].texto, /^En esta selección: /);
  const chico = F.hallazgos(l.slice(0, 9), [], 30, true);
  assert.equal(chico.length, 6);
  chico.forEach(x => assert.ok(x.texto.indexOf(F.FRASE_MUESTRA_PEQUENA) !== -1));
  assert.equal(F.FRASE_MUESTRA_PEQUENA, 'muestra muy pequeña para sacar conclusiones');
  const diez = F.hallazgos(l.slice(0, 10), [], 30, true);
  assert.ok(diez.every(x => x.texto.indexOf(F.FRASE_MUESTRA_PEQUENA) === -1));
});

test('hallazgos: textos de extensiones con y sin datos', () => {
  const ext = [{ sku: 'a', corriente: '32A', largo_m: 10 }, { sku: 'b', corriente: '32A', largo_m: 20 }, { sku: 'c', corriente: '63A', largo_m: 15 }];
  const h = F.hallazgos(muestra(), ext, 30, false);
  assert.match(h[5].texto, /3 extensiones; la corriente más común es 32A \(2\) y el largo mediano es 15 m\./);
  assert.match(F.hallazgos(muestra(), [], 30, true)[5].texto, /No hay extensiones/);
  assert.ok(!/Con el filtro de corriente/.test(F.hallazgos(muestra(), ext, 30, true, false)[5].texto));
  assert.match(F.hallazgos(muestra(), ext, 30, true, true)[5].texto, /^Con el filtro de corriente: /);
});

test('buscar ignora mayusculas y tildes; ordenar por columna; paginar de a 25', () => {
  const l = [equipo(1, 'AA', 'disponible', { descripcion: 'Calefacción grande' }), equipo(2, 'BB', 'arrendado', { descripcion: 'Otro' })];
  assert.equal(F.buscar(l, 'calefaccion').length, 1);
  assert.equal(F.buscar(l, 'XX-00002').length, 1);
  assert.equal(F.buscar(l, 'xx-0000').length, 2);
  assert.equal(F.buscar(l, '   ').length, 2);
  assert.equal(F.ordenar(l, 'familia', 'desc')[0].familia, 'BB');
  assert.equal(F.ordenar(l, 'estado', 'asc')[0].estado, 'arrendado');
  assert.equal(F.ordenar(l, 'columna_inexistente', 'asc')[0].sku, 'XX-00001');
  const muchos = [];
  for (let i = 1; i <= 60; i++) muchos.push(equipo(i, 'AA', 'disponible'));
  const p3 = F.paginar(muchos, 3);
  assert.deepEqual([p3.pagina, p3.paginas, p3.desde, p3.hasta, p3.filas.length], [3, 3, 51, 60, 10]);
  assert.equal(F.paginar(muchos, 99).pagina, 3);
  assert.equal(F.paginar([], 1).paginas, 1);
  assert.equal(F.paginar([], 1).desde, 0);
  assert.equal(F.paginar(muchos, 1).filas.length, 25);
});

test('CSV: encabezado, comillas escapadas, UTF-8 con BOM y proteccion contra formulas', () => {
  const l = [equipo(1, 'AA', 'disponible', { descripcion: 'Dice "hola"; y =SUMA(A1)' })];
  const csv = F.aCsv(l);
  assert.ok(csv.startsWith('﻿"SKU";"Descripción"'));
  assert.ok(csv.indexOf('"Dice ""hola""; y =SUMA(A1)"') !== -1);
  const f = F.aCsv([equipo(2, 'AA', 'disponible', { descripcion: '=2+2' })]);
  assert.ok(f.indexOf('"\'=2+2"') !== -1);
  assert.equal(F.aCsv([]).split('\r\n').length, 2);
});

test('chips: uno por valor con su texto', () => {
  let f = F.alternar(F.filtrosVacios(), 'estado', 'en_mantencion');
  f = F.alternar(f, 'familia', 'AC');
  assert.deepEqual(F.chips(f).map(c => c.texto), ['Estado: En mantención', 'Familia: AC']);
  assert.deepEqual(F.chips(F.filtrosVacios()), []);
});
