import os
from typing import Optional
from .latex_masker import LatexMasker
from .glossary import Glossary, DEFAULT_GLOSSARY
from .providers.base import BaseMTProvider
from .providers.ctranslate2_marian import MarianCTranslate2Provider

try:
    # необязательная зависимость для простого детекта языка
    from langdetect import detect
except Exception:  # если не установлено — считаем английским по эвристике
    detect = None

class TranslationService:
    def __init__(
        self,
        provider: Optional[BaseMTProvider] = None,
        glossary: Optional[Glossary] = DEFAULT_GLOSSARY,
    ):
        self.masker = LatexMasker()
        self.glossary = glossary

        if provider is None:
            model_dir = os.getenv("TRANSLATION_MODEL_DIR", "/models/opus-mt-en-ru-ctranslate2")
            spm_path  = os.getenv("TRANSLATION_SPM_PATH",  "/models/opus-mt-en-ru-ctranslate2/spm.model")
            provider = MarianCTranslate2Provider(model_dir, spm_path, glossary=self.glossary)
        self.provider = provider

    @staticmethod
    def _looks_english(text: str) -> bool:
        if detect:
            try:
                return detect(text) == "en"
            except Exception:
                pass
        # fallback: есть ли латиница + мало кириллицы
        latin = sum(c.isalpha() and 'A' <= c <= 'Z' or 'a' <= c <= 'z' for c in text)
        cyr   = sum('А' <= c <= 'я' or c == 'ё' or c == 'Ё' for c in text)
        return latin > cyr

    async def translate_text(self, text: str, target_lang: str = "ru") -> str:
        masked, repl = self.masker.mask(text)
        translated = (await self.provider.translate([masked]))[0]
        out = self.masker.unmask(translated, repl)
        if self.glossary:
            out = self.glossary.apply_post(out)
        return out

    async def translate_if_english(self, text: str) -> str:
        return await self.translate_text(text) if self._looks_english(text) else text
