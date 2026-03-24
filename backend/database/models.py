from dataclasses import dataclass
from typing import Optional


@dataclass
class PredictionRecord:
	id: Optional[int]
	dataset: str
	engine_id: Optional[int]
	predicted_rul: float
	status: str
	features_json: Optional[str]
	source: str
	created_at: Optional[str] = None
