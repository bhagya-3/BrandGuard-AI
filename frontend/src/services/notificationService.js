const STORAGE_KEY = 'brandguard_notifications'

function readNotifications() {
  if (typeof window === 'undefined') return []
  try {
    const stored = JSON.parse(window.localStorage.getItem(STORAGE_KEY) || '[]')
    return Array.isArray(stored) ? stored : []
  } catch {
    return []
  }
}

function writeNotifications(notifications) {
  if (typeof window !== 'undefined') {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(notifications))
  }
}

export function listNotifications() {
  return readNotifications()
}

export function addNotification(notification) {
  if (!notification?.message) throw new TypeError('A notification message is required.')
  const item = {
    id: globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    title: notification.title || 'Workspace update',
    message: notification.message,
    created_at: new Date().toISOString(),
    read: false,
    href: notification.href || null,
  }
  const notifications = [item, ...readNotifications()].slice(0, 50)
  writeNotifications(notifications)
  return item
}

export function markNotificationRead(notificationId) {
  const notifications = readNotifications().map((item) => (
    item.id === notificationId ? { ...item, read: true } : item
  ))
  writeNotifications(notifications)
  return notifications
}

export function markAllNotificationsRead() {
  const notifications = readNotifications().map((item) => ({ ...item, read: true }))
  writeNotifications(notifications)
  return notifications
}