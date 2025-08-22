import os
from fastapi import FastAPI
from mlflow.sklearn import load_model

try:
    from models import Advertising
except:
    from fastapi_advertising_prediction.models import Advertising

# Tell where is the tracking server and artifact server
os.environ['MLFLOW_TRACKING_URI'] = 'http://mlflow:5000/'
os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'http://minio:9000/'

# Learn, decide and get model from mlflow model registry
model_name = "AdvertisingRFModel"
model_version = 1
estimator_advertising_loaded = load_model(
    model_uri=f"models:/{model_name}/{model_version}"
)

app = FastAPI()


def make_advertising_prediction(model, request):
    # parse input from request
    TV = request["TV"]
    Radio = request['Radio']
    Newspaper = request['Newspaper']

    # Make an input vector
    advertising = [[TV, Radio, Newspaper]]

    # Predict
    prediction = model.predict(advertising)

    return prediction[0]


# Advertising prediction endpoint
@app.post("/prediction/advertising")
def predict_iris(request: Advertising):
    prediction = make_advertising_prediction(estimator_advertising_loaded, request.dict())
    return {"result": prediction}