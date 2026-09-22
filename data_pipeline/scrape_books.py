
import time
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://books.toscrape.com/"
TARGET_CATEGORIES = 3
MIN_BOOKS = 60


def get_soup(url):
    """Download a page and parse its HTML."""
    response = requests.get(url, timeout=15)
    response.raise_for_status()

    # Books to Scrape uses UTF-8 text.
    # Set the encoding explicitly to avoid corrupted
    # characters such as â€™ in book titles.
    response.encoding = "utf-8"

    return BeautifulSoup(response.text, "html.parser")


def get_categories():
    """Discover category names and URLs."""
    soup = get_soup(BASE_URL)

    category_links = soup.select(
        ".side_categories ul li ul li a"
    )

    categories = []

    for link in category_links:
        name = link.get_text(strip=True)
        url = urljoin(BASE_URL, link["href"])

        categories.append({
            "name": name,
            "url": url
        })

    return categories


def scrape_category(category):
    """Scrape every paginated page in one category."""
    records = []
    page_url = category["url"]

    while page_url:
        soup = get_soup(page_url)

        for book in soup.select("article.product_pod"):
            title = book.select_one("h3 a")["title"]

            price = book.select_one(
                ".price_color"
            ).get_text(strip=True)

            rating_classes = book.select_one(
                ".star-rating"
            ).get("class", [])

            star_rating = next(
                (
                    value for value in rating_classes
                    if value in [
                        "One", "Two", "Three",
                        "Four", "Five"
                    ]
                ),
                None
            )

            availability = book.select_one(
                ".availability"
            ).get_text(" ", strip=True)

            records.append({
                "title": title,
                "price": price,
                "star_rating": star_rating,
                "availability": availability,
                "category": category["name"]
            })

        next_link = soup.select_one("li.next a")

        if next_link:
            page_url = urljoin(
                page_url,
                next_link["href"]
            )
            time.sleep(0.5)
        else:
            page_url = None

    return records


def main():
    categories = get_categories()
    all_books = []

    for category in categories:
        print(f"Scraping: {category['name']}")

        books = scrape_category(category)
        all_books.extend(books)

        print(f"  Found {len(books)} books")

        # Stop after at least three categories
        # AND at least 60 books.
        category_count = len(
            set(book["category"] for book in all_books)
        )

        if (
            category_count >= TARGET_CATEGORIES
            and len(all_books) >= MIN_BOOKS
        ):
            break

    df = pd.DataFrame(all_books)

    output_path = "data_pipeline/raw_books.csv"
    df.to_csv(output_path, index=False)

    print("\nScraping complete!")
    print(f"Total books: {len(df)}")
    print(f"Categories: {df['category'].nunique()}")
    print(df.head())


if __name__ == "__main__":
    main()
