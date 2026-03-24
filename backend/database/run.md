Follow these exact steps in Windows PowerShell.

1. Open terminal in project root  
PrognosAI-AI-Driven-Predictive-Maintenance-System-Using-Time-Series-Sensor-Data-akanchha

2. Install dependencies  
Run:
```powershell
c:/python313/python.exe -m pip install fastapi uvicorn numpy pandas joblib xgboost scikit-learn python-multipart
```
Note: `python-multipart` is a package name, not a command. So don’t run `python-multipart` directly.

3. Start backend API  
Run:
```powershell
cd backend
c:/python313/python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

4. Open Swagger UI  
Go to:
`http://127.0.0.1:8000/docs`

5. Verify API is running  
Open:
`http://127.0.0.1:8000/`  
You should see message + available datasets.

6. Test single prediction  
In Swagger:
- Endpoint: `POST /predict_single`
- Click **Try it out**
- Use body:
```json
{
  "dataset": "fd001",
  "features": [0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
}
```

7. Test CSV upload prediction  
In Swagger:
- Endpoint: `POST /predict_csv`
- Click **Try it out**
- Set dataset = `fd001`
- Upload your `.csv` file
- Click **Execute**

CSV can be:
- `op_setting_1..3` + `sensor_1..21`, or
- `op1..3` + `s1..21`, or
- first 24 columns as features

8. Check saved predictions  
In Swagger:
- Endpoint: `GET /predictions/recent`
- Example: `dataset=fd001`, `limit=20`

9. Stop server  
In the terminal running uvicorn, press:
`Ctrl + C`

If you want, I can give you a ready-to-use sample CSV file format you can paste and test immediately.