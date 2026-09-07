"""Layer 5: Permission Filtering - RBAC/ABAC access control."""

import logging
from typing import List, Dict, Any
import structlog

logger = structlog.get_logger(__name__)


class AccessControl:
    """Layer 5: Permission filtering with RBAC/ABAC."""
    
    def __init__(self, metadata_config: "MetadataConfig"):
        """Initialize access control."""
        self.config = metadata_config
        self.filtered_count = 0
        logger.info(
            "access_control_initialized",
            enable_rbac=metadata_config.enable_access_control,
            access_levels=list(metadata_config.access_levels.keys())
        )
    
    async def filter_results(
        self,
        documents: List["Chunk"],
        user_context: Dict[str, Any]
    ) -> List["Chunk"]:
        """Filter documents based on user permissions."""
        logger.info(
            "filtering_documents_start",
            total_docs=len(documents),
            user_id=user_context.get("user_id"),
            team_id=user_context.get("team_id")
        )
        
        if not self.config.enable_access_control:
            logger.info("access_control_disabled")
            return documents
        
        filtered = []
        
        for doc in documents:
            if self._has_access(doc, user_context):
                filtered.append(doc)
            else:
                logger.debug(
                    "document_filtered_out",
                    doc_id=doc.id,
                    reason="access_denied"
                )
        
        self.filtered_count += len(documents) - len(filtered)
        logger.info(
            "filtering_complete",
            before=len(documents),
            after=len(filtered),
            filtered_out=len(documents) - len(filtered)
        )
        
        return filtered
    
    def _has_access(
        self,
        document: "Chunk",
        user_context: Dict[str, Any]
    ) -> bool:
        """Check if user has access to document."""
        metadata = document.metadata
        
        # Get document access level
        doc_access_level = metadata.get("access_level", "private")
        doc_access_level_value = self.config.access_levels.get(doc_access_level, 99)
        
        # Public documents - everyone has access
        if doc_access_level == "public":
            logger.debug("access_granted", reason="public_document", doc_id=document.id)
            return True
        
        # Get user access level
        user_access_level = user_context.get("access_level", "private")
        user_access_level_value = self.config.access_levels.get(user_access_level, 99)
        
        # Check hierarchy: higher level (lower value) can access lower level content
        if user_access_level_value <= doc_access_level_value:
            logger.debug(
                "access_granted",
                reason="access_level_hierarchy",
                user_level=user_access_level,
                doc_level=doc_access_level,
                doc_id=document.id
            )
            return True
        
        # User-specific access
        doc_user_id = metadata.get("user_id")
        if doc_user_id and doc_user_id == user_context.get("user_id"):
            logger.debug("access_granted", reason="owner", doc_id=document.id)
            return True
        
        # Team-level access
        if metadata.get("access_level") == "team":
            doc_team_id = metadata.get("team_id")
            user_team_id = user_context.get("team_id")
            if doc_team_id and doc_team_id == user_team_id:
                logger.debug("access_granted", reason="team_member", doc_id=document.id)
                return True
        
        logger.debug(
            "access_denied",
            doc_id=document.id,
            reason="no_matching_criteria"
        )
        return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get access control statistics."""
        return {
            "total_filtered": self.filtered_count,
            "access_control_enabled": self.config.enable_access_control,
        }
