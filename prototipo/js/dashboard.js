/* Dashboard: carga los datos una vez, filtra en memoria y dibuja indicadores, graficos, lectura y tabla.
   La logica de filtros esta en filtros.js (se prueba aparte) y los graficos en graficos.js.
   Todo el HTML que arma este archivo escapa los textos y no usa atributos style (la pagina tiene CSP sin 'unsafe-inline'). */
(function () {
  'use strict';
  var F = window.Filtros;
  var G = window.Graficos;
  var esc = G.esc;

  /* Entorno: donde viven la direccion (#filtros) y la forma del panel. En el prototipo es la propia pagina. El MVP
     (src/dashboard_incrustado/entorno.js) lo reemplaza porque corre dentro de un iframe de Streamlit. */
  var ENT = window.DASHBOARD_ENTORNO || {
    leerHash: function () { return window.location.hash; },
    guardarHash: function (h) {
      var destino = window.location.pathname + window.location.search + (h ? '#' + h : '');
      if (window.location.hash.replace(/^#/, '') !== h) window.history.replaceState(null, '', destino);
    },
    alCambiarHash: function (cb) { window.addEventListener('hashchange', cb); },
    panelAcoplado: function () { return false; }
  };

  var datos = { equipos: [], extensiones: [], actividad: null };
  var st = {
    filtros: F.filtrosVacios(), modo3: 'porcentaje', modo4: 'porcentaje', unidad: null, tablas: {},
    busqueda: '', orden: { columna: 'sku', direccion: 'asc' }, pagina: 1, panelDe: null
  };
  var instancias = {};
  var resultados = {};          // ultimo resultado de cada grafico (para clics y "ver como tabla")
  var accionesTabla = {};
  var listaTabla = [];
  var reducido = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  var abridor = null;
  var acoplado = false;

  function $(id) { return document.getElementById(id); }
  function html(el, texto) { el.innerHTML = texto; }

  /* ---------- Carga ---------- */
  function mostrarCarga() {
    $('contenido').hidden = true;
    html($('estado-carga'), '<p class="estado-carga"><span class="giro" aria-hidden="true"></span> Cargando el inventario…</p>');
  }

  function mostrarError(error) {
    $('contenido').hidden = true;
    html($('estado-carga'), '<div class="aviso aviso-error" role="alert"><p>' + esc(error.mensaje) + '</p><button type="button" class="boton boton-secundario" id="reintentar">Reintentar</button></div>');
    $('reintentar').addEventListener('click', cargar);
  }

  function cargar() {
    mostrarCarga();
    window.API.leerDashboard().then(function (r) {
      if (r.error) { mostrarError(r.error); return; }
      var d = r.datos || {};
      datos.equipos = F.prepararEquipos(d.equipos);
      datos.extensiones = F.prepararExtensiones(d.extensiones);
      datos.actividad = d.actividad || null;
      if (!datos.equipos.length) {
        html($('estado-carga'), '<div class="vacio"><p><strong>Todavía no hay inventario cargado.</strong></p><p>Cuando el equipo cargue el inventario en la base de datos, aparecerá aquí.</p></div>');
        return;
      }
      html($('estado-carga'), '');
      $('contenido').hidden = false;
      armarGraficos();
      st.filtros = F.desdeHash(ENT.leerHash());
      render();
    });
  }

  /* ---------- Estructura de las tarjetas (una sola vez) ---------- */
  var TARJETAS = [
    { id: 1, ancha: false }, { id: 2, ancha: false }, { id: 3, ancha: false, modos: 'modo3' }, { id: 4, ancha: false, modos: 'modo4' },
    { id: 5, ancha: false }, { id: 6, ancha: false }, { id: 7, ancha: false }, { id: 8, ancha: false },
    { id: 9, ancha: true }, { id: 10, ancha: true }, { id: 11, ancha: false, unidades: true }, { id: 12, ancha: false, doble: true }
  ];

  function armarGraficos() {
    var cont = $('graficos');
    html(cont, TARJETAS.map(function (t) {
      var lienzos = t.doble
        ? '<h3 class="sub-titulo" id="g-12a-t"></h3><div class="sin-datos" id="g-12a-vacio" hidden></div><div class="grafico" id="g-12a" role="img" aria-labelledby="g-12a-t"></div><h3 class="sub-titulo" id="g-12b-t"></h3><div class="sin-datos" id="g-12b-vacio" hidden></div><div class="grafico" id="g-12b" role="img" aria-labelledby="g-12b-t"></div>'
        : '<div class="grafico" id="g-' + t.id + '" role="img" aria-labelledby="g-' + t.id + '-titulo"></div>';
      return '<article class="tarjeta' + (t.ancha ? ' ancha' : '') + '" id="tarjeta-' + t.id + '">' +
        '<h2 class="tarjeta-titulo" id="g-' + t.id + '-titulo"></h2>' +
        '<div class="tarjeta-acciones">' + (t.modos ? '<div class="modos" role="group" aria-label="Qué mostrar" id="modos-' + t.id + '"></div>' : '') +
        (t.unidades ? '<div class="modos" role="group" aria-label="Unidad de capacidad" id="unidades-' + t.id + '"></div>' : '') +
        '<button type="button" class="enlace" data-ver-tabla="' + t.id + '" aria-pressed="false">Ver como tabla</button></div>' +
        '<div class="sin-datos" id="g-' + t.id + '-vacio" hidden></div>' + lienzos +
        '<div class="envoltura-tabla" id="g-' + t.id + '-tabla" hidden></div>' +
        '<p class="nota" id="g-' + t.id + '-nota"></p></article>';
    }).join(''));
  }

  function instancia(idElemento) {
    if (instancias[idElemento]) return instancias[idElemento];
    var el = $(idElemento);
    var ch = window.echarts.init(el, null, { renderer: 'canvas' });
    ch.on('click', function (p) { clicGrafico(idElemento, p); });
    instancias[idElemento] = ch;
    return ch;
  }

  function clicGrafico(idElemento, p) {
    var id = idElemento.replace('g-', '');
    var r = resultados[id];
    var accion = (p.data && p.data.accion) || (r && r.acciones && r.acciones[p.name]);
    if (accion) aplicarAccion(accion);
  }

  /* ---------- Filtros ---------- */
  function aplicarAccion(a) {
    st.filtros = a.tipo === 'par' ? F.alternarPar(st.filtros, a.dimA, a.valA, a.dimB, a.valB) : F.alternar(st.filtros, a.dim, a.valor);
    st.pagina = 1;
    render();
  }

  function cambiarFiltros(f) { st.filtros = f; st.pagina = 1; render(); }

  function guardarHash() { ENT.guardarHash(F.aHash(st.filtros)); }

  /* ---------- Dibujo ---------- */
  function render() {
    var total = datos.equipos.length;
    var lista = F.aplicar(datos.equipos, st.filtros);
    var ext = F.aplicarExtensiones(datos.extensiones, st.filtros);
    renderVistas();
    renderIndicadores(lista, total);
    renderChips();
    renderGraficos(total);
    renderLectura(lista, ext, total);
    renderTabla(lista);
    guardarHash();
  }

  function renderVistas() {
    var activa = F.vistaActiva(st.filtros);
    html($('vistas'), Object.keys(F.VISTAS).map(function (id) {
      var v = F.VISTAS[id];
      return '<button type="button" class="vista" data-vista="' + id + '" aria-pressed="' + (activa === id) + '" title="' + esc(v.descripcion) + '">' + esc(v.etiqueta) + '</button>';
    }).join(''));
    var v = activa ? F.VISTAS[activa] : null;
    $('vista-ayuda').textContent = v ? v.descripcion + '. Es solo un conjunto de filtros: todos los roles ven los mismos datos.' : 'Filtros personalizados. Las vistas rápidas son solo conjuntos de filtros; todos los roles ven los mismos datos.';
  }

  function renderIndicadores(lista, total) {
    var base = F.aplicar(datos.equipos, st.filtros, ['estado']);
    var ind = F.indicadores(base, total);
    var tot = F.indicadores(lista, total).total;
    var partes = ['<div class="kpi kpi-total"><button type="button" class="kpi-boton" data-kpi="total" aria-pressed="false" aria-label="Total: ' + F.formatoNumero(tot.n) + ' equipos. Quita el filtro de estado.">' +
      '<span class="kpi-num">' + F.formatoNumero(tot.n) + '</span><span class="kpi-etq">Total de equipos</span><span class="kpi-pct">' + F.formatoPct(tot.pct) + ' del total general</span></button></div>'];
    F.ESTADOS.forEach(function (e) {
      var sel = F.tiene(st.filtros, 'estado', e);
      partes.push('<div class="kpi kpi-' + e + '"><button type="button" class="kpi-boton" data-kpi="' + e + '" aria-pressed="' + sel + '" aria-label="' + esc(ind[e].etiqueta) + ': ' + F.formatoNumero(ind[e].n) + ' equipos, ' + F.formatoPct(ind[e].pct) + '. Filtrar por este estado.">' +
        '<span class="kpi-num">' + F.formatoNumero(ind[e].n) + '</span><span class="kpi-etq">' + esc(ind[e].etiqueta) + '</span><span class="kpi-pct">' + F.formatoPct(ind[e].pct) + (F.hayFiltros(st.filtros) ? ' de lo filtrado' : ' del total') + '</span></button></div>');
    });
    html($('indicadores'), partes.join(''));
  }

  function renderChips() {
    var chips = F.chips(st.filtros);
    if (!chips.length) {
      html($('filtros-activos'), '<p class="sin-filtros">Sin filtros: se ve todo el inventario. Haz clic en una barra, trozo, celda o área de un gráfico, o en un indicador, para filtrar.</p>');
      return;
    }
    html($('filtros-activos'), '<ul class="chips" aria-label="Filtros activos">' + chips.map(function (c) {
      return '<li><span class="chip">' + esc(c.texto) + '<button type="button" class="chip-quitar" data-quitar-dim="' + esc(c.dim) + '" data-quitar-valor="' + esc(c.valor) + '" aria-label="Quitar filtro ' + esc(c.texto) + '">×</button></span></li>';
    }).join('') + '</ul><button type="button" class="enlace" id="limpiar">Limpiar todo</button>');
  }

  function contexto(ancho) {
    return { F: F, filtros: st.filtros, equipos: datos.equipos, extensiones: datos.extensiones, totalGeneral: datos.equipos.length, actividad: datos.actividad,
      modo3: st.modo3, modo4: st.modo4, unidad: st.unidad, ancho: ancho, reducido: reducido };
  }

  function anchoDe(id) { var el = $('g-' + id) || $('g-12a'); return el ? el.parentNode.clientWidth || 600 : 600; }

  function renderGraficos() {
    G.definiciones.forEach(function (d) {
      var r = d.construir(contexto(anchoDe(d.id)));
      resultados[d.id] = r;
      $('g-' + d.id + '-titulo').textContent = r.titulo || '';
      $('g-' + d.id + '-nota').textContent = r.nota || '';
      accionesTabla[d.id] = [];
      var verTabla = !!st.tablas[d.id];
      var btn = document.querySelector('[data-ver-tabla="' + d.id + '"]');
      btn.setAttribute('aria-pressed', String(verTabla));
      btn.textContent = verTabla ? 'Ver como gráfico' : 'Ver como tabla';
      renderModos(d.id, r);
      renderTablaGrafico(d.id, r, verTabla);
      var vacio = $('g-' + d.id + '-vacio');
      if (r.doble) { renderDoble(d.id, r, verTabla, vacio); return; }
      var el = $('g-' + d.id);
      var oculto = verTabla || !r.opcion;
      el.hidden = oculto;
      vacio.hidden = !(!r.opcion && !verTabla);
      vacio.textContent = r.vacio || '';
      if (oculto) return;
      el.style.height = r.alto + 'px';
      el.setAttribute('aria-label', r.titulo + '. ' + (r.aria || ''));
      var ch = instancia('g-' + d.id);
      ch.resize();
      ch.setOption(r.opcion, true);
    });
  }

  function renderDoble(id, r, verTabla, vacio) {
    vacio.hidden = true;
    r.sub.forEach(function (s) {
      var el = $('g-12' + s.id);
      var aviso = $('g-12' + s.id + '-vacio');
      $('g-12' + s.id + '-t').textContent = s.titulo;
      $('g-12' + s.id + '-t').hidden = verTabla;
      el.hidden = verTabla || !s.opcion;
      aviso.hidden = verTabla || !!s.opcion;
      aviso.textContent = s.vacio || '';
      if (verTabla || !s.opcion) return;
      el.style.height = s.alto + 'px';
      el.setAttribute('aria-label', s.titulo);
      var ch = instancia('g-12' + s.id);
      ch.resize();
      ch.setOption(s.opcion, true);
    });
  }

  function renderModos(id, r) {
    var caja = $('modos-' + id);
    if (caja) {
      var clave = id === 3 ? 'modo3' : 'modo4';
      var etiquetas = id === 3 ? [['porcentaje', 'Tasa (% del grupo)'], ['cantidad', 'Cantidad arrendada']] : [['porcentaje', '% del grupo'], ['cantidad', 'Cantidad']];
      html(caja, etiquetas.map(function (o) {
        return '<button type="button" class="modo" data-modo="' + clave + '" data-valor="' + o[0] + '" aria-pressed="' + (st[clave] === o[0]) + '">' + o[1] + '</button>';
      }).join(''));
    }
    var u = $('unidades-' + id);
    if (u) {
      var lista = r.unidades || [];
      html(u, lista.length > 1 ? lista.map(function (x) {
        return '<button type="button" class="modo" data-unidad="' + esc(x) + '" aria-pressed="' + (r.unidad === x) + '">' + esc(x === 'm3/h' ? 'm³/h' : x) + '</button>';
      }).join('') : '');
    }
  }

  function renderTablaGrafico(id, r, verTabla) {
    var cont = $('g-' + id + '-tabla');
    cont.hidden = !verTabla;
    if (!verTabla) { html(cont, ''); return; }
    var t = r.tabla;
    if (!t.filas.length) { html(cont, '<p class="sin-datos">' + esc(r.vacio || 'Sin datos.') + '</p>'); return; }
    var conAccion = t.filas.some(function (f) { return f.accion; });
    var cuerpo = t.filas.map(function (f, i) {
      var celdas = f.celdas.map(function (c, j) { return j === 0 ? '<th scope="row">' + esc(c) + '</th>' : '<td>' + esc(c) + '</td>'; }).join('');
      if (conAccion) {
        accionesTabla[id][i] = f.accion;
        celdas += '<td>' + (f.accion ? '<button type="button" class="enlace" data-filtrar-tabla="' + id + '" data-indice="' + i + '">Filtrar</button>' : '') + '</td>';
      }
      return '<tr>' + celdas + '</tr>';
    }).join('');
    html(cont, '<table class="tabla-datos"><caption class="solo-lectores">' + esc(r.titulo) + '</caption><thead><tr>' +
      t.cabecera.map(function (c) { return '<th scope="col">' + esc(c) + '</th>'; }).join('') + (conAccion ? '<th scope="col">Acción</th>' : '') + '</tr></thead><tbody>' + cuerpo + '</tbody></table>');
  }

  function renderLectura(lista, ext) {
    var h = F.hallazgos(lista, ext, datos.equipos.length, F.hayFiltros(st.filtros), st.filtros.corriente.length > 0);
    html($('hallazgos'), h.map(function (x) { return '<li><strong>' + esc(x.titulo) + '.</strong> ' + esc(x.texto) + '</li>'; }).join(''));
  }

  /* ---------- Tabla de casos ---------- */
  function renderTabla(lista) {
    var n = lista.length;
    $('casos-titulo').textContent = F.formatoNumero(n) + (n === 1 ? ' equipo que compone esta selección' : ' equipos que componen esta selección');
    var buscada = F.buscar(lista, st.busqueda);
    listaTabla = F.ordenar(buscada, st.orden.columna, st.orden.direccion);
    var pag = F.paginar(listaTabla, st.pagina);
    st.pagina = pag.pagina;
    var cab = F.COLUMNAS_TABLA.map(function (c) {
      var activo = st.orden.columna === c.id;
      var dir = activo ? (st.orden.direccion === 'asc' ? 'ascending' : 'descending') : 'none';
      return '<th scope="col" aria-sort="' + dir + '"><button type="button" class="orden" data-orden="' + c.id + '">' + esc(c.etiqueta) + '<span aria-hidden="true">' + (activo ? (st.orden.direccion === 'asc' ? ' ▲' : ' ▼') : '') + '</span></button></th>';
    }).join('');
    var filas = pag.filas.map(function (e) {
      return '<tr class="fila" data-id="' + esc(e.id) + '"><th scope="row"><button type="button" class="enlace sku" data-abrir="' + esc(e.id) + '">' + esc(e.sku) + '</button></th><td>' + esc(e.descripcion) + '</td><td>' + esc(e.familia) +
        '</td><td><span class="estado e-' + esc(e.estado) + '">' + esc(F.ETIQUETA_ESTADO[e.estado] || e.estado) + '</span></td><td>' + esc(e.situacion || '—') + '</td></tr>';
    }).join('');
    html($('tabla-casos'), '<thead><tr>' + cab + '</tr></thead><tbody>' + (filas || '<tr><td colspan="5">Ningún equipo coincide con la búsqueda.</td></tr>') + '</tbody>');
    $('pagina-info').textContent = pag.total ? 'Mostrando ' + pag.desde + ' a ' + pag.hasta + ' de ' + F.formatoNumero(pag.total) + (st.busqueda ? ' (con la búsqueda)' : '') : 'Sin resultados';
    $('pag-ant').disabled = pag.pagina <= 1;
    $('pag-sig').disabled = pag.pagina >= pag.paginas;
    $('pag-num').textContent = 'Página ' + pag.pagina + ' de ' + pag.paginas;
    $('descargar').disabled = !listaTabla.length;
  }

  function descargarCsv() {
    var blob = new Blob([F.aCsv(listaTabla)], { type: 'text/csv;charset=utf-8' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url; a.download = 'inventario_seleccion.csv';
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    window.setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  /* ---------- Panel lateral ---------- */
  function abrirPanel(id, desde) {
    var e = datos.equipos.filter(function (x) { return String(x.id) === String(id); })[0];
    if (!e) return;
    abridor = desde || null;
    var cap = e.capacidad_valor != null ? F.formatoNumero(e.capacidad_valor) + ' ' + (e.capacidad_unidad === 'm3/h' ? 'm³/h' : e.capacidad_unidad) : 'No se pudo leer de la descripción';
    function fila(k, v) { return '<dt>' + esc(k) + '</dt><dd>' + esc(v) + '</dd>'; }
    html($('panel-cuerpo'), '<dl class="detalle-equipo">' + fila('SKU', e.sku) + fila('Descripción', e.descripcion) + fila('Familia', e.familia) + fila('Categoría', e.categoria) +
      fila('Estado', F.ETIQUETA_ESTADO[e.estado] || e.estado) + fila('Situación de origen', e.situacion || 'Sin dato') + fila('Capacidad', cap) +
      fila('Modelo (leído de la descripción)', e.modelo === F.SIN_MODELO ? 'No se indica en la descripción' : e.modelo) + '</dl>' +
      '<p class="nota">Pendiente como mejora futura: indicar aquí si el equipo aparece en alguna orden del prototipo.</p>');
    $('panel-titulo').textContent = 'Detalle del equipo';
    /* En pantallas anchas del MVP el panel se acopla a un lado y no tapa los graficos: no es modal. */
    acoplado = !!(ENT.panelAcoplado && ENT.panelAcoplado());
    $('panel').setAttribute('aria-modal', acoplado ? 'false' : 'true');
    $('panel').hidden = false;
    if (!acoplado) { $('velo').hidden = false; document.querySelector('.app').inert = true; }
    document.body.classList.add('con-panel');
    if (acoplado) { document.body.classList.add('panel-acoplado'); window.setTimeout(reajustar, 0); }
    $('panel-cerrar').focus();
  }

  function cerrarPanel() {
    if ($('panel').hidden) return;
    $('panel').hidden = true; $('velo').hidden = true;
    document.querySelector('.app').inert = false;
    document.body.classList.remove('con-panel');
    if (acoplado) { document.body.classList.remove('panel-acoplado'); acoplado = false; window.setTimeout(reajustar, 0); }
    if (abridor && document.contains(abridor)) abridor.focus();
    abridor = null;
  }

  /* Los graficos se redibujan cuando cambia el ancho (el panel acoplado lo cambia sin cambiar la ventana). */
  function reajustar() { window.dispatchEvent(new Event('resize')); }

  /* ---------- Eventos ---------- */
  document.addEventListener('click', function (ev) {
    var t = ev.target.closest ? ev.target.closest('button, tr.fila') : null;
    if (!t) return;
    var d = t.dataset || {};
    if (d.vista) { var v = F.VISTAS[d.vista]; st.orden = v.orden ? { columna: v.orden.columna, direccion: v.orden.direccion } : { columna: 'sku', direccion: 'asc' }; cambiarFiltros(F.filtrosDeVista(d.vista)); return; }
    if (d.kpi) { cambiarFiltros(d.kpi === 'total' ? Object.assign(F.filtrosVacios(), st.filtros, { estado: [] }) : F.alternar(st.filtros, 'estado', d.kpi)); return; }
    if (d.quitarDim) { cambiarFiltros(F.quitar(st.filtros, d.quitarDim, d.quitarValor)); return; }
    if (t.id === 'limpiar') { cambiarFiltros(F.filtrosVacios()); return; }
    if (d.verTabla) { st.tablas[d.verTabla] = !st.tablas[d.verTabla]; render(); return; }
    if (d.modo) { st[d.modo] = d.valor; render(); return; }
    if (d.unidad) { st.unidad = d.unidad; render(); return; }
    if (d.filtrarTabla) { var a = accionesTabla[d.filtrarTabla][Number(d.indice)]; if (a) aplicarAccion(a); return; }
    if (d.orden) { st.orden = st.orden.columna === d.orden ? { columna: d.orden, direccion: st.orden.direccion === 'asc' ? 'desc' : 'asc' } : { columna: d.orden, direccion: 'asc' }; st.pagina = 1; render(); return; }
    if (d.abrir) { abrirPanel(d.abrir, t); return; }
    if (t.tagName === 'TR' && d.id) { abrirPanel(d.id, t.querySelector('button')); return; }
    if (t.id === 'pag-ant') { st.pagina--; render(); return; }
    if (t.id === 'pag-sig') { st.pagina++; render(); return; }
    if (t.id === 'descargar') { descargarCsv(); return; }
    if (t.id === 'panel-cerrar') { cerrarPanel(); return; }
  });

  document.addEventListener('keydown', function (ev) { if (ev.key === 'Escape') cerrarPanel(); });

  function arrancar() {
    $('velo').addEventListener('click', cerrarPanel);
    $('buscar').addEventListener('input', function (ev) { st.busqueda = ev.target.value; st.pagina = 1; renderTabla(F.aplicar(datos.equipos, st.filtros)); });
    ENT.alCambiarHash(function () {
      if (!datos.equipos.length) return;
      var f = F.desdeHash(ENT.leerHash());
      if (!F.mismosFiltros(f, st.filtros)) { st.filtros = f; st.pagina = 1; render(); }
    });
    var pendiente = null;
    window.addEventListener('resize', function () {
      window.clearTimeout(pendiente);
      pendiente = window.setTimeout(function () { if (datos.equipos.length && !$('contenido').hidden) render(); }, 150);
    });
    cargar();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', arrancar); else arrancar();
})();
