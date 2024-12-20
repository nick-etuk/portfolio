import re
from icecream import ic


def liquidity_pool(columns, product, chain, project, html_label):
    print("=>liquidity_pool")
    ic(product, chain, project, html_label)
    # non-standard selector
    project_label = chain + "_" + project
    marker = html.find("div", id=re.compile(project_label, re.IGNORECASE))
    if not marker:
        print(f"Div not found for {product} {project_label}")
        return ""
    product_div = marker.find_parent("div")
    ic(product_div)
    product_row_div = product_div.find_next(
        "div", class_=re.compile("Panel_container.*")
    )
    product_type = ""
    if "liquidity pool" in product.lower():
        product_type = "liquidity pool"
    if "farming" in product.lower():
        product_type = "farming"

    if product_type:
        farm_marker = product_div.find(text=re.compile(product_type, re.IGNORECASE))
        if not farm_marker:
            return ""
        parent1 = farm_marker.find_parent("div")
        if not parent1:
            return ""
        parent2 = parent1.find_parent("div")
        if not parent2:
            return ""
        parent3 = parent2.find_parent("div")
        if not parent3:
            return ""
        parent = parent3.find_parent("div")
        if not parent:
            return ""

        ic(parent)
        # div1 = html.find_next(
        #     "div", id=re.compile(project_label, re.IGNORECASE)
        # )
        # print("***** bp  1 *****")
        # ic(div1)
        pool_components = html_label.split("+")

        for component in pool_components:
            link = parent.find_next(
                "a", text=re.compile(component.strip(), re.IGNORECASE)
            )
            if not link:
                print(f"Link not found for {product} pool component {component}")
                return ""
    else:
        return ""  # todo: implement case where text_before is not found
        # parent = html.find("div", id=re.compile(project_label, re.IGNORECASE))
        parent = ""

    if not parent:
        return ""
    table_row = parent.find_next("div", class_=re.compile("table_contentRow.*"))

    next_col = table_row.find_next("div")
    # print("col1:", next_col)
    for col in range(2, columns + 1):
        next_col = next_col.find_next_sibling("div")
        # print(f"col{col}: {next_col}")

    if not next_col:
        return ""
    return next_col.text
