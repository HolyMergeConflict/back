import re
from typing import Dict, Tuple

class LatexMasker:
    LATEX_PATTERNS = [
        (r"\$\$.*?\$\$", re.DOTALL),
        (r"(?<!\$)\$(?!\$).*?(?<!\$)\$(?!\$)", re.DOTALL),
        (r"\\\[.*?\\\]", re.DOTALL),
        (r"\\\(.*?\\\)", re.DOTALL),
        (r"\\begin\{[a-zA-Z*]+\}.*?\\end\{\w+\}", re.DOTALL),
    ]
    CODE_PATTERNS = [
        (r"```.*?```", re.DOTALL),
        (r"`[^`]+`", 0),
    ]

    def mask(self, text: str) -> Tuple[str, Dict[str, str]]:
        repl: Dict[str, str] = {}
        i = 0

        def _sub(pattern, flags):
            nonlocal text, i
            def _r(m):
                nonlocal i
                key = f"⟪MASK_{i}⟫"
                repl[key] = m.group(0)
                i += 1
                return key
            text = re.sub(pattern, _r, text, flags=flags)

        for p, f in self.CODE_PATTERNS + self.LATEX_PATTERNS:
            _sub(p, f)
        return text, repl

    def unmask(self, text: str, repl: Dict[str, str]) -> str:
        for k in sorted(repl.keys(), key=len, reverse=True):
            text = text.replace(k, repl[k])
        return text
