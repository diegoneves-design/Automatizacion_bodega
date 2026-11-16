/* Constructores de los 12 graficos del Dashboard (ECharts). Cada uno recibe el contexto y devuelve:
     titulo   la conclusion que muestra el grafico (se recalcula con los filtros)
     nota     como leerlo y que filtros lo afectan
     opcion   la configuracion de ECharts (null si no hay datos)
     vacio    mensaje cuando no hay datos
     tabla    { cabecera, filas:[{celdas, accion}] } para "Ver como tabla" (y para quien no usa el mouse)
     acciones { nombre: accion } para el clic; las celdas y areas del mapa de calor y del treemap la traen en el dato
     alto     alto en pixeles
   Una accion es { tipo:'alternar', dim, valor } o { tipo:'par', dimA, valA, dimB, valB }.
   No toca el DOM: solo arma datos. Usa Filtros (filtros.js). */
(function () {
  'use strict';
  var F = window.Filtros;

  var COLOR_ESTADO = { disponible: '#009E73', arrendado: '#0072B2', en_mantencion: '#E69F00', fuera_servicio: '#6b6f76' };
  var TEXTO_SOBRE = { disponible: '#000000', arrendado: '#ffffff', en_mantencion: '#000000', fuera_servicio: '#ffffff' };
  var TINTA = '#0f2540';
  var APOYO = '#4a586b';
  var LINEA = '#d3dae4';
  var NEUTRO = '#5b6b82';
  var ACENTO = '#b45309';
  var RECUPERABLE = '#009E73';
  var PALETA_ARBOL = ['#cfe3f5', '#d6ecd9', '#f9e3b4', '#e7d4ef', '#f6d0c9', '#d3dde8', '#e8e2c4', '#c9ebe6', '#e5e5e5', '#f3d9e6', '#dfe9c4'];
  var FUENTE = 'inherit';

  function esc(t) {
    return String(t).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; });
  }
  function nEq(n) { return F.formatoNumero(n) + (n === 1 ? ' equipo' : ' equipos'); }
  function pct(v) { return F.formatoPct(v); }
  function base(ctx, omitir) { return F.aplicar(ctx.equipos, ctx.filtros, omitir); }
  function a(dim, valor) { return { tipo: 'alternar', dim: dim, valor: valor }; }
  function seleccionado(ctx, dim, valor) { return F.tiene(ctx.filtros, dim, valor); }
  function haySeleccion(ctx, dim) { return ctx.filtros[dim] && ctx.filtros[dim].length > 0; }
  function opacidad(ctx, dim, valor) { return !haySeleccion(ctx, dim) || seleccionado(ctx, dim, valor) ? 1 : 0.35; }
  function marcaSeleccion(ctx, dim, valor) { return seleccionado(ctx, dim, valor) ? { borderColor: TINTA, borderWidth: 3 } : { borderWidth: 0 }; }

  /* Texto del tooltip: cantidad, % de lo que muestra el grafico y % del total general */
  function tip(nombre, n, poblacion, totalGeneral, extra) {
    return '<b>' + esc(nombre) + '</b><br>' + nEq(n) + (extra ? '<br>' + extra : '') +
      '<br>' + pct(F.porcentaje(n, poblacion)) + ' de los ' + F.formatoNumero(poblacion) + ' equipos filtrados' +
      '<br>' + pct(F.porcentaje(n, totalGeneral)) + ' del total general (' + F.formatoNumero(totalGeneral) + ')';
  }

  function comun(ctx) {
    return {
      animation: !ctx.reducido, animationDuration: 300, animationDurationUpdate: 300,
      textStyle: { fontFamily: FUENTE, color: TINTA }, aria: { enabled: true },
      tooltip: { trigger: 'item', confine: true, textStyle: { color: TINTA, fontSize: 13 }, borderColor: LINEA, extraCssText: 'max-width:280px;white-space:normal;' }
    };
  }

  var ejeTexto = { color: TINTA, fontSize: 12, fontFamily: FUENTE };
  var ejeLinea = { lineStyle: { color: LINEA } };
  var sinDatos = function (msg) { return { opcion: null, vacio: msg, tabla: { cabecera: [], filas: [] }, acciones: {} }; };

  function angosto(ctx) { return ctx.ancho < 520; }

  /* ---------- 1. Estado del inventario (dona) ---------- */
  function g1(ctx) {
    var lista = base(ctx, ['estado']);
    var c = F.conteoPorEstado(lista);
    var n = lista.length;
    if (!n) return sinDatos('No hay equipos con estos filtros.');
    var datos = F.ESTADOS.filter(function (e) { return c[e] > 0; }).map(function (e) {
      return { name: F.ETIQUETA_ESTADO[e], value: c[e], estado: e, accion: a('estado', e),
        itemStyle: Object.assign({ color: COLOR_ESTADO[e], opacity: opacidad(ctx, 'estado', e) }, marcaSeleccion(ctx, 'estado', e)) };
    });
    var mayor = datos.slice().sort(function (x, y) { return y.value - x.value; })[0];
    var op = Object.assign(comun(ctx), {
      tooltip: Object.assign(comun(ctx).tooltip, { formatter: function (p) { return tip(p.name, p.value, n, ctx.totalGeneral); } }),
      legend: angosto(ctx) ? { bottom: 0, selectedMode: false, textStyle: ejeTexto, itemGap: 10 } : { show: false },
      series: [{
        type: 'pie', radius: angosto(ctx) ? ['24%', '42%'] : ['42%', '66%'], center: ['50%', angosto(ctx) ? '38%' : '50%'], data: datos, avoidLabelOverlap: true,
        minShowLabelAngle: 0, itemStyle: { borderColor: '#fff', borderWidth: 2 },
        label: { color: TINTA, fontSize: angosto(ctx) ? 12 : 13, overflow: 'none', edgeDistance: 2, formatter: function (p) { return (angosto(ctx) ? '' : p.name + '\n') + F.formatoNumero(p.value) + ' · ' + pct(p.percent); }, lineHeight: 17 },
        labelLine: { length: 10, length2: 8, lineStyle: { color: APOYO } },
        emphasis: { scale: !ctx.reducido }
      }]
    });
    return {
      titulo: F.formatoPct(F.porcentaje(mayor.value, n)) + ' de los equipos está ' + mayor.name.toLowerCase(),
      nota: 'Cada trozo es un estado. Clic en un trozo para filtrar por ese estado; clic de nuevo para quitarlo. No lo afecta el filtro de estado, para que puedas cambiarlo.',
      aria: 'Gráfico de dona con la cantidad de equipos por estado.', alto: angosto(ctx) ? 330 : 360, opcion: op,
      tabla: { cabecera: ['Estado', 'Equipos', '% de lo filtrado', '% del total general'],
        filas: datos.map(function (d) { return { celdas: [d.name, F.formatoNumero(d.value), pct(F.porcentaje(d.value, n)), pct(F.porcentaje(d.value, ctx.totalGeneral))], accion: d.accion }; }) },
      acciones: {}
    };
  }

  /* ---------- 2. Equipos por categoria ---------- */
  function g2(ctx) {
    var lista = base(ctx, ['categoria']);
    var n = lista.length;
    if (!n) return sinDatos('No hay equipos con estos filtros.');
    var cuenta = F.contar(lista, function (e) { return e.categoria; });
    var acciones = {};
    cuenta.forEach(function (c) { acciones[c.clave] = a('categoria', c.clave); });
    var op = Object.assign(comun(ctx), {
      tooltip: Object.assign(comun(ctx).tooltip, { formatter: function (p) { return tip(p.name, p.value, n, ctx.totalGeneral); } }),
      grid: { left: 8, right: angosto(ctx) ? 70 : 90, top: 8, bottom: 8, containLabel: true },
      xAxis: { type: 'value', axisLabel: ejeTexto, splitLine: ejeLinea, minInterval: 1 },
      yAxis: { type: 'category', inverse: true, data: cuenta.map(function (c) { return c.clave; }), axisLabel: Object.assign({}, ejeTexto, { width: angosto(ctx) ? 110 : 190, overflow: 'break' }), axisLine: ejeLinea },
      series: [{
        type: 'bar', barMaxWidth: 26,
        data: cuenta.map(function (c) { return { name: c.clave, value: c.n, accion: acciones[c.clave], itemStyle: { color: NEUTRO, opacity: opacidad(ctx, 'categoria', c.clave), borderColor: TINTA, borderWidth: seleccionado(ctx, 'categoria', c.clave) ? 3 : 0 } }; }),
        label: { show: true, position: 'right', color: TINTA, fontSize: 12, formatter: function (p) { return F.formatoNumero(p.value) + ' (' + pct(F.porcentaje(p.value, n)) + ')'; } }
      }]
    });
    var tope = cuenta[0];
    return {
      titulo: tope.clave + ' es la categoría más grande: ' + F.formatoPct(F.porcentaje(tope.n, n)) + ' de los equipos',
      nota: 'Una barra por categoría del catálogo. Clic en una barra para filtrar por esa categoría.',
      aria: 'Gráfico de barras horizontales con equipos por categoría.', alto: Math.max(220, cuenta.length * 34 + 30), opcion: op, acciones: acciones,
      tabla: { cabecera: ['Categoría', 'Equipos', '% de lo filtrado', '% del total general'],
        filas: cuenta.map(function (c) { return { celdas: [c.clave, F.formatoNumero(c.n), pct(F.porcentaje(c.n, n)), pct(F.porcentaje(c.n, ctx.totalGeneral))], accion: acciones[c.clave] }; }) }
    };
  }

  /* ---------- 3. Tasa de arriendo por familia ---------- */
  function g3(ctx) {
    var lista = base(ctx, ['familia', 'estado']);
    var t = F.tasaArriendo(lista);
    var nota = 'Solo familias con ' + F.MINIMO_FAMILIA_TASA + ' o más equipos: con menos, un solo equipo cambia mucho el porcentaje. La línea punteada es el promedio general de lo filtrado. No la afectan los filtros de familia ni de estado.';
    if (!t.filas.length) return Object.assign(sinDatos('Ninguna familia tiene ' + F.MINIMO_FAMILIA_TASA + ' o más equipos con estos filtros.'), { titulo: 'Sin familias con ' + F.MINIMO_FAMILIA_TASA + ' o más equipos', nota: nota, aria: 'Gráfico sin datos.', alto: 120 });
    var porc = ctx.modo3 !== 'cantidad';
    var acciones = {};
    t.filas.forEach(function (f) { acciones[f.familia] = a('familia', f.familia); });
    var series = [{
      name: porc ? 'Tasa de arriendo' : 'Equipos arrendados', type: 'bar', barMaxWidth: 46,
      data: t.filas.map(function (f) { return { name: f.familia, value: porc ? Math.round(f.tasa * 10) / 10 : f.arrendados, accion: acciones[f.familia], itemStyle: { color: COLOR_ESTADO.arrendado, opacity: opacidad(ctx, 'familia', f.familia), borderColor: TINTA, borderWidth: seleccionado(ctx, 'familia', f.familia) ? 3 : 0 } }; }),
      label: { show: true, position: 'top', color: TINTA, fontSize: 12, formatter: function (p) { return porc ? pct(p.value) : F.formatoNumero(p.value); } }
    }];
    if (porc) {
      series.push({
        name: 'Promedio general (' + pct(t.promedio) + ')', type: 'line', symbol: 'none', silent: true, data: t.filas.map(function () { return Math.round(t.promedio * 10) / 10; }),
        lineStyle: { color: ACENTO, type: 'dashed', width: 2 }, itemStyle: { color: ACENTO },
        endLabel: { show: true, formatter: 'Promedio ' + pct(t.promedio), color: ACENTO, fontSize: 12, distance: 4 }, z: 5
      });
    }
    var op = Object.assign(comun(ctx), {
      tooltip: Object.assign(comun(ctx).tooltip, { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: function (ps) {
        var f = t.filas[ps[0].dataIndex];
        return '<b>Familia ' + esc(f.familia) + '</b><br>' + nEq(f.arrendados) + ' arrendados de ' + F.formatoNumero(f.total) + ' (' + pct(f.tasa) + ')' +
          '<br>' + pct(F.porcentaje(f.arrendados, lista.length)) + ' de los ' + F.formatoNumero(lista.length) + ' equipos filtrados' +
          '<br>' + pct(F.porcentaje(f.arrendados, ctx.totalGeneral)) + ' del total general (' + F.formatoNumero(ctx.totalGeneral) + ')';
      } }),
      legend: { top: 0, textStyle: ejeTexto, itemWidth: 18 }, grid: { left: 8, right: 100, top: 36, bottom: 8, containLabel: true },
      xAxis: { type: 'category', data: t.filas.map(function (f) { return f.familia; }), axisLabel: ejeTexto, axisLine: ejeLinea },
      yAxis: { type: 'value', axisLabel: Object.assign({}, ejeTexto, { formatter: porc ? '{value} %' : '{value}' }), splitLine: ejeLinea, minInterval: porc ? undefined : 1, max: porc ? undefined : undefined },
      series: series
    });
    var alta = t.filas[0];
    return {
      titulo: 'La familia ' + alta.familia + ' es la que más se arrienda: ' + pct(alta.tasa) + ' (promedio ' + pct(t.promedio) + ')',
      nota: nota, aria: 'Gráfico de barras con la tasa de arriendo por familia y una línea con el promedio general.', alto: 360, opcion: op, acciones: acciones, modos: 'modo3',
      tabla: { cabecera: ['Familia', 'Equipos', 'Arrendados', 'Tasa de arriendo'],
        filas: t.filas.map(function (f) { return { celdas: [f.familia, F.formatoNumero(f.total), F.formatoNumero(f.arrendados), pct(f.tasa)], accion: acciones[f.familia] }; }) }
    };
  }

  /* ---------- 4. Estado por familia (apilado) ---------- */
  function g4(ctx) {
    var lista = base(ctx, ['familia', 'estado']);
    var filas = F.estadoPorFamilia(lista, 8);
    if (!filas.length) return sinDatos('No hay equipos con estos filtros.');
    var porc = ctx.modo4 !== 'cantidad';
    var series = F.ESTADOS.map(function (e) {
      return {
        name: F.ETIQUETA_ESTADO[e], type: 'bar', stack: 'estado', barMaxWidth: 34,
        itemStyle: { color: COLOR_ESTADO[e] },
        data: filas.map(function (f) {
          var sel = F.tiene(ctx.filtros, 'familia', f.familia) && F.tiene(ctx.filtros, 'estado', e);
          return { name: f.familia, value: porc ? Math.round(f.pct[e] * 10) / 10 : f.conteo[e], n: f.conteo[e], total: f.total, familia: f.familia, estado: e,
            accion: { tipo: 'par', dimA: 'familia', valA: f.familia, dimB: 'estado', valB: e },
            itemStyle: { color: COLOR_ESTADO[e], borderColor: TINTA, borderWidth: sel ? 3 : 0 } };
        }),
        label: { show: true, color: TEXTO_SOBRE[e], fontSize: 11, formatter: function (p) {
          var minimo = porc ? 6 : Math.max(...filas.map(function (f) { return f.total; })) * 0.06;
          return p.value >= minimo ? (porc ? Math.round(p.value) + ' %' : F.formatoNumero(p.value)) : '';
        } }
      };
    });
    var op = Object.assign(comun(ctx), {
      tooltip: Object.assign(comun(ctx).tooltip, { formatter: function (p) {
        var d = p.data;
        return '<b>Familia ' + esc(d.familia) + ' · ' + esc(F.ETIQUETA_ESTADO[d.estado]) + '</b><br>' + nEq(d.n) + ' de ' + F.formatoNumero(d.total) + ' (' + pct(F.porcentaje(d.n, d.total)) + ' de la familia)' +
          '<br>' + pct(F.porcentaje(d.n, lista.length)) + ' de los ' + F.formatoNumero(lista.length) + ' equipos filtrados' +
          '<br>' + pct(F.porcentaje(d.n, ctx.totalGeneral)) + ' del total general (' + F.formatoNumero(ctx.totalGeneral) + ')';
      } }),
      legend: { top: 0, textStyle: ejeTexto }, grid: { left: 8, right: 16, top: angosto(ctx) ? 64 : 36, bottom: 8, containLabel: true },
      xAxis: { type: 'value', max: porc ? 100 : undefined, axisLabel: Object.assign({}, ejeTexto, { formatter: porc ? '{value} %' : '{value}' }), splitLine: ejeLinea },
      yAxis: { type: 'category', inverse: true, data: filas.map(function (f) { return f.familia; }), axisLabel: ejeTexto, axisLine: ejeLinea },
      series: series
    });
    var peor = filas.slice().sort(function (x, y) { return y.pct.fuera_servicio - x.pct.fuera_servicio; })[0];
    return {
      titulo: 'En la familia ' + peor.familia + ' ' + pct(peor.pct.fuera_servicio) + ' de los equipos está fuera de servicio, la proporción más alta entre las 8 mayores',
      nota: 'Las 8 familias con más equipos. Clic en un tramo para filtrar por esa familia y ese estado a la vez. No la afectan los filtros de familia ni de estado.',
      aria: 'Gráfico de barras apiladas con el estado de los equipos en las 8 familias más grandes.', alto: filas.length * 44 + (angosto(ctx) ? 90 : 60), opcion: op, acciones: {}, modos: 'modo4',
      tabla: { cabecera: ['Familia', 'Equipos'].concat(F.ESTADOS.map(function (e) { return F.ETIQUETA_ESTADO[e]; })),
        filas: filas.map(function (f) { return { celdas: [f.familia, F.formatoNumero(f.total)].concat(F.ESTADOS.map(function (e) { return F.formatoNumero(f.conteo[e]) + ' (' + pct(f.pct[e]) + ')'; })), accion: a('familia', f.familia) }; }) }
    };
  }

  /* ---------- 5. Fuera de servicio por motivo ---------- */
  function g5(ctx) {
    var lista = base(ctx, ['estado', 'situacion']);
    var r = F.fueraDeServicioPorMotivo(lista);
    if (!r.total) return sinDatos('No hay equipos fuera de servicio con estos filtros.');
    var acciones = {};
    r.filas.forEach(function (f) { acciones[f.situacion] = a('situacion', f.situacion); });
    var op = Object.assign(comun(ctx), {
      tooltip: Object.assign(comun(ctx).tooltip, { formatter: function (p) {
        var rec = p.name === 'POR HABILITAR' ? 'Inventario recuperable' : '';
        return tip(p.name, p.value, r.total, ctx.totalGeneral, rec).replace('equipos filtrados', 'equipos fuera de servicio');
      } }),
      grid: { left: 8, right: 16, top: 28, bottom: 8, containLabel: true },
      xAxis: { type: 'category', data: r.filas.map(function (f) { return f.situacion; }), axisLabel: Object.assign({}, ejeTexto, { interval: 0, width: angosto(ctx) ? 64 : 120, overflow: 'break' }), axisLine: ejeLinea },
      yAxis: { type: 'value', axisLabel: ejeTexto, splitLine: ejeLinea, minInterval: 1 },
      series: [{
        type: 'bar', barMaxWidth: 56,
        data: r.filas.map(function (f) { return { name: f.situacion, value: f.n, accion: acciones[f.situacion],
          itemStyle: { color: f.situacion === 'POR HABILITAR' ? RECUPERABLE : '#6b6f76', opacity: opacidad(ctx, 'situacion', f.situacion), borderColor: TINTA, borderWidth: seleccionado(ctx, 'situacion', f.situacion) ? 3 : 0 } }; }),
        label: { show: true, position: 'top', color: TINTA, fontSize: 12, formatter: function (p) { return F.formatoNumero(p.value) + ' (' + pct(F.porcentaje(p.value, r.total)) + ')'; } }
      }]
    });
    var por = r.filas.filter(function (f) { return f.situacion === 'POR HABILITAR'; })[0];
    return {
      titulo: F.formatoNumero(por.n) + ' equipos fuera de servicio están «por habilitar»: inventario que se podría recuperar',
      nota: 'Solo equipos fuera de servicio. «Por habilitar» va en verde porque podría volver a servicio; «baja» puede ser definitiva (por confirmar con la bodega). No la afectan los filtros de estado ni de situación.',
      aria: 'Gráfico de barras con los equipos fuera de servicio según su motivo.', alto: 340, opcion: op, acciones: acciones,
      tabla: { cabecera: ['Situación', 'Equipos', '% de los fuera de servicio'],
        filas: r.filas.map(function (f) { return { celdas: [f.situacion, F.formatoNumero(f.n), pct(f.pct)], accion: acciones[f.situacion] }; }) }
    };
  }

  /* ---------- 6. Pareto de modelos ---------- */
  function g6(ctx) {
    var lista = base(ctx, ['modelo']);
    var p = F.pareto(lista, 10);
    if (!p.filas.length) return sinDatos('Ningún equipo de esta selección trae el modelo en su descripción.');
    var acciones = {};
    p.filas.forEach(function (f) { acciones[f.modelo] = a('modelo', f.modelo); });
    var op = Object.assign(comun(ctx), {
      tooltip: Object.assign(comun(ctx).tooltip, { trigger: 'axis', axisPointer: { type: 'shadow' }, formatter: function (ps) {
        var f = p.filas[ps[0].dataIndex];
        return '<b>Modelo ' + esc(f.modelo) + '</b><br>' + nEq(f.n) + '<br>' + pct(f.pct) + ' de los ' + F.formatoNumero(p.total) + ' equipos filtrados' +
          '<br>' + pct(F.porcentaje(f.n, ctx.totalGeneral)) + ' del total general (' + F.formatoNumero(ctx.totalGeneral) + ')<br>Acumulado: ' + pct(f.acumulado) + ' del total filtrado';
      } }),
      legend: { top: 0, textStyle: ejeTexto }, grid: { left: 8, right: 8, top: 36, bottom: 8, containLabel: true },
      xAxis: { type: 'category', data: p.filas.map(function (f) { return f.modelo; }), axisLabel: Object.assign({}, ejeTexto, { interval: 0, rotate: angosto(ctx) ? 60 : 30 }), axisLine: ejeLinea },
      yAxis: [{ type: 'value', axisLabel: ejeTexto, splitLine: ejeLinea, minInterval: 1 },
        { type: 'value', min: 0, max: 100, axisLabel: Object.assign({}, ejeTexto, { formatter: '{value} %' }), splitLine: { show: false } }],
      series: [
        { name: 'Equipos por modelo', type: 'bar', barMaxWidth: 40,
          data: p.filas.map(function (f) { return { name: f.modelo, value: f.n, accion: acciones[f.modelo], itemStyle: { color: NEUTRO, opacity: opacidad(ctx, 'modelo', f.modelo), borderColor: TINTA, borderWidth: seleccionado(ctx, 'modelo', f.modelo) ? 3 : 0 } }; }),
          label: { show: true, position: 'top', color: TINTA, fontSize: 12, formatter: function (x) { return F.formatoNumero(x.value); } } },
        { name: '% acumulado del total', type: 'line', yAxisIndex: 1, symbol: 'circle', symbolSize: 7, lineStyle: { color: ACENTO, width: 2 }, itemStyle: { color: ACENTO },
          data: p.filas.map(function (f) { return Math.round(f.acumulado * 10) / 10; }),
          label: { show: true, position: 'top', color: ACENTO, fontSize: 12, fontWeight: 'bold', backgroundColor: '#ffffff', padding: [1, 3], borderRadius: 3, formatter: function (x) { return pct(x.value); } } }
      ]
    });
    var top = p.filas[0];
    return {
      titulo: 'El modelo ' + top.modelo + ' reúne ' + F.formatoNumero(top.n) + ' equipos (' + pct(top.pct) + ' del total); los ' + p.filas.length + ' principales suman ' + pct(p.filas[p.filas.length - 1].acumulado),
      nota: 'Regla de agrupación: el modelo es la primera palabra que sigue a «MODELO» en la descripción del equipo, en mayúsculas; las descripciones distintas con el mismo modelo se suman. ' +
        F.formatoNumero(p.sinModelo) + ' equipos no traen la palabra «modelo» y no entran al ranking, pero sí al total sobre el que se calcula el % acumulado (' + F.formatoNumero(p.total) + '). No la afecta el filtro de modelo.',
      aria: 'Gráfico de Pareto: barras con las unidades de los diez modelos más repetidos y una línea con el porcentaje acumulado.', alto: 380, opcion: op, acciones: acciones,
      tabla: { cabecera: ['Modelo', 'Equipos', '% del total filtrado', '% acumulado'],
        filas: p.filas.map(function (f) { return { celdas: [f.modelo, F.formatoNumero(f.n), pct(f.pct), pct(f.acumulado)], accion: acciones[f.modelo] }; }) }
    };
  }

  /* ---------- 7. Extensiones por corriente ---------- */
  function g7(ctx) {
    var ext = F.aplicarExtensiones(ctx.extensiones, ctx.filtros, ['corriente']);
    if (!ext.length) return sinDatos('No hay extensiones eléctricas cargadas.');
    var filas = F.extensionesPorCorriente(ext);
    var acciones = {};
    filas.forEach(function (f) { acciones[f.corriente] = a('corriente', f.corriente); });
    var op = Object.assign(comun(ctx), {
      tooltip: Object.assign(comun(ctx).tooltip, { formatter: function (p) {
        return '<b>' + esc(p.name) + '</b><br>' + F.formatoNumero(p.value) + ' extensiones<br>' + pct(F.porcentaje(p.value, ext.length)) + ' de las ' + F.formatoNumero(ext.length) + ' extensiones';
      } }),
      grid: { left: 8, right: 8, top: 28, bottom: 8, containLabel: true },
      xAxis: { type: 'category', data: filas.map(function (f) { return f.corriente; }), axisLabel: Object.assign({}, ejeTexto, { interval: 0 }), axisLine: ejeLinea },
      yAxis: { type: 'value', axisLabel: ejeTexto, splitLine: ejeLinea, minInterval: 1 },
      series: [{ type: 'bar', barMaxWidth: 48,
        data: filas.map(function (f) { return { name: f.corriente, value: f.n, accion: acciones[f.corriente], itemStyle: { color: NEUTRO, opacity: opacidad(ctx, 'corriente', f.corriente), borderColor: TINTA, borderWidth: seleccionado(ctx, 'corriente', f.corriente) ? 3 : 0 } }; }),
        label: { show: true, position: 'top', color: TINTA, fontSize: 12, formatter: function (p) { return F.formatoNumero(p.value) + ' (' + pct(F.porcentaje(p.value, ext.length)) + ')'; } } }]
    });
    var top = filas.slice().sort(function (x, y) { return y.n - x.n; })[0];
    return {
      titulo: 'La corriente más común es ' + top.corriente + ': ' + F.formatoNumero(top.n) + ' de ' + F.formatoNumero(ext.length) + ' extensiones (' + pct(top.pct) + ')',
      nota: 'Las extensiones eléctricas son otra lista (no tienen estado), por eso los filtros de equipos no las afectan; solo el filtro de corriente. Clic en una barra para filtrar por corriente.',
      aria: 'Gráfico de barras con la cantidad de extensiones eléctricas por corriente.', alto: 330, opcion: op, acciones: acciones,
      tabla: { cabecera: ['Corriente', 'Extensiones', '% del total'],
        filas: filas.map(function (f) { return { celdas: [f.corriente, F.formatoNumero(f.n), pct(f.pct)], accion: acciones[f.corriente] }; }) }
    };
  }

  /* Caja con mediana etiquetada y atipicos. `cajas` = [{nombre, caja}] */
  function opcionCaja(ctx, cajas, nombreEje, unidad, dim) {
    var acciones = {};
    cajas.forEach(function (c) { acciones[c.nombre] = a(dim, c.nombre); });
    var fmt = function (v) { return F.formatoNumero(v) + (unidad ? ' ' + unidad : ''); };
    var atipicos = [];
    cajas.forEach(function (c) { c.caja.atipicos.forEach(function (v) { atipicos.push({ name: c.nombre, value: [c.nombre, v] }); }); });
    var medianas = cajas.map(function (c) { return { name: c.nombre, value: [c.nombre, c.caja.mediana] }; });
    return {
      acciones: acciones,
      opcion: Object.assign(comun(ctx), {
        tooltip: Object.assign(comun(ctx).tooltip, { formatter: function (p) {
          if (p.seriesType === 'scatter') return '<b>' + esc(p.name) + '</b><br>' + (p.seriesName === 'Mediana' ? 'Mediana: ' : 'Valor atípico: ') + fmt(p.value[1]);
          var c = cajas[p.dataIndex].caja;
          return '<b>' + esc(p.name) + '</b> · ' + F.formatoNumero(c.n) + ' equipos<br>Mediana: ' + fmt(c.mediana) + '<br>Cuartiles: ' + fmt(c.q1) + ' a ' + fmt(c.q3) +
            '<br>Sin atípicos: ' + fmt(c.min) + ' a ' + fmt(c.max) + '<br>Valores atípicos: ' + c.atipicos.length;
        } }),
        legend: { top: 0, textStyle: ejeTexto, data: ['Caja (cuartiles)', 'Mediana', 'Valor atípico'] },
        grid: { left: 8, right: 24, top: angosto(ctx) ? 64 : 40, bottom: 8, containLabel: true },
        xAxis: { type: 'category', data: cajas.map(function (c) { return c.nombre; }), axisLabel: Object.assign({}, ejeTexto, { interval: 0 }), axisLine: ejeLinea, name: nombreEje, nameLocation: 'middle', nameGap: 30, nameTextStyle: ejeTexto },
        yAxis: { type: 'value', name: unidad || '', nameTextStyle: ejeTexto, axisLabel: ejeTexto, splitLine: ejeLinea, scale: true },
        series: [
          { name: 'Caja (cuartiles)', type: 'boxplot', boxWidth: [12, 40],
            data: cajas.map(function (c) { return { name: c.nombre, value: [c.caja.min, c.caja.q1, c.caja.mediana, c.caja.q3, c.caja.max], accion: acciones[c.nombre],
              itemStyle: { color: '#dbe7f5', borderColor: TINTA, borderWidth: seleccionado(ctx, dim, c.nombre) ? 3 : 1.5, opacity: opacidad(ctx, dim, c.nombre) } }; }) },
          { name: 'Mediana', type: 'scatter', symbol: 'diamond', symbolSize: 9, itemStyle: { color: ACENTO }, data: medianas, z: 6,
            label: { show: true, position: 'right', offset: [8, 0], color: ACENTO, fontWeight: 'bold', fontSize: 12, backgroundColor: '#ffffff', padding: [1, 3], borderRadius: 3, formatter: function (p) { return F.formatoNumero(p.value[1]); } } },
          { name: 'Valor atípico', type: 'scatter', symbol: 'circle', symbolSize: 7, itemStyle: { color: 'rgba(255,255,255,0)', borderColor: '#b42323', borderWidth: 2 }, data: atipicos, z: 5 }
        ]
      })
    };
  }

  /* ---------- 8. Largo de las extensiones por corriente ---------- */
  function g8(ctx) {
    var ext = F.aplicarExtensiones(ctx.extensiones, ctx.filtros);
    var l = F.largoPorCorriente(ext);
    if (!l.filas.length) return sinDatos('No hay extensiones con largo para mostrar.');
    var cajas = l.filas.map(function (f) { return { nombre: f.corriente, caja: f.caja }; });
    var oc = opcionCaja(ctx, cajas, 'Corriente', 'm', 'corriente');
    var todas = F.estadisticaCaja(ext.map(function (x) { return x.largo_m; }).filter(function (v) { return v != null; }));
    return {
      titulo: 'La mitad de las extensiones mide entre ' + F.formatoNumero(todas.q1) + ' y ' + F.formatoNumero(todas.q3) + ' m; la mediana es ' + F.formatoNumero(todas.mediana) + ' m',
      nota: 'La caja va del primer al tercer cuartil y la línea interior y el rombo son la mediana; los círculos rojos son valores atípicos (lejos del resto). ' +
        (l.sinLargo ? F.formatoNumero(l.sinLargo) + ' extensiones sin largo no aparecen. ' : '') + 'Muestra solo las corrientes filtradas; no la afectan los filtros de equipos.',
      aria: 'Diagrama de caja con el largo en metros de las extensiones eléctricas, por corriente.', alto: 380, opcion: oc.opcion, acciones: oc.acciones,
      tabla: { cabecera: ['Corriente', 'Extensiones', 'Mínimo', 'Cuartil 1', 'Mediana', 'Cuartil 3', 'Máximo', 'Atípicos'],
        filas: cajas.map(function (c) { var k = c.caja; return { celdas: [c.nombre, F.formatoNumero(k.n), k.min + ' m', k.q1 + ' m', k.mediana + ' m', k.q3 + ' m', k.max + ' m', String(k.atipicos.length)], accion: oc.acciones[c.nombre] }; }) }
    };
  }

  /* ---------- 9. Mapa de calor familia x estado ---------- */
  function g9(ctx) {
    var lista = base(ctx, ['familia', 'estado']);
    if (!lista.length) return sinDatos('No hay equipos con estos filtros.');
    var h = F.mapaDeCalor(lista);
    var datos = h.celdas.map(function (c) {
      var oscuro = c.n > h.maximo * 0.65;
      var sel = F.tiene(ctx.filtros, 'familia', c.familia) && F.tiene(ctx.filtros, 'estado', c.estado);
      return { value: [c.x, c.y, c.n], n: c.n, familia: c.familia, estado: c.estado,
        accion: { tipo: 'par', dimA: 'familia', valA: c.familia, dimB: 'estado', valB: c.estado },
        label: { show: true, color: oscuro ? '#ffffff' : TINTA, formatter: c.n ? F.formatoNumero(c.n) : '0' },
        itemStyle: { borderColor: sel ? TINTA : '#ffffff', borderWidth: sel ? 3 : 1 } };
    });
    var op = Object.assign(comun(ctx), {
      tooltip: Object.assign(comun(ctx).tooltip, { formatter: function (p) {
        var d = p.data;
        return tip('Familia ' + d.familia + ' · ' + F.ETIQUETA_ESTADO[d.estado], d.n, lista.length, ctx.totalGeneral);
      } }),
      grid: { left: 8, right: 8, top: 36, bottom: 8, containLabel: true },
      xAxis: { type: 'category', position: 'top', data: h.estados.map(function (e) { return F.ETIQUETA_ESTADO[e]; }), axisLabel: Object.assign({}, ejeTexto, { interval: 0, width: angosto(ctx) ? 62 : 120, overflow: 'break' }), axisLine: ejeLinea, splitArea: { show: false } },
      yAxis: { type: 'category', inverse: true, data: h.familias, axisLabel: Object.assign({}, ejeTexto, { interval: 0 }), axisLine: ejeLinea },
      visualMap: { show: false, min: 0, max: Math.max(1, h.maximo), inRange: { color: ['#eef3fa', '#00507f'] } },
      series: [{ type: 'heatmap', data: datos, emphasis: { itemStyle: { borderColor: TINTA, borderWidth: 2 } } }]
    });
    var mayor = h.celdas.slice().sort(function (x, y) { return y.n - x.n; })[0];
    return {
      titulo: 'La mayor concentración está en ' + mayor.familia + ' · ' + F.ETIQUETA_ESTADO[mayor.estado].toLowerCase() + ': ' + F.formatoNumero(mayor.n) + ' equipos',
      nota: 'Cada celda cuenta los equipos de una familia en un estado; más oscuro, más equipos. Clic en una celda para filtrar por esa familia y ese estado. No la afectan los filtros de familia ni de estado.',
      aria: 'Mapa de calor con la cantidad de equipos por familia y estado.', alto: h.familias.length * 28 + 70, opcion: op, acciones: {}, ancho: true,
      tabla: { cabecera: ['Familia'].concat(h.estados.map(function (e) { return F.ETIQUETA_ESTADO[e]; })),
        filas: h.familias.map(function (fam) { return { celdas: [fam].concat(h.estados.map(function (e) { return F.formatoNumero(h.celdas.filter(function (c) { return c.familia === fam && c.estado === e; })[0].n); })), accion: a('familia', fam) }; }) }
    };
  }

  /* ---------- 10. Treemap categoria > familia ---------- */
  function g10(ctx) {
    var lista = base(ctx, ['categoria', 'familia']);
    if (!lista.length) return sinDatos('No hay equipos con estos filtros.');
    var arbol = F.arbol(lista);
    var n = lista.length;
    var datos = arbol.map(function (c, i) {
      var color = PALETA_ARBOL[i % PALETA_ARBOL.length];
      return { name: c.nombre, value: c.valor, accion: a('categoria', c.nombre),
        itemStyle: { color: color, borderColor: seleccionado(ctx, 'categoria', c.nombre) ? TINTA : '#ffffff', borderWidth: seleccionado(ctx, 'categoria', c.nombre) ? 4 : 2 },
        children: c.hijos.map(function (h) { return { name: h.nombre, value: h.valor, categoria: c.nombre, accion: a('familia', h.nombre),
          itemStyle: { color: color, borderColor: seleccionado(ctx, 'familia', h.nombre) ? TINTA : '#ffffff', borderWidth: seleccionado(ctx, 'familia', h.nombre) ? 3 : 1 } }; }) };
    });
    var op = Object.assign(comun(ctx), {
      tooltip: Object.assign(comun(ctx).tooltip, { formatter: function (p) {
        var d = p.data;
        return tip((d.categoria ? d.categoria + ' › familia ' : 'Categoría ') + d.name, d.value, n, ctx.totalGeneral);
      } }),
      series: [{ type: 'treemap', roam: false, nodeClick: false, breadcrumb: { show: false }, left: 0, right: 0, top: 0, bottom: 0, data: datos,
        visibleMin: 80,
        label: { show: true, color: TINTA, fontSize: 12, formatter: function (p) { return p.name + '\n' + F.formatoNumero(p.value) + ' · ' + pct(F.porcentaje(p.value, n)); } },
        upperLabel: { show: true, height: 22, color: TINTA, fontWeight: 'bold', fontSize: 12 },
        levels: [{ itemStyle: { borderColor: '#ffffff', borderWidth: 0, gapWidth: 0 }, upperLabel: { show: false } },
          { itemStyle: { borderColor: '#ffffff', borderWidth: 3, gapWidth: 3 }, upperLabel: { show: true, height: 22, formatter: function (p) { return p.name + ' · ' + F.formatoNumero(p.value) + ' (' + pct(F.porcentaje(p.value, n)) + ')'; } } },
          { itemStyle: { borderColor: '#ffffff', borderWidth: 1, gapWidth: 1 }, upperLabel: { show: false } }] }]
    });
    return {
      titulo: arbol[0].nombre + ' es la categoría más grande: ' + pct(F.porcentaje(arbol[0].valor, n)) + ' de los equipos, repartida en ' + arbol[0].hijos.length + (arbol[0].hijos.length === 1 ? ' familia' : ' familias'),
      nota: 'El área es la cantidad de equipos: cada bloque grande es una categoría y los bloques interiores son sus familias. Clic en una familia o en el título de una categoría para filtrar. No la afectan los filtros de categoría ni de familia.',
      aria: 'Treemap de equipos por categoría y familia.', alto: angosto(ctx) ? 420 : 460, opcion: op, acciones: {}, ancho: true,
      tabla: { cabecera: ['Categoría', 'Familia', 'Equipos', '% de lo filtrado'],
        filas: [].concat.apply([], arbol.map(function (c) { return c.hijos.map(function (h) { return { celdas: [c.nombre, h.nombre, F.formatoNumero(h.valor), pct(F.porcentaje(h.valor, n))], accion: a('familia', h.nombre) }; }); })) }
    };
  }

  /* ---------- 11. Capacidad por familia ---------- */
  function g11(ctx) {
    var lista = base(ctx, ['familia']);
    var unidades = F.unidadesDisponibles(lista);
    var unidad = ctx.unidad && unidades.indexOf(ctx.unidad) !== -1 ? ctx.unidad : unidades[0];
    if (!unidad) return Object.assign(sinDatos('Ningún equipo de esta selección tiene capacidad extraída.'), { titulo: 'Sin capacidad extraída en esta selección', nota: '', aria: 'Gráfico sin datos.', alto: 120, unidades: [] });
    var c = F.capacidadPorFamilia(lista, unidad);
    var notaBase = 'La capacidad se leyó de la descripción de cada equipo (BTU/H, m³/h o kW), así que puede faltar. Cada vista usa una sola unidad y muestra familias con ' + F.MINIMO_CAPACIDAD + ' o más equipos con capacidad en esa unidad. ';
    var detalle = F.formatoNumero(c.sinCapacidad) + ' equipos quedaron sin capacidad extraída' +
      (c.enOtraUnidad ? '; ' + F.formatoNumero(c.enOtraUnidad) + ' tienen capacidad en otra unidad (cámbiala arriba para verlos)' : '') +
      (c.enFamiliasPequenas ? '; ' + F.formatoNumero(c.enFamiliasPequenas) + ' están en familias con menos de ' + F.MINIMO_CAPACIDAD + ' equipos' : '') + '.';
    var conversion = unidad === 'BTU/H' ? ' ' + (c.convertidosDeTR ? F.formatoNumero(c.convertidosDeTR) + ' equipos venían en TR y se convirtieron a BTU/H (1 TR = 12.000 BTU/H).' : 'Los equipos en TR se convertirían a BTU/H (1 TR = 12.000 BTU/H); ninguno entra en esta selección.') : '';
    if (!c.filas.length) return Object.assign(sinDatos('Ninguna familia tiene ' + F.MINIMO_CAPACIDAD + ' o más equipos con capacidad en ' + unidad + ' con estos filtros.'), { titulo: 'Sin familias con capacidad suficiente en ' + unidad, nota: notaBase + detalle + conversion, aria: 'Gráfico sin datos.', alto: 120, unidades: unidades, unidad: unidad });
    var cajas = c.filas.map(function (f) { return { nombre: f.familia, caja: f.caja }; });
    var oc = opcionCaja(ctx, cajas, 'Familia', unidad, 'familia');
    var mayor = c.filas.slice().sort(function (x, y) { return y.caja.mediana - x.caja.mediana; })[0];
    return {
      titulo: 'La familia ' + mayor.familia + ' tiene la mayor capacidad mediana: ' + F.formatoNumero(mayor.caja.mediana) + ' ' + unidad,
      nota: notaBase + detalle + conversion + ' No la afecta el filtro de familia.',
      aria: 'Diagrama de caja con la capacidad de los equipos por familia en ' + unidad + '.', alto: 400, opcion: oc.opcion, acciones: oc.acciones, unidades: unidades, unidad: unidad,
      tabla: { cabecera: ['Familia', 'Equipos', 'Mínimo', 'Cuartil 1', 'Mediana', 'Cuartil 3', 'Máximo', 'Atípicos'],
        filas: cajas.map(function (k) { var q = k.caja; var u = ' ' + unidad; return { celdas: [k.nombre, F.formatoNumero(q.n), F.formatoNumero(q.min) + u, F.formatoNumero(q.q1) + u, F.formatoNumero(q.mediana) + u, F.formatoNumero(q.q3) + u, F.formatoNumero(q.max) + u, String(q.atipicos.length)], accion: oc.acciones[k.nombre] }; }) }
    };
  }

  /* ---------- 12. Actividad del MVP (no depende de los filtros) ---------- */
  var ETIQUETA_ORDEN = { pendiente: 'Pendiente', bloqueada: 'Bloqueada', validada: 'Validada', emitida: 'Guía emitida' };
  function barrasSimples(ctx, lista, color) {
    return Object.assign(comun(ctx), {
      tooltip: Object.assign(comun(ctx).tooltip, { formatter: function (p) { return '<b>' + esc(p.name) + '</b><br>' + F.formatoNumero(p.value); } }),
      grid: { left: 8, right: 40, top: 8, bottom: 8, containLabel: true },
      xAxis: { type: 'value', axisLabel: ejeTexto, splitLine: ejeLinea, minInterval: 1 },
      yAxis: { type: 'category', inverse: true, data: lista.map(function (x) { return x.nombre; }), axisLabel: Object.assign({}, ejeTexto, { width: angosto(ctx) ? 120 : 200, overflow: 'break' }), axisLine: ejeLinea },
      series: [{ type: 'bar', barMaxWidth: 26, itemStyle: { color: color }, data: lista.map(function (x) { return { name: x.nombre, value: x.n }; }),
        label: { show: true, position: 'right', color: TINTA, fontSize: 12, formatter: function (p) { return F.formatoNumero(p.value); } } }]
    });
  }

  function g12(ctx) {
    var act = F.actividad(ctx.actividad);
    var ordenes = act.ordenes.map(function (x) { return { nombre: ETIQUETA_ORDEN[x.clave] || x.clave, n: x.n }; });
    var cambios = act.cambios.map(function (x) { return { nombre: x.clave, n: x.n }; });
    var pocos = act.totalOrdenes + act.totalCambios < 10;
    return {
      titulo: act.totalOrdenes + (act.totalOrdenes === 1 ? ' orden' : ' órdenes') + ' y ' + act.totalCambios + (act.totalCambios === 1 ? ' cambio registrado' : ' cambios registrados') + ' en el MVP hasta ahora',
      nota: 'Esta actividad viene de las órdenes de la demo del prototipo, no del inventario, y no depende de ninguno de los filtros de arriba. ' +
        (pocos ? 'Hay muy pocos datos: son órdenes de ejemplo y, al reiniciar la demo, los cambios se borran. Sirve para ver que el registro funciona, no para sacar conclusiones.' : 'Son datos de ejemplo; al reiniciar la demo se borran.'),
      doble: true, aria: 'Dos gráficos de barras: órdenes por estado y cambios registrados por motivo.',
      sub: [
        { id: 'a', titulo: 'Órdenes por estado', vacio: ordenes.length ? null : 'Todavía no hay órdenes.', opcion: ordenes.length ? barrasSimples(ctx, ordenes, NEUTRO) : null, alto: Math.max(120, ordenes.length * 40 + 30) },
        { id: 'b', titulo: 'Cambios registrados por motivo', vacio: cambios.length ? null : 'Todavía no se registraron cambios: aparecen cuando alguien registra un cambio en el prototipo.', opcion: cambios.length ? barrasSimples(ctx, cambios, ACENTO) : null, alto: Math.max(120, cambios.length * 40 + 30) }
      ],
      tabla: { cabecera: ['Tipo', 'Detalle', 'Cantidad'],
        filas: ordenes.map(function (x) { return { celdas: ['Órdenes por estado', x.nombre, F.formatoNumero(x.n)] }; }).concat(cambios.map(function (x) { return { celdas: ['Cambios por motivo', x.nombre, F.formatoNumero(x.n)] }; })) },
      acciones: {}
    };
  }

  window.Graficos = {
    definiciones: [
      { id: 1, construir: g1 }, { id: 2, construir: g2 }, { id: 3, construir: g3 }, { id: 4, construir: g4 }, { id: 5, construir: g5 }, { id: 6, construir: g6 },
      { id: 7, construir: g7 }, { id: 8, construir: g8 }, { id: 9, construir: g9 }, { id: 10, construir: g10 }, { id: 11, construir: g11 }, { id: 12, construir: g12 }
    ],
    COLOR_ESTADO: COLOR_ESTADO, TEXTO_SOBRE: TEXTO_SOBRE, esc: esc
  };
})();
