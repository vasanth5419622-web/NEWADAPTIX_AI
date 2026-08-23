import pytest
from app.services.planner.planner import AgriculturalPlanner
from app.schemas.shared import UserInput, UserContext, TaskType

def test_planner_creates_structured_tasks():
    p = AgriculturalPlanner()
    user_input = UserInput(text="Tomato leaves with black spots", language="en")
    image_meta = {"file_path": "/fake/path/tomato.jpg"}
    context = UserContext(crop="Tomato", growth_stage="Vegetative")

    plan = p.create_plan("REQ-TEST-1", user_input, image_meta, context)
    
    assert plan.request_id == "REQ-TEST-1"
    assert len(plan.tasks) >= 6
    
    task_types = [t.task_type for t in plan.tasks]
    assert TaskType.IMAGE_QUALITY in task_types
    assert TaskType.CROP_IDENTIFICATION in task_types
    assert TaskType.SYMPTOM_ANALYSIS in task_types
    assert TaskType.ADVISORY_RETRIEVAL in task_types
    assert TaskType.EVIDENCE_FUSION in task_types
    assert TaskType.VERIFICATION in task_types
    assert TaskType.RECOMMENDATION in task_types

def test_planner_handles_unseen_request():
    p = AgriculturalPlanner()
    user_input = UserInput(text="My chilli plant leaves are curling with pale patches", language="en")
    context = UserContext(crop="Chilli")

    plan = p.create_plan("REQ-UNSEEN", user_input, {}, context)
    assert len(plan.tasks) >= 5
    assert any(t.task_type == TaskType.ADVISORY_RETRIEVAL for t in plan.tasks)
