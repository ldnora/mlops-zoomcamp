"""
About data: https://www.nyc.gov/assets/tlc/downloads/plf/data_dictionary_trip_records_yellow.plf

I need to predict the time of the travel

The first steap is underestand your data



Selecting the variables:

tpep_pickup_datetime The date and time when the meter was engaged.
tpep_dropoff_datetime The date and time when the meter was disengaged.
trip_distance The elapsed trip distance in miles reported by the taximeter.
"""

import polars as pl
import pyarrow
import seaborn as sns
import matplotlib.pyplot as plt


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


def main() -> None:
    df = pl.read_parquet("01-intro/data/yellow_tripdata_2021-01.parquet")

    df = get_duration(df)

    # print(df["duration"].describe())
    # basic_statistics(df)


if __name__ == "__main__":
    main()
