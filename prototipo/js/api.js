/* Acceso a Supabase. Todas las funciones devuelven una promesa con { datos } o { error }.
   error = { tipo: 'regla' | 'conexion' | 'sistema' | 'config', mensaje, campo }
     regla     la base rechazo el dato con un mensaje pensado para la persona (campo = a que campo corresponde)
     conexion  no se pudo llegar a la base (sin internet o demasiada espera)
     sistema   cualquier otro fallo: se registra en la consola y la persona ve un mensaje generico
   Las lecturas usan las tablas (solo lectura); toda escritura pasa por las funciones de la base (rpc). */
(function () {
  'use strict';

  var TIEMPO_MS = 10000;
  var M = window.REGLAS.mensajes;
  var cliente = null;

  function fetchConTiempo(url, opciones) {
    var control = new AbortController();
    var reloj = window.setTimeout(function () { control.abort(); }, TIEMPO_MS);
    var o = Object.assign({}, opciones, { signal: control.signal });
    return fetch(url, o).finally(function () { window.clearTimeout(reloj); });
  }

  function configurado() {
    var c = window.CONFIG;
    return !!(c && c.SUPABASE_URL && c.SUPABASE_KEY && window.supabase && window.supabase.createClient);
  }

  function conectar() {
    if (cliente) return cliente;
    if (!configurado()) return null;
    cliente = window.supabase.createClient(window.CONFIG.SUPABASE_URL, window.CONFIG.SUPABASE_KEY, {
      auth: { persistSession: false, autoRefreshToken: false, detectSessionInUrl: false },
      global: { fetch: fetchConTiempo }
    });
    return cliente;
  }

  function traducir(e) {
    if (e && e.code === 'P0001') {
      return { tipo: 'regla', mensaje: e.message, campo: e.hint || '' };
    }
    var texto = String((e && (e.message || e.details)) || e || '');
    if (/abort|failed to fetch|networkerror|network request failed|load failed|timeout/i.test(texto)) {
      return { tipo: 'conexion', mensaje: M.conexion, campo: '' };
    }
    if (window.console) console.error('Error de la base de datos:', e);
    return { tipo: 'sistema', mensaje: M.sistema, campo: '' };
  }

  var SIN_CONFIG = { tipo: 'config', mensaje: M.sinConfig, campo: '' };

  /* Ejecuta una consulta o una llamada rpc y normaliza el resultado */
  function ejecutar(hacer) {
    var c = conectar();
    if (!c) return Promise.resolve({ error: SIN_CONFIG });
    var promesa;
    try { promesa = Promise.resolve(hacer(c)); } catch (e) { return Promise.resolve({ error: traducir(e) }); }
    return promesa.then(
      function (r) { return r.error ? { error: traducir(r.error) } : { datos: r.data }; },
      function (e) { return { error: traducir(e) }; }
    );
  }

  function varias(consultas) {
    return Promise.all(consultas).then(function (rs) {
      for (var i = 0; i < rs.length; i++) if (rs[i].error) return { error: rs[i].error };
      return { datos: rs.map(function (r) { return r.datos; }) };
    });
  }

  window.API = {
    configurado: configurado,

    /* Lo que se necesita para armar la primera pantalla. De usuarios solo se piden las columnas publicas. */
    leerCatalogo: function () {
      return varias([
        ejecutar(function (c) { return c.from('clientes').select('id_cliente,razon_social').order('id_cliente'); }),
        ejecutar(function (c) { return c.from('usuarios').select('id_usuario,nombre,rol,activo').order('id_usuario'); }),
        ejecutar(function (c) { return c.from('equipos').select('id_equipo,sku,descripcion,estado').order('id_equipo'); }),
        ejecutar(function (c) {
          return c.from('ordenes')
            .select('id_orden,id_cliente,tipo_movimiento,modalidad,motivo_retiro,estado,detalle_orden(id_detalle,sku_informado,vigente)')
            .order('id_orden');
        })
      ]).then(function (r) {
        if (r.error) return r;
        return { datos: { clientes: r.datos[0], usuarios: r.datos[1], equipos: r.datos[2], ordenes: r.datos[3] } };
      });
    },

    /* Una orden con sus lineas, sus cambios y su guia (si ya se preparo) */
    leerPedido: function (id) {
      return varias([
        ejecutar(function (c) {
          return c.from('ordenes')
            .select('id_orden,id_cliente,tipo_movimiento,modalidad,motivo_retiro,estado').eq('id_orden', id).maybeSingle();
        }),
        ejecutar(function (c) {
          return c.from('detalle_orden')
            .select('id_detalle,id_equipo,sku_informado,resultado_validacion,vigente').eq('id_orden', id).order('id_detalle');
        }),
        ejecutar(function (c) {
          return c.from('registro_cambios')
            .select('id_cambio,sku_sale,id_equipo_entra,id_usuario,fecha_hora_cambio,motivo_cambio').eq('id_orden', id).order('id_cambio');
        }),
        ejecutar(function (c) {
          return c.from('guias').select('numero_guia,fecha_emision,id_usuario_emite').eq('id_orden', id).maybeSingle();
        })
      ]).then(function (r) {
        if (r.error) return r;
        if (!r.datos[0]) return { error: { tipo: 'regla', mensaje: 'Esa orden no existe. Elige otra.', campo: 'orden' } };
        return { datos: { orden: r.datos[0], lineas: r.datos[1], cambios: r.datos[2], guia: r.datos[3] } };
      });
    },

    cargarPedido: function (f, skus) {
      return ejecutar(function (c) {
        return c.rpc('cargar_pedido', {
          p_id_orden: f.id_orden,
          p_tipo: f.tipo_movimiento,
          p_modalidad: f.tipo_movimiento === 'despacho' ? f.modalidad : null,
          p_motivo_retiro: f.tipo_movimiento === 'retiro' ? f.motivo_retiro : null,
          p_skus: skus
        });
      });
    },

    validarPedido: function (id) {
      return ejecutar(function (c) { return c.rpc('validar_pedido', { p_id_orden: id }); });
    },

    registrarCambio: function (id, sale, entra, idUsuario, motivo) {
      return ejecutar(function (c) {
        return c.rpc('registrar_cambio', {
          p_id_orden: id, p_sku_sale: sale, p_sku_entra: entra, p_id_usuario: idUsuario, p_motivo: motivo
        });
      });
    },

    prepararGuia: function (id, idUsuario) {
      return ejecutar(function (c) { return c.rpc('preparar_guia', { p_id_orden: id, p_id_usuario: idUsuario }); });
    },

    reiniciarDemo: function () {
      return ejecutar(function (c) { return c.rpc('reiniciar_demo'); });
    }
  };
})();
