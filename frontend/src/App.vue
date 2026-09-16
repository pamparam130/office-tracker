<script setup>
import { ref } from 'vue'
import { clearSession, getName, getToken } from './api.js'
import AuthView from './components/AuthView.vue'
import DashboardView from './components/DashboardView.vue'

const currentName = ref(getToken() ? getName() : null)

function onAuthenticated(name) {
  currentName.value = name
}

function logout() {
  clearSession()
  currentName.value = null
}
</script>

<template>
  <div class="wrap">
    <DashboardView
      v-if="currentName"
      :key="currentName"
      :name="currentName"
      @logout="logout"
    />
    <AuthView v-else @authenticated="onAuthenticated" />
  </div>
</template>
