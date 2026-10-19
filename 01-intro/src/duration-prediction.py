"""
About data: https://www.nyc.gov/assets/tlc/downloads/plf/data_dictionary_trip_records_yellow.plf

I need to predict the time of the travel

The first steap is underestand your data



Selecting the variables:

tpep_pickup_datetime The date and time when the meter was engaged.
tpep_dropoff_datetime The date and time when the meter was disengaged.
trip_distance The elapsed trip distance in miles reported by the taximeter.
"""
import os
import pyarrow
import pickle
import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, root_mean_squared_error


def get_duration(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.filter(
            pl.col("tpep_dropoff_datetime") > pl.col("tpep_pickup_datetime")
        )
        .with_columns(
            ((pl.col("tpep_dropoff_datetime") - pl.col("tpep_pickup_datetime"))
             .dt.total_seconds() / 60)
            .alias("duration")
        )
    )


def basic_statistics(df: pl.DataFrame) -> None:
    # print("DESCRIBE:")
    # print(df.describe())

    # print('MISSING VALUES:')
    # print(df.null_count())

    # print("\nDuplicated rows:", df.select(
    #     pl.struct(df.columns).is_duplicated().sum().item()))

    col = "duration"

    sns.histplot(
        data=df.filter(
            (pl.col(col) >= 0) &
            (pl.col(col) <= 120)
        ).select(col).to_pandas(),
        x=col,
        bins=60
    )

    plt.xlim(0, 120)
    plt.xlabel("Duração da viagem (minutos)")
    plt.ylabel("Frequência")
    plt.title("Distribuição da duração das viagens (0–120 min)")
    plt.savefig("01-intro/images/duration_distribution.png",
                dpi=300, bbox_inches="tight")
    plt.show()


def train(df: pl.DataFrame):
    categorical = ["PULocationID", "DOLocationID"]
    numerical = ["trip_distance"]
    target = "duration"

    df = df.with_columns(
        pl.col(categorical).cast(pl.String)
    )

    X = df.select(categorical + numerical).to_dicts()
    y = df[target].to_numpy()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    dv = DictVectorizer()
    X_train = dv.fit_transform(X_train)
    X_test = dv.transform(X_test)

    lr = LinearRegression()
    lr.fit(X_train, y_train)

    y_pred = lr.predict(X_test)

    print("MAE:", mean_absolute_error(y_test, y_pred))
    print("RMSE:", root_mean_squared_error(y_test, y_pred))

    return lr, dv


def predict_trip(lr, dv, pickup_id, dropoff_id, distance):
    trip = {
        "PULocationID": str(pickup_id),
        "DOLocationID": str(dropoff_id),
        "trip_distance": distance,
    }

    X_trip = dv.transform([trip])

    return lr.predict(X_trip)[0]


def save_model(lr, dv, model_name):
    os.makedirs("./01-intro/models/", exist_ok=True)

    with open("./01-intro/models/" + model_name, 'wb') as out:
        pickle.dump((dv, lr), out)


def main() -> None:
    df = pl.read_parquet("01-intro/data/yellow_tripdata_2021-01.parquet")

    df = get_duration(df)

    # basic_statistics(df)

    lr, dv = train(df)

    duration = predict_trip(lr, dv, 161, 236, 5.2)
    print(f"Predicted duration: {duration:.2f} minutes")

    save_model(lr, dv, "lin_reg.bin")


if __name__ == "__main__":
    main()
