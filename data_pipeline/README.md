
# Module 1: Book Data Pipeline

## 1. Project Overview

This module implements an end-to-end data pipeline using
Python. It collects book information from Books to Scrape,
cleans the extracted data, stores it in a normalized SQLite
database, and performs analysis using SQL and pandas.

The pipeline has four stages:

1. Web scraping
2. Data cleaning and currency conversion
3. SQLite database creation
4. SQL querying and pandas analysis

The final dataset contains 69 books from three categories:
Travel, Mystery and Historical Fiction.

## 2. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| requests | Download webpage HTML |
| BeautifulSoup | Extract book information |
| pandas | Clean, transform and analyze data |
| SQLite | Store data in relational tables |
| Git | Version control |

## 3. Project Structure

```text
data_pipeline/
├── README.md
├── scrape_books.py
├── clean_books.py
├── create_database.py
├── run_queries.py
├── raw_books.csv
├── cleaned_books.csv
├── zepto_books.db
└── query_results/
    ├── 01_top_rated.sql
    ├── 01_top_rated.csv
    ├── 02_distinct_categories.sql
    ├── 02_distinct_categories.csv
    ├── 03_mid_price_books.sql
    ├── 03_mid_price_books.csv
    ├── 04_selected_ratings.sql
    ├── 04_selected_ratings.csv
    ├── 05_category_summary.sql
    ├── 05_category_summary.csv
    ├── 06_books_with_categories.sql
    ├── 06_books_with_categories.csv
    └── 07_pandas_merge.csv
```

## 4. Web Scraping

### Objective

Collect at least 60 books from at least three categories
on https://books.toscrape.com/.

### Implementation

The `scrape_books.py` script uses `requests` to download
webpages and BeautifulSoup to parse their HTML.

First, the script identifies category links from the
website's sidebar. It then visits each selected category
and extracts book information.

The following fields are collected:

- Title
- Price in GBP
- Star rating
- Availability
- Category

The script also follows pagination links so that it can
collect books from categories containing multiple pages.

A short delay is included between paginated requests.

Scraping stops after both conditions are satisfied:
at least three categories have been processed and at
least 60 books have been collected.

The collected records are converted into a pandas
DataFrame and saved to `raw_books.csv`.

### Results

The scraper collected 69 books from three categories.

| Category | Books |
|---|---:|
| Mystery | 32 |
| Historical Fiction | 26 |
| Travel | 11 |
| **Total** | **69** |

The dataset satisfies both collection requirements.

## 5. Data Cleaning

### Character Encoding

During initial scraping, some special characters in book
titles were decoded incorrectly. For example, the title
"Noah’s Ark" contained corrupted characters.

To resolve this, UTF-8 encoding was explicitly specified
in the `get_soup()` function before parsing the HTML
with BeautifulSoup.

After applying the fix, the scraping, cleaning, database
creation and SQL analysis scripts were rerun to ensure
the corrected titles appeared throughout the pipeline.

### Implementation

The `clean_books.py` script reads `raw_books.csv`
and performs the following operations.

#### Duplicate removal

Exact duplicate records are identified using pandas
and removed with `drop_duplicates()`.

#### Price conversion

The scraped price is initially a string containing
a currency symbol.

The currency symbol is removed and the remaining
value is converted into a numeric GBP price.

Invalid numeric values are converted to missing
values. If any invalid prices are found, they are
replaced with the median valid price.

#### Star rating conversion

Text ratings are mapped to integers:

| Text | Numeric rating |
|---|---:|
| One | 1 |
| Two | 2 |
| Three | 3 |
| Four | 4 |
| Five | 5 |

If an invalid rating is encountered, it is replaced
with the rounded median of the valid ratings.

#### Availability conversion

Availability is converted into a Boolean field
named `in_stock`.

- In stock → True
- Out of stock → False

Rows containing unrecognized availability values
are dropped because their stock status cannot
be reliably determined.

#### Title and category validation

Rows with missing or empty titles or category names
are removed.

#### Currency conversion

GBP prices are converted to INR using the fixed
assignment exchange rate:

1 GBP = 105.50 INR

The formula is:

`price_inr = price_gbp * 105.50`

The INR result is rounded to two decimal places.

### Cleaning Results

| Check | Result |
|---|---:|
| Raw records | 69 |
| Duplicate records removed | 0 |
| Invalid prices imputed | 0 |
| Invalid ratings imputed | 0 |
| Invalid availability rows dropped | 0 |
| Invalid title/category rows dropped | 0 |
| Final records | 69 |

No missing values or duplicate records were found
in the collected dataset.

Although the cleaning script includes rules for
invalid and missing values, no imputation or row
removal was required for this particular dataset.

### Final Dataset

The cleaned dataset contains six columns:

| Column | Description |
|---|---|
| title | Book title |
| price_gbp | Numeric price in GBP |
| price_inr | Converted price in INR |
| rating | Integer rating from 1 to 5 |
| in_stock | Boolean availability |
| category | Book category |

The cleaned records are saved to `cleaned_books.csv`.

## 6. SQLite Database Design

### Objective

Store the cleaned dataset in a normalized relational
database instead of keeping all information in one table.

### Implementation

The `create_database.py` script creates an SQLite
database named `zepto_books.db`.

It contains two related tables.

### categories

| Column | Constraint |
|---|---|
| category_id | Primary key |
| category_name | Unique, not null |

### books

| Column | Constraint |
|---|---|
| book_id | Primary key |
| title | Not null |
| price_gbp | Not null |
| price_inr | Not null |
| rating | Integer between 1 and 5 |
| in_stock | Integer representing Boolean |
| category_id | Foreign key |

The `category_id` column in `books` references
the `category_id` column in `categories`.

This creates a one-to-many relationship:
one category can contain multiple books.

### Why Normalize the Database?

Storing category names repeatedly in every book
record would introduce unnecessary duplication.

Instead, category names are stored once in the
`categories` table. Each book stores only its
corresponding category ID.

This reduces redundancy and allows category
information to be maintained in one place.

### Database Validation

The script enables SQLite foreign-key enforcement
and runs `PRAGMA foreign_key_check` after insertion.

The results were:

- Books inserted: 69
- Categories inserted: 3
- Foreign-key errors: 0

The database creation script can be rerun without
duplicating records because it recreates the
tables before loading the cleaned dataset.

## 7. SQL Analysis

The `run_queries.py` script executes six SQL queries.

Each query is saved as a `.sql` file and its results
are exported to a corresponding `.csv` file inside
the `query_results` directory.

### Query 1: Top-Rated Books

**SQL concepts:** SELECT, WHERE, ORDER BY, LIMIT

This query selects books rated four stars or higher,
sorts them by rating and price in descending order,
and returns the first ten records.

Result: 10 books.

### Query 2: Distinct Categories

**SQL concepts:** SELECT DISTINCT, ORDER BY

This query retrieves the unique category names.

Result:

- Historical Fiction
- Mystery
- Travel

### Query 3: Mid-Priced Books

**SQL concepts:** WHERE, BETWEEN, ORDER BY

This query selects books priced between £20 and £40
and sorts them by price.

Result: 33 books.

### Query 4: Selected Ratings

**SQL concepts:** WHERE, IN

This query retrieves books with ratings of either
four or five stars.

Result: 27 books.

### Query 5: Category Summary

**SQL concepts:** JOIN, GROUP BY, COUNT, AVG, ORDER BY

This query joins the books and categories tables,
groups books by category, and calculates the
number of books and average GBP price.

Results:

| Category | Book count | Average price |
|---|---:|---:|
| Mystery | 32 | £31.72 |
| Historical Fiction | 26 | £33.64 |
| Travel | 11 | £39.79 |

Mystery has the largest number of books in the
collected dataset.

Travel has the highest average book price, despite
having the smallest number of collected books.

These findings apply to the collected sample and
should not be interpreted as statistics for the
entire Books to Scrape website.

### Query 6: Books with Categories

**SQL concepts:** INNER JOIN

This query joins the `books` and `categories`
tables using `category_id`.

It returns each book's ID, title, price in GBP
and category name.

Result: 69 rows.

## 8. pandas Integration

SQL query results are loaded into pandas DataFrames
using `pd.read_sql_query()`.

The script uses this function to execute and export
all six SQL queries.

To demonstrate the relationship between SQL JOIN
and pandas merge, the script also loads the
`books` and `categories` tables separately.

It combines them using:

```python
pd.merge(
    books_df,
    categories_df,
    on="category_id",
    how="inner",
    validate="many_to_one"
)
```

The resulting DataFrame is arranged to match
the SQL JOIN output.

The two DataFrames are compared using
`pd.testing.assert_frame_equal()`.

### Comparison Result

The SQL JOIN and pandas merge produced equivalent
results containing 69 rows.

The pandas result is saved as
`query_results/07_pandas_merge.csv`.

## 9. How to Run the Pipeline

### Prerequisites

Python 3.11 and the following packages:

- requests
- beautifulsoup4
- pandas

Install them in a virtual environment:

```bash
python -m pip install requests beautifulsoup4 pandas
```

From the project root, run these commands in order:

```bash
python data_pipeline/scrape_books.py
python data_pipeline/clean_books.py
python data_pipeline/create_database.py
python data_pipeline/run_queries.py
```

The scripts generate the raw CSV, cleaned CSV,
SQLite database and saved SQL query results.

## 10. Limitations and Future Improvements

The scraper collects a subset of categories from
Books to Scrape rather than the entire website.

The GBP-to-INR conversion uses the fixed rate
specified in the assignment, not a live exchange
rate.

The cleaning script handles invalid prices and
ratings, but the collected dataset did not contain
any missing or invalid values that required
imputation.

Future improvements could include more extensive
scraping, automated tests, structured logging
and additional data-quality checks.