"""
ProduGen - FastAPI Application
Main server that serves the API and static frontend.
"""

import os
import uuid
import json
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.config import Config
from backend import database as db


# =============================================================================
# App Setup
# =============================================================================

app = FastAPI(
    title="ProduGen",
    description="AI Product Image Generator for Small Businesses",
    version="0.1.0",
)

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active chat sessions in memory (chat objects can't be serialized)
active_chats: dict = {}


# =============================================================================
# Request/Response Models
# =============================================================================

class ChatMessage(BaseModel):
    session_id: str
    message: str


class GenerateRequest(BaseModel):
    session_id: str
    num_images: int = 1
    platform: str = "instagram_post"


# =============================================================================
# API Routes
# =============================================================================

@app.get("/api/health")
async def health_check():
    """Check server status and API key configuration."""
    status = Config.validate()
    return {
        "status": "running",
        "app": "ProduGen",
        "version": "0.1.0",
        "api_keys": status,
    }


@app.post("/api/chat/start")
async def start_chat():
    """Start a new AI questionnaire session."""
    status = Config.validate()
    if not status["gemini"]:
        raise HTTPException(
            status_code=503,
            detail="Gemini API key not configured. Add it to your .env file."
        )

    try:
        from backend.ai_questionnaire import AIQuestionnaire

        questionnaire = AIQuestionnaire()
        session_data = questionnaire.start_session()

        # Create a database session
        session_id = db.create_session()

        # Store the chat object in memory
        active_chats[session_id] = {
            "questionnaire": questionnaire,
            "session": session_data,
        }

        # Save chat history to DB
        db.update_session_chat(session_id, session_data["history"])

        return {
            "session_id": session_id,
            "message": session_data["message"],
            "is_complete": False,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/message")
async def send_chat_message(chat_msg: ChatMessage):
    """Send a message to the AI questionnaire."""
    session_id = chat_msg.session_id

    if session_id not in active_chats:
        raise HTTPException(
            status_code=404,
            detail="Session not found. Start a new chat first."
        )

    try:
        chat_data = active_chats[session_id]
        questionnaire = chat_data["questionnaire"]
        session = chat_data["session"]

        # Send message and get response
        updated_session = questionnaire.send_message(session, chat_msg.message)
        active_chats[session_id]["session"] = updated_session

        # Save to database
        db.update_session_chat(session_id, updated_session["history"])

        if updated_session["is_complete"] and updated_session["brief"]:
            db.update_session_brief(session_id, updated_session["brief"])

        return {
            "session_id": session_id,
            "message": updated_session["message"],
            "is_complete": updated_session["is_complete"],
            "brief": updated_session["brief"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload")
async def upload_product_image(session_id: str, file: UploadFile = File(...)):
    """Upload a product image for a session."""
    # Validate session exists
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}"
        )

    try:
        # Save the uploaded file
        file_ext = os.path.splitext(file.filename)[1] or ".png"
        saved_filename = f"{session_id}_product{file_ext}"
        save_path = os.path.join(Config.UPLOAD_DIR, saved_filename)

        with open(save_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Update session with image path
        db.update_session_image(session_id, save_path)

        return {
            "session_id": session_id,
            "filename": saved_filename,
            "message": "Image uploaded successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate")
async def generate_images(req: GenerateRequest):
    """Generate product images using AI."""
    status = Config.validate()
    if not status["replicate"]:
        raise HTTPException(
            status_code=503,
            detail="Replicate API token not configured. Add it to your .env file."
        )

    # Get session
    session = db.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session.get("brief"):
        raise HTTPException(
            status_code=400,
            detail="Questionnaire not completed. Finish the chat first."
        )

    try:
        from backend.image_generator import ImageGenerator

        generator = ImageGenerator()

        # Clamp num_images to valid range
        num_images = max(1, min(req.num_images, 5))

        print(f"\n🎨 Starting image generation for session {req.session_id}")
        print(f"   Generating {num_images} images for {req.platform}")

        results = generator.generate_images(
            brief=session["brief"],
            num_images=num_images,
            platform=req.platform,
            session_id=req.session_id,
        )

        # Save results to database
        for result in results:
            if result.get("path"):
                db.save_generated_image(req.session_id, result)

        db.update_session_status(req.session_id, "completed")

        return {
            "session_id": req.session_id,
            "images": results,
            "count": len([r for r in results if r.get("path")]),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions")
async def list_sessions():
    """List all sessions."""
    sessions = db.list_sessions()
    return {"sessions": sessions}


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get a specific session with its generated images."""
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    images = db.get_session_images(session_id)
    session["images"] = images
    return session


@app.get("/api/images/{session_id}")
async def get_session_images(session_id: str):
    """Get all generated images for a session."""
    images = db.get_session_images(session_id)
    return {"session_id": session_id, "images": images}


@app.get("/api/images/file/{session_id}/{filename}")
async def serve_image(session_id: str, filename: str):
    """Serve a generated image file."""
    filepath = os.path.join(Config.OUTPUT_DIR, session_id, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(filepath, media_type="image/png")


@app.get("/api/uploads/{filename}")
async def serve_upload(filename: str):
    """Serve an uploaded image file."""
    filepath = os.path.join(Config.UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Upload not found")
    return FileResponse(filepath)


# =============================================================================
# Static Frontend
# =============================================================================

# Serve frontend files
frontend_dir = os.path.join(Config.BASE_DIR, "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/")
async def serve_frontend():
    """Serve the main frontend page."""
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "ProduGen API is running. Frontend not found at /frontend/index.html"}
