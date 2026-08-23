import pytest
from app.services.orchestrator import orchestrator
from app.schemas.shared import UserInput, UserContext

@pytest.mark.asyncio
async def test_end_to_end_orchestrator_pipeline():
    user_input = UserInput(text="Tomato leaves with concentric dark spots", language="en")
    context = UserContext(crop="Tomato", growth_stage="Vegetative")

    state = await orchestrator.run_pipeline(
        user_input=user_input,
        image_path=None,
        context=context
    )

    assert state.status == "completed"
    assert state.final_result is not None
    assert state.final_result.crop == "Tomato"
    assert len(state.route_trace) >= 4
    assert state.total_latency_ms > 0
    assert state.confidence is not None
