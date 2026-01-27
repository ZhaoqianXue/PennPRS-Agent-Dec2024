import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from lib.langextract.core import LangExtractor, SectionType

def test_langextract():
    print("Testing LangExtract...")
    
    # Create dummy document
    doc = """
    Abstract
    This is the abstract of the paper. It summarizes everything.
    
    Introduction
    Alzheimer's disease is a neurodegenerative disorder.
    Here we study the heritability of AD.
    
    Methods
    We collected 1000 samples.
    We used a logistic regression model.
    
    Results
    The heritability was estimated to be 0.75.
    This is a significant finding.
    
    Discussion
    Our results align with previous studies.
    """
    
    extractor = LangExtractor(chunk_size=100, overlap=20)
    chunks = extractor.chunk_text(doc)
    
    print(f"Generated {len(chunks)} chunks.")
    
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i} [{chunk.section_type.value}]: {chunk.text[:30]}...")
        
    # Test Evidence
    quote = "heritability was estimated to be 0.75"
    evidence = extractor.locate_evidence(doc, quote)
    
    if evidence:
        print("\nEvidence found:")
        print(f"Quote: {evidence.quote}")
        print(f"HTML: {evidence.to_html_snippet()}")
    else:
        print("\nEvidence NOT found!")

if __name__ == "__main__":
    test_langextract()
