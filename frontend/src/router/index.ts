import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: MainLayout,
      redirect: '/orders',
      children: [
        {
          path: '/orders',
          name: 'orders',
          component: () => import('../views/orders/OrderList.vue'),
        },
        {
          path: '/orders/create',
          name: 'create-order',
          component: () => import('../views/orders/CreateOrder.vue'),
        },
        {
          path: '/orders/detail/:id',
          name: 'order-detail',
          component: () => import('../views/orders/OrderDetail.vue'),
        },
        {
          path: '/orders/edit/:id',
          name: 'edit-order',
          component: () => import('../views/orders/EditOrder.vue'),
        },
        {
          path: '/repair-process',
          name: 'repair-process',
          component: () => import('../views/repair/RepairRecord.vue'),
        },
        {
          path: '/repair-history',
          name: 'repair-history',
          component: () => import('../views/repair/RepairHistory.vue'),
        },
        {
          path: '/warehouse',
          name: 'warehouse',
          component: () => import('../views/warehouse/WarehouseManage.vue'),
        },
        {
          path: '/quality-control',
          name: 'quality-control',
          component: () => import('../views/orders/OrderList.vue'),
        },
        {
          path: '/repair-workorder',
          name: 'repair-workorder',
          component: () => import('../views/orders/OrderList.vue'),
        },
        {
          path: '/equipment',
          name: 'equipment',
          component: () => import('../views/orders/OrderList.vue'),
        },
        {
          path: '/news',
          name: 'news',
          component: () => import('../views/orders/OrderList.vue'),
        },
        {
          path: '/users',
          name: 'users',
          component: () => import('../views/orders/OrderList.vue'),
        },
      ],
    },
  ],
})

export default router
