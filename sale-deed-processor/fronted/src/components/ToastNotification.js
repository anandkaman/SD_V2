import React from 'react';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';
import { useNotifications } from '../context/NotificationContext';
import '../styles/Toast.css';

const ToastNotification = () => {
    const { showToast, toastNotification, setShowToast } = useNotifications();

    if (!showToast || !toastNotification) return null;

    const getIcon = (type) => {
        switch (type) {
            case 'success':
                return <CheckCircle size={20} />;
            case 'error':
                return <AlertCircle size={20} />;
            case 'warning':
                return <AlertTriangle size={20} />;
            default:
                return <Info size={20} />;
        }
    };

    return (
        <div className={`toast toast-${toastNotification.notification_type}`}>
            <div className="toast-icon">
                {getIcon(toastNotification.notification_type)}
            </div>
            <div className="toast-content">
                <h4>{toastNotification.title}</h4>
                <p>{toastNotification.message}</p>
            </div>
            <button
                className="toast-close"
                onClick={() => setShowToast(false)}
            >
                <X size={16} />
            </button>
        </div>
    );
};

export default ToastNotification;
