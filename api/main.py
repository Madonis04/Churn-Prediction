# main.py
import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from fastapi import UploadFile, File
import json

# 1. Initialize the FastAPI app
app = FastAPI(title="Customer Churn Prediction API", version="1.0")

# 2. Load the trained model and column list
model = joblib.load('churn_model.joblib')
model_columns = joblib.load('model_columns.joblib')

# 3. Define the input data structure using Pydantic
# This ensures that any request to the API has the correct data format.
# We only need a subset of the most important features for the example.
class CustomerData(BaseModel):
    tenure: int
    MonthlyCharges: float
    TotalCharges: float
    gender_Male: int
    Partner_Yes: int
    Dependents_Yes: int
    PhoneService_Yes: int
    MultipleLines_No_phone_service: int
    MultipleLines_Yes: int
    InternetService_Fiber_optic: int
    InternetService_No: int
    OnlineSecurity_No_internet_service: int
    OnlineSecurity_Yes: int
    # ... add all other features from your model_columns list
    # For this example, we'll assume the rest are passed correctly.
    # In a real project, you would list every single feature here.

# 4. Define the prediction endpoint
@app.post("/predict")
def predict(data: CustomerData):
    """
    Receives customer data and predicts the churn probability.
    """
    # Convert the incoming Pydantic object to a dictionary
    data_dict = data.model_dump()
    
    # Create a pandas DataFrame from the dictionary
    # The keys of the dict must match the feature names the model expects
    df = pd.DataFrame([data_dict])
    
    # Pad with missing columns if any (fill with 0)
    # This is a robust way to handle the full feature set
    for col in model_columns:
        if col not in df.columns:
            df[col] = 0
            
    # Ensure the column order matches the order during training
    df = df[model_columns]
    
    # Make prediction (we want the probability of churn, which is the second value)
    churn_probability = model.predict_proba(df)[:, 1][0]
    
    # Determine prediction based on a 0.5 threshold
    prediction = "Churn" if churn_probability > 0.5 else "Not Churn"
    
    return {
        "prediction": prediction,
        "churn_probability": float(churn_probability)
    }

@app.post("/predict-file")
async def predict_file(file: UploadFile = File(...)):
    """
    Receives a JSON file with a list of customers and predicts churn for all of them.
    """
    # Read the file content
    contents = await file.read()

    # Parse the JSON data (assuming it's a list of customer objects)
    data = json.loads(contents)

    # Create a DataFrame from the list of dictionaries
    df = pd.DataFrame(data)

    # Ensure all required model columns are present, fill missing with 0
    for col in model_columns:
        if col not in df.columns:
            df[col] = 0

    # Reorder columns to match model's training order
    df = df[model_columns]

    # Get churn probabilities for the entire DataFrame
    probabilities = model.predict_proba(df)[:, 1]

    # Create a list of results
    results = []
    for i, prob in enumerate(probabilities):
        prediction = "Churn" if prob > 0.5 else "Not Churn"
        results.append({
            "customer_index": i,
            "prediction": prediction,
            "churn_probability": float(prob)
        })

    return results


# A simple root endpoint for checking if the API is running
@app.get("/")
def read_root():
    return RedirectResponse(url="/docs")