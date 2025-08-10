from typing import List, Optional
import ctranslate2
from sentencepiece import SentencePieceProcessor
from .base import BaseMTProvider
from ..glossary import Glossary

class MarianCTranslate2Provider(BaseMTProvider):
    def __init__(
        self,
        model_dir: str,
        spm_path: str,
        glossary: Optional[Glossary] = None,
        beam_size: int = 4,
    ):
        self.translator = ctranslate2.Translator(model_dir, inter_threads=1, intra_threads=0)
        self.spm = SentencePieceProcessor(model_file=spm_path)
        self.glossary = glossary
        self.beam_size = beam_size

    def _encode(self, s: str) -> List[str]:
        return self.spm.encode(s, out_type=str)

    def _decode(self, toks: List[str]) -> str:
        return self.spm.decode(toks)

    async def translate(self, batch: List[str]) -> List[str]:
        src_tokens = [self._encode(t) for t in batch]
        vocab = self.glossary.vocab_constraints() if self.glossary else None

        results = self.translator.translate_batch(
            src_tokens,
            beam_size=self.beam_size,
            num_hypotheses=1,
            max_decoding_length=2048,
            repetition_penalty=1.05,
            disable_unk=True,
            vocabulary=vocab,
        )
        return [self._decode(r.hypotheses[0]) for r in results]
