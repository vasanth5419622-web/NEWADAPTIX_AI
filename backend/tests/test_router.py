import pytest
from app.services.router.adaptive_router import AdaptiveModelRouter
from app.schemas.shared import TaskItem, TaskType

def test_router_selects_models_by_task_role():
    router = AdaptiveModelRouter()

    # Crop Identification -> Open-Weight
    task_crop = TaskItem(
        task_id="T-1",
        task_type=TaskType.CROP_IDENTIFICATION,
        expected_output="crop_name"
    )
    event_crop = router.route_task(task_crop, step_number=1)
    assert "Open-Weight" in event_crop.model_name
    assert event_crop.estimated_cost == 0.0

    # Symptom Analysis -> Commercial Model A
    task_symp = TaskItem(
        task_id="T-2",
        task_type=TaskType.SYMPTOM_ANALYSIS,
        expected_output="symptoms"
    )
    event_symp = router.route_task(task_symp, step_number=2)
    assert "Commercial A" in event_crop.model_name or "Commercial A" in event_symp.model_name

    # Verification -> Commercial Model B
    task_verif = TaskItem(
        task_id="T-3",
        task_type=TaskType.VERIFICATION,
        expected_output="verified"
    )
    event_verif = router.route_task(task_verif, step_number=3)
    assert "Commercial B" in event_verif.model_name
