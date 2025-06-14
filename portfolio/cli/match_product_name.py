import sqlite3 as sl
from portfolio.cli.match_check import match_check
from portfolio.cli.match_full import match_full
from portfolio.cli.match_partial import match_partial
from portfolio.utils.init import info

def match_product_name(input: list[str]) -> str:
    '''
    Search for a product in a permissive way.
    Only one product must match.
    Case insensitive.
    If all words match, it is considered a match.
    Otherwise, find products that partially match the input words.
    For example, if the input is ['bit', 'usd'], it will match 'Bitcoin USD'.
    '''

    matches = match_full(input)
    if match_check(matches, 'Full match'):
        return matches[0]
    
    info("No exact match found, trying partial matches")
    matches = match_partial(input)
    if match_check(matches, 'Partial match'):
        return matches[0]
