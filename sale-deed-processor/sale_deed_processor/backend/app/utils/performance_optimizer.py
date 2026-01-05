# backend/app/utils/performance_optimizer.py

"""
Performance Optimization Utilities

Provides database optimization, caching, and performance monitoring.
"""

import logging
from typing import Optional, Any, Callable
from functools import wraps
import time
import hashlib
import json

logger = logging.getLogger(__name__)


# Simple in-memory cache
_cache = {}
_cache_timestamps = {}
_cache_stats = {"hits": 0, "misses": 0}


class PerformanceOptimizer:
    """Performance optimization utilities"""
    
    @staticmethod
    def create_database_indexes(db_connection):
        """
        Create recommended database indexes for performance
        
        Args:
            db_connection: Database connection
        """
        indexes = [
            # Document indexes
            "CREATE INDEX IF NOT EXISTS idx_document_batch_id ON document_details(batch_id)",
            "CREATE INDEX IF NOT EXISTS idx_document_transaction_date ON document_details(transaction_date)",
            "CREATE INDEX IF NOT EXISTS idx_document_registration_office ON document_details(registration_office)",
            "CREATE INDEX IF NOT EXISTS idx_document_created_at ON document_details(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_document_file_hash ON document_details(file_hash)",
            
            # Property indexes
            "CREATE INDEX IF NOT EXISTS idx_property_state ON property_details(state)",
            "CREATE INDEX IF NOT EXISTS idx_property_pincode ON property_details(pincode)",
            "CREATE INDEX IF NOT EXISTS idx_property_document_id ON property_details(document_id)",
            
            # Party indexes
            "CREATE INDEX IF NOT EXISTS idx_seller_document_id ON seller_details(document_id)",
            "CREATE INDEX IF NOT EXISTS idx_seller_name ON seller_details(name)",
            "CREATE INDEX IF NOT EXISTS idx_seller_aadhaar ON seller_details(aadhaar)",
            "CREATE INDEX IF NOT EXISTS idx_seller_pan ON seller_details(pan)",
            
            "CREATE INDEX IF NOT EXISTS idx_buyer_document_id ON buyer_details(document_id)",
            "CREATE INDEX IF NOT EXISTS idx_buyer_name ON buyer_details(name)",
            "CREATE INDEX IF NOT EXISTS idx_buyer_aadhaar ON buyer_details(aadhaar)",
            "CREATE INDEX IF NOT EXISTS idx_buyer_pan ON buyer_details(pan)",
            
            "CREATE INDEX IF NOT EXISTS idx_confirming_document_id ON confirming_party_details(document_id)",
            
            # Batch indexes
            "CREATE INDEX IF NOT EXISTS idx_batch_status ON batch_sessions(status)",
            "CREATE INDEX IF NOT EXISTS idx_batch_created_at ON batch_sessions(created_at)",
            
            # Notification indexes
            "CREATE INDEX IF NOT EXISTS idx_notification_is_read ON notifications(is_read)",
            "CREATE INDEX IF NOT EXISTS idx_notification_created_at ON notifications(created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_notification_type ON notifications(notification_type)",
            
            # Audit log indexes
            "CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_email)",
            "CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action_type)",
            "CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_logs(entity_type)",
        ]
        
        try:
            cursor = db_connection.cursor()
            created_count = 0
            
            for index_sql in indexes:
                try:
                    cursor.execute(index_sql)
                    created_count += 1
                except Exception as e:
                    logger.warning(f"Index creation skipped (may already exist): {e}")
            
            db_connection.commit()
            logger.info(f"Database indexes created/verified: {created_count}/{len(indexes)}")
            
            return {
                "success": True,
                "total_indexes": len(indexes),
                "created": created_count
            }
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def cache_key(func_name: str, *args, **kwargs) -> str:
        """
        Generate cache key from function name and arguments
        
        Args:
            func_name: Function name
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Cache key string
        """
        # Create a string representation of arguments
        args_str = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
        key_str = f"{func_name}:{args_str}"
        
        # Hash for shorter key
        return hashlib.md5(key_str.encode()).hexdigest()
    
    @staticmethod
    def get_from_cache(key: str, max_age_seconds: int = 300) -> Optional[Any]:
        """
        Get value from cache if not expired
        
        Args:
            key: Cache key
            max_age_seconds: Maximum age in seconds (default: 5 minutes)
            
        Returns:
            Cached value or None if not found/expired
        """
        if key not in _cache:
            _cache_stats["misses"] += 1
            return None
        
        # Check if expired
        timestamp = _cache_timestamps.get(key, 0)
        age = time.time() - timestamp
        
        if age > max_age_seconds:
            # Expired, remove from cache
            del _cache[key]
            del _cache_timestamps[key]
            _cache_stats["misses"] += 1
            return None
        
        _cache_stats["hits"] += 1
        return _cache[key]
    
    @staticmethod
    def set_in_cache(key: str, value: Any):
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
        """
        _cache[key] = value
        _cache_timestamps[key] = time.time()
    
    @staticmethod
    def clear_cache():
        """Clear all cached data"""
        _cache.clear()
        _cache_timestamps.clear()
        logger.info("Cache cleared")
    
    @staticmethod
    def get_cache_stats() -> dict:
        """Get cache statistics"""
        total = _cache_stats["hits"] + _cache_stats["misses"]
        hit_rate = (_cache_stats["hits"] / total * 100) if total > 0 else 0
        
        return {
            "hits": _cache_stats["hits"],
            "misses": _cache_stats["misses"],
            "total_requests": total,
            "hit_rate_percent": round(hit_rate, 2),
            "cached_items": len(_cache)
        }


def cached(max_age_seconds: int = 300):
    """
    Decorator to cache function results
    
    Args:
        max_age_seconds: Cache expiration time in seconds
        
    Usage:
        @cached(max_age_seconds=600)
        def expensive_function(arg1, arg2):
            # expensive operation
            return result
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = PerformanceOptimizer.cache_key(func.__name__, *args, **kwargs)
            
            # Try to get from cache
            cached_value = PerformanceOptimizer.get_from_cache(cache_key, max_age_seconds)
            if cached_value is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_value
            
            # Cache miss, execute function
            logger.debug(f"Cache miss for {func.__name__}")
            result = func(*args, **kwargs)
            
            # Store in cache
            PerformanceOptimizer.set_in_cache(cache_key, result)
            
            return result
        
        return wrapper
    return decorator


def timed(func: Callable) -> Callable:
    """
    Decorator to measure function execution time
    
    Usage:
        @timed
        def my_function():
            # code
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        logger.info(f"{func.__name__} executed in {execution_time:.4f} seconds")
        
        return result
    
    return wrapper


# Global optimizer instance
performance_optimizer = PerformanceOptimizer()
