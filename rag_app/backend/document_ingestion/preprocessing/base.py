"""Base classes and abstractions for preprocessing strategies."""

from abc import ABC, abstractmethod
from typing import List

from ..metadata.models import PreprocessedDocument, PreprocessingStrategyType, RawDocument


class PreprocessingStrategy(ABC):
    """
    Abstract base class for all preprocessing strategies.
    
    Each strategy handles a specific preprocessing concern (normalization, enrichment, etc.)
    and can be chained together via PreprocessingPipeline.
    """

    @abstractmethod
    def process(self, document: RawDocument) -> RawDocument:
        """
        Apply preprocessing to a raw document.
        
        Args:
            document: RawDocument to process
            
        Returns:
            Processed RawDocument (may be new instance or mutated)
        """
        pass

    @abstractmethod
    def get_strategy_type(self) -> PreprocessingStrategyType:
        """
        Get the strategy type identifier.
        
        Returns:
            PreprocessingStrategyType enum value
        """
        pass

    def is_applicable(self, document: RawDocument) -> bool:
        """
        Check if strategy should be applied to this document.
        
        Default: applies to all documents. Override for conditional application.
        
        Args:
            document: Document to check
            
        Returns:
            True if strategy should process this document
        """
        return True


class PreprocessingPipeline:
    """
    Chain of Responsibility pattern: stacks multiple preprocessing strategies.
    
    Executes strategies sequentially, passing output of one to the input of the next.
    Tracks which strategies were applied for audit/debugging.
    """

    def __init__(self, strategies: List[PreprocessingStrategy] = None):
        """
        Initialize pipeline with strategies.
        
        Args:
            strategies: List of preprocessing strategies to execute in order
        """
        self.strategies = strategies or []

    def add_strategy(self, strategy: PreprocessingStrategy) -> "PreprocessingPipeline":
        """
        Add a strategy to the pipeline.
        
        Args:
            strategy: Preprocessing strategy to add
            
        Returns:
            Self for method chaining
        """
        self.strategies.append(strategy)
        return self

    def remove_strategy(self, strategy_type: PreprocessingStrategyType) -> None:
        """
        Remove a strategy from the pipeline.
        
        Args:
            strategy_type: Type of strategy to remove
        """
        self.strategies = [
            s for s in self.strategies
            if s.get_strategy_type() != strategy_type
        ]

    def execute(self, raw_document: RawDocument) -> PreprocessedDocument:
        """
        Execute all strategies on the document in sequence.
        
        Args:
            raw_document: Raw document to process
            
        Returns:
            PreprocessedDocument with all strategies applied
        """
        processed = raw_document
        applied_strategies = []

        for strategy in self.strategies:
            if strategy.is_applicable(processed):
                processed = strategy.process(processed)
                applied_strategies.append(strategy.get_strategy_type())

        return PreprocessedDocument(
            document_id=processed.document_id,
            document_type=processed.document_type,
            processed_content=processed.raw_content,  # Will be refined by strategies
            sections=processed.sections,
            embedded_assets=processed.embedded_assets,
            metadata=processed.metadata,
            source_document=raw_document,
            preprocessing_steps_applied=applied_strategies,
        )

    def __repr__(self) -> str:
        """String representation showing all strategies."""
        strategy_names = [s.__class__.__name__ for s in self.strategies]
        return f"PreprocessingPipeline({' -> '.join(strategy_names)})"
