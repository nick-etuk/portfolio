import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.lib import named_tuple_factory

def match_full(words: list[str]) -> str:
    '''
    Search for a product in a permissive way.
    Only one product must match.
    Case insensitive.
    All words must match.
    '''
    prod_sql = """
    select product_id, descr as product
    from product
    """
    with sl.connect(db) as conn:
        conn.row_factory = named_tuple_factory
        c = conn.cursor()
        rows = c.execute(prod_sql).fetchall()

    matches = []

    for row in rows:
        all_words_matched = True
        for word in words:
            if word.lower() not in row.product.lower():
                all_words_matched = False
                break
        
        if all_words_matched:
            matches.append({"product_id": row.product_id, "product": row.product})
    
    return matches
