# backend/app/services/audit_service.py

"""
Audit Trail Service

Logs all user actions for accountability and debugging.
"""

import logging
import json
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from app.models import AuditLog

logger = logging.getLogger(__name__)


class AuditService:
    """Service for logging user actions"""
    
    @staticmethod
    def log_action(
        db: Session,
        action_type: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        user_email: Optional[str] = None,
        action_details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> Optional[AuditLog]:
        """
        Log a user action
        
        Args:
            db: Database session
            action_type: Type of action (create, update, delete, export, etc.)
            entity_type: Type of entity (document, batch, ticket, etc.)
            entity_id: ID of the affected entity
            user_email: Email of user who performed action
            action_details: Dictionary with additional details
            ip_address: User's IP address
            user_agent: Browser/client info
            success: Whether action succeeded
            error_message: Error details if failed
            
        Returns:
            Created AuditLog object or None if failed
        """
        try:
            # Convert action_details to JSON string
            details_json = None
            if action_details:
                details_json = json.dumps(action_details)
            
            audit_log = AuditLog(
                user_email=user_email,
                action_type=action_type,
                entity_type=entity_type,
                entity_id=entity_id,
                action_details=details_json,
                ip_address=ip_address,
                user_agent=user_agent,
                success=1 if success else 0,
                error_message=error_message
            )
            
            db.add(audit_log)
            db.commit()
            db.refresh(audit_log)
            
            logger.info(
                f"Audit log created: {action_type} on {entity_type} "
                f"by {user_email or 'unknown'}"
            )
            return audit_log
            
        except Exception as e:
            logger.error(f"Error creating audit log: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def log_document_update(
        db: Session,
        document_id: str,
        updated_fields: list,
        user_email: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        """Log document update action"""
        return AuditService.log_action(
            db=db,
            action_type="update",
            entity_type="document",
            entity_id=document_id,
            user_email=user_email,
            action_details={"updated_fields": updated_fields},
            ip_address=ip_address,
            success=True
        )
    
    @staticmethod
    def log_batch_upload(
        db: Session,
        batch_id: str,
        file_count: int,
        user_email: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        """Log batch upload action"""
        return AuditService.log_action(
            db=db,
            action_type="upload",
            entity_type="batch",
            entity_id=batch_id,
            user_email=user_email,
            action_details={"file_count": file_count},
            ip_address=ip_address,
            success=True
        )
    
    @staticmethod
    def log_export(
        db: Session,
        export_type: str,
        record_count: int,
        filters: Optional[Dict] = None,
        user_email: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        """Log data export action"""
        return AuditService.log_action(
            db=db,
            action_type="export",
            entity_type=export_type,
            action_details={
                "record_count": record_count,
                "filters": filters
            },
            user_email=user_email,
            ip_address=ip_address,
            success=True
        )
    
    @staticmethod
    def log_search(
        db: Session,
        search_query: Optional[str] = None,
        filters: Optional[Dict] = None,
        result_count: int = 0,
        user_email: Optional[str] = None
    ):
        """Log search action"""
        return AuditService.log_action(
            db=db,
            action_type="search",
            entity_type="document",
            action_details={
                "search_query": search_query,
                "filters": filters,
                "result_count": result_count
            },
            user_email=user_email,
            success=True
        )
    
    @staticmethod
    def log_ticket_creation(
        db: Session,
        ticket_id: int,
        user_email: Optional[str] = None,
        error_type: Optional[str] = None
    ):
        """Log support ticket creation"""
        return AuditService.log_action(
            db=db,
            action_type="create",
            entity_type="ticket",
            entity_id=str(ticket_id),
            user_email=user_email,
            action_details={"error_type": error_type},
            success=True
        )
    
    @staticmethod
    def get_audit_logs(
        db: Session,
        user_email: Optional[str] = None,
        action_type: Optional[str] = None,
        entity_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ):
        """
        Retrieve audit logs with filters
        
        Args:
            db: Database session
            user_email: Filter by user
            action_type: Filter by action type
            entity_type: Filter by entity type
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum records to return
            
        Returns:
            List of AuditLog objects
        """
        try:
            query = db.query(AuditLog).order_by(AuditLog.timestamp.desc())
            
            if user_email:
                query = query.filter(AuditLog.user_email == user_email)
            
            if action_type:
                query = query.filter(AuditLog.action_type == action_type)
            
            if entity_type:
                query = query.filter(AuditLog.entity_type == entity_type)
            
            if start_date:
                query = query.filter(AuditLog.timestamp >= start_date)
            
            if end_date:
                query = query.filter(AuditLog.timestamp <= end_date)
            
            logs = query.limit(limit).all()
            return logs
            
        except Exception as e:
            logger.error(f"Error fetching audit logs: {e}")
            return []
    
    @staticmethod
    def get_user_activity_summary(
        db: Session,
        user_email: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get summary of user activity
        
        Args:
            db: Database session
            user_email: User email
            days: Number of days to look back
            
        Returns:
            Dictionary with activity summary
        """
        try:
            from datetime import timedelta
            start_date = datetime.utcnow() - timedelta(days=days)
            
            logs = db.query(AuditLog).filter(
                AuditLog.user_email == user_email,
                AuditLog.timestamp >= start_date
            ).all()
            
            # Count by action type
            action_counts = {}
            for log in logs:
                action_counts[log.action_type] = action_counts.get(log.action_type, 0) + 1
            
            return {
                "user_email": user_email,
                "period_days": days,
                "total_actions": len(logs),
                "action_breakdown": action_counts,
                "last_activity": logs[0].timestamp.isoformat() if logs else None
            }
            
        except Exception as e:
            logger.error(f"Error getting user activity summary: {e}")
            return {}


# Global audit service instance
audit_service = AuditService()
