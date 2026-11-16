// Entrada del build personalizado de ECharts 5.5.1: solo los componentes que usa el tablero.
// Como se genera (no hace falta para usar el tablero): ver LEEME.md en esta carpeta.
import * as echarts from 'echarts/core';
import { BarChart, LineChart, PieChart, HeatmapChart, TreemapChart, BoxplotChart, ScatterChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, LegendComponent, VisualMapComponent, MarkLineComponent, AriaComponent } from 'echarts/components';
import { LabelLayout } from 'echarts/features';
import { CanvasRenderer } from 'echarts/renderers';

echarts.use([BarChart, LineChart, PieChart, HeatmapChart, TreemapChart, BoxplotChart, ScatterChart,
  GridComponent, TooltipComponent, LegendComponent, VisualMapComponent, MarkLineComponent, AriaComponent,
  LabelLayout, CanvasRenderer]);

export * from 'echarts/core';
