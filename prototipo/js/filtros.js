/* Logica del tablero de inventario: filtros, conteos, estadisticas y textos.
   No usa el navegador (ni document ni window): se prueba con  node --test  (prototipo/pruebas/filtros.test.js).
   Funciona como modulo de Node y como variable global Filtros en la pagina. */
(function (raiz, fabrica) {
  if (typeof module === 'object' && module.exports) module.exports = fabrica();
  else raiz.Filtros = fabrica();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var ESTADOS = ['disponible', 'arrendado', 'en_mantencion', 'fuera_servicio'];
  var ETIQUETA_ESTADO = { disponible: 'Disponible', arrendado: 'Arrendado', en_mantencion: 'En mantención', fuera_servicio: 'Fuera de servicio' };
  var SITUACIONES_FUERA = ['BAJA', 'POR HABILITAR', 'EN BUSCA', 'FUERA DE NORMA'];
  var DIMENSIONES = ['estado', 'familia', 'categoria', 'situacion', 'modelo', 'corriente'];
  var ETIQUETA_DIMENSION = { estado: 'Estado', familia: 'Familia', categoria: 'Categoría', situacion: 'Situación de origen', modelo: 'Modelo', corriente: 'Corriente' };
  var MINIMO_FAMILIA_TASA = 30;     // grafico 3: familias con al menos 30 equipos
  var MINIMO_CAPACIDAD = 15;        // grafico 11: familias con capacidad extraida en al menos 15 equipos
  var MUESTRA_PEQUENA = 10;
  var BTU_POR_TR = 12000;
  var POR_PAGINA = 25;
  var FRASE_MUESTRA_PEQUENA = 'muestra muy pequeña para sacar conclusiones';
  var SIN_MODELO = 'SIN MODELO';

  /* ---------- Datos ---------- */

  /* Pasa {columnas, filas} (como lo entrega inventario_dashboard) a una lista de objetos */
  function filasAObjetos(bloque) {
    if (!bloque || !Array.isArray(bloque.columnas) || !Array.isArray(bloque.filas)) return [];
    var cols = bloque.columnas;
    return bloque.filas.map(function (f) {
      var o = {};
      for (var i = 0; i < cols.length; i++) o[cols[i]] = f[i];
      return o;
    });
  }

  /* Modelo = la primera palabra (letras, numeros y guion) que sigue a la palabra MODELO en la descripcion, en mayusculas.
     Todas las descripciones con el mismo modelo se cuentan juntas. Sin esa palabra: 'SIN MODELO'. */
  function extraerModelo(descripcion) {
    var m = /\bMODELO\s+([A-Z0-9-]+)/i.exec(String(descripcion || ''));
    if (!m) return SIN_MODELO;
    var t = m[1].replace(/^-+|-+$/g, '').toUpperCase();
    return t || SIN_MODELO;
  }

  function prepararEquipos(bloque) {
    return filasAObjetos(bloque).map(function (e) {
      return {
        id: e.id_equipo, sku: String(e.sku || ''), descripcion: String(e.descripcion || ''),
        familia: e.familia || 'SIN FAMILIA', categoria: e.categoria || 'SIN CATEGORÍA', estado: e.estado,
        situacion: e.situacion_origen || '', capacidad_valor: e.capacidad_valor == null ? null : Number(e.capacidad_valor),
        capacidad_unidad: e.capacidad_unidad || null, modelo: extraerModelo(e.descripcion)
      };
    });
  }

  function prepararExtensiones(bloque) {
    return filasAObjetos(bloque).map(function (x) {
      return { sku: String(x.sku || ''), corriente: String(x.corriente || ''), largo_m: x.largo_m == null ? null : Number(x.largo_m) };
    });
  }

  /* ---------- Filtros ---------- */

  function filtrosVacios() {
    var f = {};
    DIMENSIONES.forEach(function (d) { f[d] = []; });
    return f;
  }

  function copiar(f) {
    var n = filtrosVacios();
    DIMENSIONES.forEach(function (d) { n[d] = (f && f[d] ? f[d] : []).slice(); });
    return n;
  }

  function hayFiltros(f) {
    return DIMENSIONES.some(function (d) { return f[d] && f[d].length > 0; });
  }

  function tiene(f, dim, valor) { return !!f[dim] && f[dim].indexOf(valor) !== -1; }

  /* Clic: si el valor ya estaba lo quita; si no, lo agrega. Devuelve un objeto nuevo. */
  function alternar(f, dim, valor) {
    var n = copiar(f);
    var i = n[dim].indexOf(valor);
    if (i === -1) n[dim].push(valor); else n[dim].splice(i, 1);
    return n;
  }

  function quitar(f, dim, valor) {
    var n = copiar(f);
    n[dim] = n[dim].filter(function (v) { return v !== valor; });
    return n;
  }

  /* Dos filtros a la vez (celda del mapa de calor, segmento apilado): si los dos ya estaban, se quitan; si no, se ponen los dos. */
  function alternarPar(f, dimA, valA, dimB, valB) {
    if (tiene(f, dimA, valA) && tiene(f, dimB, valB)) return quitar(quitar(f, dimA, valA), dimB, valB);
    var n = copiar(f);
    if (n[dimA].indexOf(valA) === -1) n[dimA].push(valA);
    if (n[dimB].indexOf(valB) === -1) n[dimB].push(valB);
    return n;
  }

  /* Los filtros se suman con Y entre dimensiones y con O dentro de una misma dimension
     (familia AC y AP = los dos; familia AC y estado fuera de servicio = solo los de AC que estan fuera de servicio).
     `omitir` son las dimensiones que se ignoran (cada grafico ignora las de su propio eje para poder cambiar la seleccion). */
  var CAMPO = { estado: 'estado', familia: 'familia', categoria: 'categoria', situacion: 'situacion', modelo: 'modelo' };

  function aplicar(equipos, f, omitir) {
    var o = omitir || [];
    var activos = Object.keys(CAMPO).filter(function (d) { return f[d] && f[d].length && o.indexOf(d) === -1; });
    if (!activos.length) return equipos.slice();
    return equipos.filter(function (e) {
      return activos.every(function (d) { return f[d].indexOf(e[CAMPO[d]]) !== -1; });
    });
  }

  function aplicarExtensiones(extensiones, f, omitir) {
    if (!f.corriente || !f.corriente.length || (omitir || []).indexOf('corriente') !== -1) return extensiones.slice();
    return extensiones.filter(function (x) { return f.corriente.indexOf(x.corriente) !== -1; });
  }

  /* ---------- Direccion (#estado=fuera_servicio&familia=AC) ---------- */

  function aHash(f) {
    var partes = [];
    DIMENSIONES.forEach(function (d) {
      if (f[d] && f[d].length) partes.push(d + '=' + f[d].map(encodeURIComponent).join(','));
    });
    return partes.join('&');
  }

  /* Solo se aceptan las dimensiones conocidas, valores cortos y, en estado, valores validos: el hash viene de afuera. */
  function desdeHash(hash) {
    var f = filtrosVacios();
    String(hash || '').replace(/^#/, '').split('&').forEach(function (par) {
      var i = par.indexOf('=');
      if (i < 1) return;
      var dim = par.slice(0, i);
      if (DIMENSIONES.indexOf(dim) === -1) return;
      var valores;
      try { valores = par.slice(i + 1).split(',').map(decodeURIComponent); } catch (e) { return; }
      valores.forEach(function (v) {
        v = v.trim();
        if (!v || v.length > 60) return;
        if (dim === 'estado' && ESTADOS.indexOf(v) === -1) return;
        if (f[dim].indexOf(v) === -1) f[dim].push(v);
      });
    });
    return f;
  }

  /* ---------- Vistas rapidas por rol (solo filtros ya armados; no son permisos) ---------- */
  var VISTAS = {
    jefe: { etiqueta: 'Jefe de bodega', descripcion: 'Vista general de todo el inventario', filtros: {}, orden: null },
    mantencion: { etiqueta: 'Mantención', descripcion: 'Equipos en reparación y los que están por habilitar', filtros: { situacion: ['REPARACIÓN', 'POR HABILITAR'] }, orden: null },
    despacho: { etiqueta: 'Despacho', descripcion: 'Equipos disponibles, agrupados por familia', filtros: { estado: ['disponible'] }, orden: { columna: 'familia', direccion: 'asc' } }
  };

  function filtrosDeVista(id) {
    var base = filtrosVacios();
    var v = VISTAS[id];
    if (!v) return base;
    Object.keys(v.filtros).forEach(function (d) { base[d] = v.filtros[d].slice(); });
    return base;
  }

  function mismosFiltros(a, b) { return aHash(a) === aHash(b); }

  function vistaActiva(f) {
    var ids = Object.keys(VISTAS);
    for (var i = 0; i < ids.length; i++) if (mismosFiltros(f, filtrosDeVista(ids[i]))) return ids[i];
    return null;
  }

  /* ---------- Conteos ---------- */

  function porcentaje(parte, total) { return total > 0 ? (parte * 100) / total : 0; }

  function formatoPct(valor) {
    var r = Math.round(valor * 10) / 10;
    return (Math.abs(r - Math.round(r)) < 1e-9 ? String(Math.round(r)) : String(r).replace('.', ',')) + ' %';
  }

  function formatoNumero(n) { return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, '.'); }

  /* [{clave, n}] ordenado de mayor a menor (y por nombre si empatan) */
  function contar(lista, clave) {
    var m = {};
    lista.forEach(function (x) { var k = clave(x); m[k] = (m[k] || 0) + 1; });
    return Object.keys(m).map(function (k) { return { clave: k, n: m[k] }; })
      .sort(function (a, b) { return b.n - a.n || (a.clave < b.clave ? -1 : a.clave > b.clave ? 1 : 0); });
  }

  function conteoPorEstado(lista) {
    var c = {};
    ESTADOS.forEach(function (e) { c[e] = 0; });
    lista.forEach(function (x) { if (c[x.estado] !== undefined) c[x.estado]++; });
    return c;
  }

  function indicadores(lista, totalGeneral) {
    var c = conteoPorEstado(lista);
    var total = lista.length;
    var r = { total: { n: total, pct: porcentaje(total, totalGeneral), etiqueta: 'Total de equipos' } };
    ESTADOS.forEach(function (e) { r[e] = { n: c[e], pct: porcentaje(c[e], total), etiqueta: ETIQUETA_ESTADO[e] }; });
    return r;
  }

  /* Grafico 3: tasa de arriendo por familia (familias con 30 o mas equipos en la base de este grafico) */
  function tasaArriendo(lista, minimo) {
    var m = minimo == null ? MINIMO_FAMILIA_TASA : minimo;
    var grupos = {};
    lista.forEach(function (e) {
      var g = grupos[e.familia] || (grupos[e.familia] = { familia: e.familia, total: 0, arrendados: 0 });
      g.total++;
      if (e.estado === 'arrendado') g.arrendados++;
    });
    var filas = Object.keys(grupos).map(function (k) { return grupos[k]; })
      .filter(function (g) { return g.total >= m; })
      .map(function (g) { return { familia: g.familia, total: g.total, arrendados: g.arrendados, tasa: porcentaje(g.arrendados, g.total) }; })
      .sort(function (a, b) { return b.tasa - a.tasa || b.total - a.total; });
    var arrendados = lista.filter(function (e) { return e.estado === 'arrendado'; }).length;
    return { filas: filas, promedio: porcentaje(arrendados, lista.length), minimo: m };
  }

  /* Grafico 4: estado por familia, las 8 familias mas grandes. Devuelve conteos y, aparte, el % dentro de cada familia. */
  function estadoPorFamilia(lista, cuantas) {
    var top = contar(lista, function (e) { return e.familia; }).slice(0, cuantas || 8);
    var filas = top.map(function (t) {
      var grupo = lista.filter(function (e) { return e.familia === t.clave; });
      var c = conteoPorEstado(grupo);
      var pct = {};
      ESTADOS.forEach(function (e) { pct[e] = porcentaje(c[e], t.n); });
      return { familia: t.clave, total: t.n, conteo: c, pct: pct };
    });
    return filas;
  }

  /* Grafico 5: equipos fuera de servicio por situacion (BAJA, POR HABILITAR, EN BUSCA, FUERA DE NORMA) */
  function fueraDeServicioPorMotivo(lista) {
    var fuera = lista.filter(function (e) { return e.estado === 'fuera_servicio'; });
    return { total: fuera.length, filas: SITUACIONES_FUERA.map(function (s) {
      var n = fuera.filter(function (e) { return e.situacion === s; }).length;
      return { situacion: s, n: n, pct: porcentaje(n, fuera.length) };
    }) };
  }

  /* Grafico 6: Pareto de modelos. Los equipos sin la palabra MODELO no entran al ranking, pero si al total. */
  function pareto(lista, cuantos) {
    var total = lista.length;
    var conteo = contar(lista.filter(function (e) { return e.modelo !== SIN_MODELO; }), function (e) { return e.modelo; });
    var top = conteo.slice(0, cuantos || 10);
    var acum = 0;
    return {
      total: total,
      sinModelo: lista.filter(function (e) { return e.modelo === SIN_MODELO; }).length,
      modelosDistintos: conteo.length,
      filas: top.map(function (t) {
        acum += t.n;
        return { modelo: t.clave, n: t.n, pct: porcentaje(t.n, total), acumulado: porcentaje(acum, total) };
      })
    };
  }

  /* Grafico 7 */
  function extensionesPorCorriente(extensiones) {
    return contar(extensiones, function (x) { return x.corriente; })
      .sort(function (a, b) { return amperes(a.clave) - amperes(b.clave); })
      .map(function (c) { return { corriente: c.clave, n: c.n, pct: porcentaje(c.n, extensiones.length) }; });
  }

  function amperes(texto) {
    var m = /^(\d+)/.exec(texto);
    return m ? parseInt(m[1], 10) : 0;
  }

  /* Cuartiles por interpolacion; atipicos fuera de 1,5 veces el rango intercuartil (regla de Tukey) */
  function cuantil(ordenados, q) {
    var pos = (ordenados.length - 1) * q;
    var base = Math.floor(pos);
    var resto = pos - base;
    return ordenados[base + 1] !== undefined ? ordenados[base] + resto * (ordenados[base + 1] - ordenados[base]) : ordenados[base];
  }

  function estadisticaCaja(valores) {
    var v = valores.filter(function (x) { return typeof x === 'number' && isFinite(x); }).sort(function (a, b) { return a - b; });
    if (!v.length) return null;
    var q1 = cuantil(v, 0.25), mediana = cuantil(v, 0.5), q3 = cuantil(v, 0.75);
    var rango = q3 - q1;
    var bajo = q1 - 1.5 * rango, alto = q3 + 1.5 * rango;
    var dentro = v.filter(function (x) { return x >= bajo && x <= alto; });
    return {
      n: v.length, min: dentro[0], q1: q1, mediana: mediana, q3: q3, max: dentro[dentro.length - 1],
      atipicos: v.filter(function (x) { return x < bajo || x > alto; })
    };
  }

  /* Grafico 8: largo de las extensiones por corriente */
  function largoPorCorriente(extensiones) {
    var grupos = {};
    var sinLargo = 0;
    extensiones.forEach(function (x) {
      if (x.largo_m == null) { sinLargo++; return; }
      (grupos[x.corriente] = grupos[x.corriente] || []).push(x.largo_m);
    });
    var filas = Object.keys(grupos).sort(function (a, b) { return amperes(a) - amperes(b); })
      .map(function (c) { return { corriente: c, caja: estadisticaCaja(grupos[c]) }; });
    return { filas: filas, sinLargo: sinLargo };
  }

  /* Grafico 9: familia x estado */
  function mapaDeCalor(lista) {
    var familias = contar(lista, function (e) { return e.familia; }).map(function (c) { return c.clave; });
    var celdas = [];
    var maximo = 0;
    familias.forEach(function (fam, i) {
      ESTADOS.forEach(function (est, j) {
        var n = lista.filter(function (e) { return e.familia === fam && e.estado === est; }).length;
        if (n > maximo) maximo = n;
        celdas.push({ x: j, y: i, familia: fam, estado: est, n: n });
      });
    });
    return { familias: familias, estados: ESTADOS, celdas: celdas, maximo: maximo };
  }

  /* Grafico 10: categoria > familia */
  function arbol(lista) {
    var porCategoria = {};
    lista.forEach(function (e) {
      var c = porCategoria[e.categoria] || (porCategoria[e.categoria] = {});
      c[e.familia] = (c[e.familia] || 0) + 1;
    });
    return Object.keys(porCategoria).map(function (cat) {
      var hijos = Object.keys(porCategoria[cat]).map(function (f) { return { nombre: f, categoria: cat, valor: porCategoria[cat][f] }; })
        .sort(function (a, b) { return b.valor - a.valor; });
      return { nombre: cat, valor: hijos.reduce(function (s, h) { return s + h.valor; }, 0), hijos: hijos };
    }).sort(function (a, b) { return b.valor - a.valor; });
  }

  /* Grafico 11: capacidad por familia. Cada vista usa una sola unidad. Con BTU/H, los TR se pasan a BTU/H (1 TR = 12.000 BTU/H)
     y se declara cuantos equipos se convirtieron. */
  function capacidadEnUnidad(e, unidad) {
    if (e.capacidad_valor == null || !e.capacidad_unidad) return null;
    if (e.capacidad_unidad === unidad) return e.capacidad_valor;
    if (unidad === 'BTU/H' && e.capacidad_unidad === 'TR') return e.capacidad_valor * BTU_POR_TR;
    return null;
  }

  function capacidadPorFamilia(lista, unidad) {
    var grupos = {};
    var convertidos = 0;
    var enUnidad = 0;
    lista.forEach(function (e) {
      var v = capacidadEnUnidad(e, unidad);
      if (v == null) return;
      enUnidad++;
      if (e.capacidad_unidad !== unidad) convertidos++;
      (grupos[e.familia] = grupos[e.familia] || []).push(v);
    });
    var filas = Object.keys(grupos).filter(function (f) { return grupos[f].length >= MINIMO_CAPACIDAD; })
      .map(function (f) { return { familia: f, caja: estadisticaCaja(grupos[f]) }; })
      .sort(function (a, b) { return b.caja.n - a.caja.n; });
    var mostrados = filas.reduce(function (s, f) { return s + f.caja.n; }, 0);
    return {
      unidad: unidad, filas: filas, convertidosDeTR: convertidos,
      sinCapacidad: lista.filter(function (e) { return e.capacidad_valor == null; }).length,
      enOtraUnidad: lista.filter(function (e) { return e.capacidad_valor != null && capacidadEnUnidad(e, unidad) == null; }).length,
      enFamiliasPequenas: enUnidad - mostrados
    };
  }

  function unidadesDisponibles(lista) {
    var u = ['BTU/H', 'm3/h', 'kW'];
    return u.filter(function (x) { return lista.some(function (e) { return capacidadEnUnidad(e, x) != null; }); });
  }

  /* Grafico 12: actividad del MVP (no depende de los filtros) */
  function actividad(a) {
    var ordenes = (a && a.ordenes_por_estado) || {};
    var cambios = (a && a.cambios_por_motivo) || {};
    function lista(o) { return Object.keys(o).map(function (k) { return { clave: k, n: Number(o[k]) }; }).sort(function (x, y) { return y.n - x.n; }); }
    var o = lista(ordenes), c = lista(cambios);
    return {
      ordenes: o, cambios: c,
      totalOrdenes: o.reduce(function (s, x) { return s + x.n; }, 0),
      totalCambios: c.reduce(function (s, x) { return s + x.n; }, 0)
    };
  }

  /* ---------- Lectura de los datos (6 hallazgos que se recalculan) ---------- */
  function hallazgos(lista, extensiones, totalGeneral, hayFiltro, hayCorriente) {
    var prefijo = hayFiltro ? 'En esta selección: ' : '';
    if (lista.length < MUESTRA_PEQUENA) {
      return ['Estado del inventario', 'Concentración por familia', 'Tasa de arriendo', 'Equipos recuperables', 'Modelo más repetido', 'Extensiones eléctricas']
        .map(function (t) { return { titulo: t, texto: prefijo + FRASE_MUESTRA_PEQUENA + ' (' + lista.length + ' equipos).' }; });
    }
    var n = lista.length;
    var c = conteoPorEstado(lista);
    var r = [];

    r.push({ titulo: 'Estado del inventario', texto: prefijo + formatoPct(porcentaje(c.disponible, n)) + ' de los ' + formatoNumero(n) + ' equipos está disponible, ' +
      formatoPct(porcentaje(c.arrendado, n)) + ' arrendado, ' + formatoPct(porcentaje(c.en_mantencion, n)) + ' en mantención y ' +
      formatoPct(porcentaje(c.fuera_servicio, n)) + ' fuera de servicio.' });

    var fam = contar(lista, function (e) { return e.familia; });
    var tres = fam.slice(0, 3);
    var sumaTres = tres.reduce(function (s, x) { return s + x.n; }, 0);
    r.push({ titulo: 'Concentración por familia', texto: prefijo + 'las familias ' + tres.map(function (x) { return x.clave + ' (' + formatoNumero(x.n) + ')'; }).join(', ') +
      ' suman ' + formatoPct(porcentaje(sumaTres, n)) + ' de los equipos.' });

    var tasa = tasaArriendo(lista, MINIMO_FAMILIA_TASA);
    if (tasa.filas.length >= 2) {
      var alta = tasa.filas[0], baja = tasa.filas[tasa.filas.length - 1];
      r.push({ titulo: 'Tasa de arriendo', texto: prefijo + 'entre las familias con ' + MINIMO_FAMILIA_TASA + ' o más equipos, ' + alta.familia + ' tiene la tasa de arriendo más alta (' +
        formatoPct(alta.tasa) + ') y ' + baja.familia + ' la más baja (' + formatoPct(baja.tasa) + '); el promedio es ' + formatoPct(tasa.promedio) + '.' });
    } else {
      r.push({ titulo: 'Tasa de arriendo', texto: prefijo + 'la tasa de arriendo general es ' + formatoPct(tasa.promedio) + '; no hay dos familias con ' + MINIMO_FAMILIA_TASA + ' o más equipos para compararlas.' });
    }

    var fuera = fueraDeServicioPorMotivo(lista);
    var porHab = fuera.filas.filter(function (x) { return x.situacion === 'POR HABILITAR'; })[0];
    r.push({ titulo: 'Equipos recuperables', texto: prefijo + formatoNumero(porHab.n) + ' equipos están por habilitar y ' + formatoNumero(c.en_mantencion) + ' en reparación: ' +
      formatoNumero(porHab.n + c.en_mantencion) + ' equipos (' + formatoPct(porcentaje(porHab.n + c.en_mantencion, n)) + ') podrían volver a estar disponibles.' });

    var par = pareto(lista, 10);
    if (par.filas.length) {
      r.push({ titulo: 'Modelo más repetido', texto: prefijo + 'el modelo ' + par.filas[0].modelo + ' reúne ' + formatoNumero(par.filas[0].n) + ' equipos (' + formatoPct(par.filas[0].pct) +
        '); los 10 modelos más repetidos suman ' + formatoPct(par.filas[par.filas.length - 1].acumulado) + '.' });
    } else {
      r.push({ titulo: 'Modelo más repetido', texto: prefijo + 'ningún equipo de esta selección trae el modelo en su descripción.' });
    }

    if (extensiones.length) {
      var porC = extensionesPorCorriente(extensiones).slice().sort(function (a, b) { return b.n - a.n; })[0];
      var largos = estadisticaCaja(extensiones.map(function (x) { return x.largo_m; }).filter(function (x) { return x != null; }));
      r.push({ titulo: 'Extensiones eléctricas', texto: (hayCorriente ? 'Con el filtro de corriente: ' : '') + formatoNumero(extensiones.length) + ' extensiones; la corriente más común es ' + porC.corriente +
        ' (' + formatoNumero(porC.n) + ')' + (largos ? ' y el largo mediano es ' + String(largos.mediana).replace('.', ',') + ' m.' : '.') });
    } else {
      r.push({ titulo: 'Extensiones eléctricas', texto: 'No hay extensiones con el filtro de corriente elegido.' });
    }
    return r;
  }

  /* ---------- Tabla de casos ---------- */
  var COLUMNAS_TABLA = [
    { id: 'sku', etiqueta: 'SKU' }, { id: 'descripcion', etiqueta: 'Descripción' }, { id: 'familia', etiqueta: 'Familia' },
    { id: 'estado', etiqueta: 'Estado' }, { id: 'situacion', etiqueta: 'Situación de origen' }
  ];

  function normalizarTexto(t) { return String(t || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }

  function buscar(lista, texto) {
    var q = normalizarTexto(texto).trim();
    if (!q) return lista.slice();
    return lista.filter(function (e) { return normalizarTexto(e.sku).indexOf(q) !== -1 || normalizarTexto(e.descripcion).indexOf(q) !== -1; });
  }

  function clave(e, columna) {
    var v = columna === 'estado' ? ETIQUETA_ESTADO[e.estado] : e[columna];
    return normalizarTexto(v);
  }

  function ordenar(lista, columna, direccion) {
    var d = direccion === 'desc' ? -1 : 1;
    var col = COLUMNAS_TABLA.some(function (c) { return c.id === columna; }) ? columna : 'sku';
    return lista.slice().sort(function (a, b) {
      var x = clave(a, col), y = clave(b, col);
      if (x < y) return -1 * d;
      if (x > y) return 1 * d;
      var s1 = normalizarTexto(a.sku), s2 = normalizarTexto(b.sku);
      return s1 < s2 ? -1 : s1 > s2 ? 1 : 0;
    });
  }

  function paginar(lista, pagina, porPagina) {
    var tam = porPagina || POR_PAGINA;
    var paginas = Math.max(1, Math.ceil(lista.length / tam));
    var p = Math.min(Math.max(1, pagina || 1), paginas);
    return { pagina: p, paginas: paginas, desde: lista.length ? (p - 1) * tam + 1 : 0, hasta: Math.min(p * tam, lista.length), total: lista.length, filas: lista.slice((p - 1) * tam, p * tam) };
  }

  /* CSV para Excel: comillas dobles escapadas y, si una celda empieza con = + - @, se antepone ' para que no se ejecute como formula */
  function celdaCsv(valor) {
    var t = valor == null ? '' : String(valor);
    if (/^[=+\-@\t\r]/.test(t)) t = "'" + t;
    return '"' + t.replace(/"/g, '""') + '"';
  }

  function aCsv(lista) {
    var filas = [['SKU', 'Descripción', 'Familia', 'Categoría', 'Estado', 'Situación de origen']];
    lista.forEach(function (e) { filas.push([e.sku, e.descripcion, e.familia, e.categoria, ETIQUETA_ESTADO[e.estado] || e.estado, e.situacion]); });
    return '﻿' + filas.map(function (f) { return f.map(celdaCsv).join(';'); }).join('\r\n') + '\r\n';
  }

  /* ---------- Textos ---------- */
  function etiquetaFiltro(dim, valor) {
    if (dim === 'estado') return ETIQUETA_ESTADO[valor] || valor;
    return valor;
  }

  function chips(f) {
    var r = [];
    DIMENSIONES.forEach(function (d) {
      (f[d] || []).forEach(function (v) { r.push({ dim: d, valor: v, texto: ETIQUETA_DIMENSION[d] + ': ' + etiquetaFiltro(d, v) }); });
    });
    return r;
  }

  return {
    ESTADOS: ESTADOS, ETIQUETA_ESTADO: ETIQUETA_ESTADO, SITUACIONES_FUERA: SITUACIONES_FUERA, DIMENSIONES: DIMENSIONES,
    ETIQUETA_DIMENSION: ETIQUETA_DIMENSION, VISTAS: VISTAS, COLUMNAS_TABLA: COLUMNAS_TABLA, POR_PAGINA: POR_PAGINA,
    MINIMO_FAMILIA_TASA: MINIMO_FAMILIA_TASA, MINIMO_CAPACIDAD: MINIMO_CAPACIDAD, BTU_POR_TR: BTU_POR_TR, SIN_MODELO: SIN_MODELO,
    FRASE_MUESTRA_PEQUENA: FRASE_MUESTRA_PEQUENA,
    filasAObjetos: filasAObjetos, extraerModelo: extraerModelo, prepararEquipos: prepararEquipos, prepararExtensiones: prepararExtensiones,
    filtrosVacios: filtrosVacios, hayFiltros: hayFiltros, tiene: tiene, alternar: alternar, quitar: quitar, alternarPar: alternarPar,
    aplicar: aplicar, aplicarExtensiones: aplicarExtensiones, aHash: aHash, desdeHash: desdeHash,
    filtrosDeVista: filtrosDeVista, vistaActiva: vistaActiva, mismosFiltros: mismosFiltros,
    porcentaje: porcentaje, formatoPct: formatoPct, formatoNumero: formatoNumero, contar: contar, conteoPorEstado: conteoPorEstado,
    indicadores: indicadores, tasaArriendo: tasaArriendo, estadoPorFamilia: estadoPorFamilia, fueraDeServicioPorMotivo: fueraDeServicioPorMotivo,
    pareto: pareto, extensionesPorCorriente: extensionesPorCorriente, estadisticaCaja: estadisticaCaja, largoPorCorriente: largoPorCorriente,
    mapaDeCalor: mapaDeCalor, arbol: arbol, capacidadPorFamilia: capacidadPorFamilia, unidadesDisponibles: unidadesDisponibles,
    actividad: actividad, hallazgos: hallazgos, buscar: buscar, ordenar: ordenar, paginar: paginar, aCsv: aCsv, chips: chips, etiquetaFiltro: etiquetaFiltro
  };
});
