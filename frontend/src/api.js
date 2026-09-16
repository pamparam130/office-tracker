const TOKEN_KEY = 'office_token'
const NAME_KEY = 'office_name'

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function getName() {
  return localStorage.getItem(NAME_KEY)
}

export function saveSession(token, name) {
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(NAME_KEY, name)
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(NAME_KEY)
}

async function request(path, { method = 'GET', body } = {}) {
  const headers = {}
  if (body) headers['Content-Type'] = 'application/json'
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`

  const res = await fetch(`/api${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined
  })

  if (res.status === 401) {
    clearSession()
    throw new Error('Сессия истекла, войдите заново')
  }

  const data = res.status === 204 ? null : await res.json().catch(() => null)

  if (!res.ok) {
    const detail = data?.detail
    throw new Error(
      typeof detail === 'string' ? detail : 'Что-то пошло не так, попробуйте ещё раз'
    )
  }
  return data
}

export const api = {
  register: (name, password) =>
    request('/auth/register', { method: 'POST', body: { name, password } }),
  login: (name, password) =>
    request('/auth/login', { method: 'POST', body: { name, password } }),
  checkIn: () => request('/checkins', { method: 'POST' }),
  myStatus: () => request('/checkins/me'),
  today: () => request('/checkins/today'),
  history: () => request('/checkins/history')
}
