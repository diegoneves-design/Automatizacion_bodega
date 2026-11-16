/* Reglas y textos fijos del prototipo, en un solo lugar (clase 7: una regla vive en un solo archivo).
   La base de datos (supabase/funciones.sql) vuelve a aplicar estas reglas: ahi esta la validacion que
   cuenta. Si se cambia un limite aqui, hay que cambiarlo tambien en la funcion de la base. */
window.REGLAS = {
  MAX_SKUS: 60,          // maximo de productos por guia en el ERP
  MAX_MOTIVO: 200,       // largo maximo del motivo de un cambio

  tipos_movimiento: [
    { valor: 'despacho', etiqueta: 'Despacho' },
    { valor: 'retiro', etiqueta: 'Retiro' }
  ],

  /* Solo aplica al despacho */
  modalidades: [
    { valor: 'convencional', etiqueta: 'Convencional' },
    { valor: 'alternativo', etiqueta: 'Alternativo' }
  ],

  /* Solo aplica al retiro */
  motivos_retiro: [
    { valor: 'falla', etiqueta: 'Por falla' },
    { valor: 'mantencion_preventiva', etiqueta: 'Mantención preventiva' }
  ],

  /* El motivo de un cambio es obligatorio: no hay opcion "Sin motivo" */
  motivos_cambio: [
    { valor: 'Código mal digitado', etiqueta: 'Código mal digitado' },
    { valor: 'No pasó la prueba eléctrica', etiqueta: 'No pasó la prueba eléctrica' },
    { valor: 'Equipo en mantención', etiqueta: 'Equipo en mantención' }
  ],

  roles: {
    jefe_bodega: 'jefe de bodega',
    mantenimiento: 'mantenimiento',
    comercial: 'comercial',
    gerente: 'gerente'
  },

  /* Mensajes cuando el problema no es de quien escribe (clase 7: errores 4xx y 5xx) */
  mensajes: {
    sinConfig: 'Falta la configuración de la base de datos. Avisa al equipo.',
    conexion: 'No hay conexión con la base de datos. Lo que escribiste sigue aquí. Revisa tu internet y vuelve a intentar.',
    sistema: 'No se pudo completar por un problema del sistema. Lo que escribiste sigue aquí. Vuelve a intentar en un momento; si sigue, avisa al equipo.'
  }
};
