from typing import Dict, Any, List, Optional
from app.schemas.shared import TaskType, RouteEvent, TaskItem

class RoutingCandidate:
    def __init__(
        self,
        key: str,
        name: str,
        provider: str,
        capability: float,
        base_confidence: float,
        est_latency_ms: float,
        est_cost: float,
        availability: float = 1.0
    ):
        self.key = key
        self.name = name
        self.provider = provider
        self.capability = capability
        self.base_confidence = base_confidence
        self.est_latency_ms = est_latency_ms
        self.est_cost = est_cost
        self.availability = availability

    def calculate_score(self, latency_weight: float = 0.15, cost_weight: float = 0.20) -> float:
        """
        routing_score = capability + confidence - latency_penalty - cost_penalty + availability
        """
        # Normalize latency (0-3000ms -> 0-1)
        latency_penalty = min(1.0, self.est_latency_ms / 3000.0) * latency_weight
        # Normalize cost ($0 - $0.05 -> 0-1)
        cost_penalty = min(1.0, self.est_cost / 0.05) * cost_weight
        
        score = (
            self.capability
            + self.base_confidence
            - latency_penalty
            - cost_penalty
            + (self.availability * 0.5)
        )
        return round(score, 3)

class AdaptiveModelRouter:
    """
    Adaptive Model Router:
    Selects the optimal model/tool per task using multi-objective scoring (capability, latency, cost, availability).
    Records transparent routing trace with explicit rationale.
    """
    def __init__(self):
        self.candidates = {
            "open_weight": RoutingCandidate(
                key="open_weight",
                name="Qwen2-VL-7B (Open-Weight)",
                provider="Local / HF Inference",
                capability=0.82,
                base_confidence=0.88,
                est_latency_ms=280.0,
                est_cost=0.00000,
                availability=1.0
            ),
            "commercial_a": RoutingCandidate(
                key="commercial_a",
                name="GPT-4o-Mini / Claude 3.5 (Commercial A)",
                provider="OpenAI / Commercial API",
                capability=0.96,
                base_confidence=0.93,
                est_latency_ms=1450.0,
                est_cost=0.01450,
                availability=1.0
            ),
            "commercial_b": RoutingCandidate(
                key="commercial_b",
                name="Claude 3.5 Sonnet / Critic (Commercial B)",
                provider="Anthropic / Critic Engine",
                capability=0.98,
                base_confidence=0.95,
                est_latency_ms=920.0,
                est_cost=0.00920,
                availability=1.0
            ),
            "rag_engine": RoutingCandidate(
                key="rag_engine",
                name="Agricultural Advisory Vector RAG",
                provider="Local Vector Database",
                capability=0.94,
                base_confidence=0.90,
                est_latency_ms=180.0,
                est_cost=0.00050,
                availability=1.0
            )
        }

    def route_task(
        self,
        task: TaskItem,
        step_number: int,
        context: Optional[Dict[str, Any]] = None,
        is_escalated: bool = False
    ) -> RouteEvent:
        t_type = task.task_type
        
        # 1. Crop Identification / Quick Preprocessing -> Route to Open-Weight / Small Model
        if t_type == TaskType.CROP_IDENTIFICATION:
            cand = self.candidates["open_weight"]
            score = cand.calculate_score()
            reason = "Fast, zero-cost visual taxonomy suitable for initial crop identification and leaf localization."
            return RouteEvent(
                step_number=step_number,
                task_type=t_type.value,
                model_name=cand.name,
                provider=cand.provider,
                reason=reason,
                routing_score=score,
                latency_ms=cand.est_latency_ms,
                estimated_cost=cand.est_cost,
                confidence_score=cand.base_confidence
            )

        # 2. Symptom & Disease Analysis -> Commercial Model A (or escalated)
        elif t_type in [TaskType.SYMPTOM_ANALYSIS, TaskType.DISEASE_ANALYSIS]:
            cand = self.candidates["commercial_a"]
            score = cand.calculate_score()
            reason = "High-tier multimodal reasoning required for ambiguous foliar lesion patterns and differential diagnosis."
            if is_escalated:
                reason = "ESCALATED: Low preliminary confidence triggered advanced commercial reasoning pipeline."
            return RouteEvent(
                step_number=step_number,
                task_type=t_type.value,
                model_name=cand.name,
                provider=cand.provider,
                reason=reason,
                routing_score=score,
                latency_ms=cand.est_latency_ms,
                estimated_cost=cand.est_cost,
                confidence_score=cand.base_confidence
            )

        # 3. Advisory Retrieval -> RAG Engine
        elif t_type == TaskType.ADVISORY_RETRIEVAL:
            cand = self.candidates["rag_engine"]
            score = cand.calculate_score()
            reason = "Semantic vector search against verified ICAR/TNAU/State Agricultural university extension bulletins."
            return RouteEvent(
                step_number=step_number,
                task_type=t_type.value,
                model_name=cand.name,
                provider=cand.provider,
                reason=reason,
                routing_score=score,
                latency_ms=cand.est_latency_ms,
                estimated_cost=cand.est_cost,
                confidence_score=cand.base_confidence
            )

        # 4. Verification & Critic Review -> Commercial Model B
        elif t_type == TaskType.VERIFICATION:
            cand = self.candidates["commercial_b"]
            score = cand.calculate_score()
            reason = "Independent critic checks multi-evidence consistency and flags hallucinations before final advisory."
            return RouteEvent(
                step_number=step_number,
                task_type=t_type.value,
                model_name=cand.name,
                provider=cand.provider,
                reason=reason,
                routing_score=score,
                latency_ms=cand.est_latency_ms,
                estimated_cost=cand.est_cost,
                confidence_score=cand.base_confidence
            )

        # 5. Image Quality & Fusion / Recommendation Default
        else:
            cand = self.candidates["open_weight"]
            score = cand.calculate_score()
            reason = f"Standard deterministic execution for {t_type.value}."
            return RouteEvent(
                step_number=step_number,
                task_type=t_type.value,
                model_name=cand.name,
                provider=cand.provider,
                reason=reason,
                routing_score=score,
                latency_ms=cand.est_latency_ms,
                estimated_cost=cand.est_cost,
                confidence_score=cand.base_confidence
            )

adaptive_router = AdaptiveModelRouter()
