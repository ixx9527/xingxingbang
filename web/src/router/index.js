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
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', name: 'Dashboard', component: Dashboard },
      { path: 'children', name: 'Children', component: Children },
      { path: 'behaviors', name: 'Behaviors', component: Behaviors },
      { path: 'records', name: 'Records', component: Records },
      { path: 'invite-codes', name: 'InviteCodes', component: InviteCodes }
    ]
  }
]

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router