import pytest
from app.services.rag.service import AgriculturalRAGService

def test_rag_retrieves_tomato_citations():
    rag = AgriculturalRAGService()
    results = rag.retrieve_evidence("tomato early blight concentric spots", crop="Tomato", top_k=2)
    assert len(results) > 0
    top_res = results[0]
    assert top_res.crop == "Tomato"
    assert top_res.relevance_score > 0
    assert top_res.source_name != ""

def test_rag_retrieves_chilli_citations():
    rag = AgriculturalRAGService()
    results = rag.retrieve_evidence("chilli leaf curl upward virus whiteflies", crop="Chilli", top_k=2)
    assert len(results) > 0
    assert results[0].crop == "Chilli"
