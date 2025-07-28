from pydantic import BaseModel

class ModelInput(BaseModel):
    text: str

class ModelOutput(BaseModel):
    prediction: str
    confidence: float