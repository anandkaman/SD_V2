# backend/app/services/notification_service.py

"""
Notification Service Module

Handles creation and management of in-app notifications.
Supports different notification types and read/unread status tracking.
"""

import logging
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from datetime import datetime
from app.models import Notification

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing in-app notifications"""
    
    @staticmethod
    def create_notification(
        db: Session,
        title: str,
        message: str,
        notification_type: str = 'info',
        related_id: Optional[str] = None,
        related_type: Optional[str] = None
    ) -> Optional[Notification]:
        """
        Create a new notification
        
        Args:
            db: Database session
            title: Notification title
            message: Notification message
            notification_type: Type of notification (success, info, warning, error)
            related_id: ID of related entity (batch_id, ticket_id, etc.)
            related_type: Type of related entity (batch, ticket, document, etc.)
            
        Returns:
            Created Notification object or None if failed
        """
        try:
            notification = Notification(
                title=title,
                message=message,
                notification_type=notification_type,
                related_id=related_id,
                related_type=related_type,
                is_read=0
            )
            
            db.add(notification)
            db.commit()
            db.refresh(notification)
            
            logger.info(f"Notification created: {title} ({notification_type})")
            return notification
            
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def create_batch_completion_notification(
        db: Session,
        batch_id: str,
        batch_name: str,
        total_files: int,
        successful: int,
        failed: int
    ) -> Optional[Notification]:
        """
        Create notification for batch processing completion
        
        Args:
            db: Database session
            batch_id: Batch ID
            batch_name: Batch name
            total_files: Total number of files
            successful: Number of successful files
            failed: Number of failed files
            
        Returns:
            Created Notification object or None if failed
        """
        # Determine notification type based on results
        if failed == 0:
            notification_type = 'success'
            title = f"✅ Batch Processing Complete"
        elif successful == 0:
            notification_type = 'error'
            title = f"❌ Batch Processing Failed"
        else:
            notification_type = 'warning'
            title = f"⚠️ Batch Processing Complete with Errors"
        
        message = (
            f"Batch '{batch_name}' has finished processing. "
            f"{successful}/{total_files} files processed successfully"
        )
        
        if failed > 0:
            message += f", {failed} failed."
        else:
            message += "."
        
        return NotificationService.create_notification(
            db=db,
            title=title,
            message=message,
            notification_type=notification_type,
            related_id=batch_id,
            related_type='batch'
        )
    
    @staticmethod
    def get_all_notifications(
        db: Session,
        limit: int = 50,
        unread_only: bool = False
    ) -> List[Notification]:
        """
        Get all notifications
        
        Args:
            db: Database session
            limit: Maximum number of notifications to return
            unread_only: If True, return only unread notifications
            
        Returns:
            List of Notification objects
        """
        try:
            query = db.query(Notification).order_by(Notification.created_at.desc())
            
            if unread_only:
                query = query.filter(Notification.is_read == 0)
            
            notifications = query.limit(limit).all()
            return notifications
            
        except Exception as e:
            logger.error(f"Error fetching notifications: {e}")
            return []
    
    @staticmethod
    def get_unread_count(db: Session) -> int:
        """
        Get count of unread notifications
        
        Args:
            db: Database session
            
        Returns:
            Number of unread notifications
        """
        try:
            count = db.query(Notification).filter(Notification.is_read == 0).count()
            return count
        except Exception as e:
            logger.error(f"Error counting unread notifications: {e}")
            return 0
    
    @staticmethod
    def mark_as_read(db: Session, notification_id: int) -> bool:
        """
        Mark a notification as read
        
        Args:
            db: Database session
            notification_id: ID of notification to mark as read
            
        Returns:
            True if successful, False otherwise
        """
        try:
            notification = db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            
            if notification:
                notification.is_read = 1
                notification.read_at = datetime.utcnow()
                db.commit()
                logger.info(f"Notification #{notification_id} marked as read")
                return True
            else:
                logger.warning(f"Notification #{notification_id} not found")
                return False
                
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            db.rollback()
            return False
    
    @staticmethod
    def mark_all_as_read(db: Session) -> int:
        """
        Mark all notifications as read
        
        Args:
            db: Database session
            
        Returns:
            Number of notifications marked as read
        """
        try:
            count = db.query(Notification).filter(
                Notification.is_read == 0
            ).update({
                'is_read': 1,
                'read_at': datetime.utcnow()
            })
            db.commit()
            logger.info(f"Marked {count} notifications as read")
            return count
            
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {e}")
            db.rollback()
            return 0
    
    @staticmethod
    def delete_notification(db: Session, notification_id: int) -> bool:
        """
        Delete a notification
        
        Args:
            db: Database session
            notification_id: ID of notification to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            notification = db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            
            if notification:
                db.delete(notification)
                db.commit()
                logger.info(f"Notification #{notification_id} deleted")
                return True
            else:
                logger.warning(f"Notification #{notification_id} not found")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting notification: {e}")
            db.rollback()
            return False
    
    @staticmethod
    def delete_old_notifications(db: Session, days: int = 30) -> int:
        """
        Delete notifications older than specified days
        
        Args:
            db: Database session
            days: Delete notifications older than this many days
            
        Returns:
            Number of notifications deleted
        """
        try:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            count = db.query(Notification).filter(
                Notification.created_at < cutoff_date
            ).delete()
            db.commit()
            logger.info(f"Deleted {count} old notifications (older than {days} days)")
            return count
            
        except Exception as e:
            logger.error(f"Error deleting old notifications: {e}")
            db.rollback()
            return 0


# Global notification service instance
notification_service = NotificationService()
