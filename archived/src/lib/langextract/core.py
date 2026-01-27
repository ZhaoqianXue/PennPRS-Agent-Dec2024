import dataclasses
from typing import List, Optional, Dict
import html
from enum import Enum
import re

class SectionType(str, Enum):
    ABSTRACT = "abstract"
    INTRODUCTION = "introduction"
    METHODS = "methods"
    RESULTS = "results"
    DISCUSSION = "discussion"
    REFERENCES = "references"
    UNKNOWN = "unknown"

@dataclasses.dataclass
class Chunk:
    """Represents a chunk of text from a document."""
    text: str
    start_char: int
    end_char: int
    id: int
    section_type: SectionType = SectionType.UNKNOWN
    metadata: Dict[str, str] = dataclasses.field(default_factory=dict)

@dataclasses.dataclass
class Evidence:
    """Represents a piece of evidence found in the text."""
    quote: str
    source_chunk_id: int
    start_char: int  # Global start char in original document
    end_char: int    # Global end char in original document
    context_before: str = ""
    context_after: str = ""
    
    def to_html_snippet(self) -> str:
        """Generates an HTML snippet with the quote highlighted."""
        safe_before = html.escape(self.context_before)
        safe_quote = html.escape(self.quote)
        safe_after = html.escape(self.context_after)
        
        return f'<div class="evidence-snippet">...{safe_before}<mark class="highlight">{safe_quote}</mark>{safe_after}...</div>'

class LangExtractor:
    """
    Core engine for LangExtract.
    Handles document chunking, evidence location, and visualization.
    """
    def __init__(self, chunk_size: int = 2000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap
        
        # Simple heuristics for section headers
        self.section_patterns = {
            SectionType.ABSTRACT: re.compile(r'^\s*(abstract|summary)\s*$', re.I | re.M),
            SectionType.INTRODUCTION: re.compile(r'^\s*(introduction|background)\s*$', re.I | re.M),
            SectionType.METHODS: re.compile(r'^\s*(methods|methodology|materials and methods)\s*$', re.I | re.M),
            SectionType.RESULTS: re.compile(r'^\s*(results|findings)\s*$', re.I | re.M),
            SectionType.DISCUSSION: re.compile(r'^\s*(discussion|conclusion)\s*$', re.I | re.M),
            SectionType.REFERENCES: re.compile(r'^\s*(references|bibliography)\s*$', re.I | re.M),
        }

    def chunk_text(self, text: str) -> List[Chunk]:
        """
        Splits text into overlapping chunks and attempts to identify sections.
        """
        chunks = []
        if not text:
            return chunks
            
        current_pos = 0
        chunk_id = 0
        text_len = len(text)
        current_section = SectionType.UNKNOWN
        
        while current_pos < text_len:
            end_pos = min(current_pos + self.chunk_size, text_len)
            
            if end_pos < text_len:
                last_space = text.rfind(' ', current_pos, end_pos)
                if last_space != -1 and last_space > current_pos + (self.chunk_size * 0.5):
                    end_pos = last_space + 1
            
            chunk_text = text[current_pos:end_pos]
            
            # Detect section change within this chunk or implied from previous
            found_section = self._detect_section(chunk_text)
            if found_section != SectionType.UNKNOWN:
                current_section = found_section
            
            chunks.append(Chunk(
                text=chunk_text,
                start_char=current_pos,
                end_char=end_pos,
                id=chunk_id,
                section_type=current_section
            ))
            
            current_pos += (self.chunk_size - self.overlap)
            if current_pos <= chunks[-1].start_char:
                 current_pos = chunks[-1].end_char 
            
            chunk_id += 1
            
        return chunks

    def _detect_section(self, text: str) -> SectionType:
        """Simple heuristic to detect if a chunk establishes a new section."""
        # Check first 500 chars for headers
        header_window = text[:500]
        for section, pattern in self.section_patterns.items():
            if pattern.search(header_window):
                return section
        return SectionType.UNKNOWN

    def locate_evidence(self, text: str, quote: str, context_window: int = 100) -> Optional[Evidence]:
        """
        Locates a quote in the full text and returns an Evidence object.
        Uses exact match first, then falls back to fuzzy matching.
        """
        if not quote or not text:
            return None
            
        start_idx = text.find(quote)
        end_idx = -1
        
        if start_idx != -1:
            end_idx = start_idx + len(quote)
        else:
            # Fallback to fuzzy matching
            match = self._find_fuzzy_match(text, quote)
            if match:
                start_idx, end_idx = match
        
        if start_idx == -1:
            return None
            
        ctx_start = max(0, start_idx - context_window)
        ctx_end = min(len(text), end_idx + context_window)
        
        context_before = text[ctx_start:start_idx]
        context_after = text[end_idx:ctx_end]
        
        # Use the ACTUAL text from the document for the quote, not the LLM's version
        actual_quote = text[start_idx:end_idx]
        
        return Evidence(
            quote=actual_quote,
            source_chunk_id=-1,
            start_char=start_idx,
            end_char=end_idx,
            context_before=context_before,
            context_after=context_after
        )

    def _find_fuzzy_match(self, text: str, quote: str, threshold: float = 0.8) -> Optional[tuple[int, int]]:
        """
        Finds the best fuzzy match of quote in text. 
        Returns (start_index, end_index) or None.
        """
        import difflib
        
        # Optimization: Don't run difflib on massive text if possible.
        # But for papers (<100k chars), it's usually acceptable. 
        # For very large texts, we might need a sliding window.
        
        # Clean up whitespace for comparison
        clean_quote = " ".join(quote.split())
        if len(clean_quote) < 10: 
            return None # Too short for fuzzy match risk
            
        # Quick heuristic: Regex search with flexible whitespace
        # This handles newlines/spaces differences which are most common
        try:
            # Escape regex chars but replace spaces with \s+
            regex_pattern = re.escape(clean_quote)
            regex_pattern = regex_pattern.replace(r'\ ', r'\s+')
            match = re.search(regex_pattern, text, re.IGNORECASE)
            if match:
                return match.span()
        except Exception:
            pass # Fallback to slower difflib

        # Difflib approach
        # We look for a block in text that matches quote.
        # SequenceMatcher finds longest common substring, but we need the specific valid block.
        matcher = difflib.SequenceMatcher(None, text, quote, autojunk=False)
        match = matcher.find_longest_match(0, len(text), 0, len(quote))
        
        if match.size / len(quote) > threshold:
             return (match.a, match.a + match.size)
             
        return None
