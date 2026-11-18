import { apiGet, apiRequest } from './apiClient.js'

export function getNotificationPreferences() {
  return apiGet('/settings/notifications')
}

export function saveNotificationPreferences(preferences) {
  return apiRequest('/settings/notifications', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(preferences),
  })
}
