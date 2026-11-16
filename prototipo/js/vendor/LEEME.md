# Biblioteca de gráficos (ECharts 5.5.1)

`echarts.custom.min.js` es un build personalizado de [Apache ECharts](https://echarts.apache.org) 5.5.1 (licencia Apache 2.0, © The Apache Software Foundation). Se copió al repositorio para que el tablero no dependa de una CDN.

El build completo pesa 1,03 MB; este, con solo lo que usa el tablero, pesa unos 640 KB: gráficos de barras, línea, dona, mapa de calor, treemap, caja y dispersión; ejes, leyenda, tooltip, mapa de color, línea de marca y accesibilidad; dibujo en canvas.

## Cómo se genera (solo si hay que cambiar los componentes)

Fuera del repositorio, en una carpeta vacía:

```
npm install echarts@5.5.1 esbuild@0.23.1
(copiar echarts-entrada.js a esa carpeta)
node node_modules/esbuild/bin/esbuild echarts-entrada.js --bundle --minify --format=iife --global-name=echarts --legal-comments=none --outfile=echarts.custom.min.js
```

`echarts-entrada.js` (en esta carpeta) lista los componentes incluidos. No se carga en la página.
