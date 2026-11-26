
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

from app.core.ai_agents import get_response_from_ai_agents
from app.config.settings import settings
from app.common.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="Multi AI Agent API",
    description="Backend API for Multi AI Agent LLMOps",
    version="1.0.0"
)


# Request schema
class RequestState(BaseModel):
    model_name: str
    system_prompt: str
    messages: List[str]
    allow_search: bool = False


# Health check endpoint
@app.get("/")
def home():
    return {
        "status": "running",
        "message": "Multi AI Agent Backend is working"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# Chat endpoint
@app.post("/chat")
def chat_endpoint(request: RequestState):

    try:
        logger.info(
            f"Received request for model: {request.model_name}"
        )

        # Validate model
        if request.model_name not in settings.ALLOWED_MODEL_NAMES:
            logger.warning(
                f"Invalid model requested: {request.model_name}"
            )

            raise HTTPException(
                status_code=400,
                detail=f"Invalid model name: {request.model_name}"
            )

        # Validate messages
        if not request.messages or not any(
            message.strip() for message in request.messages
        ):
            raise HTTPException(
                status_code=400,
                detail="Please provide a valid user query"
            )

        # Call AI agent
        response = get_response_from_ai_agents(
            llm_id=request.model_name,
            query=request.messages,
            allow_search=request.allow_search,
            system_prompt=request.system_prompt
        )

        logger.info(
            f"Successfully generated response using {request.model_name}"
        )

        return {
            "status": "success",
            "model": request.model_name,
            "response": response
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.exception(
            "Error occurred during AI response generation"
        )

        raise HTTPException(
            status_code=500,
            detail=f"AI Agent Error: {str(e)}"
        )
