
import requests
from bs4 import BeautifulSoup

# The website used for our scraping exercise
url = "https://books.toscrape.com/"

# Request the webpage
response = requests.get(url, timeout=15)

# Stop with a useful error if the request fails
response.raise_for_status()

# Convert the HTML into a searchable object
soup = BeautifulSoup(response.text, "html.parser")

# Find every book on the current page
books = soup.select("article.product_pod")

print(f"Books found on this page: {len(books)}")

# Extract and display the first book's title
if books:
    first_book = books[0]
    title = first_book.select_one("h3 a")["title"]
    print(f"First book: {title}")
