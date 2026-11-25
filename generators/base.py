from abc import ABC, abstractmethod
from core.models import Task
import random

class BaseGenerator(ABC):
    @property
    @abstractmethod
    def category_id(self) ->str:
        pass
    
    @property
    @abstractmethod
    def name(self) ->str:
        pass
    
    @abstractmethod
    def generate (self) -> Task:
        pass

    def _gauss_int(
        self,
        min_val: int,
        max_val: int,
         mu: float | None = None,
        sigma: float | None = None,
    ) -> int:
        if mu is None:
            mu = (min_val + max_val) / 2
        if sigma is None:
            sigma = (max_val - min_val) / 6
            
        raw = random.gauss(mu, sigma)
        return max(min_val, min(max_val, round(raw)))
    
