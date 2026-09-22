SELECT title, price_gbp, rating
        FROM books
        WHERE rating >= 4
        ORDER BY rating DESC, price_gbp DESC
        LIMIT 10
