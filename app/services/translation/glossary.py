import re
from typing import Dict, List

class Glossary:
    def __init__(self, en2ru: Dict[str, str] | None = None):
        self.en2ru = {k.lower(): v for k, v in (en2ru or {}).items()}

    def vocab_constraints(self) -> List[List[str]]:
        return [v.split() for v in self.en2ru.values()]

    def apply_post(self, text: str) -> str:
        # страховочная сетка: закрепляем перевод терминов
        for _, tgt in self.en2ru.items():
            text = re.sub(rf"\b{re.escape(tgt)}\b", tgt, text, flags=re.IGNORECASE)
        return text

DEFAULT_GLOSSARY = Glossary({
    "rank": "ранг",
    "kernel": "ядро",
    "manifold": "многообразие",
    "trace": "след",
    "eigenvalue": "собственное значение",
    "eigenvector": "собственный вектор",
    "feature map": "отображение признаков",
    "pose": "поза",
})
