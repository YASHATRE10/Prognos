import os
from io import BytesIO

import pandas as pd


def _cmapss_columns():
	cols = ["engine_id", "cycle"]
	cols.extend([f"op_setting_{i}" for i in range(1, 4)])
	cols.extend([f"sensor_{i}" for i in range(1, 22)])
	return cols


def load_cmapss_dataframe(file_path):
	if not os.path.exists(file_path):
		raise FileNotFoundError(f"Dataset file not found: {file_path}")

	df = pd.read_csv(file_path, sep=r"\s+", header=None, engine="python")
	df = df.dropna(axis=1, how="all")

	expected_cols = len(_cmapss_columns())
	if df.shape[1] < expected_cols:
		raise ValueError(
			f"Expected at least {expected_cols} columns, found {df.shape[1]} in {file_path}"
		)

	df = df.iloc[:, :expected_cols]
	df.columns = _cmapss_columns()
	return df


def get_latest_engine_features(file_path):
	df = load_cmapss_dataframe(file_path)
	latest_rows = df.sort_values(["engine_id", "cycle"]).groupby("engine_id", as_index=False).tail(1)

	feature_columns = [f"op_setting_{i}" for i in range(1, 4)] + [f"sensor_{i}" for i in range(1, 22)]

	rows = []
	for _, row in latest_rows.iterrows():
		rows.append(
			{
				"engine_id": int(row["engine_id"]),
				"features": [float(row[col]) for col in feature_columns],
			}
		)

	return rows


def get_csv_feature_rows(file_bytes):
	df = pd.read_csv(BytesIO(file_bytes))

	if df.empty:
		raise ValueError("CSV file is empty")

	preferred_columns = [f"op_setting_{i}" for i in range(1, 4)] + [f"sensor_{i}" for i in range(1, 22)]
	short_columns = [f"op{i}" for i in range(1, 4)] + [f"s{i}" for i in range(1, 22)]

	if all(col in df.columns for col in preferred_columns):
		feature_columns = preferred_columns
	elif all(col in df.columns for col in short_columns):
		feature_columns = short_columns
	elif df.shape[1] >= 24:
		feature_columns = list(df.columns[:24])
	else:
		raise ValueError(
			"CSV must contain either op_setting_1..3 + sensor_1..21, op1..3 + s1..21, or at least 24 columns"
		)

	rows = []
	for _, row in df.iterrows():
		features = [float(row[col]) for col in feature_columns]
		if len(features) != 24:
			raise ValueError("Each CSV row must have exactly 24 feature values")

		engine_id = None
		if "engine_id" in df.columns and pd.notna(row["engine_id"]):
			engine_id = int(row["engine_id"])

		rows.append({"engine_id": engine_id, "features": features})

	return rows
