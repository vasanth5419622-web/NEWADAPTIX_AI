import pytest
from app.services.verifier.fusion import MultiEvidenceFusionEngine
from app.services.verifier.verifier import IndependentVerifier
from app.schemas.shared import UserContext, EvidenceSource

def test_fusion_detects_crop_agreement():
    fe = MultiEvidenceFusionEngine()
    vis = {"crop": "Tomato", "detected_crop": "Tomato", "possible_condition": "Early Blight"}
    sources = [
        EvidenceSource(
            source_name="tomato_advisory.pdf",
            document_title="ICAR Tomato Bulletin",
            page=4,
            relevance_score=0.92,
            matched_text="Early blight target spots on foliage."
        )
    ]
    ctx = UserContext(crop="Tomato", growth_stage="Vegetative")

    fusion = fe.fuse_evidence(vis, sources, ctx)
    assert len(fusion.conflicts_detected) == 0
    assert fusion.agreement_score >= 0.80

@pytest.mark.asyncio
async def test_verifier_critic():
    v = IndependentVerifier()
    fe = MultiEvidenceFusionEngine()
    vis = {"crop": "Tomato", "possible_condition": "Early Blight"}
    ctx = UserContext(crop="Tomato")
    fusion = fe.fuse_evidence(vis, [], ctx)

    res = await v.verify(fusion, vis, ctx.model_dump())
    assert res.consistency_score > 0
    assert res.action in ["proceed", "review_required"]
