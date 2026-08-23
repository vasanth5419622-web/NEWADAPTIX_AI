from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
import time

class ConfidenceLevel(str, Enum):
    HIGH = "High"
    MODERATE = "Moderate"
    LOW = "Low"

class TaskType(str, Enum):
    IMAGE_QUALITY = "image_quality"
    CROP_IDENTIFICATION = "crop_identification"
    SYMPTOM_ANALYSIS = "symptom_analysis"
    DISEASE_ANALYSIS = "disease_analysis"
    CONTEXT_ANALYSIS = "context_analysis"
    ADVISORY_RETRIEVAL = "advisory_retrieval"
    EVIDENCE_FUSION = "evidence_fusion"
    VERIFICATION = "verification"
    RECOMMENDATION = "recommendation"
    TRANSLATION = "translation"
    VOICE_TRANSCRIPTION = "voice_transcription"
    VOICE_GENERATION = "voice_generation"

class ImageQualityResult(BaseModel):
    passed: bool
    blur_score: float
    brightness_score: float
    contrast_score: float
    resolution: List[int] = Field(default_factory=lambda: [0, 0])
    issues: List[str] = Field(default_factory=list)
    actionable_message: Optional[str] = None

class UserContext(BaseModel):
    crop: Optional[str] = None
    location: Optional[str] = None
    growth_stage: Optional[str] = None
    season: Optional[str] = None
    soil_type: Optional[str] = None
    notes: Optional[str] = None

class UserInput(BaseModel):
    text: Optional[str] = None
    voice_transcript: Optional[str] = None
    language: str = "en" # "en" or "ta"

class TaskItem(BaseModel):
    task_id: str
    task_type: TaskType
    input_data: Dict[str, Any] = Field(default_factory=dict)
    expected_output: str
    priority: int = 1
    confidence: Optional[float] = None
    assigned_model: Optional[str] = None
    status: str = "pending" # pending, in_progress, completed, failed, skipped
    latency_ms: float = 0.0
    estimated_cost: float = 0.0
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ExecutionPlan(BaseModel):
    request_id: str
    tasks: List[TaskItem] = Field(default_factory=list)
    strategy_rationale: str = ""

class RouteEvent(BaseModel):
    step_number: int
    task_type: str
    model_name: str
    provider: str
    reason: str
    routing_score: float
    latency_ms: float
    estimated_cost: float
    confidence_score: Optional[float] = None
    status: str = "success"

class EvidenceSource(BaseModel):
    source_name: str
    document_title: str
    page: int
    relevance_score: float
    matched_text: str
    crop: Optional[str] = None
    disease_condition: Optional[str] = None
    growth_stage: Optional[str] = None

class MultiEvidenceFusion(BaseModel):
    visual_evidence: Dict[str, Any] = Field(default_factory=dict)
    advisory_evidence: List[EvidenceSource] = Field(default_factory=list)
    context_evidence: Dict[str, Any] = Field(default_factory=dict)
    combined_assessment: Dict[str, Any] = Field(default_factory=dict)
    conflicts_detected: List[str] = Field(default_factory=list)
    agreement_score: float = 1.0

class VerificationResult(BaseModel):
    verified: bool
    consistency_score: float
    issues: List[str] = Field(default_factory=list)
    reason: str
    action: str = "proceed" # proceed, escalate, review_required

class ConfidenceEvaluation(BaseModel):
    score: float # 0.0 to 1.0
    level: ConfidenceLevel
    breakdown: Dict[str, float] = Field(default_factory=dict)
    is_safe_for_direct_advice: bool = True

class FallbackEvent(BaseModel):
    case_type: str # bad_image, low_confidence, model_failure, conflicting_evidence, uncertain
    trigger_reason: str
    action_taken: str
    escalation_model: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)

class FinalRecommendation(BaseModel):
    crop: str
    possible_condition: str
    assessment_summary: str
    management_advice: List[str] = Field(default_factory=list)
    preventative_measures: List[str] = Field(default_factory=list)
    safety_disclaimer: str = (
        "AI-assisted assessment. This is not a guaranteed diagnosis. "
        "Consult local agricultural extension officers before applying treatments."
    )
    voice_audio_url: Optional[str] = None
    requires_human_review: bool = False

class ExecutionState(BaseModel):
    request_id: str
    created_at: float = Field(default_factory=time.time)
    status: str = "created"
    user_input: UserInput = Field(default_factory=UserInput)
    image_metadata: Dict[str, Any] = Field(default_factory=dict)
    context: UserContext = Field(default_factory=UserContext)
    quality_check: Optional[ImageQualityResult] = None
    plan: Optional[ExecutionPlan] = None
    model_calls: List[Dict[str, Any]] = Field(default_factory=list)
    route_trace: List[RouteEvent] = Field(default_factory=list)
    intermediate_results: Dict[str, Any] = Field(default_factory=dict)
    retrieved_sources: List[EvidenceSource] = Field(default_factory=list)
    evidence_fusion: Optional[MultiEvidenceFusion] = None
    verification_results: Optional[VerificationResult] = None
    confidence: Optional[ConfidenceEvaluation] = None
    fallback_events: List[FallbackEvent] = Field(default_factory=list)
    final_result: Optional[FinalRecommendation] = None
    total_latency_ms: float = 0.0
    total_estimated_cost: float = 0.0

# API Requests & Responses
class AnalyzeTextRequest(BaseModel):
    text: str
    crop: Optional[str] = None
    location: Optional[str] = None
    growth_stage: Optional[str] = None
    season: Optional[str] = None
    notes: Optional[str] = None
    language: str = "en"

class DocumentUploadResponse(BaseModel):
    doc_id: str
    filename: str
    title: str
    crop: str
    chunks_indexed: int
    message: str

class VoiceTranscribeRequest(BaseModel):
    language: str = "en"
    audio_base64: Optional[str] = None
    text_fallback: Optional[str] = None

class VoiceSynthesizeRequest(BaseModel):
    text: str
    language: str = "en" # "en" or "ta"
