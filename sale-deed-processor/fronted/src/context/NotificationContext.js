import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
import api from '../services/api';

const NotificationContext = createContext();

export const useNotifications = () => {
    const context = useContext(NotificationContext);
    if (!context) {
        throw new Error('useNotifications must be used within NotificationProvider');
    }
    return context;
};

export const NotificationProvider = ({ children }) => {
    const [notifications, setNotifications] = useState([]);
    const [unreadCount, setUnreadCount] = useState(0);
    const [showNotificationCenter, setShowNotificationCenter] = useState(false);
    const [showToast, setShowToast] = useState(false);
    const [toastNotification, setToastNotification] = useState(null);
    const [lastFetchedCount, setLastFetchedCount] = useState(0);

    // Fetch notifications
    const fetchNotifications = useCallback(async () => {
        try {
            const data = await api.getNotifications(50, false);
            setNotifications(data);
        } catch (error) {
            console.error('Error fetching notifications:', error);
        }
    }, []);

    // Fetch unread count
    const fetchUnreadCount = useCallback(async () => {
        try {
            const data = await api.getUnreadCount();
            const newCount = data.unread_count;

            // Show toast if new notification arrived
            if (newCount > lastFetchedCount && notifications.length > 0) {
                const latestUnread = notifications.find(n => n.is_read === 0);
                if (latestUnread) {
                    setToastNotification(latestUnread);
                    setShowToast(true);
                    setTimeout(() => setShowToast(false), 5000);
                }
            }

            setLastFetchedCount(newCount);
            setUnreadCount(newCount);
        } catch (error) {
            console.error('Error fetching unread count:', error);
        }
    }, [lastFetchedCount, notifications]);

    // Mark as read
    const markAsRead = useCallback(async (notificationId) => {
        try {
            await api.markNotificationRead(notificationId);
            await fetchNotifications();
            await fetchUnreadCount();
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    }, [fetchNotifications, fetchUnreadCount]);

    // Mark all as read
    const markAllAsRead = useCallback(async () => {
        try {
            await api.markAllRead();
            await fetchNotifications();
            await fetchUnreadCount();
        } catch (error) {
            console.error('Error marking all as read:', error);
        }
    }, [fetchNotifications, fetchUnreadCount]);

    // Delete notification
    const deleteNotification = useCallback(async (notificationId) => {
        try {
            await api.deleteNotification(notificationId);
            await fetchNotifications();
            await fetchUnreadCount();
        } catch (error) {
            console.error('Error deleting notification:', error);
        }
    }, [fetchNotifications, fetchUnreadCount]);

    // Poll for new notifications every 30 seconds
    useEffect(() => {
        // Initial fetch
        fetchNotifications();
        fetchUnreadCount();

        const interval = setInterval(() => {
            fetchNotifications();
            fetchUnreadCount();
        }, 30000); // 30 seconds

        return () => clearInterval(interval);
        // Removed fetchNotifications and fetchUnreadCount from dependencies to prevent re-running 
        // when they are recreated due to state changes
    }, []);

    const value = {
        notifications,
        unreadCount,
        showNotificationCenter,
        setShowNotificationCenter,
        showToast,
        toastNotification,
        setShowToast,
        fetchNotifications,
        fetchUnreadCount,
        markAsRead,
        markAllAsRead,
        deleteNotification
    };

    return (
        <NotificationContext.Provider value={value}>
            {children}
        </NotificationContext.Provider>
    );
};
