# PrognosAI Full Explanation (Simple Language)

This document explains everything done in this project, from scratch, in easy language.

## 1) What this project is

This is a predictive maintenance backend.
It predicts Remaining Useful Life (RUL) of machines using sensor values.

Main goal:
- Give a RUL number
- Convert that number into a health status
	- Healthy
	- At Risk
	- Critical

## 2) What was present at the beginning

At first, project had basic files, but many parts were incomplete:

- API was present but limited
- Some modules were empty (database, scheduler)
- Batch endpoint had a bug
- One dataset flow failed (fd004 scaler type issue)
- No real CSV upload endpoint

## 3) What we implemented step by step

### Step A: Core API and prediction flow

We set up and improved the main API so it can:

- run prediction for single input
- run prediction for batch input
- run prediction for file-based dataset input
- return recent stored predictions

API now starts with model loading + DB init automatically.

### Step B: Model and scaler loading made robust

We improved model loading logic so it can discover and load artifacts safely.

- Supports model files in JSON and PKL
- Supports scaler PKL
- Detects available datasets automatically (fd001, fd002, fd003, fd004)

### Step C: Fixed scaler/model compatibility problems

We handled real-world artifact issues:

- fd004 scaler was stored as a dictionary -> now resolved properly
- fd002 scaler not fitted -> now fallback uses identity transform instead of crash
- model feature size mismatch (example fd002 expecting 510, input was 102) -> now automatic padding/truncation is applied

Result: fd001, fd002, fd003, fd004 now predict successfully.

### Step D: Feature engineering + ingestion

Existing feature function expected 24 values and produced engineered features.

We added clear ingestion helpers to:

- load CMAPSS style files
- pick latest cycle per engine
- build features list for prediction

### Step E: Database layer implemented

We implemented the full persistence layer using SQLite.

- DB file is created automatically
- Table engine_predictions is created automatically
- Every successful prediction can be saved
- API can fetch recent predictions

### Step F: Scheduler layer implemented

We implemented scheduler files so batch prediction from dataset file can run on interval.

- scheduler job reads dataset
- predicts each engine
- stores results in DB
- can run repeatedly every N seconds

### Step G: Real CSV upload endpoint added

We added a true upload endpoint:

- POST /predict_csv
- accepts multipart form data
- fields:
	- dataset
	- file (csv)

Supported CSV formats:

1. op_setting_1..3 + sensor_1..21
2. op1..3 + s1..21
3. first 24 columns used as features

If engine_id column exists, it is stored.

### Step H: Dependency required for CSV upload

For multipart upload support, python-multipart is required.
Installed and verified.

## 4) Important bug fixes done

1. Batch API bug fixed
- Earlier only last item was returned
- Now all rows are processed and appended correctly

2. fd004 error fixed
- scaler type mismatch handled

3. fd002 error fixed
- unfitted scaler handled
- feature shape mismatch handled

4. Dataset alias support added
- fd0044 input is mapped to fd004

## 5) Endpoints available now

1. GET /
- health check + available datasets

2. POST /predict_single
- one feature vector input

3. POST /predict_batch
- list of feature vectors

4. POST /predict_file/{dataset}
- file-driven prediction from dataset files

5. POST /predict_csv
- upload csv for prediction

6. GET /predictions/recent
- view stored prediction rows

## 6) Data saved in database

For each saved prediction:

- dataset
- engine_id (if available)
- predicted_rul
- status
- features_json
- source
- created_at

This helps UI/dashboard team directly consume data.

## 7) How we tested the system

We validated all major flows:

- API health endpoint
- single prediction
- batch prediction
- file-based full run
- CSV upload run
- DB readback of recent predictions
- dataset compatibility checks (fd001, fd002, fd003, fd004, fd0044 alias)

## 8) Git and GitHub push

We initialized local git, connected remote repo, resolved merge conflict, and pushed to main branch.

Remote repository:
- https://github.com/YASHATRE10/Prognos.git

## 9) How to run now (quick)

From project root:

```powershell
c:/python313/python.exe -m pip install fastapi uvicorn numpy pandas joblib xgboost scikit-learn python-multipart
cd backend
c:/python313/python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Open docs:

http://127.0.0.1:8000/docs

## 10) What is ready for handover

Backend is ready for UI/dashboard integration.

UI member can now use:

- live prediction APIs
- csv upload API
- stored data API

## 11) Final summary in one line

Project moved from partial prototype to a robust, test-verified prediction pipeline with API, CSV upload, DB storage, scheduler support, and GitHub push complete.

