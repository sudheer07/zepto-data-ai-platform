
from pathlib import Path
import sqlite3

import pandas as pd


DATA_DIR = Path(__file__).resolve().parent
DB_FILE = DATA_DIR / "zepto_books.db"
RESULTS_DIR = DATA_DIR / "query_results"

RESULTS_DIR.mkdir(exist_ok=True)


QUERIES = {
    # SELECT, WHERE, ORDER BY and LIMIT
    "01_top_rated": """
        SELECT title, price_gbp, rating
        FROM books
        WHERE rating >= 4
        ORDER BY rating DESC, price_gbp DESC
        LIMIT 10
    """,

    # DISTINCT
    "02_distinct_categories": """
        SELECT DISTINCT category_name
        FROM categories
        ORDER BY category_name
    """,

    # BETWEEN
    "03_mid_price_books": """
        SELECT title, price_gbp, rating
        FROM books
        WHERE price_gbp BETWEEN 20 AND 40
        ORDER BY price_gbp
    """,

    # IN
    "04_selected_ratings": """
        SELECT title, rating, price_gbp
        FROM books
        WHERE rating IN (4, 5)
        ORDER BY rating DESC
    """,

    # JOIN and GROUP BY
    "05_category_summary": """
        SELECT
            c.category_name,
            COUNT(*) AS book_count,
            ROUND(AVG(b.price_gbp), 2)
                AS average_price_gbp
        FROM books AS b
        JOIN categories AS c
            ON b.category_id = c.category_id
        GROUP BY c.category_id, c.category_name
        ORDER BY book_count DESC
    """,

    # JOIN: individual books and category names
    "06_books_with_categories": """
        SELECT
            b.book_id,
            b.title,
            b.price_gbp,
            c.category_name
        FROM books AS b
        JOIN categories AS c
            ON b.category_id = c.category_id
        ORDER BY b.book_id
    """,
}


def main():
    with sqlite3.connect(DB_FILE) as conn:

        # Save every SQL query to a .sql file,
        # execute it and save its result to CSV.
        for name, query in QUERIES.items():
            sql_file = RESULTS_DIR / f"{name}.sql"
            csv_file = RESULTS_DIR / f"{name}.csv"

            sql_file.write_text(
                query.strip() + "\n",
                encoding="utf-8"
            )

            result = pd.read_sql_query(query, conn)
            result.to_csv(csv_file, index=False)

            print(f"\n{name}: {len(result)} rows")
            print(result.head().to_string(index=False))

        # Reproduce the SQL JOIN using pandas.
        books_df = pd.read_sql_query(
            """
            SELECT book_id, title, price_gbp, category_id
            FROM books
            """,
            conn
        )

        categories_df = pd.read_sql_query(
            """
            SELECT category_id, category_name
            FROM categories
            """,
            conn
        )

        pandas_join = pd.merge(
            books_df,
            categories_df,
            on="category_id",
            how="inner",
            validate="many_to_one"
        )

        pandas_join = (
            pandas_join[
                [
                    "book_id",
                    "title",
                    "price_gbp",
                    "category_name",
                ]
            ]
            .sort_values("book_id")
            .reset_index(drop=True)
        )

        sql_join = (
            pd.read_sql_query(
                QUERIES["06_books_with_categories"],
                conn
            )
            .reset_index(drop=True)
        )

        # Confirm both approaches produce
        # exactly the same table.
        pd.testing.assert_frame_equal(
            sql_join,
            pandas_join,
            check_dtype=False
        )

        pandas_join.to_csv(
            RESULTS_DIR / "07_pandas_merge.csv",
            index=False
        )

        print("\nSQL JOIN and pandas merge are equivalent!")
        print(f"Matching rows: {len(pandas_join)}")


if __name__ == "__main__":
    main()
