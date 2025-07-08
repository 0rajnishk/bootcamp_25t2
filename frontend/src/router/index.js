import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/HomeView.vue';
import AdminLogin from '../views/AdminLogin.vue';
import AdminView from '../views/AdminView.vue';

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        { path: '/', name: 'home', component: Home },
        { path: '/adminlogin', name: 'adminlogin', component: AdminLogin },
        { path: '/admin', name: 'admin', component: AdminView },


    ]
});

export default router;