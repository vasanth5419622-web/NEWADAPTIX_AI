import pytest
from app.services.confidence.engine import ConfidenceEngine
from app.schemas.shared import ConfidenceLevel, ImageQualityResult, VerificationResult

def test_confidence_engine_high():
    ce = ConfidenceEngine()
    quality = ImageQualityResult(
        passed=True, blur_score=120.0, brightness_score=110.0, contrast_score=45.0, resolution=[400, 400]
    )
    verif = VerificationResult(
        verified=True, consistency_score=0.92, issues=[], reason="Consistent", action="proceed"
    )
    res = ce.evaluate(
        model_confidence=0.90,
        fusion=None,
        quality=quality,
        verifier_res=verif,
        context={"crop": "Tomato", "growth_stage": "Vegetative"}
    )
    assert res.level == ConfidenceLevel.HIGH
    assert res.score >= 0.80

def test_confidence_engine_low_on_bad_quality():
    ce = ConfidenceEngine()
    quality = ImageQualityResult(
        passed=False, blur_score=20.0, brightness_score=15.0, contrast_score=10.0, resolution=[100, 100], issues=["blurry"]
    )
    verif = VerificationResult(
        verified=False, consistency_score=0.40, issues=["mismatch"], reason="Mismatch", action="review_required"
    )
    res = ce.evaluate(
        model_confidence=0.50,
        fusion=None,
        quality=quality,
        verifier_res=verif,
        context={}
    )
    assert res.score < 0.65
