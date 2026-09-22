
from pathlib import Path
import sqlite3

import pandas as pd


DATA_DIR = Path(__file__).resolve().parent
CSV_FILE = DATA_DIR / "cleaned_books.csv"
DB_FILE = DATA_DIR / "zepto_books.db"


def create_database():
    # Load cleaned data.
    df = pd.read_csv(CSV_FILE)

    # Create or open the SQLite database.
    conn = sqlite3.connect(DB_FILE)

    try:
        # Enable foreign-key enforcement.
        conn.execute("PRAGMA foreign_keys = ON")

        # Recreate both tables so the script can
        # be run repeatedly without duplicating rows.
        conn.execute("DROP TABLE IF EXISTS books")
        conn.execute("DROP TABLE IF EXISTS categories")

        conn.execute("""
            CREATE TABLE categories (
                category_id INTEGER PRIMARY KEY,
                category_name TEXT NOT NULL UNIQUE
            )
        """)

        conn.execute("""
            CREATE TABLE books (
                book_id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                price_gbp REAL NOT NULL,
                price_inr REAL NOT NULL,
                rating INTEGER CHECK(rating BETWEEN 1 AND 5),
                in_stock INTEGER NOT NULL
                    CHECK(in_stock IN (0, 1)),
                category_id INTEGER NOT NULL,
                FOREIGN KEY (category_id)
                    REFERENCES categories(category_id)
            )
        """)

        # Insert each category once.
        category_names = sorted(
            df["category"].unique()
        )

        conn.executemany(
            "INSERT INTO categories (category_name) VALUES (?)",
            [(name,) for name in category_names]
        )

        # Build a mapping of category names to IDs.
        category_rows = conn.execute(
            "SELECT category_id, category_name FROM categories"
        ).fetchall()

        category_map = {
            name: category_id
            for category_id, name in category_rows
        }

        # Insert the books using the foreign key.
        book_records = [
            (
                row.title,
                float(row.price_gbp),
                float(row.price_inr),
                int(row.rating),
                int(row.in_stock),
                category_map[row.category],
            )
            for row in df.itertuples(index=False)
        ]

        conn.executemany("""
            INSERT INTO books (
                title,
                price_gbp,
                price_inr,
                rating,
                in_stock,
                category_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, book_records)

        conn.commit()

        # Verify the result.
        book_count = conn.execute(
            "SELECT COUNT(*) FROM books"
        ).fetchone()[0]

        category_count = conn.execute(
            "SELECT COUNT(*) FROM categories"
        ).fetchone()[0]

        print(f"Database created: {DB_FILE}")
        print(f"Books inserted: {book_count}")
        print(f"Categories inserted: {category_count}")

        # Verify that all foreign keys are valid.
        fk_errors = conn.execute(
            "PRAGMA foreign_key_check"
        ).fetchall()

        print(f"Foreign-key errors: {len(fk_errors)}")

        assert book_count == len(df)
        assert category_count == df["category"].nunique()
        assert not fk_errors

        print("\nSample JOIN result:")

        query = """
            SELECT
                b.title,
                c.category_name,
                b.price_gbp,
                b.rating
            FROM books AS b
            JOIN categories AS c
                ON b.category_id = c.category_id
            LIMIT 5
        """

        print(
            pd.read_sql_query(query, conn).to_string(
                index=False
            )
        )

    finally:
        conn.close()


if __name__ == "__main__":
    create_database()
