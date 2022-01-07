/**
 * @file router 配置
 * @author wwx
 */

import Vue from 'vue'
import VueRouter from 'vue-router'
import store from '@/store'
import http from '@/api'
import preload from '@/common/preload'

Vue.use(VueRouter)

const MainEntry = () => import(/* webpackChunkName: 'entry' */ '@/views')
const Home = () => import(/* webpackChunkName: 'example1' */ '@/views/Home')
const groupDailys = () => import(/* webpackChunkName: 'example2' */ '@/views/groupDailys')
const groupDaily = () => import(/* webpackChunkName: 'example2' */ '@/views/groupDailys/groupDaily')
const excellentDaily = () => import(/* webpackChunkName: 'example2' */ '@/views/groupDailys/excellentDaily')
const myGroup = () => import(/* webpackChunkName: 'example3' */ '@/views/myGroup')
const manageGroup = () => import(/* webpackChunkName: 'example4' */ '@/views/manageGroup')
const NotFound = () => import(/* webpackChunkName: 'none' */ '@/views/404')

const routes = [
    {
        path: window.PROJECT_CONFIG.SITE_URL,
        name: 'appMain',
        component: MainEntry,
        alias: '',
        children: [
            {
                path: '/home',
                name: '/home',
                alias: '',
                component: Home
            },
            {
                path: '/group-dailys',
                name: '/group-dailys',
                component: groupDailys,
                children: [
                    {
                        path: '/group-dailys/groupDaily',
                        name: '/group-dailys/groupDaily',
                        component: groupDaily
                    }, {
                        path: '/group-dailys/excellentDaily/:groupId',
                        name: '/group-dailys/excellentDaily',
                        component: excellentDaily
                    }
                ]
            },
            {
                path: '/my-group',
                name: '/my-group',
                component: myGroup
            },
            {
                path: '/manage-group',
                name: '/manage-group',
                component: manageGroup
            }
        ]
    },
    // 404
    {
        path: '*',
        name: '404',
        component: NotFound
    }
]

const router = new VueRouter({
    mode: 'history',
    routes: routes
})

const cancelRequest = async () => {
    const allRequest = http.queue.get()
    const requestQueue = allRequest.filter((request) => request.cancelWhenRouteChange)
    await http.cancel(requestQueue.map((request) => request.requestId))
}

let preloading = true
let canceling = true
let pageMethodExecuting = true

router.beforeEach(async (to, from, next) => {
    canceling = true
    await cancelRequest()
    canceling = false
    next()
})

router.afterEach(async (to, from) => {
    store.commit('setMainContentLoading', true)

    preloading = true
    await preload()
    preloading = false

    const pageDataMethods = []
    const routerList = to.matched
    routerList.forEach((r) => {
        Object.values(r.instances).forEach((vm) => {
            if (typeof vm.fetchPageData === 'function') {
                pageDataMethods.push(vm.fetchPageData())
            }
            if (typeof vm.$options.preload === 'function') {
                pageDataMethods.push(vm.$options.preload.call(vm))
            }
        })
    })

    pageMethodExecuting = true
    await Promise.all(pageDataMethods)
    pageMethodExecuting = false

    if (!preloading && !canceling && !pageMethodExecuting) {
        store.commit('setMainContentLoading', false)
    }
})

export default router
