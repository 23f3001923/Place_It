// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';

// We will create these components next
const LoginView = () => import('../views/LoginView.vue');
const AdminDashboard = () => import('../views/AdminDashboard.vue');
const CompanyDashboard = () => import('../views/CompanyDashboard.vue');
const StudentDashboard = () => import('../views/StudentDashboard.vue');

const routes = [
    { path: '/', name: 'Login', component: LoginView },
    { path: '/admin', name: 'Admin', component: AdminDashboard, meta: { requiresAuth: true, role: 'admin' } },
    { path: '/company', name: 'Company', component: CompanyDashboard, meta: { requiresAuth: true, role: 'company' } },
    { path: '/student', name: 'Student', component: StudentDashboard, meta: { requiresAuth: true, role: 'student' } },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

// Navigation Guard: Check tokens and roles before changing pages
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token');
    const userRole = localStorage.getItem('role');

    if (to.meta.requiresAuth && !token) {
        next('/'); // Kick to login if not authenticated
    } else if (to.meta.requiresAuth && to.meta.role !== userRole) {
        next('/'); // Kick to login if wrong role
    } else {
        next(); // Proceed normally
    }
});

export default router;