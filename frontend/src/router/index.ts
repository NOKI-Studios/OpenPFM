import { createRouter, createWebHistory } from 'vue-router'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import DashboardView from '@/views/DashboardView.vue'
import PrintersView from '@/views/PrintersView.vue'
import FilamentsView from '@/views/FilamentsView.vue'
import UsersView from '@/views/UsersView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: DefaultLayout,
      children: [
        { path: '', component: DashboardView },
        { path: 'printers', component: PrintersView },
        { path: 'filaments', component: FilamentsView },
        { path: 'users', component: UsersView },
      ],
    },
  ],
})

export default router
