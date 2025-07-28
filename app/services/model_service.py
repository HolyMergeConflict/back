import pickle
from pathlib import Path

# MODEL_PATH = Path(__file__).parent / "models" / "model.pth"

#with open(MODEL_PATH, "rb") as f:
#    model = pickle.load(f)

def predict(text: str) -> tuple[str, float]:
    #prediction = model.predict([text])[0]
    #proba = max(model.predict_proba([text])[0])
    return '42', 1228.1337