import time
import json
from typing import Dict, Any, Optional, List
from app.services.models.base import BaseModelProvider, ModelResponse

class MockAgriculturalProvider(BaseModelProvider):
    """
    High-fidelity agronomic AI provider for offline evaluation, development, and testing.
    Produces structured agricultural assessments matching actual LLM/VLM schema outputs.
    """
    def __init__(self, model_name: str = "mock-vision-agent", role: str = "open_weight", api_key: str = "", base_url: str = ""):
        super().__init__(model_name, api_key, base_url)
        self.role = role # "open_weight", "commercial_a", "commercial_b"

    async def analyze_image(
        self,
        image_path: str,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ModelResponse:
        start_time = time.time()
        context = context or {}
        crop_hint = (context.get("crop") or "").lower()
        stated_text = (context.get("user_description") or prompt or "").lower()

        # Simulate processing delay based on model tier
        if self.role == "open_weight":
            sim_latency = 280.0
            cost = 0.00000
            input_tokens = 240
            output_tokens = 95
            
            # Fast Crop Identification & Quick Feature Extraction
            detected_crop = "Tomato"
            confidence = 0.92
            if "chilli" in crop_hint or "chilli" in stated_text or "pepper" in stated_text:
                detected_crop = "Chilli"
                confidence = 0.89
            elif "rice" in crop_hint or "paddy" in stated_text:
                detected_crop = "Rice"
                confidence = 0.94
            elif "potato" in crop_hint:
                detected_crop = "Potato"
                confidence = 0.91
            elif crop_hint:
                detected_crop = crop_hint.capitalize()
                confidence = 0.86

            structured = {
                "detected_crop": detected_crop,
                "confidence": confidence,
                "plant_part": "Leaf / Foliage",
                "visible_anomalies": ["Chlorosis / Yellowing", "Concentric dark necrotic lesions", "Irregular margins"],
                "initial_assessment": f"Possible early fungal or leaf spot condition on {detected_crop}.",
                "recommended_specialist_tier": "commercial_a"
            }
            content = f"Visual analysis indicates {detected_crop} foliage with visible necrotic spots and chlorotic halos."

        else:
            # Commercial Model A: Deep Multimodal Reasoning
            sim_latency = 1450.0
            cost = 0.01450
            input_tokens = 850
            output_tokens = 320
            
            crop_name = context.get("crop") or "Tomato"
            if "curl" in stated_text or "chilli" in crop_name.lower():
                condition = "Chilli Leaf Curl Complex (Gemini Virus / Thrip Vector)"
                severity = "Moderate"
                confidence = 0.87
                symptoms = ["Upward curling of apical leaves", "Shortened internodes", "Puckering and thickening of lamina"]
                differential = ["Thrips or Mite Feeding Injury", "Chilli Veinal Mottle", "Zinc Deficiency"]
            elif "blast" in stated_text or "rice" in crop_name.lower():
                condition = "Rice Blast (Magnaporthe oryzae)"
                severity = "Moderate to High"
                confidence = 0.91
                symptoms = ["Spindle-shaped or diamond-shaped lesions", "Gray center with brownish-red border", "Collar rot"]
                differential = ["Brown Spot (Bipolaris oryzae)", "Bacterial Leaf Blight"]
            else:
                condition = "Tomato Early Blight (Alternaria solani)"
                severity = "Moderate"
                confidence = 0.89
                symptoms = [
                    "Concentric ring 'bullseye' target lesions on lower mature leaves",
                    "Yellow chlorotic halo surrounding necrotic spots",
                    "Early leaf senescence in humid microclimate"
                ]
                differential = ["Septoria Leaf Spot", "Bacterial Spot (Xanthomonas)", "Target Spot (Corynespora)"]

            structured = {
                "crop": crop_name,
                "possible_condition": condition,
                "severity_level": severity,
                "confidence_score": confidence,
                "detected_symptoms": symptoms,
                "differential_diagnoses": differential,
                "pathogen_class": "Fungal / Folia Infection",
                "affected_organs": ["Lower leaves", "Petiole margins"],
                "reasoning_trace": (
                    f"Multimodal inspection confirms foliar anomalies consistent with {condition}. "
                    "Concentric banding and surrounding halo morphology align closely with standard diagnostic patterns."
                )
            }
            content = f"Detailed multimodal analysis indicates {condition} on {crop_name} with {severity} severity."

        elapsed_ms = (time.time() - start_time) * 1000 + sim_latency

        return ModelResponse(
            content=content,
            structured_data=structured,
            latency_ms=elapsed_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost=cost,
            confidence=structured.get("confidence_score", structured.get("confidence", 0.88)),
            model_name=self.model_name,
            provider="mock_agricultural_ai"
        )

    async def analyze_text(
        self,
        text_prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ModelResponse:
        start_time = time.time()
        sim_latency = 450.0
        cost = 0.00350

        crop_name = (context or {}).get("crop", "General Agricultural")
        structured = {
            "intent": "crop_health_query",
            "extracted_crop": crop_name,
            "key_symptoms": ["leaf discoloration", "abnormal growth"],
            "urgency": "medium"
        }
        elapsed_ms = (time.time() - start_time) * 1000 + sim_latency

        return ModelResponse(
            content=f"Processed query regarding {crop_name}.",
            structured_data=structured,
            latency_ms=elapsed_ms,
            input_tokens=320,
            output_tokens=110,
            estimated_cost=cost,
            confidence=0.90,
            model_name=self.model_name,
            provider="mock_agricultural_ai"
        )

    async def verify_evidence(
        self,
        visual_findings: Dict[str, Any],
        rag_evidence: list,
        crop_context: Dict[str, Any]
    ) -> ModelResponse:
        """
        Commercial Model B role: Acts as independent critic and hallucination verifier.
        """
        start_time = time.time()
        sim_latency = 920.0
        cost = 0.00920

        condition = visual_findings.get("possible_condition", visual_findings.get("initial_assessment", "Crop Foliar Condition"))
        issues = []
        consistency_score = 0.88
        
        # Check if RAG evidence is available and consistent
        if not rag_evidence:
            consistency_score = 0.70
            issues.append("Limited specific extension bulletin match in local vector library; relying on general agronomic taxonomy.")
        else:
            # Check for keyword consistency
            top_source = rag_evidence[0].get("matched_text", "")
            if len(top_source) > 20:
                consistency_score = 0.92

        verified = len(issues) == 0 or consistency_score >= 0.75
        action = "proceed" if verified else "review_required"

        structured = {
            "verified": verified,
            "consistency_score": round(consistency_score, 2),
            "issues": issues,
            "reason": "Visual symptom patterns, advisory guidelines, and seasonal crop context are coherent." if verified else "Evidence shows minor divergence.",
            "action": action,
            "critic_notes": (
                "Verified concentric lesion topology against ICAR/TNAU standard advisory benchmarks. "
                "No conflicting diagnostic signs detected in foliage inspection."
            )
        }

        elapsed_ms = (time.time() - start_time) * 1000 + sim_latency

        return ModelResponse(
            content="Verification completed successfully." if verified else "Verification flagged advisory inconsistencies.",
            structured_data=structured,
            latency_ms=elapsed_ms,
            input_tokens=520,
            output_tokens=180,
            estimated_cost=cost,
            confidence=consistency_score,
            model_name=self.model_name,
            provider="mock_agricultural_critic"
        )

    async def generate_response(
        self,
        system_instruction: str,
        user_prompt: str
    ) -> ModelResponse:
        start_time = time.time()
        sim_latency = 650.0
        cost = 0.00500

        elapsed_ms = (time.time() - start_time) * 1000 + sim_latency
        return ModelResponse(
            content="Standard structured recommendation generated.",
            structured_data={"status": "ok"},
            latency_ms=elapsed_ms,
            input_tokens=400,
            output_tokens=200,
            estimated_cost=cost,
            confidence=0.90,
            model_name=self.model_name,
            provider="mock_agricultural_ai"
        )
