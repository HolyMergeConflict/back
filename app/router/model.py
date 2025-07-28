from fastapi import APIRouter

from app.schemas.model_io import ModelInput, ModelOutput
from app.services.model_service import predict

router = APIRouter(prefix="/model", tags=["Model"])

@router.post('/predict', response_model=ModelOutput)
async def predict_view(input_data: ModelInput):
    label, confidence = predict(input_data.text)
    return ModelOutput(prediction=label, confidence=confidence)