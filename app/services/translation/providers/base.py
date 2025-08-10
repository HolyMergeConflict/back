from typing import List
import abc

class BaseMTProvider(abc.ABC):
    @abc.abstractmethod
    async def translate(self, batch: List[str]) -> List[str]:
        ...
