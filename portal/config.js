/* ÚNICO lugar donde vive la dirección de la aplicación (el MVP).
   - Vacía: el portal muestra el botón desactivado con el texto «Aplicación en despliegue». Así se puede publicar el portal
     antes de que el MVP exista.
   - Con una dirección https (por ejemplo, la del servicio donde se publique el MVP): el botón pasa a «Abrir la aplicación»
     y lleva a esa dirección. Solo se aceptan direcciones https, sin usuario ni contraseña; cualquier otra cosa se ignora.
   Cambiar esto es cambiar solo esta línea y volver a publicar. No va nada más aquí: ninguna clave ni dato. */
window.PORTAL_CONFIG = Object.freeze({
  URL_APLICACION: ''
});
