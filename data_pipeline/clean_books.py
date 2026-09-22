
from pathlib import Path

import pandas as pd


# Paths work regardless of where the script is run.
DATA_DIR = Path(__file__).resolve().parent
RAW_FILE = DATA_DIR / "raw_books.csv"
CLEAN_FILE = DATA_DIR / "cleaned_books.csv"

# Fixed conversion rate required by the assignment.
GBP_TO_INR = 105.50

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


def clean_books():
    # 1. Load the raw dataset.
    df = pd.read_csv(RAW_FILE)

    print("Original dataset shape:", df.shape)
    print("\nMissing values before cleaning:")
    print(df.isna().sum())

    # 2. Remove exact duplicate records.
    duplicates = df.duplicated().sum()
    df = df.drop_duplicates().copy()

    print(f"\nDuplicate records removed: {duplicates}")

    # 3. Convert prices to numbers.
    # Remove currency symbols and other non-numeric
    # characters, retaining digits and decimal points.
    price_text = (
        df["price"]
        .astype("string")
        .str.replace(r"[^0-9.]", "", regex=True)
    )

    df["price_gbp"] = pd.to_numeric(
        price_text,
        errors="coerce"
    )

    # Replace invalid prices with the median.
    missing_prices = df["price_gbp"].isna().sum()
    median_price = df["price_gbp"].median()

    if pd.isna(median_price):
        raise ValueError("No valid prices found.")

    df["price_gbp"] = df["price_gbp"].fillna(
        median_price
    )

    # 4. Convert text ratings to integers.
    df["rating"] = (
        df["star_rating"]
        .astype("string")
        .str.strip()
        .map(RATING_MAP)
    )

    missing_ratings = df["rating"].isna().sum()

    if df["rating"].notna().sum() == 0:
        raise ValueError("No valid ratings found.")

    median_rating = int(
        round(df["rating"].median())
    )

    df["rating"] = (
        df["rating"]
        .fillna(median_rating)
        .astype(int)
    )

    # 5. Convert availability to a boolean.
    availability = (
        df["availability"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    stock_map = {
        "in stock": True,
        "out of stock": False,
    }

    df["in_stock"] = availability.map(stock_map)

    # Drop records with unknown availability.
    invalid_stock = df["in_stock"].isna().sum()
    df = df.dropna(subset=["in_stock"]).copy()
    df["in_stock"] = df["in_stock"].astype(bool)

    # 6. Validate titles and categories.
    df["title"] = df["title"].astype("string").str.strip()
    df["category"] = (
        df["category"].astype("string").str.strip()
    )

    invalid_text = (
        df["title"].isna()
        | df["category"].isna()
        | df["title"].eq("")
        | df["category"].eq("")
    )

    invalid_text_count = invalid_text.sum()
    df = df.loc[~invalid_text].copy()

    # 7. Convert GBP to INR.
    df["price_inr"] = (
        df["price_gbp"] * GBP_TO_INR
    ).round(2)

    # 8. Select the final columns.
    df = df[
        [
            "title",
            "price_gbp",
            "price_inr",
            "rating",
            "in_stock",
            "category",
        ]
    ]

    # 9. Validate the cleaned dataset.
    assert df["rating"].between(1, 5).all()
    assert df.notna().all().all()

    # 10. Save the cleaned data.
    df.to_csv(CLEAN_FILE, index=False)

    print("\nCleaning summary:")
    print(f"Invalid prices imputed: {missing_prices}")
    print(f"Invalid ratings imputed: {missing_ratings}")
    print(f"Invalid availability rows dropped: {invalid_stock}")
    print(f"Invalid title/category rows dropped: {invalid_text_count}")

    print("\nFinal dataset shape:", df.shape)
    print("Number of categories:", df["category"].nunique())

    print("\nColumn data types:")
    print(df.dtypes)

    print("\nFirst five cleaned records:")
    print(df.head().to_string(index=False))

    print(f"\nCleaned dataset saved to: {CLEAN_FILE}")


if __name__ == "__main__":
    clean_books()
