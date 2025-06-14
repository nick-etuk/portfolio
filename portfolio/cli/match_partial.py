import sqlite3 as sl
from portfolio.utils.config import db
from portfolio.utils.init import info
from portfolio.utils.lib import named_tuple_factory

def match_partial(input_words: list[str]) -> str:
    '''
    Find product that partially matches the input words.
    For example, if the input is ['bit', 'usd'], it will match 'Bitcoin USD'.
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
        for word in input_words:
            word_matched = False
            product_descr =  row.product.lower()
            for product_word in product_descr.split():
                if product_word.startswith(word.lower()):
                    word_matched = True
                    break
            if not word_matched:
                all_words_matched = False
                break
        
        if all_words_matched:
            matches.append({"product_id": row.product_id, "product": row.product})
    
    return matches
