from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class ModelResponse:
    def __init__(
        self,
        content: str,
        structured_data: Optional[Dict[str, Any]] = None,
        latency_ms: float = 0.0,
        input_tokens: int = 0,
        output_tokens: int = 0,
        estimated_cost: float = 0.0,
        confidence: float = 0.85,
        model_name: str = "",
        provider: str = ""
    ):
        self.content = content
        self.structured_data = structured_data or {}
        self.latency_ms = latency_ms
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.estimated_cost = estimated_cost
        self.confidence = confidence
        self.model_name = model_name
        self.provider = provider

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "structured_data": self.structured_data,
            "latency_ms": round(self.latency_ms, 2),
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "estimated_cost": round(self.estimated_cost, 5),
            "confidence": round(self.confidence, 3),
            "model_name": self.model_name,
            "provider": self.provider
        }

class BaseModelProvider(ABC):
    """
    Abstract Model Provider Interface.
    Ensures modularity and zero vendor lock-in.
    """
    def __init__(self, model_name: str, api_key: str = "", base_url: str = ""):
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url

    @abstractmethod
    async def analyze_image(
        self,
        image_path: str,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ModelResponse:
        pass

    @abstractmethod
    async def analyze_text(
        self,
        text_prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ModelResponse:
        pass

    @abstractmethod
    async def verify_evidence(
        self,
        visual_findings: Dict[str, Any],
        rag_evidence: list,
        crop_context: Dict[str, Any]
    ) -> ModelResponse:
        pass

    @abstractmethod
    async def generate_response(
        self,
        system_instruction: str,
        user_prompt: str
    ) -> ModelResponse:
        pass
