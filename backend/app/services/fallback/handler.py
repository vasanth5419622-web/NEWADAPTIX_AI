from typing import Dict, Any, List, Optional
from app.schemas.shared import FallbackEvent, ExecutionState, ConfidenceLevel

class FallbackHandler:
    """
    Handles autonomous fallback and escalation logic across the agentic pipeline:
    - Image Quality Gate Fallback
    - Low Confidence Escalation to High-Capacity Commercial Models
    - Model Fault Tolerance and Alternation
    - RAG Retrieval Graceful Degradation
    - Conflict Flagging & Human Review Routing
    """
    def handle_image_quality_failure(self, issues: List[str], state: ExecutionState) -> FallbackEvent:
        event = FallbackEvent(
            case_type="bad_image",
            trigger_reason=f"Pre-flight image quality check failed: {'; '.join(issues)}",
            action_taken="Halted deep model pipeline. Prompted user to re-upload higher-clarity crop photograph.",
            escalation_model=None
        )
        state.fallback_events.append(event)
        return event

    def handle_low_confidence(self, current_confidence: float, state: ExecutionState) -> FallbackEvent:
        event = FallbackEvent(
            case_type="low_confidence",
            trigger_reason=f"Preliminary analysis confidence ({current_confidence:.2f}) was below certainty threshold (0.75).",
            action_taken="Escalated to Commercial Model A (Deep Multimodal Reasoning) for secondary path reasoning.",
            escalation_model="GPT-4o-Mini / Claude 3.5"
        )
        state.fallback_events.append(event)
        return event

    def handle_conflicting_evidence(self, conflicts: List[str], state: ExecutionState) -> FallbackEvent:
        event = FallbackEvent(
            case_type="conflicting_evidence",
            trigger_reason=f"Cross-evidence divergence: {'; '.join(conflicts)}",
            action_taken="Flagged recommendation as 'Requires Review'. Added cautionary guidelines and requested agricultural officer inspection.",
            escalation_model="Commercial Model B Critic"
        )
        state.fallback_events.append(event)
        return event

    def handle_model_failure(self, failed_model: str, error_msg: str, state: ExecutionState) -> FallbackEvent:
        event = FallbackEvent(
            case_type="model_failure",
            trigger_reason=f"Primary model {failed_model} failed: {error_msg}",
            action_taken="Switched to local deterministic agricultural engine fallback.",
            escalation_model="Local Mock / Fallback Engine"
        )
        state.fallback_events.append(event)
        return event

fallback_handler = FallbackHandler()
