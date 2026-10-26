/* Datos de ejemplo del prototipo (todos ficticios).
   Los nombres siguen docs/datos/estructura_datos.md. */
window.DATOS = {
  clientes: [
    { id_cliente: 10, razon_social: 'Constructora Andes SpA' },
    { id_cliente: 11, razon_social: 'Minera Cordillera S.A.' }
  ],

  usuarios: [
    { id_usuario: 1, nombre: 'Pedro Soto', rol: 'jefe de bodega' },
    { id_usuario: 2, nombre: 'Camila Rojas', rol: 'mantenimiento' }
  ],

  equipos: [
    { id_equipo: 501, sku: 'SD-63A20-0314', descripcion: 'Extensión 63 A x 20 m', estado: 'disponible' },
    { id_equipo: 502, sku: 'SD-63A20-0315', descripcion: 'Extensión 63 A x 20 m', estado: 'disponible' },
    { id_equipo: 503, sku: 'SD-63A20-0316', descripcion: 'Extensión 63 A x 20 m', estado: 'en_mantencion' },
    { id_equipo: 504, sku: 'SD-32A10-0102', descripcion: 'Extensión 32 A x 10 m', estado: 'disponible' },
    { id_equipo: 505, sku: 'SD-32A10-0108', descripcion: 'Extensión 32 A x 10 m', estado: 'disponible' },
    { id_equipo: 506, sku: 'ST-0042', descripcion: 'Tablero', estado: 'disponible' },
    { id_equipo: 507, sku: 'MP-0107', descripcion: 'Manga perforada', estado: 'disponible' }
  ],

  /* Pedidos de venta de ejemplo. 3002 trae un SKU que no existe (SD-63A20-9999). */
  ordenes: [
    {
      id_orden: 3001,
      id_cliente: 10,
      tipo_movimiento: 'despacho',
      modalidad: 'convencional',
      skus: ['SD-63A20-0314', 'SD-63A20-0315', 'ST-0042', 'MP-0107']
    },
    {
      id_orden: 3002,
      id_cliente: 11,
      tipo_movimiento: 'retiro',
      modalidad: 'alternativo',
      skus: ['SD-32A10-0102', 'SD-63A20-9999', 'ST-0042', 'MP-0107']
    }
  ],

  tipos_movimiento: [
    { valor: 'despacho', etiqueta: 'Despacho' },
    { valor: 'retiro', etiqueta: 'Retiro' }
  ],

  modalidades: [
    { valor: 'convencional', etiqueta: 'Convencional' },
    { valor: 'alternativo', etiqueta: 'Alternativo' }
  ],

  motivos_cambio: [
    { valor: '', etiqueta: 'Sin motivo' },
    { valor: 'Código mal digitado', etiqueta: 'Código mal digitado' },
    { valor: 'No pasó la prueba eléctrica', etiqueta: 'No pasó la prueba eléctrica' },
    { valor: 'Equipo en mantención', etiqueta: 'Equipo en mantención' }
  ]
};
