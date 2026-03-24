import pandas as pd
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

from database.crud import insert_prediction
from database.db import init_db

# Load prediction file
df = pd.read_csv(os.path.join(ROOT_DIR, "notebooks", "predictions_fd001.csv"))

# Convert RUL to health status
def get_status(rul):
    if rul > 80:
        return "Healthy"
    elif rul > 30:
        return "At Risk"
    else:
        return "Critical"

df["status"] = df["predicted_rul"].apply(get_status)

init_db()

# Insert rows into database
for _, row in df.iterrows():
    insert_prediction(
        dataset="fd001",
        engine_id=int(row.engine_id),
        predicted_rul=float(row.predicted_rul),
        status=row.status,
        source="csv_import",
    )

print("Predictions inserted successfully!")