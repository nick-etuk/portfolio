import re
from icecream import ic


def select_liquidity_pool(html, columns, product, chain, project, html_label):
    # print("=>select_liquidity_pool")
    # ic(product, chain, project, html_label)
    # non-standard selector
    project_label = chain + "_" + project
    marker = html.find("div", id=re.compile(project_label, re.IGNORECASE))
    if not marker:
        # print(f"Div not found for {product} {project_label}")
        return ""
    product_div = marker.find_parent("div")
    product_row_div = product_div.find_next(
        "div", class_=re.compile("Panel_container.*")
    )
    while product_row_div:
        result = process_table_row(product_row_div, columns, product, html_label)
        if result:
            return result
        product_row_div = product_row_div.find_next(
            "div", class_=re.compile("Panel_container.*")
        )
    return ""


def process_table_row(product_row_div, columns, product, html_label):
    # ic(product_row_div)
    if "farming" in product.lower():
        product_type = "farming"
    else:
        product_type = "liquidity pool"
    # ic(product_type)
    type_marker = product_row_div.find(
        "div",
        class_=re.compile("BookMark_bookmark*"),
        text=re.compile(product_type, re.IGNORECASE),
    )
    if not type_marker:
        # print(f"Type marker not found for {product} {product_type}")
        return ""

    pool_components = html_label.split("+")
    remove_me = ["(Multichain)", "(Bridged)"]

    for component in pool_components:
        fomatted_component = component
        for str in remove_me:
            fomatted_component = fomatted_component.replace(str, "")
        fomatted_component = fomatted_component.strip()
        link = product_row_div.find_next(
            "a", text=re.compile(fomatted_component + "*", re.IGNORECASE)
        )
        if not link:
            print(f"Link not found for {product} pool component {component}")
            return ""

    table_row = product_row_div.find_next(
        "div", class_=re.compile("table_contentRow.*")
    )

    next_col = table_row.find_next("div")
    # print("col1:", next_col)
    for col in range(2, columns + 1):
        next_col = next_col.find_next_sibling("div")
        # print(f"col{col}: {next_col}")

    if not next_col:
        return ""
    return next_col.text
