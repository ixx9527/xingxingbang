import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Layout from '../views/Layout.vue'
import Dashboard from '../views/Dashboard.vue'
import Children from '../views/Children.vue'
import Behaviors from '../views/Behaviors.vue'
import Records from '../views/Records.vue'
import InviteCodes from '../views/InviteCodes.vue'

const router = createRouter({
  history: createWebHistory('/admin/'),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: Login,
      meta: { title: '登录' }
    },
    {
      path: '/register',
      name: 'Register',
      component: Register,
      meta: { title: '注册' }
    },
    {
      path: '/',
      component: Layout,
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/dashboard' },
        { path: 'dashboard', name: 'Dashboard', component: Dashboard, meta: { title: '数据概览' } },
        { path: 'children', name: 'Children', component: Children, meta: { title: '孩子管理' } },
        { path: 'records', name: 'Records', component: Records, meta: { title: '打卡记录' } },
        { path: 'behaviors', name: 'Behaviors', component: Behaviors, meta: { title: '行为管理' } },
        { path: 'invite-codes', name: 'InviteCodes', component: InviteCodes, meta: { title: '邀请码' } }
      ]
    }
  ]
})

router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 星星榜` : '星星榜'

  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router