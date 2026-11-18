import { createContext, useCallback, useEffect, useMemo, useState } from 'react'
import {
  addNotification as persistNotification,
  listNotifications,
  markAllNotificationsRead,
  markNotificationRead,
} from '../services/notificationService.js'

export const NotificationContext = createContext(null)

export function NotificationProvider({ children }) {
  const [notifications, setNotifications] = useState([])

  useEffect(() => {
    setNotifications(listNotifications())
  }, [])

  const add = useCallback((notification) => {
    const item = persistNotification(notification)
    setNotifications((current) => [item, ...current].slice(0, 50))
    return item
  }, [])

  const markRead = useCallback((id) => {
    setNotifications(markNotificationRead(id))
  }, [])

  const markAllRead = useCallback(() => {
    setNotifications(markAllNotificationsRead())
  }, [])

  const value = useMemo(() => ({
    notifications,
    unreadCount: notifications.filter((item) => !item.read).length,
    addNotification: add,
    markRead,
    markAllRead,
  }), [notifications, add, markRead, markAllRead])

  return <NotificationContext.Provider value={value}>{children}</NotificationContext.Provider>
}