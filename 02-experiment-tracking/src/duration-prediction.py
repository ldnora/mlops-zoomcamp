"""
About data: https://www.nyc.gov/assets/tlc/downloads/plf/data_dictionary_trip_records_yellow.plf

I'm learning how to use the MLFlow

"""
import os
import pickle
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Lasso
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, root_mean_squared_error
import mlflow

import xgboost as xgb
from hyperopt import fmin, tpe, hp, STATUS_OK, Trials
from hyperopt.pyll import scope


mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("nyc-taxi-experiment-2")

def read_dataframe(filename):
    df = pd.read_parquet(filename, columns=[
                         'tpep_dropoff_datetime', 'tpep_pickup_datetime', 'PULocationID', 'DOLocationID', 'trip_distance'
                         ])

    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df.duration = df.duration.apply(lambda td: td.total_seconds() / 60)

    df = df[(df.duration >= 1) & (df.duration <= 60)]

    categorical = ['PULocationID', 'DOLocationID']
    df[categorical] = df[categorical].astype(str)
    
    return df


df = pd.concat([read_dataframe('02-experiment-tracking/data/yellow_tripdata_2021-01.parquet'),
               read_dataframe('02-experiment-tracking/data/yellow_tripdata_2021-02.parquet')], ignore_index=False)


df['PU_DO'] = df['PULocationID'] + '_' + df['DOLocationID']

categorical = ['PU_DO']  # 'PULocationID', 'DOLocationID']
numerical = ['trip_distance']

X = df[categorical + numerical]
y = df.duration

X_train, X_val, y_train, y_val = train_test_split(
    X, y, random_state=42, test_size=0.33)

dv = DictVectorizer(dtype=np.int64)

X_train_transformed = dv.fit_transform(X_train.to_dict(orient="records"))

X_val_transformed = dv.transform(X_val.to_dict(orient="records"))

for X in [X_train_transformed, X_val_transformed]:
    X.indices = X.indices.astype(np.int32)
    X.indptr = X.indptr.astype(np.int32)

train_categories = X_train["PU_DO"].astype("category").cat.categories

X_train["PU_DO"] = pd.Categorical(
    X_train["PU_DO"],
    categories=train_categories
)

X_val["PU_DO"] = pd.Categorical(
    X_val["PU_DO"],
    categories=train_categories
)

train = xgb.DMatrix(X_train, label=y_train)
valid = xgb.DMatrix(X_val, label=y_val)


with mlflow.start_run():

    train = xgb.DMatrix(X_train, label=y_train, enable_categorical=True)
    validation = xgb.DMatrix(X_val, label=y_val, enable_categorical=True)

    best_params = {
        'learning_rate': 0.09585355369315604,
        'max_depth': 6,
        'min_child_weight': 1.060597050922164,
        'objective': 'reg:linear',
        'reg_alpha': 0.018060244040060163,
        'reg_lambda': 0.011658731377413597,
        'seed': 42,
        'tree_method': 'hist',
        'nthread': 2,
    }

    mlflow.log_params(best_params)

    booster = xgb.train(
        params=best_params,
        dtrain=train,
        num_boost_round=200,
        evals=[(validation, 'validation')],
        early_stopping_rounds=20,
    )

    y_pred = booster.predict(valid)
    rmse = root_mean_squared_error(y_val, y_pred)
    mlflow.log_metric("rmse", rmse)

    with open("02-experiment-tracking/models/preprocessor.b", "wb") as f_out:
        pickle.dump(dv, f_out)
    mlflow.log_artifact("02-experiment-tracking/models/preprocessor.b",
                        artifact_path="preprocessor")

    mlflow.xgboost.log_model(booster, artifact_path="models_mlflow")
