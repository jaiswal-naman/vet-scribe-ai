import asyncio
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import json
import tempfile
import logging
from pathlib import Path
from typing import Dict, Optional, List
from pydantic import BaseModel
import uuid
from datetime import datetime

from .transcription import VoskTranscriber
from .ner_processor import BioBERTProcessor
from .models import TranscriptionResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Vet Voice Transcription API",
    description="AI-powered veterinary voice transcription with medical entity extraction",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend-domain.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processors
transcriber = None
ner_processor = None

# Global progress tracking
task_progress: Dict[str, Dict] = {}

# Add a new response model for task-based transcription
class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

class ProgressUpdate(BaseModel):
    task_id: str
    stage: str
    progress: int
    message: str
    timestamp: str
    details: Optional[Dict] = None

@app.on_event("startup")
async def startup_event():
    global transcriber, ner_processor
    logger.info("Initializing transcription and NER processors...")
    
    try:
        transcriber = VoskTranscriber()
        ner_processor = BioBERTProcessor()
        logger.info("Processors initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize processors: {str(e)}")
        raise

@app.get("/")
async def root():
    return {"message": "Vet Voice Transcription API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "transcriber_ready": transcriber is not None and transcriber.model_loaded,
        "ner_ready": ner_processor is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/progress/{task_id}")
async def get_progress(task_id: str):
    """Get progress for a specific task"""
    if task_id not in task_progress:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task_progress[task_id]

@app.get("/test")
async def test_endpoint():
    """Test endpoint"""
    return {"message": "Backend is working!"}

def update_progress(task_id: str, stage: str, progress: int, message: str, details: Optional[Dict] = None):
    """Update progress for a specific task"""
    if task_id not in task_progress:
        task_progress[task_id] = {
            "stages": [],
            "current_stage": stage,
            "overall_progress": progress,
            "status": "processing",
            "start_time": datetime.now().isoformat(),
            "last_update": datetime.now().isoformat()
        }
    
    task_progress[task_id]["stages"].append({
        "stage": stage,
        "progress": progress,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "details": details or {}
    })
    
    task_progress[task_id]["current_stage"] = stage
    task_progress[task_id]["overall_progress"] = progress
    task_progress[task_id]["last_update"] = datetime.now().isoformat()
    
    logger.info(f"Task {task_id}: {stage} - {progress}% - {message}")

async def process_transcription_task(task_id: str, file_path: str):
    """Background task to process transcription with detailed progress tracking"""
    try:
        # Stage 1: File validation and preparation
        update_progress(task_id, "file_preparation", 10, "Validating uploaded audio file")
        await asyncio.sleep(0.5)  # Simulate processing time
        
        if not os.path.exists(file_path):
            update_progress(task_id, "error", 0, "Audio file not found")
            return
        
        file_size = os.path.getsize(file_path)
        update_progress(task_id, "file_preparation", 20, f"Audio file validated ({file_size} bytes)")
        
        # Stage 2: Audio conversion
        update_progress(task_id, "audio_conversion", 30, "Converting audio to WAV format")
        await asyncio.sleep(0.5)
        
        try:
            import librosa
            import soundfile as sf
            
            # Detect the actual file format and handle conversion properly
            update_progress(task_id, "audio_conversion", 35, "Detecting audio format and loading audio")
            
            # Verify file exists and has content
            if not os.path.exists(file_path):
                error_msg = f"Audio file not found: {file_path}"
                logger.error(f"File not found for task {task_id}: {error_msg}")
                update_progress(task_id, "error", 0, error_msg)
                return
            
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                error_msg = "Audio file is empty"
                logger.error(f"Empty file for task {task_id}: {error_msg}")
                update_progress(task_id, "error", 0, error_msg)
                return
            
            logger.info(f"File exists: {file_path}, size: {file_size} bytes")
            
            # Load audio with librosa (it can handle multiple formats)
            try:
                logger.info(f"Attempting to load audio file: {file_path}")
                audio_data, sample_rate = librosa.load(file_path, sr=16000, mono=True)
                update_progress(task_id, "audio_conversion", 40, f"Audio loaded: {sample_rate}Hz, {len(audio_data)/sample_rate:.2f}s")
            except Exception as load_error:
                error_msg = f"Failed to load audio file: {str(load_error)}"
                logger.error(f"Audio loading error for task {task_id}: {error_msg}")
                update_progress(task_id, "error", 0, error_msg)
                return
            
            # Save as WAV file for Vosk
            converted_path = file_path.replace('.wav', '_converted.wav')
            # Handle different file extensions properly
            if file_path.endswith('.webm'):
                converted_path = file_path.replace('.webm', '_converted.wav')
            elif file_path.endswith('.mp3'):
                converted_path = file_path.replace('.mp3', '_converted.wav')
            elif file_path.endswith('.m4a'):
                converted_path = file_path.replace('.m4a', '_converted.wav')
            elif file_path.endswith('.ogg'):
                converted_path = file_path.replace('.ogg', '_converted.wav')
            
            try:
                sf.write(converted_path, audio_data, sample_rate, subtype='PCM_16')
                update_progress(task_id, "audio_conversion", 50, "Audio converted successfully")
                update_progress(task_id, "audio_conversion", 60, f"Sample rate: {sample_rate}Hz, Duration: {len(audio_data)/sample_rate:.2f}s")
            except Exception as write_error:
                error_msg = f"Failed to save converted audio: {str(write_error)}"
                logger.error(f"Audio write error for task {task_id}: {error_msg}")
                update_progress(task_id, "error", 0, error_msg)
                return
            
        except Exception as e:
            error_msg = f"Audio conversion failed: {str(e)}"
            logger.error(f"Audio conversion error for task {task_id}: {error_msg}")
            update_progress(task_id, "error", 0, error_msg)
            return
        
        # Stage 3: Vosk model loading check
        update_progress(task_id, "model_loading", 70, "Checking Vosk transcription model")
        await asyncio.sleep(0.5)
        
        if not transcriber.model_loaded:
            update_progress(task_id, "error", 0, "Vosk model not loaded")
            return
        
        update_progress(task_id, "model_loading", 80, "Vosk model ready for transcription")
        
        # Stage 4: Transcription
        update_progress(task_id, "transcription", 85, "Starting speech-to-text transcription")
        await asyncio.sleep(0.5)
        
        try:
            # Use the converted WAV file for transcription
            transcript = transcriber.transcribe(converted_path)
            if not transcript or transcript.strip() == "":
                update_progress(task_id, "error", 0, "Transcription failed - no speech detected")
                return
            
            update_progress(task_id, "transcription", 90, f"Transcription completed: {len(transcript)} characters")
            update_progress(task_id, "transcription", 95, f"Transcript preview: {transcript[:100]}...")
            
        except Exception as e:
            error_msg = f"Transcription failed: {str(e)}"
            logger.error(f"Transcription error for task {task_id}: {error_msg}")
            update_progress(task_id, "error", 0, error_msg)
            return
        
        # Stage 5: NER processing
        update_progress(task_id, "ner_processing", 96, "Extracting medical entities")
        await asyncio.sleep(0.5)
        
        try:
            entities = ner_processor.extract_entities(transcript)
            update_progress(task_id, "ner_processing", 98, f"Found {len(entities)} medical entities")
            
        except Exception as e:
            update_progress(task_id, "error", 0, f"NER processing failed: {str(e)}")
            return
        
        # Stage 6: Final processing
        update_progress(task_id, "final_processing", 99, "Generating final results")
        await asyncio.sleep(0.5)
        
        # Generate diagnosis and treatment suggestions
        diagnosis = "Based on the transcription, please consult with a veterinarian for proper diagnosis."
        treatment = "Treatment recommendations should be provided by a qualified veterinarian."
        
        # Store final results
        task_progress[task_id]["results"] = {
            "transcript": transcript,
            "diagnosis": diagnosis,
            "treatment": treatment,
            "entities": entities
        }
        
        update_progress(task_id, "completed", 100, "Processing completed successfully")
        task_progress[task_id]["status"] = "completed"
        
        # Cleanup temporary files
        try:
            os.remove(file_path)
            if os.path.exists(converted_path):
                os.remove(converted_path)
        except:
            pass
            
    except Exception as e:
        logger.error(f"Task {task_id} failed: {str(e)}")
        update_progress(task_id, "error", 0, f"Processing failed: {str(e)}")
        task_progress[task_id]["status"] = "error"

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    """
    Transcribe audio file and extract medical entities
    """
    if not file.filename.lower().endswith((
        '.wav', '.mp3', '.m4a', '.ogg', '.webm')):
        raise HTTPException(status_code=400, detail="Unsupported audio format")
    
    try:
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Determine the correct file extension from the uploaded file
        original_filename = file.filename.lower()
        if original_filename.endswith('.webm'):
            file_extension = '.webm'
        elif original_filename.endswith('.mp3'):
            file_extension = '.mp3'
        elif original_filename.endswith('.m4a'):
            file_extension = '.m4a'
        elif original_filename.endswith('.ogg'):
            file_extension = '.ogg'
        else:
            file_extension = '.wav'  # Default fallback
        
        # Save uploaded file temporarily with correct extension
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        logger.info(f"Starting transcription task {task_id} for file: {file.filename} (saved as {temp_file_path})")
        
        # Initialize progress tracking
        update_progress(task_id, "started", 0, f"Task started for file: {file.filename}")
        
        # Add background task
        background_tasks.add_task(process_transcription_task, task_id, temp_file_path)
        
        return TaskResponse(
            task_id=task_id,
            status="started",
            message="Transcription task started"
        )
        
    except Exception as e:
        logger.error(f"Error starting transcription: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start transcription: {str(e)}")

@app.get("/results/{task_id}")
async def get_results(task_id: str):
    """Get final results for a completed task"""
    if task_id not in task_progress:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_data = task_progress[task_id]
    
    if task_data["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed yet")
    
    results = task_data.get("results", {})
    return TranscriptionResponse(
        transcript=results.get("transcript", ""),
        diagnosis=results.get("diagnosis", ""),
        treatment=results.get("treatment", ""),
        entities=results.get("entities", [])
    )

@app.get("/tasks")
async def list_tasks():
    """List all tasks and their status"""
    return {
        "tasks": [
            {
                "task_id": task_id,
                "status": data["status"],
                "current_stage": data.get("current_stage", ""),
                "progress": data.get("overall_progress", 0),
                "start_time": data.get("start_time", ""),
                "last_update": data.get("last_update", "")
            }
            for task_id, data in task_progress.items()
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    