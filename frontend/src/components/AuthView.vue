<script setup>
import { ref } from 'vue'
import { api, saveSession } from '../api.js'

const emit = defineEmits(['authenticated'])

const mode = ref('login')
const name = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

function toggleMode() {
  mode.value = mode.value === 'login' ? 'register' : 'login'
  error.value = ''
}

async function submit() {
  error.value = ''
  if (name.value.trim().length < 2) {
    error.value = 'Имя должно быть не короче 2 символов'
    return
  }
  if (password.value.length < 6) {
    error.value = 'Пароль должен быть не короче 6 символов'
    return
  }

  loading.value = true
  try {
    const call = mode.value === 'login' ? api.login : api.register
    const data = await call(name.value.trim(), password.value)
    saveSession(data.access_token, data.name)
    emit('authenticated', data.name)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="card">
    <h1>{{ mode === 'login' ? 'Вход' : 'Регистрация' }}</h1>
    <p class="sub">Отметка прихода в офис</p>

    <form @submit.prevent="submit">
      <div class="field">
        <label for="name">Имя сотрудника</label>
        <input id="name" v-model="name" autocomplete="username" placeholder="Иван Иванов" />
      </div>

      <div class="field">
        <label for="password">Пароль</label>
        <input
          id="password"
          v-model="password"
          type="password"
          :autocomplete="mode === 'login' ? 'current-password' : 'new-password'"
          placeholder="Минимум 6 символов"
        />
      </div>

      <button class="big" type="submit" :disabled="loading">
        {{ loading ? 'Подождите…' : mode === 'login' ? 'Войти' : 'Зарегистрироваться' }}
      </button>
    </form>

    <p v-if="error" class="error">{{ error }}</p>

    <p class="switch">
      {{ mode === 'login' ? 'Ещё нет аккаунта?' : 'Уже зарегистрированы?' }}
      <span @click="toggleMode">{{ mode === 'login' ? 'Создать' : 'Войти' }}</span>
    </p>
  </div>
</template>
