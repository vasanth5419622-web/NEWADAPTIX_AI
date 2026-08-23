from typing import Dict, Any, List, Optional
from app.schemas.shared import VerificationResult, MultiEvidenceFusion
from app.services.models.factory import model_factory

class IndependentVerifier:
    """
    Independent Critic and Verifier Engine (Commercial Model B role).
    Cross-checks the fused evidence to prevent hallucinations and excessive certainty.
    """
    async def verify(
        self,
        fusion: MultiEvidenceFusion,
        visual_findings: Dict[str, Any],
        context: Dict[str, Any]
    ) -> VerificationResult:
        critic_model = model_factory.get_commercial_b()
        
        # Prepare structured input for critic
        res = await critic_model.verify_evidence(
            visual_findings=visual_findings,
            rag_evidence=[src.model_dump() for src in fusion.advisory_evidence],
            crop_context=context
        )

        crit_data = res.structured_data
        verified = crit_data.get("verified", True)
        consistency_score = crit_data.get("consistency_score", fusion.agreement_score)
        issues = list(crit_data.get("issues", [])) + list(fusion.conflicts_detected)
        
        # If conflicts exist, flag for review
        if len(fusion.conflicts_detected) > 0:
            verified = False
            consistency_score = min(consistency_score, 0.65)
            action = "review_required"
            reason = f"Evidence inconsistency detected: {'; '.join(fusion.conflicts_detected)}"
        else:
            action = "proceed" if verified else "escalate"
            reason = crit_data.get("reason", "Visual symptoms, advisory literature, and field context are consistent.")

        return VerificationResult(
            verified=verified,
            consistency_score=round(float(consistency_score), 2),
            issues=issues,
            reason=reason,
            action=action
        )

verifier = IndependentVerifier()
