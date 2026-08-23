from typing import Dict, Any, Optional
from app.schemas.shared import ConfidenceEvaluation, ConfidenceLevel, ImageQualityResult, VerificationResult, MultiEvidenceFusion

class ConfidenceEngine:
    """
    Confidence Evaluation Engine:
    Calculates weighted confidence based on:
    - Model intrinsic probability
    - Multi-evidence agreement score
    - Image clarity & photometric quality
    - Context completeness
    - Independent verifier consistency
    """
    def evaluate(
        self,
        model_confidence: float,
        fusion: Optional[MultiEvidenceFusion],
        quality: Optional[ImageQualityResult],
        verifier_res: Optional[VerificationResult],
        context: Dict[str, Any]
    ) -> ConfidenceEvaluation:
        # 1. Model Confidence Component (weight: 0.30)
        c_model = max(0.0, min(1.0, model_confidence))

        # 2. Evidence Agreement Component (weight: 0.25)
        c_fusion = fusion.agreement_score if fusion else 0.70

        # 3. Image Quality Component (weight: 0.20)
        if quality:
            if quality.passed:
                # Scaled blur and contrast health
                c_quality = 0.95
            else:
                c_quality = 0.40
        else:
            c_quality = 0.80

        # 4. Verifier Consistency Component (weight: 0.15)
        c_verifier = verifier_res.consistency_score if verifier_res else 0.80

        # 5. Context Completeness (weight: 0.10)
        filled_fields = sum(1 for v in context.values() if v)
        c_context = min(1.0, 0.5 + (filled_fields * 0.15))

        # Total Weighted Composite Score
        total_score = (
            (c_model * 0.30)
            + (c_fusion * 0.25)
            + (c_quality * 0.20)
            + (c_verifier * 0.15)
            + (c_context * 0.10)
        )
        total_score = round(max(0.10, min(0.99, total_score)), 2)

        # Categorize Level
        if total_score >= 0.80 and (verifier_res is None or verifier_res.verified):
            level = ConfidenceLevel.HIGH
            is_safe = True
        elif total_score >= 0.60:
            level = ConfidenceLevel.MODERATE
            is_safe = True
        else:
            level = ConfidenceLevel.LOW
            is_safe = False

        breakdown = {
            "model_confidence": round(c_model, 2),
            "evidence_agreement": round(c_fusion, 2),
            "image_quality": round(c_quality, 2),
            "verifier_consistency": round(c_verifier, 2),
            "context_completeness": round(c_context, 2)
        }

        return ConfidenceEvaluation(
            score=total_score,
            level=level,
            breakdown=breakdown,
            is_safe_for_direct_advice=is_safe
        )

confidence_engine = ConfidenceEngine()
