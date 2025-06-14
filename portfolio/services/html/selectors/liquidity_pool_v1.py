import re
from icecream import ic


def select_liquidity_pool_v1(html, project, product):
    div1 = html.find("div", id=project)
    if not div1:
        return ""
    div2 = div1.find_next("div", text=product)
    if not div2:
        return ""
    span = div2.find_next("span", text=re.compile(r"\$\d+(?:\.\d+)?"))
    if project == "matic_stargate":
        span = div2.find_next("span", text=re.compile(r"\$\d+(?:\.\d+)?"))
    if not span:
        return ""
    result = span.text
    return result
