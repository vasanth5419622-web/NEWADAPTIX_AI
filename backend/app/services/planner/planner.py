import uuid
from typing import Dict, Any, List, Optional
from app.schemas.shared import (
    ExecutionPlan, TaskItem, TaskType, UserInput, UserContext
)

class AgriculturalPlanner:
    """
    Decomposes incoming farmer queries and media into an explicit, adaptive execution plan.
    Dynamic and reusable for any crop, symptom, or advisory request.
    """
    def create_plan(
        self,
        request_id: str,
        user_input: UserInput,
        image_metadata: Dict[str, Any],
        context: UserContext
    ) -> ExecutionPlan:
        tasks: List[TaskItem] = []
        step_counter = 1
        has_image = bool(image_metadata.get("file_path"))
        has_text = bool(user_input.text or user_input.voice_transcript)
        crop_name = context.crop

        strategy_notes = []

        # 1. Quality Check Task (if image provided)
        if has_image:
            tasks.append(TaskItem(
                task_id=f"T-{request_id}-{step_counter}",
                task_type=TaskType.IMAGE_QUALITY,
                input_data={"image_path": image_metadata["file_path"]},
                expected_output="image_quality_passed_or_issues",
                priority=1,
                status="pending"
            ))
            step_counter += 1
            strategy_notes.append("Execute pre-flight image quality check.")

        # 2. Crop Identification Task
        # If crop is not specified by the farmer, or if image is provided, identify/verify crop
        tasks.append(TaskItem(
            task_id=f"T-{request_id}-{step_counter}",
            task_type=TaskType.CROP_IDENTIFICATION,
            input_data={
                "image_path": image_metadata.get("file_path"),
                "stated_crop": crop_name,
                "text": user_input.text or user_input.voice_transcript
            },
            expected_output="crop_name_and_identification_confidence",
            priority=2,
            status="pending"
        ))
        step_counter += 1
        strategy_notes.append("Identify/confirm crop type using visual features and context.")

        # 3. Symptom & Disease Analysis Task
        tasks.append(TaskItem(
            task_id=f"T-{request_id}-{step_counter}",
            task_type=TaskType.SYMPTOM_ANALYSIS,
            input_data={
                "image_path": image_metadata.get("file_path"),
                "user_description": user_input.text or user_input.voice_transcript,
                "growth_stage": context.growth_stage,
                "season": context.season,
                "location": context.location
            },
            expected_output="possible_conditions_symptoms_severity",
            priority=3,
            status="pending"
        ))
        step_counter += 1
        strategy_notes.append("Analyze visual symptoms, lesion patterns, and reported abnormalities.")

        # 4. Advisory Retrieval Task (RAG)
        tasks.append(TaskItem(
            task_id=f"T-{request_id}-{step_counter}",
            task_type=TaskType.ADVISORY_RETRIEVAL,
            input_data={
                "crop": crop_name,
                "query": user_input.text or user_input.voice_transcript or f"{crop_name} crop health symptoms",
                "growth_stage": context.growth_stage
            },
            expected_output="relevant_agricultural_bulletins_and_citations",
            priority=4,
            status="pending"
        ))
        step_counter += 1
        strategy_notes.append("Retrieve verified extension bulletins and agricultural advisories via vector search.")

        # 5. Multi-Evidence Fusion Task
        tasks.append(TaskItem(
            task_id=f"T-{request_id}-{step_counter}",
            task_type=TaskType.EVIDENCE_FUSION,
            input_data={"context": context.model_dump()},
            expected_output="synthesized_evidence_and_conflict_check",
            priority=5,
            status="pending"
        ))
        step_counter += 1
        strategy_notes.append("Cross-reference visual findings, RAG advisory guidelines, and environmental context.")

        # 6. Verification & Critic Task (Commercial Model B)
        tasks.append(TaskItem(
            task_id=f"T-{request_id}-{step_counter}",
            task_type=TaskType.VERIFICATION,
            input_data={},
            expected_output="independent_consistency_verification_and_critic_review",
            priority=6,
            status="pending"
        ))
        step_counter += 1
        strategy_notes.append("Conduct independent verification to prevent false diagnoses and hallucinations.")

        # 7. Recommendation Generation Task
        tasks.append(TaskItem(
            task_id=f"T-{request_id}-{step_counter}",
            task_type=TaskType.RECOMMENDATION,
            input_data={"language": user_input.language},
            expected_output="actionable_farmer_advice_with_safety_disclaimer",
            priority=7,
            status="pending"
        ))
        step_counter += 1
        strategy_notes.append("Format structured, non-prescriptive advisory with clear safety warnings.")

        return ExecutionPlan(
            request_id=request_id,
            tasks=tasks,
            strategy_rationale=" -> ".join(strategy_notes)
        )

planner = AgriculturalPlanner()
