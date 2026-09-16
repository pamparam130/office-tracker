<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../api.js'

const props = defineProps({ name: { type: String, required: true } })
const emit = defineEmits(['logout'])

const status = ref({ checked_in_today: false, last_arrival: null })
const todayList = ref([])
const history = ref([])
const error = ref('')
const sending = ref(false)

const timeFmt = new Intl.DateTimeFormat('ru-RU', {
  hour: '2-digit',
  minute: '2-digit'
})
const dateTimeFmt = new Intl.DateTimeFormat('ru-RU', {
  day: '2-digit',
  month: '2-digit',
  hour: '2-digit',
  minute: '2-digit'
})

const formatTime = (iso) => timeFmt.format(new Date(iso))
const formatDateTime = (iso) => dateTimeFmt.format(new Date(iso))

const todayArrival = computed(() =>
  todayList.value.find((row) => row.name === props.name)
)

async function load() {
  error.value = ''
  try {
    const [st, list, hist] = await Promise.all([
      api.myStatus(),
      api.today(),
      api.history()
    ])
    status.value = st
    todayList.value = list
    history.value = hist
  } catch (e) {
    error.value = e.message
    if (e.message.includes('Сессия')) emit('logout')
  }
}

async function checkIn() {
  error.value = ''
  sending.value = true
  try {
    await api.checkIn()
    await load()
  } catch (e) {
    error.value = e.message
    if (e.message.includes('Сессия')) emit('logout')
  } finally {
    sending.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="stack">
    <div class="topbar">
      <div>
        <h1>{{ name }}</h1>
        <p class="sub" style="margin: 0">
          {{
            status.checked_in_today
              ? 'Вы отметились сегодня'
              : 'Сегодня вы ещё не отмечались'
          }}
        </p>
      </div>
      <button class="ghost" @click="emit('logout')">Выйти</button>
    </div>

    <div class="card">
      <button
        v-if="!status.checked_in_today"
        class="big"
        :disabled="sending"
        @click="checkIn"
      >
        {{ sending ? 'Отмечаем…' : 'Пришёл в офис' }}
      </button>

      <button v-else class="big done" disabled>
        Отмечен в {{ todayArrival ? formatTime(todayArrival.arrived_at) : '—' }}
      </button>

      <p v-if="error" class="error">{{ error }}</p>
    </div>

    <div class="card">
      <h2>Сегодня в офисе — {{ todayList.length }}</h2>
      <ul v-if="todayList.length" class="list">
        <li v-for="row in todayList" :key="row.id">
          <span>{{ row.name }}</span>
          <span class="time">{{ formatTime(row.arrived_at) }}</span>
        </li>
      </ul>
      <p v-else class="empty">Пока никто не отметился</p>
    </div>

    <div class="card">
      <h2>Моя история</h2>
      <ul v-if="history.length" class="list">
        <li v-for="row in history" :key="row.id">
          <span>Пришёл в офис</span>
          <span class="time">{{ formatDateTime(row.arrived_at) }}</span>
        </li>
      </ul>
      <p v-else class="empty">Отметок пока нет</p>
    </div>
  </div>
</template>
