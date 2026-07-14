import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import CompanyDashboard from '../views/CompanyDashboard.vue'
import StudentDashboard from '../views/StudentDashboard.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { requiresAuth: false }
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, role: 'Admin' }
  },
  {
    path: '/company/dashboard',
    name: 'CompanyDashboard',
    component: CompanyDashboard,
    meta: { requiresAuth: true, role: 'Company' }
  },
  {
    path: '/student/dashboard',
    name: 'StudentDashboard',
    component: StudentDashboard,
    meta: { requiresAuth: true, role: 'Student' }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Global Navigation Security Authorization Guard Loop
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const userRole = localStorage.getItem('user_role')

  // Check if route requires authentication validation flags
  if (to.meta.requiresAuth) {
    if (!token) {
      // Unauthenticated access attempt: Redirect instantly to login interface
      return next({ name: 'Login' })
    }

    // Role verification step matching against explicit route rule requirements
    if (to.meta.role && to.meta.role !== userRole) {
      alert('Access Denied: You do not possess the authorization permissions for this module.')
      
      // Fallback safe routing matrix
      if (userRole === 'Admin') return next({ name: 'AdminDashboard' })
      if (userRole === 'Company') return next({ name: 'CompanyDashboard' })
      if (userRole === 'Student') return next({ name: 'StudentDashboard' })
      return next({ name: 'Login' })
    }
  }

  // Allow routing transition to proceed normally
  next()
})

export default router