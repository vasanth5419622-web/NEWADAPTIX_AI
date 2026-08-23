import os
import uuid
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from app.core.config import UPLOAD_DIR, DOCUMENTS_DIR, settings
from app.core.db import get_analysis_by_id, get_all_analyses
from app.schemas.shared import (
    UserInput, UserContext, ExecutionState, AnalyzeTextRequest,
    DocumentUploadResponse, VoiceTranscribeRequest, VoiceSynthesizeRequest
)
from app.services.orchestrator import orchestrator
from app.services.rag.service import rag_service
from app.services.rag.vector_store import vector_store
from app.services.voice.stt_tts import voice_service

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ADAPTIX-FARM Agricultural Intelligence API",
        "version": "1.0.0",
        "vector_chunks_indexed": len(vector_store.chunks)
    }

@router.post("/analyze")
async def analyze_crop(
    image: Optional[UploadFile] = File(None),
    crop: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    growth_stage: Optional[str] = Form(None),
    season: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    user_query: Optional[str] = Form(None),
    language: str = Form("en")
):
    """
    Main multimodal analysis endpoint.
    Accepts crop image photograph, speech transcript/text, and environmental context.
    """
    image_path = None
    if image and image.filename:
        # Validate extension
        ext = Path(image.filename).suffix.lower()
        if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
            raise HTTPException(status_code=400, detail="Invalid image format. Please upload JPG, PNG, or WEBP.")
            
        file_id = f"IMG-{uuid.uuid4().hex[:8]}"
        saved_filename = f"{file_id}_{image.filename}"
        dest = UPLOAD_DIR / saved_filename
        with open(dest, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_path = str(dest)

    user_input = UserInput(text=user_query, language=language)
    context = UserContext(
        crop=crop,
        location=location,
        growth_stage=growth_stage,
        season=season,
        notes=notes
    )

    state = await orchestrator.run_pipeline(
        user_input=user_input,
        image_path=image_path,
        context=context
    )
    return state.model_dump()

@router.post("/analyze/text")
async def analyze_text(request: AnalyzeTextRequest):
    """
    Text/Voice-only analysis pipeline for unseen or general agronomic queries.
    """
    user_input = UserInput(text=request.text, language=request.language)
    context = UserContext(
        crop=request.crop,
        location=request.location,
        growth_stage=request.growth_stage,
        season=request.season,
        notes=request.notes
    )
    state = await orchestrator.run_pipeline(
        user_input=user_input,
        image_path=None,
        context=context
    )
    return state.model_dump()

@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    crop: str = Form("General"),
    title: Optional[str] = Form(None)
):
    """
    Upload and index agricultural advisory PDF/bulletin into the RAG vector engine.
    """
    if not file.filename.endswith((".pdf", ".txt", ".md")):
        raise HTTPException(status_code=400, detail="Only PDF, TXT, and MD advisory documents are supported.")
        
    doc_id = f"DOC-{uuid.uuid4().hex[:8]}"
    saved_name = f"{doc_id}_{file.filename}"
    dest = DOCUMENTS_DIR / saved_name
    
    with open(dest, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    indexed_count = rag_service.index_document(str(dest), default_crop=crop, title=title)
    
    return DocumentUploadResponse(
        doc_id=doc_id,
        filename=file.filename,
        title=title or file.filename,
        crop=crop,
        chunks_indexed=indexed_count,
        message=f"Successfully extracted and indexed {indexed_count} semantic advisory chunks into vector store."
    )

@router.get("/documents/list")
async def list_documents():
    """
    Lists indexed RAG advisory chunks and metadata.
    """
    return {
        "total_chunks": len(vector_store.chunks),
        "chunks": vector_store.chunks[:100]
    }

@router.post("/documents/query")
async def query_documents(query: str = Form(...), crop: Optional[str] = Form(None)):
    """
    Test vector retrieval directly for agricultural advisory queries.
    """
    evidence = rag_service.retrieve_evidence(query=query, crop=crop, top_k=5)
    return {"query": query, "crop": crop, "results": [e.model_dump() for e in evidence]}

@router.get("/analysis/{request_id}")
async def get_analysis(request_id: str):
    """
    Fetch full execution state for an analysis.
    """
    state = get_analysis_by_id(request_id)
    if not state:
        raise HTTPException(status_code=404, detail="Analysis record not found.")
    return state

@router.get("/analysis/{request_id}/trace")
async def get_analysis_trace(request_id: str):
    """
    Fetch granular route trace for an analysis.
    """
    state = get_analysis_by_id(request_id)
    if not state:
        raise HTTPException(status_code=404, detail="Analysis record not found.")
    return {"request_id": request_id, "route_trace": state.get("route_trace", [])}

@router.get("/analysis/{request_id}/evidence")
async def get_analysis_evidence(request_id: str):
    """
    Fetch evidence fusion matrix and citations for an analysis.
    """
    state = get_analysis_by_id(request_id)
    if not state:
        raise HTTPException(status_code=404, detail="Analysis record not found.")
    return {
        "request_id": request_id,
        "evidence_fusion": state.get("evidence_fusion", {}),
        "retrieved_sources": state.get("retrieved_sources", [])
    }

@router.get("/history")
async def get_history(limit: int = 50):
    """
    Fetch past analyses history.
    """
    return get_all_analyses(limit=limit)

@router.post("/transcribe")
async def transcribe_voice(req: VoiceTranscribeRequest):
    """
    Speech-to-Text endpoint.
    """
    return voice_service.transcribe(
        audio_base64=req.audio_base64,
        text_fallback=req.text_fallback,
        language=req.language
    )

@router.post("/synthesize")
async def synthesize_voice(req: VoiceSynthesizeRequest):
    """
    Text-to-Speech endpoint.
    """
    return voice_service.synthesize(text=req.text, language=req.language)

@router.get("/metrics")
async def get_system_metrics():
    """
    Aggregates latency, cost, and routing distribution metrics.
    """
    history = get_all_analyses(limit=100)
    total_calls = len(history)
    avg_latency = (
        round(sum(h.get("total_latency_ms", 0) for h in history) / total_calls, 1)
        if total_calls > 0 else 0.0
    )
    total_cost = round(sum(h.get("total_estimated_cost", 0) for h in history), 5)
    
    return {
        "total_requests": total_calls,
        "average_latency_ms": avg_latency,
        "total_estimated_cost_usd": total_cost,
        "models_active": [
            {"role": "Open-weight / Small", "model": settings.open_model.name, "provider": settings.open_model.provider},
            {"role": "Commercial Model A", "model": settings.commercial_a.name, "provider": settings.commercial_a.provider},
            {"role": "Commercial Model B (Critic)", "model": settings.commercial_b.name, "provider": settings.commercial_b.provider}
        ],
        "indexed_rag_documents": len(vector_store.chunks)
    }

@router.get("/settings")
async def get_current_settings():
    return {
        "open_model": settings.open_model.model_dump(),
        "commercial_a": settings.commercial_a.model_dump(),
        "commercial_b": settings.commercial_b.model_dump(),
        "embedding_provider": settings.embedding_provider,
        "image_thresholds": {
            "min_blur": settings.min_blur_variance,
            "min_brightness": settings.min_brightness,
            "min_contrast": settings.min_contrast,
            "min_res": settings.min_resolution
        }
    }
