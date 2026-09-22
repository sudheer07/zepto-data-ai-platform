SELECT
            b.book_id,
            b.title,
            b.price_gbp,
            c.category_name
        FROM books AS b
        JOIN categories AS c
            ON b.category_id = c.category_id
        ORDER BY b.book_id
