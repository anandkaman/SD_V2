# backend/app/schemas/__init__.py

"""
Pydantic schemas package
"""

# Import from legacy schemas (original implementation)
from .legacy_schemas import (
    DocumentDetailSchema,
    PropertyDetailSchema as LegacyPropertyDetailSchema,  # Alias to avoid conflict if needed, or just let one overwrite
    SellerDetailSchema as LegacySellerDetailSchema,
    BuyerDetailSchema as LegacyBuyerDetailSchema,
    ConfirmingPartyDetailSchema as LegacyConfirmingPartyDetailSchema,
    ProcessingStatsSchema,
    SystemInfoSchema,
    BatchResultSchema,
    UserInfoCreateSchema,
    UserInfoSchema,
    UserTicketCreateSchema,
    UserTicketSchema
)

# Import from new document schemas (manual review implementation)
from .document_schemas import (
    DocumentDetailResponse,
    DocumentUpdateRequest,
    DocumentUpdateResponse,
    PropertyDetailSchema,
    SellerDetailSchema,
    BuyerDetailSchema,
    ConfirmingPartyDetailSchema
)

__all__ = [
    # Legacy
    'DocumentDetailSchema',
    'ProcessingStatsSchema',
    'SystemInfoSchema',
    'BatchResultSchema',
    'UserInfoCreateSchema',
    'UserInfoSchema',
    'UserTicketCreateSchema',
    'UserTicketSchema',
    
    # New
    'DocumentDetailResponse',
    'DocumentUpdateRequest',
    'DocumentUpdateResponse',
    'PropertyDetailSchema',
    'SellerDetailSchema',
    'BuyerDetailSchema',
    'ConfirmingPartyDetailSchema'
]
