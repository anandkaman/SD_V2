import React from 'react';
import { X, Bell, Check, CheckCheck, Trash2, AlertCircle, CheckCircle, Info, AlertTriangle } from 'lucide-react';
import { useNotifications } from '../context/NotificationContext';
import '../styles/NotificationCenter.css';

const NotificationCenter = () => {
    const {
        notifications,
        showNotificationCenter,
        setShowNotificationCenter,
        markAsRead,
        markAllAsRead,
        deleteNotification
    } = useNotifications();

    if (!showNotificationCenter) return null;

    const getNotificationIcon = (type) => {
        switch (type) {
            case 'success':
                return <CheckCircle size={20} className="icon-success" />;
            case 'error':
                return <AlertCircle size={20} className="icon-error" />;
            case 'warning':
                return <AlertTriangle size={20} className="icon-warning" />;
            default:
                return <Info size={20} className="icon-info" />;
        }
    };

    const formatTime = (timestamp) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);

        if (minutes < 1) return 'Just now';
        if (minutes < 60) return `${minutes}m ago`;
        if (hours < 24) return `${hours}h ago`;
        if (days < 7) return `${days}d ago`;
        return date.toLocaleDateString();
    };

    return (
        <div className="notification-overlay" onClick={() => setShowNotificationCenter(false)}>
            <div className="notification-center" onClick={(e) => e.stopPropagation()}>
                {/* Header */}
                <div className="notification-header">
                    <div className="header-left">
                        <Bell size={20} />
                        <h3>Notifications</h3>
                    </div>
                    <div className="header-right">
                        {notifications.some(n => n.is_read === 0) && (
                            <button
                                className="mark-all-btn"
                                onClick={markAllAsRead}
                                title="Mark all as read"
                            >
                                <CheckCheck size={18} />
                                Mark all read
                            </button>
                        )}
                        <button
                            className="close-btn"
                            onClick={() => setShowNotificationCenter(false)}
                            aria-label="Close"
                        >
                            <X size={20} />
                        </button>
                    </div>
                </div>

                {/* Notifications List */}
                <div className="notifications-list">
                    {notifications.length === 0 ? (
                        <div className="empty-state">
                            <Bell size={48} />
                            <p>No notifications yet</p>
                            <span>You'll see notifications here when batches complete</span>
                        </div>
                    ) : (
                        notifications.map((notification) => (
                            <div
                                key={notification.id}
                                className={`notification-item ${notification.is_read === 0 ? 'unread' : 'read'}`}
                            >
                                <div className="notification-icon">
                                    {getNotificationIcon(notification.notification_type)}
                                </div>
                                <div className="notification-content">
                                    <h4>{notification.title}</h4>
                                    <p>{notification.message}</p>
                                    <span className="notification-time">
                                        {formatTime(notification.created_at)}
                                    </span>
                                </div>
                                <div className="notification-actions">
                                    {notification.is_read === 0 && (
                                        <button
                                            className="action-btn"
                                            onClick={() => markAsRead(notification.id)}
                                            title="Mark as read"
                                        >
                                            <Check size={16} />
                                        </button>
                                    )}
                                    <button
                                        className="action-btn delete-btn"
                                        onClick={() => deleteNotification(notification.id)}
                                        title="Delete"
                                    >
                                        <Trash2 size={16} />
                                    </button>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

export default NotificationCenter;
