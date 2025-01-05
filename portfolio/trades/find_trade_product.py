import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.init import info
from portfolio.utils.lib import named_tuple_factory

def find_trade_product(words: list[str]) -> str:
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
    
    if len(matches) == 0:
        joined_words = " ".join(words)
        info(f"Product {joined_words} not found")
        return
    
    if len(matches) > 1:
        info("Multiple matches found")
        for match in matches:
            info(f"{match['product_id']} {match['product']}")
        return
    
    return matches[0]