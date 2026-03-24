from pydantic import BaseModel
from typing import List


class SensorInput(BaseModel):
    dataset: str
    features: List[float]


    def normalized_dataset(self):
        return self.dataset.lower().strip()


class BatchInput(BaseModel):
    dataset: str
    batch: List[List[float]]


    def normalized_dataset(self):
        return self.dataset.lower().strip()