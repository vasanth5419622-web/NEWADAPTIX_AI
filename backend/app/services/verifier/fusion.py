from typing import Dict, Any, List, Optional
from app.schemas.shared import MultiEvidenceFusion, EvidenceSource, UserContext

class MultiEvidenceFusionEngine:
    """
    Synthesizes multiple disparate streams of agronomic evidence:
    1. Visual Pathology Analysis (Image symptoms & lesion morphology)
    2. Verified RAG Advisory Bulletins (ICAR/TNAU literature)
    3. User Context (Growth stage, location, weather, season)
    
    Detects agronomic conflicts (e.g. stage mismatch, contradictory symptom signs).
    """
    def fuse_evidence(
        self,
        visual_evidence: Dict[str, Any],
        advisory_sources: List[EvidenceSource],
        context: UserContext
    ) -> MultiEvidenceFusion:
        conflicts: List[str] = []
        agreed_points: List[str] = []

        crop = context.crop or visual_evidence.get("crop", "Unknown Crop")
        condition = visual_evidence.get("possible_condition", visual_evidence.get("initial_assessment", "Crop Condition"))

        # 1. Check Crop Agreement
        if context.crop and visual_evidence.get("detected_crop"):
            if context.crop.lower() != visual_evidence["detected_crop"].lower():
                conflicts.append(f"Visual crop identification ({visual_evidence['detected_crop']}) conflicts with farmer stated crop ({context.crop}).")
            else:
                agreed_points.append(f"Crop identity confirmed: {context.crop}")

        # 2. Check Growth Stage & Environmental Coherence
        growth_stage = context.growth_stage
        season = context.season

        if growth_stage and "seedling" in growth_stage.lower() and "early blight" in condition.lower():
            conflicts.append("Early Blight concentric target spots are predominantly mature foliage diseases; seedling onset is less typical unless severe dampening occurs.")

        # 3. Check Advisory Match
        if advisory_sources:
            top_evidence = advisory_sources[0]
            agreed_points.append(f"Found supporting extension advisory: '{top_evidence.document_title}' (Relevance: {top_evidence.relevance_score:.2f})")
        else:
            conflicts.append("No specific university extension bulletin matched the exact visual condition keywords.")

        # Compute Agreement Score (0.0 to 1.0)
        base_score = 0.90
        penalty = len(conflicts) * 0.25
        agreement_score = max(0.20, min(1.0, base_score - penalty + (0.05 * len(agreed_points))))

        combined_assessment = {
            "crop": crop,
            "condition": condition,
            "agreement_status": "High Agreement" if agreement_score >= 0.75 else "Requires Review",
            "agreed_points": agreed_points,
            "conflicts": conflicts
        }

        return MultiEvidenceFusion(
            visual_evidence=visual_evidence,
            advisory_evidence=advisory_sources,
            context_evidence=context.model_dump(),
            combined_assessment=combined_assessment,
            conflicts_detected=conflicts,
            agreement_score=round(agreement_score, 2)
        )

fusion_engine = MultiEvidenceFusionEngine()
