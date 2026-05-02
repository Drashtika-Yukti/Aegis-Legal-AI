import os
import uvicorn
import json
from fastapi import FastAPI, HTTPException, Depends, status, Request, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional

from core.config import settings
from core.security import create_access_token, verify_password, get_current_active_user, oauth2_scheme
from core.orchestrator import run_aegis_stream
from core.logger import get_logger
from core.rate_limit import limiter
from models.user import UserCreate, UserPublic, PasswordResetVerify, PasswordResetConfirm, Token

logger = get_logger("AegisAPI")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# 1. Professional CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Security Setup
class QueryRequest(BaseModel):
    query: str
    session_id: str = "default"

# 3. Global Error Handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global Crash: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Aegis has detected an anomaly in the legal grid.",
            "message": "Our engineers are stabilizing the core. Please stand by.",
            "error_type": "GRID_ANOMALY"
        }
    )

# 4. Authentication & Account Management (Question/DOB Based)
@app.post("/api/v1/auth/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # In production, check DB. Mocking admin for now.
    if form_data.username != "admin" or form_data.password != "aegis2024":
        throw_auth_error()
    access_token = create_access_token(subject=form_data.username)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/v1/auth/signup")
async def signup(user: UserCreate):
    logger.info(f"New Registration Attempt: {user.email}")
    # Logic to save to DB (Supabase/Postgres)
    return {"message": "Account created successfully. You can now log in."}

@app.post("/api/v1/auth/reset-password-verify")
async def reset_verify(data: PasswordResetVerify):
    logger.info(f"Password Reset Attempt for: {data.email}")
    # Logic: 
    # 1. Fetch user by email.
    # 2. If data.answer provided, check security answer.
    # 3. If data.dob provided, check DOB.
    # For now, we simulate a 'match' if the input isn't empty.
    if data.answer == "mock_answer" or data.dob == "2000-01-01":
        return {"status": "verified", "message": "Identity confirmed. Proceed to update password."}
    
    raise HTTPException(status_code=400, detail="Security verification failed.")

@app.post("/api/v1/auth/reset-password-confirm")
async def reset_confirm(data: PasswordResetConfirm):
    logger.info(f"Password Updated for: {data.email}")
    return {"message": "Password updated successfully."}

def throw_auth_error():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

# 5. Core AI & Document Endpoints
@app.post("/api/v1/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_active_user)
):
    logger.info(f"User {current_user['email']} uploading: {file.filename}")
    return {
        "filename": file.filename,
        "status": "Processing",
        "size": file.size,
        "document_id": "doc_" + str(os.urandom(4).hex())
    }

@app.get("/api/v1/documents")
async def list_documents(current_user: dict = Depends(get_current_active_user)):
    return [
        {"filename": "Merger Agreement v2.pdf", "status": "Analyzed", "size": "2.4 MB"},
        {"filename": "Risk Assessment.docx", "status": "Pending", "size": "1.1 MB"}
    ]

@app.post("/api/v1/chat")
async def chat(
    request: QueryRequest, 
    current_user: dict = Depends(get_current_active_user),
    _rate_limit = Depends(limiter.check_rate_limit)
):
    async def event_generator():
        async for event in run_aegis_stream(request.query, request.session_id):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/health")
async def health():
    return {"status": "healthy", "engine": "Aegis-v2"}

# 6. Static File Serving
portal_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "portal")
if os.path.exists(portal_path):
    app.mount("/portal", StaticFiles(directory=portal_path, html=True), name="portal")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
