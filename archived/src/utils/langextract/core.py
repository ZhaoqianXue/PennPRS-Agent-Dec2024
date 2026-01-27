"""
Core implementation of LangExtract logic.
"""

import json
import logging
from typing import Type, List, Dict, Any, TypeVar, Optional
from pydantic import BaseModel, create_model

from . import SourceSpan, GroundedExtraction

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

class SmartChunker:
    """Handles text chunking with sentence boundary awareness."""
    
    def __init__(self, chunk_size: int = 8000, overlap: int = 500):
        self.chunk_size = chunk_size
        self.overlap = overlap
        
    def chunk(self, text: str) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks.
        Returns list of dicts with 'text', 'start_char', 'end_char'.
        """
        if not text:
            return []
            
        chunks = []
        text_len = len(text)
        start = 0
        
        while start < text_len:
            # Determine end position
            end = min(start + self.chunk_size, text_len)
            
            # If not at end of text, try to find a sentence break
            if end < text_len:
                # Look for last period, newline, or punctuation in the last 10% of chunk
                search_zone = text[end - int(self.chunk_size * 0.1):end]
                last_period = max(
                    search_zone.rfind('. '), 
                    search_zone.rfind('.\n'),
                    search_zone.rfind('\n\n')
                )
                
                if last_period != -1:
                    # Adjust end to specific break point
                    end = end - int(self.chunk_size * 0.1) + last_period + 1
            
            chunk_text = text[start:end]
            chunks.append({
                "text": chunk_text,
                "start_char": start,
                "end_char": end,
                "id": len(chunks)
            })
            
            # Prepare next start
            if end >= text_len:
                break
                
            start = end - self.overlap
            
            # Adjust start to sentence boundary if possible to avoid cutting context
            # (Simplified logic for now)
            
        return chunks

class GroundingVerifier:
    """Verifies extractions against source text to provide grounding."""
    
    @staticmethod
    def verify_quote(full_text: str, quote: str, approximate: bool = True) -> Optional[SourceSpan]:
        """Find the quote in the text and return its span."""
        if not quote:
            return None
            
        # Exact match
        start = full_text.find(quote)
        if start != -1:
            end = start + len(quote)
            return SourceSpan(
                start_char=start,
                end_char=end,
                text=quote,
                context_before=full_text[max(0, start-50):start],
                context_after=full_text[end:min(len(full_text), end+50)]
            )
            
        if approximate:
            # Simple fuzzy fallback: strip whitespace/punctuation
            # In a real implementation, use Levenshtein or specialized library
            clean_text = "".join(full_text.split())
            clean_quote = "".join(quote.split())
            # This is hard to map back to indices, so we skip complex fuzzy for this shim
            pass
            
        return None

class LangExtract:
    """
    The main extractor class.
    
    Wraps an LLM client to perform:
    1. Chunking
    2. Extraction (using strict mode if available)
    3. Grounding (verification)
    """
    
    def __init__(self, llm_client, model_name: str, silent: bool = False):
        self.client = llm_client
        self.model_name = model_name
        self.silent = silent
        self.chunker = SmartChunker()
        self.verifier = GroundingVerifier()
        
    def extract(self, text: str, schema: Type[T]) -> List[GroundedExtraction]:
        """
        Extract data from text conforming to schema, with grounding.
        """
        # 1. Chunking
        chunks = self.chunker.chunk(text)
        if not self.silent:
            logger.info(f"LangExtract: Split text into {len(chunks)} chunks.")
        
        all_extractions = []
        
        # 2. Process chunks (Parallelization could happen here)
        for chunk in chunks:
            chunk_text = chunk['text']
            chunk_start_idx = chunk['start_char']
            
            # We modify the schema to require a "quote" field for grounding
            # This is the "Citational" strategy
            GroundedSchema = self._create_grounded_schema(schema)
            
            try:
                # Use the new beta strict parse method if available (assumed from recent updates)
                # Note: We need to recreate the messages structure
                messages = [
                    {"role": "system", "content": "You are a precise data extraction assistant. Extract all instances of the requested data from the text. For every extraction, you MUST provide the exact 'quote' from the text that supports it."},
                    {"role": "user", "content": f"Text to extract from:\n\n{chunk_text}"}
                ]
                
                response = self.client.beta.chat.completions.parse(
                    model=self.model_name,
                    messages=messages,
                    response_format=GroundedSchema,
                    temperature=0.0
                )
                
                if hasattr(response.choices[0].message, 'parsed'):
                    parsed_result = response.choices[0].message.parsed
                    
                    # parsed_result will have a 'items' list or similar depending on how we wrapped it
                    # Let's assume GroundedSchema has a 'items' list
                    if hasattr(parsed_result, 'items'):
                        items = parsed_result.items
                    else:
                        items = [parsed_result] # Single item case
                        
                    for item in items:
                        # 3. Verify and Ground
                        # Extract the data model part
                        data_dict = item.dict(exclude={'quote'})
                        quote = getattr(item, 'quote', '')
                        
                        source_span = self.verifier.verify_quote(text, quote) # Verify against FULL text
                        
                        # Correct the span indices if verified against chunk?
                        # Actually verify_quote on full_text is safer for global coordinates
                        # But might be ambiguous. 
                        # Optimization: Verify against chunk first, then offset indices.
                        
                        if source_span is None and quote:
                            # Try verifying against chunk and offset
                            local_span = self.verifier.verify_quote(chunk_text, quote)
                            if local_span:
                                source_span = SourceSpan(
                                    start_char=local_span.start_char + chunk_start_idx,
                                    end_char=local_span.end_char + chunk_start_idx,
                                    text=local_span.text,
                                    context_before=local_span.context_before,
                                    context_after=local_span.context_after
                                )
                        
                        spans = [source_span] if source_span else []
                        
                        all_extractions.append(GroundedExtraction(
                            data=data_dict,
                            source_spans=spans
                        ))
                        
            except Exception as e:
                logger.error(f"LangExtract failed on chunk {chunk['id']}: {e}")
                continue
                
        return all_extractions

    def _create_grounded_schema(self, original_schema: Type[T]) -> Type[BaseModel]:
        """
        Dynamically create a new Pydantic model that wraps the original
        and adds a 'quote' field for citation.
        Also wraps in a 'Container' to handle multiple extractions (list).
        """
        # 1. Create a model that inherits fields from original but adds quote
        # We assume original_schema is a Pydantic model
        
        # Helper to create a new class with 'quote'
        
        # We need to construct a new type that looks like:
        # class GroundedItem(original_schema):
        #     quote: str = Field(..., description="Exact substring from text supporting this extraction")
        
        # But we can't easily inherit dynamically if we want to preserve fields exactly for 'strict'.
        # Better approach: Create a new model with all fields from original + quote.
        
        fields = {k: (v.annotation, v) for k, v in original_schema.model_fields.items()}
        fields['quote'] = (str, Field(..., description="The exact substring from the text that serves as evidence for this extraction."))
        
        GroundedItem = create_model(
            f"Grounded{original_schema.__name__}",
            **fields
        )
        
        # 2. Create the container list model
        # class ExtractionResult(BaseModel):
        #     items: List[GroundedItem]
        
        Container = create_model(
            f"{original_schema.__name__}List",
            items=(List[GroundedItem], Field(default_factory=list))
        )
        
        return Container
