import Vue from 'vue'

// vue-router
import VueRouter from 'vue-router'
Vue.use(VueRouter)

const routes = [
    {
        path: '/chart',
        name: 'chart',
        component: () => import('../views/Charts.vue')
    },
    {
        path: '*',
        name: 'index',
        component: () => import('../views/index.vue')
    },
]

const router = new VueRouter({
    routes
})

export default router