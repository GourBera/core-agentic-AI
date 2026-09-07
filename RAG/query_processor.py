"""Layer 4: Query Processing - Normalize, expand, and process queries."""

import logging
from typing import Dict, Any
from dataclasses import dataclass
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ProcessedQuery:
    """Represents a processed query."""
    original_text: str
    normalized_text: str
    intent: str
    entities: list
    expanded_keywords: list


class QueryProcessor:
    """Layer 4: Process and enhance user queries."""
    
    def __init__(self, config: "RAGConfig"):
        """Initialize query processor."""
        self.config = config
        self.queries_processed = 0
        logger.info("query_processor_initialized")
    
    async def process(self, query_text: str) -> ProcessedQuery:
        """Process and enhance a query."""
        logger.info("processing_query", query=query_text[:50])
        
        # Normalize
        normalized = self._normalize_text(query_text)
        
        # Extract intent
        intent = self._detect_intent(normalized)
        
        # Extract entities
        entities = self._extract_entities(normalized)
        
        # Expand with keywords
        expanded_keywords = self._expand_keywords(normalized)
        
        processed = ProcessedQuery(
            original_text=query_text,
            normalized_text=normalized,
            intent=intent,
            entities=entities,
            expanded_keywords=expanded_keywords
        )
        
        self.queries_processed += 1
        logger.info(
            "query_processed",
            intent=intent,
            entities_count=len(entities),
            keywords_count=len(expanded_keywords)
        )
        
        return processed
    
    def _normalize_text(self, text: str) -> str:
        """Normalize query text."""
        # Convert to lowercase
        text = text.lower()
        # Remove extra whitespace
        text = " ".join(text.split())
        return text
    
    def _detect_intent(self, query: str) -> str:
        """Detect query intent."""
        # Simple intent detection
        intents = {
            "question": ["what", "when", "where", "who", "why", "how"],
            "command": ["show", "list", "get", "find", "search"],
            "statement": [],
        }
        
        for intent, keywords in intents.items():
            if any(keyword in query for keyword in keywords):
                return intent
        
        return "statement"
    
    def _extract_entities(self, query: str) -> list:
        """Extract named entities from query."""
        # Simple entity extraction - can be enhanced with NER models
        entities = []
        words = query.split()
        
        for word in words:
            if word.isupper() or (len(word) > 3 and word[0].isupper()):
                entities.append(word)
        
        return entities
    
    def _expand_keywords(self, query: str) -> list:
        """Expand query with related keywords."""
        # Simple keyword expansion - can use synonyms/knowledge base
        keywords = query.split()
        expanded = keywords.copy()
        
        # Add common variations
        variations = {
            "data": ["information", "records", "dataset"],
            "model": ["algorithm", "system", "approach"],
            "train": ["learn", "fit", "train"],
        }
        
        for keyword in keywords:
            if keyword in variations:
                expanded.extend(variations[keyword])
        
        return expanded
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get query processor statistics."""
        return {
            "queries_processed": self.queries_processed
        }
