from pydantic import BaseModel
from typing import Dict, Any, Optional

class TranscriptionResponse(BaseModel):
    transcript: str
    diagnosis: str
    treatment: str
    entities: Dict[str, Any] = {}
    
class HealthResponse(BaseModel):
    status: str
    transcriber_ready: bool
    ner_ready: bool