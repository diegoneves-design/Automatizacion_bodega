/* Prototipo conectado a Supabase (prueba de concepto): rutas por hash (#/p1 a #/p4).
   Sin paso de build. Las reglas viven en reglas.js y se aplican en tres capas:
   1) este archivo, mientras la persona escribe (mejora la experiencia, no es seguridad);
   2) las funciones de la base (supabase/funciones.sql), que vuelven a validar todo;
   3) las restricciones de las tablas (supabase/schema.sql). */
(function () {
  'use strict';

  var R = window.REGLAS;
  var MAX_SKUS = R.MAX_SKUS;
  var RUTAS = ['p1', 'p2', 'p3', 'p4'];
  var NOMBRE_APP = 'Automatizacion_bodega';
  var vista = document.getElementById('vista');

  var catalogo = null;      // clientes, usuarios, equipos y ordenes leidos de la base
  var estado = estadoInicial();
  var ultimaRuta = null;

  /* ---------- Utilidades ---------- */

  function esc(texto) {
    return String(texto == null ? '' : texto).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function buscar(lista, campo, valor) {
    for (var i = 0; i < lista.length; i++) {
      if (lista[i][campo] === valor) return lista[i];
    }
    return null;
  }

  function orden(id) { return buscar(catalogo.ordenes, 'id_orden', id); }
  function cliente(id) { return buscar(catalogo.clientes, 'id_cliente', id); }
  function usuario(id) { return buscar(catalogo.usuarios, 'id_usuario', id); }
  function equipo(sku) { return buscar(catalogo.equipos, 'sku', sku); }
  function etiqueta(lista, valor) { var e = buscar(lista, 'valor', valor); return e ? e.etiqueta : valor; }
  function nombreCliente(id) { var c = cliente(id); return c ? c.razon_social : '—'; }
  function rolLegible(u) { return R.roles[u.rol] || u.rol; }
  function jefeDeBodega() {
    return catalogo.usuarios.filter(function (u) { return u.rol === 'jefe_bodega' && u.activo; })[0] || null;
  }

  function plural(n, uno, varios) { return n + ' ' + (n === 1 ? uno : varios); }

  function dosDigitos(n) { return (n < 10 ? '0' : '') + n; }
  function hhmm(fecha) { return dosDigitos(fecha.getHours()) + ':' + dosDigitos(fecha.getMinutes()); }
  function fechaHora(fecha) {
    return dosDigitos(fecha.getDate()) + '/' + dosDigitos(fecha.getMonth() + 1) + '/' + fecha.getFullYear() + ' ' + hhmm(fecha);
  }

  function opciones(lista, campoValor, campoEtiqueta, seleccionado) {
    return lista.map(function (e) {
      var valor = e[campoValor];
      return '<option value="' + esc(valor) + '"' + (String(valor) === String(seleccionado) ? ' selected' : '') + '>' +
        esc(e[campoEtiqueta]) + '</option>';
    }).join('');
  }

  /* ---------- Estado ---------- */

  function estadoInicial() {
    return {
      carga: 'pendiente',   // del catalogo: pendiente, cargando, error o lista
      errorCarga: '',
      form: null,           // lo que hay escrito en P1
      pedido: null,         // { orden, lineas, cambios, guia }, siempre leido de la base
      aviso: null,          // mensaje de exito de una sola vez
      banner: null,         // error general (conexion, sistema o regla sin campo), de una sola vez
      errores: {},          // mensajes junto a cada campo, de una sola vez
      ocupado: false,       // hay una peticion en curso: evita enviar dos veces
      validando: false,
      p3: null
    };
  }

  function formDeOrden(id) {
    var o = orden(id);
    var lineas = o.detalle_orden.filter(function (l) { return l.vigente; })
      .sort(function (a, b) { return a.id_detalle - b.id_detalle; });
    return {
      id_orden: id,
      tipo_movimiento: o.tipo_movimiento,
      modalidad: o.modalidad || 'convencional',
      motivo_retiro: o.motivo_retiro || 'falla',
      listado: lineas.map(function (l) { return l.sku_informado; }).join('\n')
    };
  }

  /* ---------- Reglas de validacion (capa del navegador) ---------- */

  function parsearListado(texto) {
    var vistos = Object.create(null);
    var skus = [];
    var repetidos = 0;
    texto.split(/\r?\n/).forEach(function (linea) {
      var sku = linea.trim().toUpperCase();
      if (!sku) return;
      if (vistos[sku]) { repetidos++; return; }
      vistos[sku] = true;
      skus.push(sku);
    });
    return { skus: skus, repetidos: repetidos };
  }

  function vigentes() { return estado.pedido.lineas.filter(function (l) { return l.vigente; }); }
  function resultadoDe(l) { return l.resultado_validacion; }
  function conProblema(l) { return resultadoDe(l) === 'no_existe' || resultadoDe(l) === 'no_disponible'; }
  function todoOk() {
    if (!estado.pedido) return false;
    var v = vigentes();
    return v.length > 0 && v.every(function (l) { return resultadoDe(l) === 'ok'; });
  }

  /* Cada error se muestra junto a su campo. Si la base rechaza algo que el navegador no detecto,
     se muestra igual junto al campo que indica; si no hay campo, va en un aviso arriba. */
  function aplicarError(e, camposValidos) {
    if (e.tipo === 'regla' && e.campo && camposValidos.indexOf(e.campo) >= 0) {
      estado.errores[e.campo] = e.mensaje;
      return e.campo;
    }
    estado.banner = e.mensaje;
    return 'aviso';
  }

  /* ---------- Navegacion ---------- */

  function rutaActual() {
    var h = location.hash.replace(/^#\/?/, '');
    return RUTAS.indexOf(h) >= 0 ? h : 'p1';
  }

  function ir(ruta) {
    if (location.hash === '#/' + ruta) render(true);
    else location.hash = '#/' + ruta;
  }

  function migas(actual) {
    var pasos = [
      ['p1', 'Cargar pedido'],
      ['p2', 'Validar'],
      [actual === 'p3' ? 'p3' : 'p4', actual === 'p3' ? 'Registrar cambio' : 'Guía lista']
    ];
    return '<nav class="migas" aria-label="Dónde estoy"><ol>' + pasos.map(function (p) {
      return '<li' + (p[0] === actual ? ' aria-current="step"' : '') + '>' + esc(p[1]) + '</li>';
    }).join('') + '</ol></nav>';
  }

  function botonCargando(boton, texto) {
    boton.disabled = true;
    boton.classList.add('cargando');
    boton.setAttribute('aria-busy', 'true');
    boton.innerHTML = '<span class="giro" aria-hidden="true"></span><span>' + esc(texto) + '</span>';
  }

  /* Aviso de exito y error general, en la parte de arriba de cada pantalla */
  function avisosHtml() {
    var aviso = estado.aviso;
    var banner = estado.banner;
    estado.aviso = null;
    estado.banner = null;
    return '<div class="aviso" id="aviso" tabindex="-1" role="status" aria-live="polite">' + esc(aviso || '') + '</div>' +
      '<div class="aviso aviso-error" id="aviso-error" tabindex="-1" role="alert">' + esc(banner || '') + '</div>';
  }

  function errorCampo(id) {
    var msg = estado.errores[id];
    return '<p class="error" id="' + id + '-error" role="alert">' + (msg ? '✕ ' + esc(msg) : '') + '</p>';
  }

  function marcar(campo, msg) {
    var error = document.getElementById(campo.id + '-error');
    if (error) error.textContent = msg ? '✕ ' + msg : '';
    if (msg) campo.setAttribute('aria-invalid', 'true'); else campo.removeAttribute('aria-invalid');
  }

  /* Lleva el foco al primer campo con error (o al aviso general) despues de volver a dibujar */
  function focoDelError(campo) {
    return campo === 'aviso' ? 'aviso-error' : campo;
  }

  /* ---------- Pantallas ---------- */
  var VISTAS = {};

  /* ----- P1 Cargar pedido (HU-02) ----- */

  function textoContador(p) {
    var n = p.skus.length;
    var t = plural(n, 'producto detectado', 'productos detectados') + ' · máximo ' + MAX_SKUS;
    if (p.repetidos) t += ' · ' + plural(p.repetidos, 'repetido ignorado', 'repetidos ignorados');
    return t;
  }

  /* Devuelve { campo, mensaje } o null */
  function errorFormularioP1(f, p) {
    var n = p.skus.length;
    if (n === 0) return { campo: 'skus', mensaje: 'Pega al menos un SKU, uno por línea. Ejemplo: SD-63A20-0314' };
    if (n > MAX_SKUS) return { campo: 'skus', mensaje: 'Hay ' + n + ' productos y el máximo es ' + MAX_SKUS + '. Quita ' + (n - MAX_SKUS) + ' para continuar.' };
    if (f.tipo_movimiento === 'despacho' && !f.modalidad) return { campo: 'modalidad', mensaje: 'Elige la modalidad del despacho.' };
    if (f.tipo_movimiento === 'retiro' && !f.motivo_retiro) return { campo: 'motivo_retiro', mensaje: 'Elige el motivo del retiro.' };
    return null;
  }

  function estadoDeCarga(titulo) {
    if (estado.carga === 'error') {
      return migas('p1') + '<h1 id="titulo" tabindex="-1">' + esc(titulo) + '</h1>' +
        '<div class="aviso aviso-error" role="alert">' + esc(estado.errorCarga) + '</div>' +
        '<div class="acciones"><button type="button" class="boton boton-primario" id="reintentar">Reintentar</button></div>';
    }
    return migas('p1') + '<h1 id="titulo" tabindex="-1">' + esc(titulo) + '</h1>' +
      '<p class="estado-carga" role="status" aria-live="polite"><span class="giro" aria-hidden="true"></span> Cargando las órdenes…</p>';
  }

  VISTAS.p1 = {
    titulo: function () { return 'Cargar pedido'; },

    html: function () {
      if (estado.carga !== 'lista') return estadoDeCarga('Cargar pedido');

      /* Estado vacio: sin ordenes no hay nada que cargar, y la pantalla lo explica */
      if (catalogo.ordenes.length === 0) {
        return migas('p1') + '<h1 id="titulo" tabindex="-1">Cargar pedido</h1>' + avisosHtml() +
          '<div class="vacio"><p><strong>Aún no hay órdenes para cargar.</strong></p>' +
          '<p>Presiona Reiniciar demo, abajo, para crear las órdenes de ejemplo.</p></div>';
      }

      if (!estado.form || !orden(estado.form.id_orden)) estado.form = formDeOrden(catalogo.ordenes[0].id_orden);
      var f = estado.form;
      var o = orden(f.id_orden);
      var p = parsearListado(f.listado);
      var ordenes = catalogo.ordenes.map(function (x) {
        return { valor: x.id_orden, etiqueta: x.id_orden + ' · ' + nombreCliente(x.id_cliente) };
      });
      var esDespacho = f.tipo_movimiento === 'despacho';

      return migas('p1') +
        '<h1 id="titulo" tabindex="-1">Cargar pedido</h1>' +
        '<p class="ayuda-pantalla">Datos de ejemplo: edita el listado para probar un error.</p>' +
        avisosHtml() +
        '<form id="form-carga" novalidate>' +
          '<div class="campo"><label for="orden">Orden</label>' +
            '<select id="orden" aria-describedby="orden-error">' + opciones(ordenes, 'valor', 'etiqueta', f.id_orden) + '</select>' +
            errorCampo('orden') + '</div>' +
          '<div class="campo"><label for="cliente">Cliente</label>' +
            '<input id="cliente" type="text" readonly value="' + esc(nombreCliente(o.id_cliente)) + '"></div>' +
          '<div class="fila-2">' +
            '<div class="campo"><label for="tipo">Tipo de movimiento</label>' +
              '<select id="tipo" aria-describedby="tipo-error">' + opciones(R.tipos_movimiento, 'valor', 'etiqueta', f.tipo_movimiento) + '</select>' +
              errorCampo('tipo') + '</div>' +
            (esDespacho
              ? '<div class="campo"><label for="modalidad">Modalidad</label>' +
                  '<select id="modalidad" aria-describedby="modalidad-error">' + opciones(R.modalidades, 'valor', 'etiqueta', f.modalidad) + '</select>' +
                  errorCampo('modalidad') + '</div>'
              : '<div class="campo"><label for="motivo_retiro">Motivo del retiro</label>' +
                  '<select id="motivo_retiro" aria-describedby="motivo_retiro-error">' + opciones(R.motivos_retiro, 'valor', 'etiqueta', f.motivo_retiro) + '</select>' +
                  errorCampo('motivo_retiro') + '</div>') +
          '</div>' +
          '<div class="campo"><label for="skus">Productos del pedido, uno por línea</label>' +
            '<textarea id="skus" rows="7" spellcheck="false" autocapitalize="characters" autocomplete="off" aria-describedby="skus-ayuda skus-error"' +
              (estado.errores.skus ? ' aria-invalid="true"' : '') + '>' + esc(f.listado) + '</textarea>' +
            '<p class="ayuda' + (p.skus.length > MAX_SKUS ? ' es-alerta' : '') + '" id="skus-ayuda" aria-live="polite">' + esc(textoContador(p)) + '</p>' +
            errorCampo('skus') + '</div>' +
          '<div class="acciones">' +
            '<button type="submit" class="boton boton-primario" id="cargar">Cargar pedido →</button>' +
            '<button type="button" class="boton boton-secundario" id="cancelar">Cancelar</button>' +
          '</div>' +
        '</form>';
    },

    enlazar: function () {
      var reintentar = document.getElementById('reintentar');
      if (reintentar) { reintentar.addEventListener('click', iniciarCatalogo); return; }
      if (estado.carga !== 'lista' || !document.getElementById('form-carga')) return;

      var f = estado.form;
      var selOrden = document.getElementById('orden');
      var selTipo = document.getElementById('tipo');
      var selModalidad = document.getElementById('modalidad');
      var selMotivo = document.getElementById('motivo_retiro');
      var area = document.getElementById('skus');
      var ayuda = document.getElementById('skus-ayuda');

      selOrden.addEventListener('change', function () {
        estado.form = formDeOrden(Number(selOrden.value));
        render('orden');
      });
      selTipo.addEventListener('change', function () { f.tipo_movimiento = selTipo.value; render('tipo'); });
      if (selModalidad) selModalidad.addEventListener('change', function () { f.modalidad = selModalidad.value; marcar(selModalidad, ''); });
      if (selMotivo) selMotivo.addEventListener('change', function () { f.motivo_retiro = selMotivo.value; marcar(selMotivo, ''); });

      area.addEventListener('input', function () {
        f.listado = area.value;
        var p = parsearListado(area.value);
        ayuda.textContent = textoContador(p);
        ayuda.classList.toggle('es-alerta', p.skus.length > MAX_SKUS);
        marcar(area, '');
      });

      document.getElementById('cancelar').addEventListener('click', function () {
        if (estado.ocupado) return;
        estado.form = formDeOrden(f.id_orden);
        estado.form.listado = '';
        estado.aviso = 'Carga cancelada. No se guardó nada.';
        render('aviso');
      });

      document.getElementById('form-carga').addEventListener('submit', function (ev) {
        ev.preventDefault();
        if (estado.ocupado) return;
        var p = parsearListado(area.value);
        var err = errorFormularioP1(f, p);
        if (err) {
          marcar(document.getElementById(err.campo), err.mensaje);
          document.getElementById(err.campo).focus();
          return;
        }

        estado.ocupado = true;
        botonCargando(document.getElementById('cargar'), 'Cargando…');
        document.getElementById('cancelar').disabled = true;

        window.API.cargarPedido(f, p.skus).then(function (r) {
          if (r.error) return fallo(r.error, ['orden', 'tipo', 'modalidad', 'motivo_retiro', 'skus']);
          return window.API.leerPedido(f.id_orden).then(function (lectura) {
            if (lectura.error) return fallo(lectura.error, ['orden']);
            estado.ocupado = false;
            estado.pedido = lectura.datos;
            // la orden cambio en la base: se actualiza el catalogo para que P1 muestre lo vigente
            return window.API.leerCatalogo().then(function (c) {
              if (!c.error) catalogo = c.datos;
              ir('p2');
            });
          });
        });
      });

      /* Vuelve a dibujar la pantalla sin perder lo escrito y muestra el error donde corresponde */
      function fallo(e, campos) {
        estado.ocupado = false;
        var campo = aplicarError(e, campos);
        render(focoDelError(campo));
      }
    }
  };

  /* ----- P2 Validar pedido (HU-01, HU-04) ----- */

  var PASTILLAS = {
    pendiente: ['p-neutra', 'Pendiente'],
    validando: ['p-neutra', 'Validando…'],
    ok: ['p-ok', '✓ ok'],
    no_existe: ['p-alerta', '✕ no existe'],
    no_disponible: ['p-alerta', '✕ sin stock']
  };

  /* El cambio mas reciente que dejo esta linea vigente (HU-04) */
  function cambioDeLinea(l) {
    if (!l.id_equipo) return null;
    var hallados = estado.pedido.cambios.filter(function (c) { return c.id_equipo_entra === l.id_equipo; });
    return hallados.length ? hallados[hallados.length - 1] : null;
  }

  function lineaHtml(l, validando) {
    var e = equipo(l.sku_informado);
    var res = validando ? 'validando' : resultadoDe(l);
    var pastilla = PASTILLAS[res];
    var cambio = cambioDeLinea(l);
    var clases = 'linea' + (!validando && conProblema(l) ? ' es-alerta' : '') + (cambio ? ' es-cambio' : '');
    var detalle = '';

    if (!validando && resultadoDe(l) === 'no_existe') {
      detalle = 'No está en el inventario. Revisa el código o cámbialo con Registrar cambio.';
    } else if (!validando && resultadoDe(l) === 'no_disponible') {
      detalle = 'El equipo está en mantención y no se puede despachar. Cámbialo con Registrar cambio.';
    }

    var textoCambio = '';
    if (cambio) {
      var u = usuario(cambio.id_usuario);
      textoCambio = '<p class="detalle cambio"><span aria-hidden="true">↻</span> Cambiado por ' + esc(u ? u.nombre : '—') +
        (u ? ' (' + esc(rolLegible(u)) + ')' : '') + ' a las ' + esc(hhmm(new Date(cambio.fecha_hora_cambio))) +
        ' · reemplaza a ' + esc(cambio.sku_sale) + ' · ' + esc(cambio.motivo_cambio) + '</p>';
    }

    return '<li class="' + clases + '">' +
      '<div><div class="sku">' + esc(l.sku_informado) + '</div>' +
      '<div class="desc">' + esc(e ? e.descripcion : '— (no se encuentra)') + '</div></div>' +
      '<span class="pastilla ' + pastilla[0] + '">' + esc(pastilla[1]) + '</span>' +
      (detalle ? '<p class="detalle">' + esc(detalle) + '</p>' : '') + textoCambio + '</li>';
  }

  VISTAS.p2 = {
    titulo: function () { return 'Validar pedido'; },

    html: function () {
      var p = estado.pedido;
      var o = p.orden;
      var v = vigentes();
      var validando = estado.validando;
      var pend = v.filter(function (l) { return resultadoDe(l) === 'pendiente'; }).length;
      var err = v.filter(conProblema).length;
      var modo = pend > 0 ? 'validar' : (err > 0 ? 'registrar' : 'preparar');
      var bloqueado = modo !== 'preparar';

      var resumen;
      if (validando) {
        resumen = ['r-neutro', 'Validando el pedido…'];
      } else if (pend > 0) {
        resumen = ['r-neutro', plural(pend, 'producto sin validar', 'productos sin validar') + '. Presiona Validar para revisar.'];
      } else if (err > 0) {
        resumen = ['r-alerta', '✕ Corrige ' + plural(err, 'producto', 'productos') + ' para continuar'];
      } else {
        resumen = ['r-ok', '✓ ' + v.length + ' de ' + v.length + ' productos ok'];
      }

      function clase(m) { return 'boton ' + (modo === m ? 'boton-primario' : 'boton-secundario'); }

      var detalleOrden = esc(nombreCliente(o.id_cliente)) + ' · ' + esc(etiqueta(R.tipos_movimiento, o.tipo_movimiento)) + ' · ' +
        (o.tipo_movimiento === 'despacho' ? esc(etiqueta(R.modalidades, o.modalidad)) : esc(etiqueta(R.motivos_retiro, o.motivo_retiro)));

      return migas('p2') +
        '<a class="enlace volver" id="volver" href="#/p1"><span aria-hidden="true">‹</span> Volver</a>' +
        '<h1 id="titulo" tabindex="-1">Validar pedido · orden ' + o.id_orden + '</h1>' +
        '<p class="meta">' + detalleOrden + '</p>' +
        avisosHtml() +
        '<div class="acciones acciones-arriba">' +
          '<button type="button" class="' + clase('validar') + (validando ? ' cargando' : '') + '" id="validar"' + (validando ? ' disabled aria-busy="true"' : '') + '>' +
            (validando ? '<span class="giro" aria-hidden="true"></span><span>Validando…</span>' : 'Validar') + '</button>' +
        '</div>' +
        '<ul class="lista" aria-label="Productos del pedido">' + v.map(function (l) { return lineaHtml(l, validando); }).join('') + '</ul>' +
        '<div class="resumen ' + resumen[0] + '" id="resumen" tabindex="-1" role="status" aria-live="polite">' + esc(resumen[1]) + '</div>' +
        '<div class="acciones">' +
          '<button type="button" class="' + (bloqueado ? 'boton boton-secundario' : clase('preparar')) + '" id="preparar"' + (bloqueado || validando ? ' disabled' : '') + '>' +
            (bloqueado ? 'Preparar guía (bloqueado)' : 'Preparar guía →') + '</button>' +
          '<button type="button" class="' + clase('registrar') + '" id="registrar"' + (validando ? ' disabled' : '') + '>Registrar cambio</button>' +
        '</div>';
    },

    enlazar: function () {
      var id = estado.pedido.orden.id_orden;

      function recargarPedido(foco) {
        return window.API.leerPedido(id).then(function (l) {
          if (l.error) { estado.banner = l.error.mensaje; }
          else estado.pedido = l.datos;
          estado.validando = false;
          estado.ocupado = false;
          if (rutaActual() === 'p2') render(foco);
        });
      }

      document.getElementById('validar').addEventListener('click', function () {
        if (estado.ocupado) return;
        estado.ocupado = true;
        estado.validando = true;
        render('resumen');
        window.API.validarPedido(id).then(function (r) {
          if (r.error) { estado.banner = r.error.mensaje; }
          return recargarPedido(r.error ? 'aviso-error' : 'resumen');
        });
      });

      document.getElementById('preparar').addEventListener('click', function () {
        if (estado.ocupado || !todoOk()) return;
        var jefe = jefeDeBodega();
        if (!jefe) { estado.banner = 'No hay un jefe de bodega activo para preparar la guía.'; render('aviso-error'); return; }
        estado.ocupado = true;
        botonCargando(document.getElementById('preparar'), 'Preparando guía…');
        document.getElementById('registrar').disabled = true;
        window.API.prepararGuia(id, jefe.id_usuario).then(function (r) {
          if (r.error) {
            estado.banner = r.error.mensaje;
            return recargarPedido('aviso-error');
          }
          return window.API.leerPedido(id).then(function (l) {
            estado.ocupado = false;
            if (l.error) { estado.banner = l.error.mensaje; render('aviso-error'); return; }
            estado.pedido = l.datos;
            ir('p4');
          });
        });
      });

      document.getElementById('registrar').addEventListener('click', function () {
        if (estado.ocupado) return;
        abrirP3();
        ir('p3');
      });
    }
  };

  /* ----- P3 Registrar cambio (HU-03) ----- */

  function motivoSugerido(l) {
    if (!l) return '';
    if (resultadoDe(l) === 'no_existe') return 'Código mal digitado';
    if (resultadoDe(l) === 'no_disponible') return 'Equipo en mantención';
    return '';
  }

  function abrirP3() {
    var problema = vigentes().filter(conProblema)[0];
    var responsable = catalogo.usuarios.filter(function (u) { return u.rol === 'mantenimiento' && u.activo; })[0] ||
      catalogo.usuarios.filter(function (u) { return u.activo; })[0];
    estado.p3 = {
      sale: problema ? problema.sku_informado : '',
      entra: '',
      motivo: motivoSugerido(problema),
      id_usuario: responsable ? responsable.id_usuario : ''
    };
  }

  function etiquetaSale(l) {
    var e = equipo(l.sku_informado);
    if (!e) return l.sku_informado + ' · no existe en el inventario';
    return l.sku_informado + ' · ' + e.descripcion + (resultadoDe(l) === 'no_disponible' ? ' · sin stock' : '');
  }

  function etiquetaEntra(e) {
    return e.sku + ' · ' + e.descripcion + ' · ' + (e.estado === 'disponible' ? 'disponible' : 'sin stock');
  }

  VISTAS.p3 = {
    titulo: function () { return 'Registrar cambio'; },

    html: function () {
      if (!estado.p3) abrirP3();
      var f = estado.p3;
      var p = estado.pedido;

      var sale = [{ valor: '', etiqueta: 'Elige el equipo que sale' }].concat(vigentes().map(function (l) {
        return { valor: l.sku_informado, etiqueta: etiquetaSale(l) };
      }));
      var entra = [{ valor: '', etiqueta: 'Elige el equipo que entra' }].concat(catalogo.equipos.map(function (e) {
        return { valor: e.sku, etiqueta: etiquetaEntra(e) };
      }));
      var motivos = [{ valor: '', etiqueta: 'Elige un motivo' }].concat(R.motivos_cambio);
      var responsables = [{ valor: '', etiqueta: 'Elige quién lo registra' }].concat(
        catalogo.usuarios.filter(function (u) { return u.activo; }).map(function (u) {
          return { valor: u.id_usuario, etiqueta: u.nombre + ' · ' + rolLegible(u) };
        }));

      return migas('p3') +
        '<h1 id="titulo" tabindex="-1">Registrar cambio · orden ' + p.orden.id_orden + '</h1>' +
        '<p class="ayuda-pantalla">Cambia un equipo del pedido. La línea nueva queda destacada en la validación.</p>' +
        avisosHtml() +
        '<form id="form-cambio" novalidate>' +
          '<div class="campo"><label for="sale">Equipo que sale</label>' +
            '<select id="sale" aria-describedby="sale-error">' + opciones(sale, 'valor', 'etiqueta', f.sale) + '</select>' +
            errorCampo('sale') + '</div>' +
          '<div class="campo"><label for="entra">Equipo que entra</label>' +
            '<select id="entra" aria-describedby="entra-error">' + opciones(entra, 'valor', 'etiqueta', f.entra) + '</select>' +
            errorCampo('entra') + '</div>' +
          '<div class="campo"><label for="motivo">Motivo del cambio</label>' +
            '<select id="motivo" aria-describedby="motivo-error">' + opciones(motivos, 'valor', 'etiqueta', f.motivo) + '</select>' +
            errorCampo('motivo') + '</div>' +
          '<div class="campo"><label for="responsable">Quién lo registra</label>' +
            '<select id="responsable" aria-describedby="responsable-error">' + opciones(responsables, 'valor', 'etiqueta', f.id_usuario) + '</select>' +
            errorCampo('responsable') +
            '<p class="ayuda">Fecha y hora: se guardan solas al presionar Guardar cambio.</p></div>' +
          '<div class="acciones">' +
            '<button type="submit" class="boton boton-primario" id="guardar">Guardar cambio →</button>' +
            '<button type="button" class="boton boton-secundario" id="volver-p2">Volver</button>' +
          '</div>' +
        '</form>';
    },

    enlazar: function () {
      var f = estado.p3;
      var selSale = document.getElementById('sale');
      var selEntra = document.getElementById('entra');
      var selMotivo = document.getElementById('motivo');
      var selResp = document.getElementById('responsable');

      selSale.addEventListener('change', function () {
        f.sale = selSale.value;
        marcar(selSale, '');
        var l = vigentes().filter(function (x) { return x.sku_informado === f.sale; })[0];
        var sugerido = motivoSugerido(l);
        if (sugerido) { f.motivo = sugerido; selMotivo.value = sugerido; marcar(selMotivo, ''); }
      });
      selEntra.addEventListener('change', function () { f.entra = selEntra.value; marcar(selEntra, ''); });
      selMotivo.addEventListener('change', function () { f.motivo = selMotivo.value; marcar(selMotivo, ''); });
      selResp.addEventListener('change', function () { f.id_usuario = selResp.value === '' ? '' : Number(selResp.value); marcar(selResp, ''); });

      document.getElementById('volver-p2').addEventListener('click', function () {
        if (estado.ocupado) return;
        estado.p3 = null;
        ir('p2');
      });

      document.getElementById('form-cambio').addEventListener('submit', function (ev) {
        ev.preventDefault();
        if (estado.ocupado) return;
        var sale = selSale.value;
        var entra = selEntra.value;
        var errores = [];   // [campo, mensaje] en el orden en que aparecen

        if (!sale) errores.push([selSale, 'Elige el equipo que sale.']);
        if (!entra) errores.push([selEntra, 'Elige el equipo que entra.']);
        else if (entra === sale) errores.push([selEntra, 'El equipo que entra debe ser distinto del que sale.']);
        else if (vigentes().some(function (l) { return l.sku_informado === entra; })) errores.push([selEntra, 'Ese equipo ya está en el pedido. Elige otro.']);
        if (!selMotivo.value) errores.push([selMotivo, 'Elige el motivo del cambio.']);
        if (selResp.value === '') errores.push([selResp, 'Elige quién registra el cambio.']);

        [selSale, selEntra, selMotivo, selResp].forEach(function (campo) {
          var e = errores.filter(function (x) { return x[0] === campo; })[0];
          marcar(campo, e ? e[1] : '');
        });
        if (errores.length) { errores[0][0].focus(); return; }

        estado.ocupado = true;
        botonCargando(document.getElementById('guardar'), 'Guardando…');
        document.getElementById('volver-p2').disabled = true;

        window.API.registrarCambio(estado.pedido.orden.id_orden, sale, entra, Number(selResp.value), selMotivo.value).then(function (r) {
          if (r.error) {
            // lo escrito se conserva: f ya tiene los valores elegidos
            estado.ocupado = false;
            var campo = aplicarError(r.error, ['sale', 'entra', 'motivo', 'responsable']);
            render(focoDelError(campo));
            return;
          }
          return window.API.leerPedido(estado.pedido.orden.id_orden).then(function (l) {
            estado.ocupado = false;
            if (l.error) { estado.banner = l.error.mensaje; render('aviso-error'); return; }
            estado.pedido = l.datos;
            estado.p3 = null;
            estado.aviso = 'Cambio guardado. Presiona Validar para revisar la línea nueva.';
            ir('p2');
          });
        });
      });
    }
  };

  /* ----- P4 Guía lista (HU-05) ----- */

  function textoGuia(p, u, v) {
    var o = p.orden;
    var lineas = [
      'GUIA DE EJEMPLO (PRUEBA DE CONCEPTO, SIN VALIDEZ)',
      'La guia oficial se emite en el ERP.',
      'N. interno: ' + p.guia.numero_guia,
      'Orden: ' + o.id_orden,
      'Cliente: ' + nombreCliente(o.id_cliente),
      'Tipo de movimiento: ' + etiqueta(R.tipos_movimiento, o.tipo_movimiento),
      o.tipo_movimiento === 'despacho'
        ? 'Modalidad: ' + etiqueta(R.modalidades, o.modalidad)
        : 'Motivo del retiro: ' + etiqueta(R.motivos_retiro, o.motivo_retiro),
      'Preparada por: ' + (u ? u.nombre + ' (' + rolLegible(u) + ')' : '—'),
      'Fecha de emision: ' + fechaHora(new Date(p.guia.fecha_emision)),
      '',
      'Productos vigentes:'
    ];
    v.forEach(function (l) { var e = equipo(l.sku_informado); lineas.push('- ' + l.sku_informado + ' | ' + (e ? e.descripcion : '')); });
    lineas.push('', 'Total de equipos: ' + v.length);
    return lineas.join('\r\n');
  }

  function descargar(nombre, texto) {
    var blob = new Blob([texto], { type: 'text/plain;charset=utf-8' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = nombre;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  VISTAS.p4 = {
    titulo: function () { return 'Guía lista'; },

    html: function () {
      var p = estado.pedido;
      var o = p.orden;
      var u = usuario(p.guia.id_usuario_emite);

      return migas('p4') +
        '<h1 id="titulo" tabindex="-1">Guía lista · orden ' + o.id_orden + '</h1>' +
        '<p class="meta">' + esc(nombreCliente(o.id_cliente)) + ' · ' + esc(etiqueta(R.tipos_movimiento, o.tipo_movimiento)) + ' · ' +
          (o.tipo_movimiento === 'despacho' ? esc(etiqueta(R.modalidades, o.modalidad)) : esc(etiqueta(R.motivos_retiro, o.motivo_retiro))) + '</p>' +
        '<p><strong>Productos vigentes</strong></p>' +
        '<ul class="guia-lista" aria-label="Productos vigentes de la guía">' + vigentes().map(function (l) {
          var e = equipo(l.sku_informado);
          return '<li>' + esc(l.sku_informado) + ' · ' + esc(e ? e.descripcion : '') + '</li>';
        }).join('') + '</ul>' +
        '<p class="preparada">Preparada por ' + esc(u ? u.nombre : '—') + ' · ' + esc(fechaHora(new Date(p.guia.fecha_emision))) +
          ' · N.º interno ' + esc(p.guia.numero_guia) + '</p>' +
        '<div class="resumen r-ok" id="resumen" tabindex="-1" role="status" aria-live="polite">✓ Lista para pasar al ERP</div>' +
        avisosHtml() +
        '<div class="acciones">' +
          '<button type="button" class="boton boton-primario" id="descargar">Descargar para el ERP</button>' +
          '<button type="button" class="boton boton-secundario" id="volver-p1">Volver a cargar pedido</button>' +
        '</div>';
    },

    enlazar: function () {
      document.getElementById('volver-p1').addEventListener('click', function () { ir('p1'); });

      document.getElementById('descargar').addEventListener('click', function () {
        var p = estado.pedido;
        var nombre = 'guia_orden_' + p.orden.id_orden + '.txt';
        descargar(nombre, textoGuia(p, usuario(p.guia.id_usuario_emite), vigentes()));
        estado.aviso = 'Archivo descargado: ' + nombre;
        render('aviso');
      });
    }
  };

  /* ---------- Carga inicial y reinicio ---------- */

  function iniciarCatalogo() {
    estado.carga = 'cargando';
    estado.errorCarga = '';
    render();
    return window.API.leerCatalogo().then(function (r) {
      if (r.error) {
        estado.carga = 'error';
        estado.errorCarga = r.error.mensaje;
      } else {
        catalogo = r.datos;
        estado.carga = 'lista';
      }
      render();
    });
  }

  /* ---------- Render ---------- */

  function render(foco) {
    var ruta = rutaActual();
    if (ruta !== 'p1' && (estado.carga !== 'lista' || !estado.pedido)) { location.replace('#/p1'); return; }
    if (ruta === 'p4' && !(estado.pedido && estado.pedido.guia)) { location.replace('#/p2'); return; }

    var v = VISTAS[ruta];
    if (!v) { vista.innerHTML = ''; return; }
    var cambioRuta = ruta !== ultimaRuta;
    ultimaRuta = ruta;

    vista.setAttribute('aria-busy', estado.carga === 'cargando' ? 'true' : 'false');
    vista.innerHTML = v.html();
    document.title = v.titulo() + ' · ' + NOMBRE_APP;
    v.enlazar();

    var destino = null;
    if (typeof foco === 'string') destino = document.getElementById(foco);
    else if (cambioRuta || foco === true) destino = document.getElementById('titulo');
    if (destino) destino.focus();
    if (cambioRuta) window.scrollTo(0, 0);
  }

  window.addEventListener('hashchange', function () { render(); });

  document.getElementById('reiniciar').addEventListener('click', function () {
    if (estado.ocupado || !window.API.configurado()) return;
    estado.ocupado = true;
    var boton = document.getElementById('reiniciar');
    boton.disabled = true;
    window.API.reiniciarDemo().then(function (r) {
      var nuevo = estadoInicial();
      if (r.error) nuevo.banner = r.error.mensaje; else nuevo.aviso = 'Demo reiniciada: las órdenes volvieron a su estado inicial.';
      estado = nuevo;
      ultimaRuta = null;
      boton.disabled = false;
      return iniciarCatalogo().then(function () {
        if (location.hash !== '#/p1') location.hash = '#/p1';
      });
    });
  });

  /* ---------- Arranque ---------- */

  if (!window.API.configurado()) {
    estado.carga = 'error';
    estado.errorCarga = R.mensajes.sinConfig;
    document.getElementById('reiniciar').hidden = true;
    render();
  } else {
    iniciarCatalogo();
  }
})();
