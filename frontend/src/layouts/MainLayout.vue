<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const isCollapse = ref(false)

const menuItems = [
  { index: '/orders', title: '客户订单系统', icon: 'Document' },
  { index: '/repair-process', title: '维修过程记录', icon: 'Timer' },
  { index: '/repair-history', title: '阀门维修履历', icon: 'DocumentCopy' },
  { index: '/warehouse', title: '仓储管理', icon: 'Box' },
  { index: '/quality-control', title: '质量控制', icon: 'CircleCheck' },
  { index: '/repair-workorder', title: '维修工单管理', icon: 'List' },
  { index: '/equipment', title: '设备维护', icon: 'Tools' },
  { index: '/news', title: '新闻', icon: 'Grid' },
  { index: '/users', title: '用户管理', icon: 'User' },
]

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}
</script>

<template>
  <el-container class="main-layout">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar">
      <div class="logo">
        <el-icon class="logo-icon"><Setting /></el-icon>
        <span v-show="!isCollapse" class="logo-text">阀门维修管理系统</span>
      </div>
      <el-menu
        :default-active="route.path"
        :collapse="isCollapse"
        :collapse-transition="false"
        router
        background-color="#001529"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        class="sidebar-menu"
      >
        <el-menu-item v-for="item in menuItems" :key="item.index" :index="item.index">
          <el-icon>
            <component :is="item.icon" />
          </el-icon>
          <template #title>{{ item.title }}</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <!-- 顶部头部 -->
      <el-header class="header">
        <div class="header-left">
          <el-icon class="toggle-btn" @click="toggleSidebar">
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
        </div>
        <div class="header-right">
          <span class="welcome-text">欢迎, 用户</span>
        </div>
      </el-header>

      <!-- 主内容区 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.main-layout {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

.sidebar {
  background-color: #001529;
  transition: width 0.3s;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
}

.logo-icon {
  font-size: 24px;
  margin-right: 8px;
}

.logo-text {
  white-space: nowrap;
}

.sidebar-menu {
  border-right: none;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background-color: #1890ff !important;
  color: #fff !important;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background-color: #1890ff !important;
}

:deep(.el-container) {
  height: 100%;
}

.header {
  background: linear-gradient(90deg, #001529 0%, #1890ff 100%);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  flex-shrink: 0;
}

.toggle-btn {
  font-size: 20px;
  color: #fff;
  cursor: pointer;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.welcome-text {
  color: #fff;
  font-size: 14px;
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
  overflow-x: hidden;
  flex: 1;
}
</style>
