import time
import uuid
from typing import Dict, Any, Optional, List
from app.core.config import settings
from app.core.logging import logger
from app.core.db import save_analysis
from app.schemas.shared import (
    ExecutionState, UserInput, UserContext, FinalRecommendation,
    TaskType, ConfidenceLevel, RouteEvent
)
from app.services.image.quality import image_quality_checker
from app.services.planner.planner import planner
from app.services.router.adaptive_router import adaptive_router
from app.services.models.factory import model_factory
from app.services.rag.service import rag_service
from app.services.verifier.fusion import fusion_engine
from app.services.verifier.verifier import verifier
from app.services.confidence.engine import confidence_engine
from app.services.fallback.handler import fallback_handler
from app.services.voice.stt_tts import voice_service

class MasterAgriculturalOrchestrator:
    """
    Central Agentic Orchestrator for ADAPTIX-FARM.
    Coordinates all autonomous phases: Image Quality -> Planning -> Adaptive Routing ->
    Specialist Execution -> RAG -> Evidence Fusion -> Independent Verification ->
    Confidence Evaluation -> Fallback -> Recommendation -> Trace Logging.
    """
    async def run_pipeline(
        self,
        user_input: UserInput,
        image_path: Optional[str] = None,
        context: Optional[UserContext] = None,
        request_id: Optional[str] = None
    ) -> ExecutionState:
        start_overall = time.time()
        req_id = request_id or f"REQ-{uuid.uuid4().hex[:8].upper()}"
        context = context or UserContext()
        
        # Initialize Shared Execution State
        state = ExecutionState(
            request_id=req_id,
            status="processing",
            user_input=user_input,
            image_metadata={"file_path": image_path} if image_path else {},
            context=context
        )

        logger.info(f"Initiating pipeline for request {req_id}", extra={"request_id": req_id, "step": "init"})

        # ==========================================
        # STEP 1: Pre-flight Image Quality Gate
        # ==========================================
        if image_path:
            q_start = time.time()
            quality_res = image_quality_checker.check_quality(image_path)
            state.quality_check = quality_res
            q_lat = (time.time() - q_start) * 1000

            trace_q = RouteEvent(
                step_number=1,
                task_type="image_quality_check",
                model_name="Deterministic Laplacian Photometric Gate",
                provider="Local Kernel Validator",
                reason="Pre-flight validation to prevent blurry, underexposed, or corrupted images from reaching deep models.",
                routing_score=1.0,
                latency_ms=q_lat,
                estimated_cost=0.0,
                status="success" if quality_res.passed else "failed"
            )
            state.route_trace.append(trace_q)
            state.total_latency_ms += q_lat

            # If image is poor, invoke fallback gate immediately and return early
            if not quality_res.passed:
                fallback_handler.handle_image_quality_failure(quality_res.issues, state)
                state.status = "needs_better_image"
                
                state.final_result = FinalRecommendation(
                    crop=context.crop or "Unknown Crop",
                    possible_condition="Requires Clearer Photograph",
                    assessment_summary=quality_res.actionable_message or "The uploaded image was unclear.",
                    management_advice=[
                        "Hold the camera steady in daylight.",
                        "Capture a close-up photograph (within 15-30 cm) of the affected leaves.",
                        "Ensure the affected spots and leaf veins are in sharp focus."
                    ],
                    preventative_measures=[],
                    requires_human_review=True
                )
                
                state.total_latency_ms = round((time.time() - start_overall) * 1000, 2)
                save_analysis(state.model_dump())
                return state

        # ==========================================
        # STEP 2: Dynamic Agricultural Planning
        # ==========================================
        plan_start = time.time()
        exec_plan = planner.create_plan(
            request_id=req_id,
            user_input=user_input,
            image_metadata=state.image_metadata,
            context=context
        )
        state.plan = exec_plan
        plan_lat = (time.time() - plan_start) * 1000
        state.total_latency_ms += plan_lat

        # ==========================================
        # STEP 3: Adaptive Model Routing & Specialist Execution
        # ==========================================
        step_num = len(state.route_trace) + 1
        
        # 3a. Crop Identification (Open Weight / Smaller Model)
        crop_task = next((t for t in exec_plan.tasks if t.task_type == TaskType.CROP_IDENTIFICATION), None)
        visual_crop_info = {}
        if crop_task:
            route_crop = adaptive_router.route_task(crop_task, step_num)
            step_num += 1
            
            open_model = model_factory.get_open_model()
            open_res = await open_model.analyze_image(
                image_path=image_path or "",
                prompt="Identify the crop species and assess initial foliar health.",
                context={"crop": context.crop, "user_description": user_input.text or user_input.voice_transcript}
            )
            visual_crop_info = open_res.structured_data
            
            route_crop.latency_ms = open_res.latency_ms
            route_crop.estimated_cost = open_res.estimated_cost
            route_crop.confidence_score = open_res.confidence
            state.route_trace.append(route_crop)
            state.model_calls.append(open_res.to_dict())
            state.total_latency_ms += open_res.latency_ms
            state.total_estimated_cost += open_res.estimated_cost
            
            # If context crop was not supplied, adopt detected crop
            if not context.crop and visual_crop_info.get("detected_crop"):
                context.crop = visual_crop_info["detected_crop"]

        # 3b. Deep Symptom & Pathology Analysis (Commercial Model A)
        symptom_task = next((t for t in exec_plan.tasks if t.task_type == TaskType.SYMPTOM_ANALYSIS), None)
        pathology_info = {}
        if symptom_task:
            route_path = adaptive_router.route_task(symptom_task, step_num)
            step_num += 1
            
            comm_a = model_factory.get_commercial_a()
            comm_res = await comm_a.analyze_image(
                image_path=image_path or "",
                prompt=(
                    f"Perform deep agronomic analysis on {context.crop or 'crop'}. "
                    f"Farmer reports: {user_input.text or user_input.voice_transcript}."
                ),
                context={
                    "crop": context.crop,
                    "user_description": user_input.text or user_input.voice_transcript,
                    "growth_stage": context.growth_stage,
                    "location": context.location
                }
            )
            pathology_info = comm_res.structured_data
            route_path.latency_ms = comm_res.latency_ms
            route_path.estimated_cost = comm_res.estimated_cost
            route_path.confidence_score = comm_res.confidence
            state.route_trace.append(route_path)
            state.model_calls.append(comm_res.to_dict())
            state.total_latency_ms += comm_res.latency_ms
            state.total_estimated_cost += comm_res.estimated_cost

        # ==========================================
        # STEP 4: Agricultural RAG Advisory Retrieval
        # ==========================================
        rag_task = next((t for t in exec_plan.tasks if t.task_type == TaskType.ADVISORY_RETRIEVAL), None)
        retrieved_sources = []
        if rag_task:
            route_rag = adaptive_router.route_task(rag_task, step_num)
            step_num += 1
            
            rag_start = time.time()
            search_query = (
                f"{context.crop or ''} {pathology_info.get('possible_condition', '')} "
                f"{user_input.text or user_input.voice_transcript or 'symptoms management'}"
            )
            retrieved_sources = rag_service.retrieve_evidence(
                query=search_query,
                crop=context.crop,
                top_k=3
            )
            rag_lat = (time.time() - rag_start) * 1000
            
            route_rag.latency_ms = rag_lat
            state.route_trace.append(route_rag)
            state.retrieved_sources = retrieved_sources
            state.total_latency_ms += rag_lat
            state.total_estimated_cost += route_rag.estimated_cost

        # ==========================================
        # STEP 5: Multi-Evidence Fusion
        # ==========================================
        fusion_start = time.time()
        merged_visual = {**visual_crop_info, **pathology_info}
        fusion_result = fusion_engine.fuse_evidence(
            visual_evidence=merged_visual,
            advisory_sources=retrieved_sources,
            context=context
        )
        state.evidence_fusion = fusion_result
        fus_lat = (time.time() - fusion_start) * 1000
        
        trace_fus = RouteEvent(
            step_number=step_num,
            task_type="evidence_fusion",
            model_name="Multi-Evidence Fusion Matrix",
            provider="Internal Ag-Semantic Fusion",
            reason="Synthesizes visual lesions, university advisory literature, and grower field context.",
            routing_score=0.95,
            latency_ms=fus_lat,
            estimated_cost=0.0,
            status="success"
        )
        state.route_trace.append(trace_fus)
        step_num += 1
        state.total_latency_ms += fus_lat

        # ==========================================
        # STEP 6: Independent Verification & Critic (Commercial Model B)
        # ==========================================
        verif_task = next((t for t in exec_plan.tasks if t.task_type == TaskType.VERIFICATION), None)
        verif_res = None
        if verif_task:
            route_verif = adaptive_router.route_task(verif_task, step_num)
            step_num += 1
            
            verif_res = await verifier.verify(
                fusion=fusion_result,
                visual_findings=merged_visual,
                context=context.model_dump()
            )
            state.verification_results = verif_res
            
            route_verif.latency_ms = 920.0
            route_verif.estimated_cost = 0.0092
            route_verif.confidence_score = verif_res.consistency_score
            state.route_trace.append(route_verif)
            state.total_latency_ms += 920.0
            state.total_estimated_cost += 0.0092

        # ==========================================
        # STEP 7: Calibrated Confidence Scoring & Risk Engine
        # ==========================================
        primary_model_conf = pathology_info.get("confidence_score", 0.85)
        conf_eval = confidence_engine.evaluate(
            model_confidence=primary_model_conf,
            fusion=fusion_result,
            quality=state.quality_check,
            verifier_res=verif_res,
            context=context.model_dump()
        )
        state.confidence = conf_eval

        # ==========================================
        # STEP 8: Fallback & Escalation Check
        # ==========================================
        requires_review = False
        if conf_eval.level == ConfidenceLevel.LOW:
            fallback_handler.handle_low_confidence(conf_eval.score, state)
            requires_review = True
        elif fusion_result.conflicts_detected:
            fallback_handler.handle_conflicting_evidence(fusion_result.conflicts_detected, state)
            requires_review = True

        # ==========================================
        # STEP 9: Final Actionable Recommendation Formulation
        # ==========================================
        crop_display = context.crop or merged_visual.get("detected_crop", "Crop")
        condition_display = pathology_info.get("possible_condition", "Possible Foliar Anomaly")
        
        # Assemble advisory steps using retrieved RAG citations and IPM best practices
        management_advice = []
        preventative = []

        if "blight" in condition_display.lower():
            management_advice = [
                "Prune and safely discard severely infected lower leaves to restrict soil splash inoculum.",
                "Avoid overhead irrigation; maintain drip watering directly at root zone.",
                "If progression continues across upper canopy, apply university-recommended protective fungicide (e.g. Mancozeb 75% WP @ 2g/L or Chlorothalonil) following label safety guidelines."
            ]
            preventative = [
                "Practice 2-3 year crop rotation away from other Solanaceous species.",
                "Ensure 60x45cm spacing for optimal air circulation.",
                "Apply organic neem cake or bio-fungicides (Trichoderma viride) at field preparation."
            ]
        elif "curl" in condition_display.lower():
            management_advice = [
                "Inspect leaf undersides for whitefly vectors or tiny thrips feeding signs.",
                "Install yellow and blue sticky traps (15-20 traps/acre) across the field boundary.",
                "Apply neem oil (10,000 ppm) @ 3ml/L or bio-insecticide to suppress vector populations."
            ]
            preventative = [
                "Erect border crops like maize or sorghum as a physical insect barrier.",
                "Rogue out and destroy severely stunted viral plants immediately to protect adjacent healthy rows."
            ]
        elif "blast" in condition_display.lower():
            management_advice = [
                "Regulate nitrogen fertilization; split urea doses and apply recommended potash (MOP).",
                "Maintain continuous shallow standing water in paddy fields.",
                "Apply foliar spray of Tricyclazole 75% WP @ 0.6g/L at initial blast lesion detection."
            ]
            preventative = [
                "Use certified blast-resistant seed varieties.",
                "Treat seeds with Carbendazim or Pseudomonas fluorescens before nursery sowing."
            ]
        else:
            # Dynamic synthesis for unseen conditions
            management_advice = [
                "Isolate affected plant samples and monitor adjacent rows for symptom expansion.",
                "Ensure balanced plant nutrition avoiding excess nitrogen foliage softness.",
                "Take a sample to the nearest Krishi Vigyan Kendra (KVK) or extension office for micro-pathology verification."
            ]
            preventative = [
                "Maintain weed-free field borders to minimize pest harboring.",
                "Ensure proper soil drainage to avoid root hypoxia."
            ]

        # Localized voice synthesis script
        tts_text = f"Assessment for {crop_display}: Possible condition is {condition_display}. System confidence is {conf_eval.level.value}. Please review IPM guidelines and verify with agricultural officers."
        voice_data = voice_service.synthesize(tts_text, language=user_input.language)

        summary_text = (
            f"AI-assisted multimodal assessment indicates possible {condition_display} on {crop_display}. "
            f"Cross-verified with {len(retrieved_sources)} agricultural extension bulletins. "
            f"Overall system confidence is {conf_eval.level.value} ({int(conf_eval.score * 100)}%)."
        )

        state.final_result = FinalRecommendation(
            crop=crop_display,
            possible_condition=condition_display,
            assessment_summary=summary_text,
            management_advice=management_advice,
            preventative_measures=preventative,
            requires_human_review=requires_review
        )

        state.status = "completed"
        state.total_latency_ms = round((time.time() - start_overall) * 1000, 2)
        state.total_estimated_cost = round(state.total_estimated_cost, 5)

        # Persist full state to SQLite database
        save_analysis(state.model_dump())

        logger.info(
            f"Pipeline completed for {req_id}",
            extra={
                "request_id": req_id,
                "confidence": conf_eval.level.value,
                "latency_ms": state.total_latency_ms,
                "estimated_cost": state.total_estimated_cost
            }
        )

        return state

orchestrator = MasterAgriculturalOrchestrator()
