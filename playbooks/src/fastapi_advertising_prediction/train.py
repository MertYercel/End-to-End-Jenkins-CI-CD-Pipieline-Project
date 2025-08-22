import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from urllib.parse import urlparse
import mlflow.sklearn


def read_and_train():
    # read data
    df = pd.read_csv("https://raw.githubusercontent.com/erkansirin78/datasets/master/Advertising.csv")
    print(df.head())

    # Feature matrix
    X = df.iloc[:, 1:-1].values
    print(X.shape)
    print(X[:3])

    # Output variable
    y = df.iloc[:, -1]
    print(y.shape)
    print(y[:6])

    # split test train
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

    os.environ['MLFLOW_TRACKING_URI'] = 'http://localhost:5001/'
    os.environ['MLFLOW_S3_ENDPOINT_URL'] = 'http://localhost:9000/'

    def eval_metrics(actual, pred):
        rmse = np.sqrt(mean_squared_error(actual, pred))
        mae = mean_absolute_error(actual, pred)
        r2 = r2_score(actual, pred)
        return rmse, mae, r2

    experiment_name = "FastAPI with MLflow"
    mlflow.set_experiment(experiment_name)

    registered_model_name = "AdvertisingRFModel"

    number_of_trees = 200

    with mlflow.start_run(run_name="with-reg-rf-sklearn") as run:
        estimator = RandomForestRegressor(n_estimators=number_of_trees)
        estimator.fit(X_train, y_train)

        y_pred = estimator.predict(X_test)

        (rmse, mae, r2) = eval_metrics(y_test, y_pred)

        print(f"Random Forest model number of trees: {number_of_trees}")
        print("  RMSE: %s" % rmse)
        print("  MAE: %s" % mae)
        print("  R2: %s" % r2)

        mlflow.log_param("n_estimators", number_of_trees)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)
        mlflow.log_metric("mae", mae)

        tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme

        # Model registry does not work with file store
        if tracking_url_type_store != "file":

            # Register the model
            # There are other ways to use the Model Registry, which depends on the use case,
            # please refer to the doc for more information:
            # https://mlflow.org/docs/latest/model-registry.html#api-workflow
            mlflow.sklearn.log_model(estimator, "model", registered_model_name=registered_model_name)
        else:
            mlflow.sklearn.log_model(estimator, "model")