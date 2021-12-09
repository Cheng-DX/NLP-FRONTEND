import Vue from 'vue'
import App from './App.vue'

// vue-router
import router from './router'

// element-ui
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
Vue.use(ElementUI)

// vue-echarts
import ECharts from 'vue-echarts'
Vue.component('v-chart', ECharts)
// echarts按需引入
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  ToolboxComponent,
  DataZoomComponent,
  MarkLineComponent,
  MarkPointComponent,
  LegendScrollComponent,
  DatasetComponent,
} from 'echarts/components'

use([
  CanvasRenderer,
  PieChart,
  BarChart,
  LineChart,

  GridComponent,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  ToolboxComponent,
  DataZoomComponent,
  MarkLineComponent,
  MarkPointComponent,
  LegendScrollComponent,
  DatasetComponent,
]);

// my tools
import EChartsFull from './dEcharts/echartsFull.vue'
import EChartsData from './dEcharts/echartsData.vue'
import DCharts from './dEcharts/dcharts.vue'
Vue.component('d-chart',DCharts)
Vue.component('chart-full',EChartsFull)
Vue.component('chart-data',EChartsData)

new Vue({
  render: h => h(App),
  router,
}).$mount('#app')