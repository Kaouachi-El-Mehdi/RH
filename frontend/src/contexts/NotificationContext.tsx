import React, { createContext, useContext, useEffect, useState } from 'react';
import axios from 'axios';

export interface Notification {
  id: number;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
  notification_type: string;
  priority: string;
  action_url?: string;
  action_label?: string;
  related_application_id?: number;
  related_job_id?: number;
}

interface NotificationContextType {
  notifications: Notification[];
  unreadCount: number;
  markAsRead: (id: number) => void;
  refresh: () => void;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) throw new Error('useNotifications must be used within NotificationProvider');
  return context;
};

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const fetchNotifications = async () => {
    try {
  const token = localStorage.getItem('access_token');
      console.log('NotificationContext: JWT token used:', token);
      const res = await axios.get('/api/notifications/user/', {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      setNotifications(res.data);
      setUnreadCount(res.data.filter((n: Notification) => !n.is_read).length);
    } catch (err) {
      setNotifications([]);
      setUnreadCount(0);
      console.error('NotificationContext: fetchNotifications error', err);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  const markAsRead = (id: number) => {
    setNotifications((prev) => prev.map((n) => n.id === id ? { ...n, is_read: true } : n));
    setUnreadCount((prev) => Math.max(0, prev - 1));
    // Optionally: send PATCH to backend to mark as read
  };

  const refresh = fetchNotifications;

  return (
    <NotificationContext.Provider value={{ notifications, unreadCount, markAsRead, refresh }}>
      {children}
    </NotificationContext.Provider>
  );
};
