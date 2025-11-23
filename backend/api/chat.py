from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from ..services.freecad_service import FreeCADService
from src.agent.generative_design import GenerativeDesignCoordinator
from src.agent.vlm_validator import VLMValidator

router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    enable_validation: bool = False  # Optional validation flag
    model: Optional[str] = None  # Optional model override for code generation
    vlm_model: Optional[str] = None  # Optional model override for VLM validation
    history: Optional[List[ChatMessage]] = None
    context: Optional[Dict[str, Any]] = None  # last xml/model/png/validation

class ChatResponse(BaseModel):
    message: str
    model_url: Optional[str] = None
    xml_url: Optional[str] = None
    xml_content: Optional[str] = None
    png_url: Optional[str] = None
    validation: Optional[dict] = None
    builder_code: Optional[str] = None
    xml_validation: Optional[dict] = None
    agent_trace: Optional[list] = None
    debug_info: Optional[dict] = None

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        pipeline = GenerativeDesignCoordinator(model=request.model or "gpt-4o")
        generation_result = pipeline.run(
            user_prompt=request.message,
            history=request.history,
            context=request.context,
        )

        if not generation_result.get("success"):
            return ChatResponse(
                message=f"Failed to generate OCX via builder: {generation_result.get('error')}",
                debug_info={"agent_trace": generation_result.get("attempts")},
            )

        xml_content = generation_result["xml_content"]
        builder_code = generation_result.get("code")
        
        # 2. Process with FreeCAD (optionally generate PNG for validation)
        generate_png = request.enable_validation
        result = FreeCADService.process_ocx(xml_content, generate_png=generate_png)
        
        if result["success"]:
            response_data = {
                "message": result.get("message", "Generated 3D model"),
                "model_url": result.get("model_url"),
                "xml_url": result.get("xml_url"),
                "xml_content": result.get("xml_content"),
                "png_url": result.get("png_url"),
                "builder_code": builder_code,
                "xml_validation": generation_result.get("xml_validation"),
                "agent_trace": generation_result.get("attempts"),
                "debug_info": result.get("debug_info"),
            }
            
            # 3. Validate with VLM if requested and PNG is available
            if request.enable_validation and result.get("png_path"):
                try:
                    # VLM 모델 지정 (요청에서 지정하거나 환경 변수 사용)
                    vlm_model = request.vlm_model
                    validator = VLMValidator(model=vlm_model)
                    validation_result = validator.validate(
                        user_request=request.message,
                        image_path=result["png_path"],
                        xml_content=xml_content
                    )
                    response_data["validation"] = validation_result
                    
                    # Update message based on validation
                    if validation_result.get("success") and validation_result.get("matches_request") is False:
                        response_data["message"] = "Generated 3D model (validation found issues)"
                        
                except Exception as e:
                    response_data["validation"] = {
                        "success": False,
                        "error": f"Validation failed: {str(e)}"
                    }
            
            return ChatResponse(**response_data)
        else:
            return ChatResponse(
                message=f"Failed to generate 3D model: {result.get('error', 'Unknown error')}",
                xml_content=xml_content,
                model_url=None,
                xml_url=result.get("xml_url"),
                debug_info={
                    "stdout": result.get("stdout"),
                    "stderr": result.get("stderr")
                }
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
